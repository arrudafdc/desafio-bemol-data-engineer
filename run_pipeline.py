import sys
import os
from datetime import datetime
from pathlib import Path

try:
    from papermill import execute_notebook
except ImportError:
    print("Instale: pip install papermill")
    sys.exit(1)


os.chdir(Path.cwd() / "notebooks")
output_dir = Path.cwd().parent / "output"
output_dir.mkdir(exist_ok=True)

notebooks = [
    ("bronze_products_carts.ipynb", "Bronze: Carts & Products"),
    ("bronze_users.ipynb", "Bronze: Users"),
    ("silver_products_sales.ipynb", "Silver: Products Analytics"),
    ("silver_users.ipynb", "Silver: Users"),
]

print("\n" + "="*50)
print("PIPELINE BEMOL - DATA ENGINEER")
print("="*50 + "\n")

start = datetime.now()
failed = []

for notebook, name in notebooks:
    print(f"Iniciando: {name}")
    try:
        execute_notebook(
            input_path=notebook,
            output_path=str(output_dir / notebook)
        )
        print(f"Concluido: {name}\n")
    except Exception as e:
        print(f"Erro em {name}: {str(e)}\n")
        failed.append(name)
        if "bronze" in name.lower():
            break

duration = (datetime.now() - start).total_seconds()
print("="*50)
print(f"Tempo: {duration/60:.1f}m | Sucesso: {len(notebooks)-len(failed)}/{len(notebooks)}")

if failed:
    print(f"Falhas: {', '.join(failed)}")
    sys.exit(1)

print("Pipeline concluido com sucesso!\n")
sys.exit(0)