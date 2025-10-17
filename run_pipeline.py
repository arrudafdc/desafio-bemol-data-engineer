"""
Pipeline de Orquestração - Desafio Bemol Data Engineer
Executa os 4 notebooks localmente com PySpark.
Uso:
    python run_pipeline.py
"""

import sys
from datetime import datetime
from pathlib import Path

try:
    from papermill import execute_notebook
except ImportError:
    print("Instale: pip install papermill")
    sys.exit(1)


class Pipeline:
    def __init__(self):
        import os
        self.root_dir = Path.cwd()
        self.notebooks_dir = self.root_dir / "notebooks"
        self.output_dir = self.root_dir / "output"
        self.failed = []
        self.start_time = datetime.now()
        
        # Cria diretório de output se não existir
        self.output_dir.mkdir(exist_ok=True)
        
        # Muda para diretório notebooks para que imports funcionem
        os.chdir(self.notebooks_dir)
    
    def run_notebook(self, notebook_name, display_name):
        """Executa um notebook"""
        print(f"🚀 Iniciando: {display_name}")
        
        notebook_path = Path(notebook_name)
        
        # Verifica se arquivo existe
        if not notebook_path.exists():
            print(f"❌ Arquivo não encontrado: {notebook_path}\n")
            self.failed.append(display_name)
            return False
        
        try:
            # Define arquivo de output
            output_file = self.output_dir / notebook_name
            
            # Executa notebook
            execute_notebook(
                input_path=str(notebook_path),
                output_path=str(output_file)
            )
            
            print(f"✅ Concluído: {display_name}\n")
            return True
        
        except Exception as e:
            print(f"❌ Erro em {display_name}: {str(e)}\n")
            self.failed.append(display_name)
            return False
    
    def run(self):
        """Executa pipeline completo"""
        print("\n" + "="*50)
        print("PIPELINE BEMOL - DATA ENGINEER")
        print("="*50 + "\n")

        notebooks = [
            ("bronze_products_carts.ipynb", "Bronze: Carts & Products"),
            ("bronze_users.ipynb", "Bronze: Users"),
            ("silver_products_sales.ipynb", "Silver: Products Analytics"),
            ("silver_users.ipynb", "Silver: Users"),
        ]
        
        total = len(notebooks)
        
        for notebook_name, display_name in notebooks:
            if not self.run_notebook(notebook_name, display_name):
                if "bronze" in display_name.lower():
                    print("⚠️  Bronze falhou. Abortando pipeline.\n")
                    break
        
        # Resumo
        duration = (datetime.now() - self.start_time).total_seconds()
        successful = total - len(self.failed)
        
        print("="*50)
        print(f"Tempo total: {duration/60:.1f}m")
        print(f"✅ Sucesso: {successful}/{total}")
        
        if self.failed:
            print(f"❌ Falhas: {', '.join(self.failed)}")
            return False
        
        print(f"✅ Pipeline concluído com sucesso!\n")
        return True


if __name__ == "__main__":
    pipeline = Pipeline()
    success = pipeline.run()
    sys.exit(0 if success else 1)



