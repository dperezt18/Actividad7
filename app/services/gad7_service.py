from typing import List

from app.exceptions import CuestionarioIncompletoError, EntidadNoEncontradaError
from app.interfaces.i_repository import IRepository
from app.models.cuestionario_gad7 import CuestionarioGAD7
from app.models.estado_riesgo import EstadoRiesgo
from app.models.respuesta import Respuesta


class GAD7Service:
    """Lógica de negocio para la gestión de cuestionarios GAD-7."""

    def __init__(self, repositorio: IRepository[CuestionarioGAD7]) -> None:
        self._repo = repositorio

    def crear_cuestionario(
        self, codigo_estudiante: str, respuestas: List[Respuesta]
    ) -> CuestionarioGAD7:
        """Crea y persiste un cuestionario completo para un estudiante."""
        cuestionario = CuestionarioGAD7(
            codigo_estudiante=codigo_estudiante,
            respuestas=respuestas,
        )
        if not cuestionario.validar():
            raise CuestionarioIncompletoError(
                "El cuestionario debe tener exactamente 7 respuestas."
            )
        return self._repo.crear(cuestionario)

    def listar_cuestionarios(self) -> List[CuestionarioGAD7]:
        """Retorna todos los cuestionarios almacenados."""
        return self._repo.listar()

    def buscar_cuestionario(self, id_cuestionario: str) -> CuestionarioGAD7:
        """Busca un cuestionario; lanza error si no existe."""
        cuestionario = self._repo.buscar_por_codigo(id_cuestionario)
        if cuestionario is None:
            raise EntidadNoEncontradaError(
                f"No se encontró el cuestionario con id '{id_cuestionario}'."
            )
        return cuestionario

    def actualizar_respuestas(
        self, id_cuestionario: str, nuevas_respuestas: List[Respuesta]
    ) -> CuestionarioGAD7:
        """Reemplaza las respuestas de un cuestionario existente."""
        cuestionario = self.buscar_cuestionario(id_cuestionario)
        cuestionario.respuestas = nuevas_respuestas
        if not cuestionario.validar():
            raise CuestionarioIncompletoError(
                "El cuestionario debe tener exactamente 7 respuestas."
            )
        return self._repo.actualizar(cuestionario)

    def eliminar_cuestionario(self, id_cuestionario: str) -> None:
        """Elimina un cuestionario por su ID."""
        self._repo.eliminar(id_cuestionario)

    def evaluar_riesgo(self, id_cuestionario: str) -> EstadoRiesgo:
        """Retorna el nivel de riesgo de ansiedad de un cuestionario."""
        cuestionario = self.buscar_cuestionario(id_cuestionario)
        return cuestionario.clasificar_severidad()
