import glob
import os

print("DEBUG: Iniciando script de diagnostico")
with open("diag.log", "w") as f:
    f.write("Iniciado\n")
    files = glob.glob("/Users/felixsanhueza/Developer/goreos/model/stories/*.yml")[:5]
    f.write(f"Archivos encontrados: {len(files)}\n")
    for file in files:
        f.write(f"Procesando {file}\n")
    f.write("Finalizado\n")
print("DEBUG: Finalizado")
