import csv
import sys

files = [
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (1).csv",
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (2).csv"
]
file_honorarios = "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (4).csv"

roles = set()

print("--- PLANTA / CONTRATA ROLES (EXTRACTED) ---")
for fpath in files:
    try:
        with open(fpath, 'r', encoding='iso-8859-1') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)
            
            # Find base index in header
            header_idx = -1
            for i, h in enumerate(headers):
                if "Cargo" in h and "funci" in h:
                    header_idx = i
                    break
            
            if header_idx == -1: continue

            for row in reader:
                # Heuristic: If row is longer than headers by 2, and starts with Year-like digit
                data_idx = header_idx
                if len(row) == len(headers) + 2:
                     data_idx = header_idx + 2
                
                if len(row) > data_idx:
                    val = row[data_idx].strip().upper()
                    if val and val not in roles:
                        roles.add(val)
                        print(val)
    except Exception as e:
        print(f"Error {fpath}: {e}")

print("\n--- HONORARIOS FUNCTIONS (EXTRACTED) ---")
# For file 4
try:
    with open(file_honorarios, 'r', encoding='iso-8859-1') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        # Headers: Nombre, Grado, Descripcion...
        # Data: 2025, Noviembre, Nombre, Grado...
        
        desc_idx = -1
        for i, h in enumerate(headers):
            if "escripci" in h and "funci" in h:
                desc_idx = i
                break
        
        if desc_idx != -1:
            for row in reader:
                real_idx = desc_idx
                if len(row) == len(headers) + 2:
                    real_idx = desc_idx + 2
                
                if len(row) > real_idx:
                    desc = row[real_idx].strip().upper()
                    # Print if it contains keywords like "ENCARGADO", "JEFE"
                    if "JEFE" in desc or "ENCARGADO" in desc or "COORDINADOR" in desc:
                         # Try to grab the first sentence or 80 chars
                         summary = desc.split('.')[0]
                         if len(summary) > 60: summary = summary[:60] + "..."
                         print(f"HONOR: {summary}")

except Exception as e:
    print(f"Error {file_honorarios}: {e}")

