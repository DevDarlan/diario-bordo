"""
Módulo principal para execução da aplicação.
"""
import os
import sys
from views.viagem_view import ViagemView

#sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Função principal para iniciar a aplicação."""
    app = ViagemView()
    app.executar()

if __name__ == "__main__":
    main()