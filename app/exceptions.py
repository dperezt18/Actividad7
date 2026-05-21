class AppError(Exception):
    """Base para todas las excepciones de dominio."""


class EntidadNoEncontradaError(AppError):
    """Se lanza cuando no se encuentra una entidad por su identificador."""


class CuestionarioIncompletoError(AppError):
    """Se lanza cuando un cuestionario no tiene las 7 respuestas requeridas."""


class ValorFueraDeRangoError(AppError):
    """Se lanza cuando un valor numérico está fuera del rango permitido."""
