import csv
import sys

files = [
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (1).csv",
    "/Users/felixsanhueza/fx_felixiando/gore_os/temp/TransparenciaActiva (2).csv"
]

for fpath in files:
    print(f"File: {fpath}")
    with open(fpath, 'r', encoding='iso-8859-1') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)
        print(f"Headers: {headers}")
        
        # Find index
        for i, h in enumerate(headers):
            if "Cargo" in h and "funci" in h:
                print(f"Found 'Cargo o funci...' at index {i}: {h}")
                # Print first 3 values
                count = 0
                for row in reader:
                    if len(row) > i:
                        print(f"Sample Row[{i}]: {row[i]}")
                        count += 1
                        if count >= 3: break
                break
            # Check for Estamento to see if confused
            if "Estamento" in h:
                 print(f"Found 'Estamento' at index {i}: {h}")
                 
