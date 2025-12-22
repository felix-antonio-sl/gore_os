import csv
import sys

files_roles = [
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (1).csv",
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (2).csv"
]
file_honorarios = "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (4).csv"

unique_titles = set()

print("--- PLANTA / CONTRATA ROLES ---")
for fpath in files_roles:
    try:
        with open(fpath, 'r', encoding='iso-8859-1') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            # Find column
            col_idx = -1
            for i, h in enumerate(headers):
                if "Cargo o funci" in h:
                    col_idx = i
                    break
            
            if col_idx == -1: continue

            for row in reader:
                if len(row) > col_idx:
                    val = row[col_idx].strip().upper()
                    if val and val not in unique_titles:
                        unique_titles.add(val)
                        print(val)
    except Exception as e:
        print(f"Error {fpath}: {e}")

print("\n--- HONORARIOS KEYWORDS ---")
# Scan descriptions for "Encargado", "Jefe", "Coordinador", "Asesor"
keywords = ["ENCARGADO", "JEFE", "COORDINADOR", "ASESOR", "ARQUITECTO", "INGENIERO", "ANALISTA"]
honorarios_roles = set()

try:
    with open(file_honorarios, 'r', encoding='iso-8859-1') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        col_idx = -1
        for i, h in enumerate(headers):
            if "escripci" in h and "funci" in h:
                col_idx = i
                break
        
        if col_idx != -1:
            for row in reader:
                if len(row) > col_idx:
                    desc = row[col_idx].strip().upper()
                    # heuristic: find lines starting with these or containing "COORDINAR", "LIDERAR"
                    for kw in keywords:
                        if kw in desc:
                            # Extract a snippet around the keyword or just the keyword usage
                            # For now, just print unique keywords found combined with context if short
                            # Actually, listing unique descriptions is too much.
                            # Let's try to extract titles like "COORDINADOR DE..."
                            import re
                            match = re.search(rf"({kw}\s+DE\s+[A-Z\s]+)", desc)
                            if match:
                                role = match.group(1).split('.')[0].split(',')[0] # rough truncation
                                if len(role) < 50 and role not in honorarios_roles:
                                    honorarios_roles.add(role)
                                    print(role)
except Exception as e:
    print(f"Error {file_honorarios}: {e}")

