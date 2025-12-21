import csv
import re
import sys

files = [
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (1).csv",
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (2).csv",
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (4).csv"
]

roles_found = set()
units_found = set()

def clean_text(text):
    if not text: return ""
    # Remove encoding artifacts if present, though python open 'r' with utf-8 or latin-1 usually handles it.
    # The files seem to have mixed encoding or are ISO-8859-1.
    return text.strip().replace('', 'ñ').replace('', 'NN').upper()

print("--- ROLES EXTRACTED FROM FILES 1 & 2 (PLANTA/CONTRATA) ---")
for fpath in files[:2]:
    try:
        with open(fpath, 'r', encoding='latin-1', errors='replace') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            # Find index of 'Cargo o funci...n'
            idx = -1
            for i, h in enumerate(headers):
                if "Cargo o funci" in h:
                    idx = i
                    break
            
            if idx == -1: continue

            for row in reader:
                if len(row) > idx:
                    role = clean_text(row[idx])
                    if role and role not in roles_found:
                        roles_found.add(role)
                        print(role)
    except Exception as e:
        print(f"Error reading {fpath}: {e}")

print("\n--- FUNCTIONS EXTRACTED FROM FILE 4 (HONORARIOS) ---")
# Only print summary or keywords, as descriptions are long
try:
    with open(files[2], 'r', encoding='latin-1', errors='replace') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        # Find index of 'Descripci...n de la funci...n'
        idx = -1
        for i, h in enumerate(headers):
            if "Descripci" in h and "funci" in h:
                idx = i
                break
        
        if idx != -1:
            for row in reader:
                if len(row) > idx:
                    desc = clean_text(row[idx])
                    # Extract potential role-like keywords (e.g., "ARQUITECTO", "APOYO TÉCNICO")
                    # Just print first 60 chars for scan
                    print(desc[:80] + "...")
except Exception as e:
    print(f"Error reading {files[2]}: {e}")
