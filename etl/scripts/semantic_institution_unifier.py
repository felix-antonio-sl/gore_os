import csv
import re
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent / "normalized"


def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def clean_name(name):
    if not name:
        return ""
    n = name.upper().strip()
    n = re.sub(r'[",.\-()\[\]/]', " ", n)
    n = re.sub(r"\s+", " ", n).strip()

    # Normalization rules
    n = re.sub(r"\bI\s+MUNICIPALIDAD\b", "MUNICIPALIDAD", n)
    n = re.sub(r"\bILUSTRE\s+MUNICIPALIDAD\b", "MUNICIPALIDAD", n)
    n = re.sub(r"\bMUNI\b", "MUNICIPALIDAD", n)
    n = re.sub(r"\bMUN\b", "MUNICIPALIDAD", n)

    # Semantic noise reduction
    semantic_stop_words = [
        r"\bILUSTRE\b",
        r"\bGENERAL\b",
        r"\bSOCIAL\b",
        r"\bCULTURAL\b",
        r"\bDEPORTIV[OA]\b",
        r"\bRECREATIV[OA]\b",
        r"\bESTUDIANTIL\b",
        r"\bVECINAL\b",
        r"\bFOLCLORIC[OA]\b",
        r"\bARTISTIC[OA]\b",
        r"\bADULTO\s+MAYOR\b",
        r"\bJUVENIL\b",
        r"\bCAMPESIN[OA]\b",
        r"\bS\s+F\s+LUCRO\b",
        r"\bSIN\s+FINES?\s+DE\s+LUCRO\b",
        r"\bÑUBLE\b",
    ]
    for pattern in semantic_stop_words:
        n = re.sub(pattern, " ", n)

    # Connectors
    for word in ["DE", "Y", "LA", "EL", "LAS", "LOS", "DEL", "PARA"]:
        n = re.sub(rf"\b{word}\b", " ", n)

    return re.sub(r"\s+", " ", n).strip()


def run_normalization():
    input_file = BASE_DIR / "dimensions" / "dim_institucion_unificada.csv"
    output_file = BASE_DIR / "dimensions" / "dim_institucion_unificada_nlp.csv"
    mapping_file = BASE_DIR / "metadata" / "institution_id_mapping.csv"

    if not input_file.exists():
        return

    institutions = []
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["name_cleaned"] = clean_name(
                row.get("nombre_normalizado", "") or row.get("nombre_original", "")
            )
            institutions.append(row)

    canonical_map = {}
    rut_groups = defaultdict(list)
    no_rut_list = []

    for inst in institutions:
        rut = inst.get("rut", "").strip()
        if rut and rut != "0" and len(rut) > 5:
            # Clean RUT format
            rut = re.sub(r"[.\-]", "", rut).upper()
            rut_groups[rut].append(inst)
        else:
            no_rut_list.append(inst)

    rut_representatives = []
    for rut, group in rut_groups.items():
        best = sorted(
            group, key=lambda x: len(x.get("nombre_normalizado", "")), reverse=True
        )[0]
        best["rep_clean"] = best["name_cleaned"]
        rut_representatives.append(best)
        for member in group:
            canonical_map[member["id"]] = best["id"]

    new_rows = list(rut_representatives)
    processed_no_rut = set()
    no_rut_list = sorted(no_rut_list, key=lambda x: x["name_cleaned"])

    for i, inst in enumerate(no_rut_list):
        if inst["id"] in processed_no_rut:
            continue
        group = [inst]
        processed_no_rut.add(inst["id"])
        window = 30
        for j in range(i + 1, min(i + window + 1, len(no_rut_list))):
            other = no_rut_list[j]
            if other["id"] in processed_no_rut:
                continue
            dist = levenshtein_distance(inst["name_cleaned"], other["name_cleaned"])
            limit = max(2, int(len(inst["name_cleaned"]) * 0.15))
            if dist <= limit:
                group.append(other)
                processed_no_rut.add(other["id"])

        found_id = None
        for rep in rut_representatives:
            dist = levenshtein_distance(inst["name_cleaned"], rep["rep_clean"])
            if dist <= 2:
                found_id = rep["id"]
                break

        if found_id:
            for member in group:
                canonical_map[member["id"]] = found_id
        else:
            best = sorted(
                group, key=lambda x: len(x.get("nombre_normalizado", "")), reverse=True
            )[0]
            for member in group:
                canonical_map[member["id"]] = best["id"]
            new_rows.append(best)

    final_output = []
    seen_ids = set()
    for row in new_rows:
        cid = canonical_map.get(row["id"], row["id"])
        if cid not in seen_ids:
            final_output.append(
                {
                    "id": cid,
                    "nombre_original": row["nombre_original"],
                    "nombre_normalizado": row["nombre_normalizado"],
                    "nombre_nlp": row["name_cleaned"],
                    "rut": row.get("rut", ""),
                    "fuente_original": row.get("fuente_original", ""),
                    "tipo_institucion": row.get("tipo_institucion", ""),
                }
            )
            seen_ids.add(cid)

    with open(output_file, "w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "id",
            "nombre_original",
            "nombre_normalizado",
            "nombre_nlp",
            "rut",
            "fuente_original",
            "tipo_institucion",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_output)

    with open(mapping_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["old_id", "canonical_id"])
        for old_id, cid in canonical_map.items():
            writer.writerow([old_id, cid])

    return canonical_map, final_output


def link_all_facts(canonical_map, unified_dim):
    """
    Perform deep linking of facts to the unified dimension.
    """
    # Build lookup maps
    rut_map = {}
    name_map = {}
    for inst in unified_dim:
        rut = re.sub(r"[.\-]", "", inst.get("rut", "")).upper()
        if rut and len(rut) > 5:
            rut_map[rut] = inst["id"]
        name_map[inst["nombre_nlp"]] = inst["id"]

    fact_subdir = BASE_DIR / "facts"
    for fact_file in fact_subdir.glob("*.csv"):
        rows = []
        updated = False
        with open(fact_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = list(reader.fieldnames)

            # Map column names
            # ID columns
            id_cols = [c for c in fieldnames if c in ("institucion_id", "ejecutor_id")]
            # Name/RUT columns
            rut_col = next(
                (
                    c
                    for c in fieldnames
                    if "rut" in c.lower() and "institucion" in c.lower()
                ),
                None,
            )
            name_col = next(
                (
                    c
                    for c in fieldnames
                    if "nombre" in c.lower() and "institucion" in c.lower()
                ),
                None,
            )
            # Special case for FRIL
            if fact_file.name == "fact_fril.csv":
                name_col = "unidad_tecnica"
                if "ejecutor_id" not in fieldnames:
                    fieldnames.append("ejecutor_id")
                    updated = True
                id_cols.append("ejecutor_id")
            # Special case for 8%
            if fact_file.name == "fact_rendicion_8pct.csv":
                if "institucion_id" not in fieldnames:
                    fieldnames.append("institucion_id")
                    updated = True
                id_cols.append("institucion_id")

            for row in reader:
                # 1. Update existing IDs
                for col in id_cols:
                    if col in row and row[col] in canonical_map:
                        if row[col] != canonical_map[row[col]]:
                            row[col] = canonical_map[row[col]]
                            updated = True

                # 2. Link by RUT or Name if ID is missing
                target_id_col = (
                    "institucion_id"
                    if "institucion_id" in fieldnames
                    else ("ejecutor_id" if "ejecutor_id" in fieldnames else None)
                )
                if target_id_col and (
                    not row.get(target_id_col) or row[target_id_col] == ""
                ):
                    match_id = None
                    if rut_col and row.get(rut_col):
                        crut = re.sub(r"[.\-]", "", row[rut_col]).upper()
                        match_id = rut_map.get(crut)
                    if not match_id and name_col and row.get(name_col):
                        cname = clean_name(row[name_col])
                        match_id = name_map.get(cname)

                    if match_id:
                        row[target_id_col] = match_id
                        updated = True
                rows.append(row)

        if updated:
            temp = fact_file.with_suffix(".tmp")
            with open(temp, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            os.replace(temp, fact_file)
            print(f"  Linked/Updated: {fact_file.name}")


def link_documents(canonical_map, unified_dim):
    """
    Link doc_documento.csv remitentes to institutions.
    """
    doc_file = BASE_DIR / "documents" / "doc_documento.csv"
    if not doc_file.exists():
        return

    # Build lookup map for clean names
    name_map = {}
    for inst in unified_dim:
        name_map[inst["nombre_nlp"]] = inst["id"]

    rows = []
    updated = False

    with open(doc_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)

        if "institucion_id" not in fieldnames:
            fieldnames.append("institucion_id")
            updated = True

        for row in reader:
            # Try to match remitente to institution
            if not row.get("institucion_id") or row["institucion_id"] == "":
                remitente = row.get("remitente")
                if remitente:
                    cname = clean_name(remitente)
                    match_id = name_map.get(cname)
                    if match_id:
                        row["institucion_id"] = match_id
                        updated = True
            rows.append(row)

    if updated:
        temp = doc_file.with_suffix(".tmp")
        with open(temp, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp, doc_file)
        print(f"  Linked/Updated: {doc_file.name}")


if __name__ == "__main__":
    print("Starting Deep Semantic Normalization & Fact Linking...")
    cmap, udim = run_normalization()
    if cmap:
        print("\nLinking Fact tables to Unified Dimension...")
        link_all_facts(cmap, udim)
        print("\nLinking Documents to Unified Dimension...")
        link_documents(cmap, udim)

        os.replace(
            BASE_DIR / "dimensions" / "dim_institucion_unificada_nlp.csv",
            BASE_DIR / "dimensions" / "dim_institucion_unificada.csv",
        )
        print(f"\nFinalized.")
