"""
Pacote principal do Diário de Bordo.

Exporta os principais componentes para acesso direto.
"""

from .controllers import ViagemController
from .models import Viagem, Veiculo
from .views import ViagemView

__version__ = "1.0.0"
__all__ = ['ViagemController', 'Viagem', 'Veiculo', 'ViagemView']