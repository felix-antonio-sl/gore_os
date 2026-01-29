"""
Base loader class for all ETL migrations

FASE 0 - Día 5: Implementación de LoaderBase
Clase abstracta base que implementa el pipeline común:
Load → Transform → Validate → Resolve FKs → Insert/Update
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
import sys
from pathlib import Path
from sqlalchemy import text

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.db import get_session
from utils.validators import validate_row
from utils.resolvers import resolve_foreign_keys, get_system_user_id

class LoaderBase(ABC):
    """
    Base class for all ETL loaders

    Implements common pipeline pattern:
    1. Load CSV into pandas DataFrame
    2. Transform each row to match target schema
    3. Validate transformed row
    4. Resolve foreign keys
    5. Insert or update in database

    Subclasses must implement:
    - transform_row(): Transform source row to target schema
    - get_natural_key(): Define natural key for deduplication
    """

    def __init__(
        self,
        csv_path: str,
        target_table: str,
        compatibility_score: int,
        batch_size: int = 1000,
        dry_run: bool = False
    ):
        """
        Initialize loader

        Args:
            csv_path: Path to source CSV file
            target_table: Target PostgreSQL table (e.g., 'core.person')
            compatibility_score: Compatibility score from assessment (0-100)
            batch_size: Number of records to process in each batch
            dry_run: If True, validate only without writing to database
        """
        self.csv_path = csv_path
        self.target_table = target_table
        self.compatibility_score = compatibility_score
        self.batch_size = batch_size
        self.dry_run = dry_run

        # State tracking
        self.df: Optional[pd.DataFrame] = None
        self.errors: List[Dict] = []
        self.warnings: List[Dict] = []
        self.success_count: int = 0
        self.skip_count: int = 0
        self.update_count: int = 0
        self.insert_count: int = 0

        # Timestamps
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

    # =========================================================================
    # Abstract methods - must be implemented by subclasses
    # =========================================================================

    @abstractmethod
    def transform_row(self, row: pd.Series) -> Dict:
        """
        Transform source CSV row to target database row

        Args:
            row: Pandas Series representing one CSV row

        Returns:
            Dictionary with target table column names and values

        Example:
            >>> def transform_row(self, row):
            ...     return {
            ...         'id': uuid.uuid5(uuid.NAMESPACE_DNS, f"person:{row['rut']}"),
            ...         'tax_id': row['rut'],
            ...         'first_name': row['nombres'],
            ...         'last_name': row['apellido_paterno']
            ...     }
        """
        pass

    @abstractmethod
    def get_natural_key(self, row: pd.Series) -> str:
        """
        Get natural key for deduplication

        Args:
            row: Pandas Series representing one CSV row

        Returns:
            String that uniquely identifies this row (e.g., RUT, codigo_bip)

        Example:
            >>> def get_natural_key(self, row):
            ...     return row['rut']  # For persons
            ...     return row['codigo_bip']  # For IPRs
        """
        pass

    # =========================================================================
    # Pipeline methods
    # =========================================================================

    def load_csv(self) -> pd.DataFrame:
        """
        Load CSV file into pandas DataFrame

        Returns:
            Loaded DataFrame

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            pd.errors.ParserError: If CSV format is invalid
        """
        try:
            self.df = pd.read_csv(self.csv_path)
            return self.df
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading CSV: {e}")

    def validate_transformed_row(self, row: Dict) -> bool:
        """
        Validate transformed row against target schema

        Args:
            row: Transformed row dictionary

        Returns:
            True if valid, False otherwise (warnings added to self.warnings)
        """
        is_valid, errors = validate_row(row, self.target_table)

        if not is_valid:
            self.warnings.append({
                'natural_key': self.get_natural_key_from_dict(row),
                'validation_errors': errors,
                'row': row
            })

        return is_valid

    def resolve_row_fks(self, row: Dict) -> Dict:
        """
        Resolve foreign keys for row

        Args:
            row: Transformed row with FK placeholders

        Returns:
            Row with resolved FK UUIDs

        Raises:
            ValueError: If required FK cannot be resolved
        """
        return resolve_foreign_keys(row, self.target_table)

    def insert_or_update(self, row: Dict):
        """
        Insert or update row in database (UPSERT)

        Args:
            row: Fully transformed and validated row

        Raises:
            Exception: If database operation fails
        """
        if self.dry_run:
            # In dry-run mode, just count as success
            self.success_count += 1
            return

        try:
            with get_session() as session:
                # Determine if record exists
                natural_key = self.get_natural_key_from_dict(row)
                exists = self.check_exists(session, natural_key)

                # Apply pre_insert hook (for data transformations like dict → JSON)
                row = self.pre_insert(row)

                if exists:
                    # Update existing record
                    self.update_record(session, row, natural_key)
                    self.update_count += 1
                else:
                    # Insert new record
                    self.insert_record(session, row)
                    self.insert_count += 1

                session.commit()
                self.success_count += 1

                # Call post_insert hook after successful commit
                self.post_insert(row)

        except Exception as e:
            self.errors.append({
                'natural_key': natural_key,
                'error': str(e),
                'row': row
            })

    def check_exists(self, session, natural_key: str) -> bool:
        """
        Check if record with natural key already exists

        Args:
            session: SQLAlchemy session
            natural_key: Natural key value

        Returns:
            True if exists, False otherwise
        """
        # Get natural key columns for this table
        from utils.deduplication import get_natural_key_for_table

        key_columns = get_natural_key_for_table(self.target_table)

        if not key_columns:
            return False

        # Build WHERE clause
        where_conditions = []
        params = {}

        for col in key_columns:
            where_conditions.append(f"{col} = :{col}")
            # Extract value from natural_key string
            # (This is simplified - in production, use proper parsing)
            params[col] = natural_key

        where_clause = " AND ".join(where_conditions)

        query = f"""
            SELECT 1 FROM {self.target_table}
            WHERE {where_clause}
              AND deleted_at IS NULL
            LIMIT 1
        """

        result = session.execute(text(query), params).fetchone()
        return result is not None

    def insert_record(self, session, row: Dict):
        """
        Insert new record into database

        Args:
            session: SQLAlchemy session
            row: Record to insert
        """
        # Build INSERT statement
        columns = list(row.keys())
        placeholders = [f":{col}" for col in columns]

        query = f"""
            INSERT INTO {self.target_table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
        """

        session.execute(text(query), row)

    def update_record(self, session, row: Dict, natural_key: str):
        """
        Update existing record in database

        Args:
            session: SQLAlchemy session
            row: Updated record data
            natural_key: Natural key for WHERE clause
        """
        # Build UPDATE statement
        columns = [col for col in row.keys() if col != 'id']  # Don't update ID
        set_clause = ", ".join([f"{col} = :{col}" for col in columns])

        # Build WHERE clause based on natural key
        from utils.deduplication import get_natural_key_for_table
        key_columns = get_natural_key_for_table(self.target_table)

        where_conditions = []
        for col in key_columns:
            where_conditions.append(f"{col} = :{col}")

        where_clause = " AND ".join(where_conditions)

        query = f"""
            UPDATE {self.target_table}
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE {where_clause} AND deleted_at IS NULL
        """

        session.execute(text(query), row)

    def get_natural_key_from_dict(self, row: Dict) -> str:
        """
        Extract natural key from transformed row dictionary

        Args:
            row: Transformed row dictionary

        Returns:
            Natural key string
        """
        from utils.deduplication import get_natural_key_for_table

        key_columns = get_natural_key_for_table(self.target_table)
        key_values = [str(row.get(col, '')) for col in key_columns]
        return '|'.join(key_values)

    # =========================================================================
    # Orchestration
    # =========================================================================

    def run(self):
        """
        Run full migration pipeline for this loader

        Pipeline:
        1. Load CSV
        2. For each row:
           a. Transform
           b. Validate
           c. Resolve FKs
           d. Insert/Update
        3. Report results
        """
        self.start_time = datetime.now()

        print(f"\n{'='*70}")
        print(f"🚀 Loading: {Path(self.csv_path).name}")
        print(f"📊 Target: {self.target_table}")
        print(f"⭐ Compatibility Score: {self.compatibility_score}/100")
        if self.dry_run:
            print(f"🔍 DRY RUN MODE (no database writes)")
        print('='*70)

        # Load CSV
        try:
            self.load_csv()
            print(f"📥 Loaded {len(self.df):,} rows from CSV")
        except Exception as e:
            print(f"❌ Failed to load CSV: {e}")
            return

        # Process rows
        total_rows = len(self.df)
        for idx, row in self.df.iterrows():
            # Progress indicator every 100 rows
            if (idx + 1) % 100 == 0:
                print(f"  Progress: {idx + 1:,}/{total_rows:,} ({(idx+1)/total_rows*100:.1f}%)")

            try:
                # 1. Transform
                transformed = self.transform_row(row)

                # 2. Validate
                if not self.validate_transformed_row(transformed):
                    self.skip_count += 1
                    continue

                # 3. Resolve FKs
                resolved = self.resolve_row_fks(transformed)

                # 4. Insert/Update
                self.insert_or_update(resolved)

            except Exception as e:
                self.errors.append({
                    'row_index': idx,
                    'natural_key': self.get_natural_key(row),
                    'error': str(e),
                    'row_data': row.to_dict()
                })

        self.end_time = datetime.now()

        # Report
        self.print_report()
        self.save_errors()

    # =========================================================================
    # Reporting
    # =========================================================================

    def print_report(self):
        """Print migration report to console"""
        duration = (self.end_time - self.start_time).total_seconds()
        total = len(self.df)

        print(f"\n{'-'*70}")
        print(f"📊 MIGRATION REPORT - {self.target_table}")
        print(f"{'-'*70}")
        print(f"✅ Success:  {self.success_count:5,}/{total:,} ({self.success_count/total*100:.1f}%)")
        print(f"   Inserted: {self.insert_count:5,}")
        print(f"   Updated:  {self.update_count:5,}")
        print(f"⚠️  Warnings: {len(self.warnings):5,}")
        print(f"❌ Errors:   {len(self.errors):5,}")
        print(f"⏭️  Skipped:  {self.skip_count:5,}")
        print(f"⏱️  Duration: {duration:.2f}s ({total/duration:.0f} rows/s)")
        print(f"{'-'*70}")

        if len(self.warnings) > 0:
            print(f"\n⚠️  First 5 warnings:")
            for i, warning in enumerate(self.warnings[:5], 1):
                print(f"   {i}. {warning.get('natural_key')}: {warning.get('validation_errors')}")

        if len(self.errors) > 0:
            print(f"\n❌ First 5 errors:")
            for i, error in enumerate(self.errors[:5], 1):
                print(f"   {i}. {error.get('natural_key')}: {error.get('error')}")

    def save_errors(self):
        """Save errors and warnings to CSV files for review"""
        if len(self.errors) > 0:
            error_file = Path(self.csv_path).parent.parent / 'migration_logs' / f"errors_{self.target_table.replace('.', '_')}.csv"
            error_file.parent.mkdir(parents=True, exist_ok=True)

            pd.DataFrame(self.errors).to_csv(error_file, index=False)
            print(f"❌ Errors saved to: {error_file}")

        if len(self.warnings) > 0:
            warning_file = Path(self.csv_path).parent.parent / 'migration_logs' / f"warnings_{self.target_table.replace('.', '_')}.csv"
            warning_file.parent.mkdir(parents=True, exist_ok=True)

            pd.DataFrame(self.warnings).to_csv(warning_file, index=False)
            print(f"⚠️  Warnings saved to: {warning_file}")

    # =========================================================================
    # Hooks for subclasses
    # =========================================================================

    def pre_insert(self, row: Dict) -> Dict:
        """
        Hook called before insert/update

        Subclasses can override to add custom logic

        Args:
            row: Row about to be inserted

        Returns:
            Modified row (or same row)
        """
        return row

    def post_insert(self, row: Dict):
        """
        Hook called after successful insert/update

        Subclasses can override to add custom logic (e.g., create related records)

        Args:
            row: Row that was inserted
        """
        pass

    # =========================================================================
    # Utility methods
    # =========================================================================

    def get_system_user_id(self):
        """Get system user UUID for created_by fields"""
        return get_system_user_id()
