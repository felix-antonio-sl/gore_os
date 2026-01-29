"""
Deduplication strategies for ETL migration

FASE 0 - Día 4-5: Implementación de utilities
Estrategias para detectar y manejar registros duplicados en migración
"""
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
import hashlib
import json

# =============================================================================
# Natural key strategies
# =============================================================================

def get_natural_key_for_table(table: str) -> List[str]:
    """
    Get natural key columns for a table

    Args:
        table: Target table name (e.g., 'core.person')

    Returns:
        List of column names that form the natural key
    """
    natural_keys = {
        'core.person': ['tax_id'],
        'core.user': ['email'],
        'core.organization': ['tax_id', 'name'],  # Composite key
        'core.ipr': ['codigo_bip'],
        'core.agreement': ['number'],
        'core.budget_program': ['budget_classifier', 'year'],
        'core.document': ['number'],
        'txn.event': ['id'],  # Events always use UUID
    }

    return natural_keys.get(table, ['id'])

def generate_natural_key_hash(row: Dict, key_columns: List[str]) -> str:
    """
    Generate hash from natural key columns

    Args:
        row: Data row as dictionary
        key_columns: List of columns to include in hash

    Returns:
        SHA256 hash of natural key
    """
    # Extract values in consistent order
    key_values = []
    for col in sorted(key_columns):
        value = row.get(col)
        # Normalize value (handle None, convert to string)
        if value is None:
            normalized = 'NULL'
        elif isinstance(value, (int, float)):
            normalized = str(value)
        else:
            normalized = str(value).strip().upper()
        key_values.append(normalized)

    # Create hash
    key_string = '|'.join(key_values)
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()

# =============================================================================
# Deduplication strategies
# =============================================================================

def deduplicate_dataframe(
    df: pd.DataFrame,
    strategy: str = 'keep_first',
    subset: List[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Deduplicate DataFrame using specified strategy

    Args:
        df: Input DataFrame
        strategy: Deduplication strategy:
            - 'keep_first': Keep first occurrence (default)
            - 'keep_last': Keep last occurrence
            - 'keep_newest': Keep record with latest timestamp
            - 'merge': Merge duplicate records (combine non-null values)
        subset: Columns to consider for identifying duplicates
                (if None, uses all columns)

    Returns:
        Tuple of (deduplicated_df, duplicates_df)
    """
    if df.empty:
        return df, pd.DataFrame()

    if subset is None:
        subset = df.columns.tolist()

    if strategy == 'keep_first':
        deduplicated = df.drop_duplicates(subset=subset, keep='first')
        duplicates = df[df.duplicated(subset=subset, keep='first')]

    elif strategy == 'keep_last':
        deduplicated = df.drop_duplicates(subset=subset, keep='last')
        duplicates = df[df.duplicated(subset=subset, keep='last')]

    elif strategy == 'keep_newest':
        if 'created_at' not in df.columns and 'fecha' not in df.columns:
            # Fallback to keep_last if no timestamp column
            return deduplicate_dataframe(df, strategy='keep_last', subset=subset)

        timestamp_col = 'created_at' if 'created_at' in df.columns else 'fecha'
        df_sorted = df.sort_values(timestamp_col, ascending=False)
        deduplicated = df_sorted.drop_duplicates(subset=subset, keep='first')
        duplicates = df_sorted[df_sorted.duplicated(subset=subset, keep='first')]

    elif strategy == 'merge':
        deduplicated, duplicates = _merge_duplicates(df, subset)

    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    return deduplicated, duplicates

def _merge_duplicates(df: pd.DataFrame, subset: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge duplicate records by combining non-null values

    Args:
        df: Input DataFrame
        subset: Columns to identify duplicates

    Returns:
        Tuple of (merged_df, duplicates_df)
    """
    # Create groups based on subset
    groups = df.groupby(subset)

    merged_rows = []
    duplicates_list = []

    for name, group in groups:
        if len(group) == 1:
            # No duplicates
            merged_rows.append(group.iloc[0].to_dict())
        else:
            # Multiple records - merge them
            merged = _merge_group(group)
            merged_rows.append(merged)
            duplicates_list.extend(group.to_dict('records'))

    merged_df = pd.DataFrame(merged_rows)
    duplicates_df = pd.DataFrame(duplicates_list)

    return merged_df, duplicates_df

def _merge_group(group: pd.DataFrame) -> Dict:
    """
    Merge a group of duplicate records

    Strategy:
    - For each column, take first non-null value
    - For numeric columns, take max value
    - For dates, take latest value
    """
    merged = {}

    for col in group.columns:
        values = group[col].dropna()

        if len(values) == 0:
            merged[col] = None
        elif len(values) == 1:
            merged[col] = values.iloc[0]
        else:
            # Multiple non-null values
            dtype = values.dtype

            if pd.api.types.is_numeric_dtype(dtype):
                # For numeric: take max
                merged[col] = values.max()
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                # For dates: take latest
                merged[col] = values.max()
            else:
                # For strings: take first non-null
                merged[col] = values.iloc[0]

    return merged

# =============================================================================
# Fuzzy matching for organizations
# =============================================================================

def fuzzy_match_organizations(
    df: pd.DataFrame,
    name_column: str = 'nombre_institucion',
    threshold: float = 0.8
) -> pd.DataFrame:
    """
    Find potential duplicate organizations using fuzzy string matching

    Args:
        df: DataFrame with organization data
        name_column: Column containing organization names
        threshold: Similarity threshold (0-1)

    Returns:
        DataFrame with potential duplicates and similarity scores
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        print("Warning: rapidfuzz not installed. Skipping fuzzy matching.")
        return pd.DataFrame()

    potential_duplicates = []

    for i, row1 in df.iterrows():
        name1 = str(row1[name_column]).upper().strip()

        for j, row2 in df.iterrows():
            if i >= j:  # Skip self and already compared
                continue

            name2 = str(row2[name_column]).upper().strip()

            # Calculate similarity ratio
            ratio = fuzz.ratio(name1, name2) / 100.0

            if ratio >= threshold:
                potential_duplicates.append({
                    'id_1': row1['id'],
                    'name_1': row1[name_column],
                    'id_2': row2['id'],
                    'name_2': row2[name_column],
                    'similarity': ratio
                })

    return pd.DataFrame(potential_duplicates)

# =============================================================================
# Record linkage strategies
# =============================================================================

def link_records_by_multiple_keys(
    df: pd.DataFrame,
    key_columns_list: List[List[str]],
    priority: str = 'first'
) -> pd.DataFrame:
    """
    Link records using multiple key strategies with fallback

    Args:
        df: Input DataFrame
        key_columns_list: List of key column sets to try (in priority order)
        priority: How to handle multiple matches ('first', 'last', 'error')

    Returns:
        DataFrame with linked canonical IDs
    """
    df = df.copy()
    df['canonical_id'] = None

    for key_columns in key_columns_list:
        # Find records without canonical_id
        unlinked = df[df['canonical_id'].isnull()]

        if len(unlinked) == 0:
            break

        # Try to link using current key strategy
        for name, group in unlinked.groupby(key_columns):
            if len(group) == 0:
                continue

            # Assign canonical ID (use first record's ID)
            canonical_id = group.iloc[0]['id']

            # Update all records in group
            df.loc[group.index, 'canonical_id'] = canonical_id

    # Records still without canonical_id get their own ID
    df.loc[df['canonical_id'].isnull(), 'canonical_id'] = df.loc[df['canonical_id'].isnull(), 'id']

    return df

# =============================================================================
# Data quality checks
# =============================================================================

def check_duplicate_stats(df: pd.DataFrame, subset: List[str] = None) -> Dict:
    """
    Calculate duplicate statistics for DataFrame

    Args:
        df: Input DataFrame
        subset: Columns to check (None = all columns)

    Returns:
        Dictionary with duplicate statistics
    """
    if subset is None:
        subset = df.columns.tolist()

    total_rows = len(df)
    unique_rows = df.drop_duplicates(subset=subset)
    num_unique = len(unique_rows)
    num_duplicates = total_rows - num_unique

    # Find most duplicated values
    duplicate_counts = df[df.duplicated(subset=subset, keep=False)] \
        .groupby(subset).size() \
        .sort_values(ascending=False)

    return {
        'total_rows': total_rows,
        'unique_rows': num_unique,
        'duplicate_rows': num_duplicates,
        'duplicate_percentage': (num_duplicates / total_rows * 100) if total_rows > 0 else 0,
        'most_duplicated': duplicate_counts.head(10).to_dict() if len(duplicate_counts) > 0 else {}
    }

def identify_near_duplicates(
    df: pd.DataFrame,
    key_columns: List[str],
    similarity_threshold: float = 0.85
) -> pd.DataFrame:
    """
    Identify near-duplicates using string similarity

    Args:
        df: Input DataFrame
        key_columns: Columns to check for similarity
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        DataFrame with near-duplicate pairs and similarity scores
    """
    try:
        from rapidfuzz import fuzz
    except ImportError:
        print("Warning: rapidfuzz not installed. Skipping near-duplicate detection.")
        return pd.DataFrame()

    near_duplicates = []

    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i >= j:
                continue

            # Calculate similarity across key columns
            similarities = []
            for col in key_columns:
                val1 = str(row1[col]) if pd.notna(row1[col]) else ''
                val2 = str(row2[col]) if pd.notna(row2[col]) else ''

                if val1 and val2:
                    sim = fuzz.ratio(val1.upper(), val2.upper()) / 100.0
                    similarities.append(sim)

            if similarities:
                avg_similarity = sum(similarities) / len(similarities)

                if avg_similarity >= similarity_threshold:
                    near_duplicates.append({
                        'id_1': row1.get('id'),
                        'id_2': row2.get('id'),
                        'similarity': avg_similarity,
                        'columns_checked': key_columns
                    })

    return pd.DataFrame(near_duplicates)

# =============================================================================
# Utility functions
# =============================================================================

def export_duplicates_report(
    duplicates_df: pd.DataFrame,
    output_path: str,
    include_all_columns: bool = False
):
    """
    Export duplicates to CSV for manual review

    Args:
        duplicates_df: DataFrame with duplicate records
        output_path: Path to save CSV file
        include_all_columns: Include all columns or just key columns
    """
    if duplicates_df.empty:
        print("No duplicates to export")
        return

    duplicates_df.to_csv(output_path, index=False)
    print(f"✅ Duplicates report saved to: {output_path}")
    print(f"   Total duplicates: {len(duplicates_df)}")

def create_deduplication_mapping(
    df: pd.DataFrame,
    key_columns: List[str],
    id_column: str = 'id'
) -> Dict[str, str]:
    """
    Create mapping from duplicate IDs to canonical ID

    Args:
        df: DataFrame with records
        key_columns: Columns defining duplicates
        id_column: Column containing IDs

    Returns:
        Dictionary mapping old_id -> canonical_id
    """
    mapping = {}

    for name, group in df.groupby(key_columns):
        if len(group) <= 1:
            continue

        # First record is canonical
        canonical_id = group.iloc[0][id_column]

        # Map all IDs in group to canonical
        for idx, row in group.iterrows():
            mapping[row[id_column]] = canonical_id

    return mapping
