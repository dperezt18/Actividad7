from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from app.models.estado_riesgo import EstadoRiesgo
from app.models.respuesta import Respuesta

TOTAL_PREGUNTAS: int = 7
UMBRAL_LEVE: int = 5
UMBRAL_MODERADO: int = 10
UMBRAL_SEVERO: int = 15


@dataclass
class CuestionarioGAD7:
    """Entidad que representa una aplicación del cuestionario GAD-7."""

    codigo_estudiante: str
    respuestas: List[Respuesta] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_aplicacion: datetime = field(default_factory=datetime.now)

    @property
    def puntaje_total(self) -> int:
        """Suma de los valores de todas las respuestas."""
        return sum(r.valor for r in self.respuestas)

    @property
    def nivel_severidad(self) -> EstadoRiesgo:
        """Nivel de riesgo calculado a partir del puntaje."""
        return self.clasificar_severidad()

    def validar(self) -> bool:
        """Verifica que el cuestionario tenga exactamente 7 respuestas."""
        return len(self.respuestas) == TOTAL_PREGUNTAS

    def calcular_puntaje(self) -> int:
        """Retorna el puntaje total del cuestionario."""
        return self.puntaje_total

    def clasificar_severidad(self) -> EstadoRiesgo:
        """Clasifica el nivel de ansiedad según los umbrales GAD-7 estándar."""
        puntaje = self.puntaje_total
        if puntaje >= UMBRAL_SEVERO:
            return EstadoRiesgo.SEVERO
        if puntaje >= UMBRAL_MODERADO:
            return EstadoRiesgo.MODERADO
        if puntaje >= UMBRAL_LEVE:
            return EstadoRiesgo.LEVE
        return EstadoRiesgo.NORMAL

    def to_dict(self) -> dict:
        """Serializa el cuestionario a diccionario."""
        return {
            "id": self.id,
            "codigo_estudiante": self.codigo_estudiante,
            "respuestas": [r.to_dict() for r in self.respuestas],
            "puntaje_total": self.puntaje_total,
            "nivel_severidad": self.nivel_severidad.value,
            "fecha_aplicacion": self.fecha_aplicacion.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> CuestionarioGAD7:
        """Deserializa un cuestionario desde diccionario."""
        return cls(
            id=data["id"],
            codigo_estudiante=data["codigo_estudiante"],
            respuestas=[
                Respuesta.from_dict(r) for r in data.get("respuestas", [])
            ],
            fecha_aplicacion=datetime.fromisoformat(
                data["fecha_aplicacion"]
            ),
        )
