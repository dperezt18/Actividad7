from __future__ import annotations

from dataclasses import dataclass

PUNTAJE_MINIMO: int = 0
PUNTAJE_MAXIMO: int = 3


@dataclass
class Respuesta:
    """Representa la respuesta a un ítem del cuestionario GAD-7."""

    numero_item: int
    valor: int
    descripcion_item: str

    def __post_init__(self) -> None:
        if not (PUNTAJE_MINIMO <= self.valor <= PUNTAJE_MAXIMO):
            raise ValueError(
                f"Valor debe estar entre {PUNTAJE_MINIMO} y {PUNTAJE_MAXIMO},"
                f" se recibió {self.valor}."
            )

    def to_dict(self) -> dict:
        """Serializa la respuesta a diccionario."""
        return {
            "numero_item": self.numero_item,
            "valor": self.valor,
            "descripcion_item": self.descripcion_item,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Respuesta:
        """Deserializa una respuesta desde diccionario."""
        return cls(
            numero_item=data["numero_item"],
            valor=data["valor"],
            descripcion_item=data["descripcion_item"],
        )
