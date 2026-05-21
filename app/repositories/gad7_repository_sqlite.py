import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Optional

from app.exceptions import EntidadNoEncontradaError
from app.interfaces.i_repository import IRepository
from app.models.cuestionario_gad7 import CuestionarioGAD7

RUTA_DEFAULT: Path = Path("data/cuestionarios_gad7.db")

DDL = """
CREATE TABLE IF NOT EXISTS cuestionarios_gad7 (
    id                TEXT PRIMARY KEY,
    codigo_estudiante TEXT NOT NULL,
    respuestas        TEXT NOT NULL,
    puntaje_total     INTEGER NOT NULL,
    nivel_severidad   TEXT NOT NULL,
    fecha_aplicacion  TEXT NOT NULL
);
"""


class GAD7RepositorySQLite(IRepository[CuestionarioGAD7]):
    """Repositorio que persiste CuestionarioGAD7 en una base de datos SQLite."""

    def __init__(self, ruta: Path = RUTA_DEFAULT) -> None:
        self._ruta = ruta
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        self._inicializar_tabla()

    def _inicializar_tabla(self) -> None:
        with self._conexion() as conn:
            conn.execute(DDL)

    @contextmanager
    def _conexion(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._ruta)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _fila_a_entidad(self, fila: sqlite3.Row) -> CuestionarioGAD7:
        return CuestionarioGAD7.from_dict({
            "id": fila["id"],
            "codigo_estudiante": fila["codigo_estudiante"],
            "respuestas": json.loads(fila["respuestas"]),
            "fecha_aplicacion": fila["fecha_aplicacion"],
        })

    def crear(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Inserta el cuestionario en la tabla SQLite."""
        with self._conexion() as conn:
            conn.execute(
                """INSERT INTO cuestionarios_gad7
                   (id, codigo_estudiante, respuestas,
                    puntaje_total, nivel_severidad, fecha_aplicacion)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    entidad.id,
                    entidad.codigo_estudiante,
                    json.dumps(
                        [r.to_dict() for r in entidad.respuestas],
                        ensure_ascii=False,
                    ),
                    entidad.puntaje_total,
                    entidad.nivel_severidad.value,
                    entidad.fecha_aplicacion.isoformat(),
                ),
            )
        return entidad

    def listar(self) -> List[CuestionarioGAD7]:
        """Retorna todos los cuestionarios de la tabla."""
        with self._conexion() as conn:
            filas = conn.execute(
                "SELECT * FROM cuestionarios_gad7 ORDER BY fecha_aplicacion"
            ).fetchall()
        return [self._fila_a_entidad(f) for f in filas]

    def buscar_por_codigo(self, codigo: str) -> Optional[CuestionarioGAD7]:
        """Busca un cuestionario por ID en la tabla."""
        with self._conexion() as conn:
            fila = conn.execute(
                "SELECT * FROM cuestionarios_gad7 WHERE id = ?", (codigo,)
            ).fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def actualizar(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Actualiza el registro existente con el mismo ID."""
        with self._conexion() as conn:
            resultado = conn.execute(
                """UPDATE cuestionarios_gad7
                   SET codigo_estudiante = ?,
                       respuestas        = ?,
                       puntaje_total     = ?,
                       nivel_severidad   = ?,
                       fecha_aplicacion  = ?
                   WHERE id = ?""",
                (
                    entidad.codigo_estudiante,
                    json.dumps(
                        [r.to_dict() for r in entidad.respuestas],
                        ensure_ascii=False,
                    ),
                    entidad.puntaje_total,
                    entidad.nivel_severidad.value,
                    entidad.fecha_aplicacion.isoformat(),
                    entidad.id,
                ),
            )
            if resultado.rowcount == 0:
                raise EntidadNoEncontradaError(
                    f"Cuestionario con id '{entidad.id}' no encontrado."
                )
        return entidad

    def eliminar(self, codigo: str) -> None:
        """Elimina el registro con el ID dado de la tabla."""
        with self._conexion() as conn:
            resultado = conn.execute(
                "DELETE FROM cuestionarios_gad7 WHERE id = ?", (codigo,)
            )
            if resultado.rowcount == 0:
                raise EntidadNoEncontradaError(
                    f"Cuestionario con id '{codigo}' no encontrado."
                )
