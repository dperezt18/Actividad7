import json
from contextlib import contextmanager
from typing import Generator, List, Optional

import mysql.connector
from mysql.connector import MySQLConnection

from app.exceptions import EntidadNoEncontradaError
from app.interfaces.i_repository import IRepository
from app.models.cuestionario_gad7 import CuestionarioGAD7

DDL = """
CREATE TABLE IF NOT EXISTS cuestionarios_gad7 (
    id                VARCHAR(36)  PRIMARY KEY,
    codigo_estudiante VARCHAR(50)  NOT NULL,
    respuestas        JSON         NOT NULL,
    puntaje_total     INT          NOT NULL,
    nivel_severidad   VARCHAR(20)  NOT NULL,
    fecha_aplicacion  DATETIME     NOT NULL
);
"""


class GAD7RepositoryMySQL(IRepository[CuestionarioGAD7]):
    """Repositorio que persiste CuestionarioGAD7 en una base de datos MySQL."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        database: str = "gad7_db",
    ) -> None:
        self._config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        self._crear_base_de_datos_si_no_existe()
        self._inicializar_tabla()

    def _crear_base_de_datos_si_no_existe(self) -> None:
        config_sin_db = {k: v for k, v in self._config.items() if k != "database"}
        conn = mysql.connector.connect(**config_sin_db)
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self._config['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            conn.commit()
        finally:
            conn.close()

    def _inicializar_tabla(self) -> None:
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(DDL)

    @contextmanager
    def _conexion(self) -> Generator[MySQLConnection, None, None]:
        conn: MySQLConnection = mysql.connector.connect(**self._config)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _fila_a_entidad(self, fila: tuple) -> CuestionarioGAD7:
        id_, codigo, respuestas_raw, _, _, fecha = fila
        respuestas_data = (
            json.loads(respuestas_raw)
            if isinstance(respuestas_raw, str)
            else respuestas_raw
        )
        return CuestionarioGAD7.from_dict({
            "id": id_,
            "codigo_estudiante": codigo,
            "respuestas": respuestas_data,
            "fecha_aplicacion": (
                fecha.isoformat()
                if hasattr(fecha, "isoformat")
                else str(fecha)
            ),
        })

    def crear(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Inserta el cuestionario en la tabla MySQL."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO cuestionarios_gad7
                   (id, codigo_estudiante, respuestas,
                    puntaje_total, nivel_severidad, fecha_aplicacion)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (
                    entidad.id,
                    entidad.codigo_estudiante,
                    json.dumps(
                        [r.to_dict() for r in entidad.respuestas],
                        ensure_ascii=False,
                    ),
                    entidad.puntaje_total,
                    entidad.nivel_severidad.value,
                    entidad.fecha_aplicacion,
                ),
            )
        return entidad

    def listar(self) -> List[CuestionarioGAD7]:
        """Retorna todos los cuestionarios de la tabla."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM cuestionarios_gad7 ORDER BY fecha_aplicacion"
            )
            filas = cursor.fetchall()
        return [self._fila_a_entidad(f) for f in filas]

    def buscar_por_codigo(self, codigo: str) -> Optional[CuestionarioGAD7]:
        """Busca un cuestionario por ID en la tabla."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM cuestionarios_gad7 WHERE id = %s", (codigo,)
            )
            fila = cursor.fetchone()
        return self._fila_a_entidad(fila) if fila else None

    def actualizar(self, entidad: CuestionarioGAD7) -> CuestionarioGAD7:
        """Actualiza el registro existente con el mismo ID."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE cuestionarios_gad7
                   SET codigo_estudiante = %s,
                       respuestas        = %s,
                       puntaje_total     = %s,
                       nivel_severidad   = %s,
                       fecha_aplicacion  = %s
                   WHERE id = %s""",
                (
                    entidad.codigo_estudiante,
                    json.dumps(
                        [r.to_dict() for r in entidad.respuestas],
                        ensure_ascii=False,
                    ),
                    entidad.puntaje_total,
                    entidad.nivel_severidad.value,
                    entidad.fecha_aplicacion,
                    entidad.id,
                ),
            )
            if cursor.rowcount == 0:
                raise EntidadNoEncontradaError(
                    f"Cuestionario con id '{entidad.id}' no encontrado."
                )
        return entidad

    def eliminar(self, codigo: str) -> None:
        """Elimina el registro con el ID dado de la tabla."""
        with self._conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM cuestionarios_gad7 WHERE id = %s", (codigo,)
            )
            if cursor.rowcount == 0:
                raise EntidadNoEncontradaError(
                    f"Cuestionario con id '{codigo}' no encontrado."
                )
