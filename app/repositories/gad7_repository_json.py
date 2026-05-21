import json
from pathlib import Path
from typing import List, Optional

from app.exceptions import EntidadNoEncontradaError
from app.interfaces.i_repository import IRepository
from app.models.cuestionario_gad7 import CuestionarioGAD7

RUTA_DEFAULT: Path = Path("data/cuestionarios_gad7.json")


class GAD7RepositoryJSON(IRepository[CuestionarioGAD7]):
    """Repositorio que persiste CuestionarioGAD7 en un archivo JSON."""

    def __init__(self, ruta: Path = RUTA_DEFAULT) -> None:
        self._ruta = ruta
        self._ruta.parent.mkdir(parents=True, exist_ok=True)

    def _cargar(self) -> List[CuestionarioGAD7]:
        if not self._ruta.exists():
            return []
        with self._ruta.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return [CuestionarioGAD7.from_dict(d) for d in datos]

    def _guardar(self, cuestionarios: List[CuestionarioGAD7]) -> None:
        with self._ruta.open("w", encoding="utf-8") as archivo:
            json.dump(
                [c.to_dict() for c in cuestionarios],
                archivo,
                ensure_ascii=False,
                indent=2,
            )

    def crear(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Agrega el cuestionario al archivo JSON."""
        cuestionarios = self._cargar()
        cuestionarios.append(entidad)
        self._guardar(cuestionarios)
        return entidad

    def listar(self) -> List[CuestionarioGAD7]:
        """Carga y retorna todos los cuestionarios del archivo JSON."""
        return self._cargar()

    def buscar_por_codigo(self, codigo: str) -> Optional[CuestionarioGAD7]:
        """Busca un cuestionario por ID en el archivo JSON."""
        return next(
            (c for c in self._cargar() if c.id == codigo), None
        )

    def actualizar(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Reemplaza el cuestionario existente con el mismo ID."""
        cuestionarios = self._cargar()
        for i, c in enumerate(cuestionarios):
            if c.id == entidad.id:
                cuestionarios[i] = entidad
                self._guardar(cuestionarios)
                return entidad
        raise EntidadNoEncontradaError(
            f"Cuestionario con id '{entidad.id}' no encontrado."
        )

    def eliminar(self, codigo: str) -> None:
        """Elimina el cuestionario con el ID dado del archivo JSON."""
        cuestionarios = self._cargar()
        nuevos = [c for c in cuestionarios if c.id != codigo]
        if len(nuevos) == len(cuestionarios):
            raise EntidadNoEncontradaError(
                f"Cuestionario con id '{codigo}' no encontrado."
            )
        self._guardar(nuevos)
