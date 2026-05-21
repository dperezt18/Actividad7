from enum import Enum


class EstadoRiesgo(str, Enum):
    """Niveles de riesgo según el puntaje GAD-7."""

    NORMAL = "NORMAL"
    LEVE = "LEVE"
    MODERADO = "MODERADO"
    SEVERO = "SEVERO"
