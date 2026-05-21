"""Suite de pruebas unitarias para el sistema GAD-7.

Cubre: Respuesta, CuestionarioGAD7, GAD7Service, GAD7RepositoryJSON.
Mínimo 10 casos incluyendo edge cases (umbrales exactos, entradas inválidas).
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.exceptions import CuestionarioIncompletoError, EntidadNoEncontradaError
from app.models.cuestionario_gad7 import CuestionarioGAD7
from app.models.estado_riesgo import EstadoRiesgo
from app.models.respuesta import Respuesta
from app.repositories.gad7_repository_json import GAD7RepositoryJSON
from app.services.gad7_service import GAD7Service


# ── Utilidades ────────────────────────────────────────────────────────────────

def _respuestas(valor: int, cantidad: int = 7) -> list[Respuesta]:
    """Genera una lista de respuestas con el mismo valor para pruebas."""
    return [
        Respuesta(numero_item=i, valor=valor, descripcion_item=f"Pregunta {i}")
        for i in range(1, cantidad + 1)
    ]


# ── TestRespuesta ─────────────────────────────────────────────────────────────

class TestRespuesta:
    """Pruebas para la entidad Respuesta."""

    def test_valor_valido_crea_respuesta(self) -> None:
        r = Respuesta(numero_item=1, valor=2, descripcion_item="Test")
        assert r.valor == 2

    def test_valor_maximo_valido(self) -> None:
        r = Respuesta(numero_item=1, valor=3, descripcion_item="Test")
        assert r.valor == 3

    def test_valor_minimo_valido(self) -> None:
        r = Respuesta(numero_item=1, valor=0, descripcion_item="Test")
        assert r.valor == 0

    def test_valor_4_lanza_error(self) -> None:
        with pytest.raises(ValueError):
            Respuesta(numero_item=1, valor=4, descripcion_item="Test")

    def test_valor_negativo_lanza_error(self) -> None:
        with pytest.raises(ValueError):
            Respuesta(numero_item=1, valor=-1, descripcion_item="Test")

    def test_to_dict_y_from_dict_son_inversos(self) -> None:
        r = Respuesta(numero_item=3, valor=1, descripcion_item="Ansiedad")
        assert Respuesta.from_dict(r.to_dict()) == r


# ── TestCuestionarioGAD7 ──────────────────────────────────────────────────────

class TestCuestionarioGAD7:
    """Pruebas para la entidad CuestionarioGAD7."""

    def test_puntaje_total_suma_valores(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(2)
        )
        assert c.puntaje_total == 14  # 7 × 2

    def test_clasificar_normal_puntaje_0(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(0)
        )
        assert c.clasificar_severidad() == EstadoRiesgo.NORMAL

    def test_clasificar_normal_puntaje_4(self) -> None:
        """Edge case: 4 es el último puntaje NORMAL."""
        respuestas = [
            Respuesta(numero_item=i, valor=1 if i <= 4 else 0, descripcion_item=f"P{i}")
            for i in range(1, 8)
        ]
        c = CuestionarioGAD7(codigo_estudiante="EST001", respuestas=respuestas)
        assert c.puntaje_total == 4
        assert c.clasificar_severidad() == EstadoRiesgo.NORMAL

    def test_clasificar_leve_umbral_exacto_5(self) -> None:
        """Edge case: 5 es el primer puntaje LEVE."""
        respuestas = [
            Respuesta(numero_item=i, valor=1 if i <= 5 else 0, descripcion_item=f"P{i}")
            for i in range(1, 8)
        ]
        c = CuestionarioGAD7(codigo_estudiante="EST002", respuestas=respuestas)
        assert c.puntaje_total == 5
        assert c.clasificar_severidad() == EstadoRiesgo.LEVE

    def test_clasificar_moderado_umbral_exacto_10(self) -> None:
        """Edge case: 10 es el primer puntaje MODERADO."""
        respuestas = [
            Respuesta(numero_item=i, valor=2 if i <= 5 else 0, descripcion_item=f"P{i}")
            for i in range(1, 8)
        ]
        c = CuestionarioGAD7(codigo_estudiante="EST003", respuestas=respuestas)
        assert c.puntaje_total == 10
        assert c.clasificar_severidad() == EstadoRiesgo.MODERADO

    def test_clasificar_severo_umbral_exacto_15(self) -> None:
        """Edge case: 15 es el primer puntaje SEVERO."""
        respuestas = [
            Respuesta(numero_item=i, valor=3 if i <= 5 else 0, descripcion_item=f"P{i}")
            for i in range(1, 8)
        ]
        c = CuestionarioGAD7(codigo_estudiante="EST004", respuestas=respuestas)
        assert c.puntaje_total == 15
        assert c.clasificar_severidad() == EstadoRiesgo.SEVERO

    def test_clasificar_severo_puntaje_maximo_21(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST005", respuestas=_respuestas(3)
        )
        assert c.puntaje_total == 21
        assert c.clasificar_severidad() == EstadoRiesgo.SEVERO

    def test_validar_retorna_false_sin_respuestas(self) -> None:
        c = CuestionarioGAD7(codigo_estudiante="EST001")
        assert not c.validar()

    def test_validar_retorna_false_con_respuestas_incompletas(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(1, cantidad=5)
        )
        assert not c.validar()

    def test_validar_retorna_true_con_7_respuestas(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(1)
        )
        assert c.validar()

    def test_to_dict_y_from_dict_preservan_datos(self) -> None:
        c = CuestionarioGAD7(
            codigo_estudiante="EST002", respuestas=_respuestas(2)
        )
        restaurado = CuestionarioGAD7.from_dict(c.to_dict())
        assert restaurado.id == c.id
        assert restaurado.puntaje_total == c.puntaje_total
        assert restaurado.codigo_estudiante == c.codigo_estudiante


# ── TestGAD7Service ───────────────────────────────────────────────────────────

class TestGAD7Service:
    """Pruebas unitarias del servicio usando repositorio simulado (mock)."""

    def _servicio_con_mock(self) -> tuple[GAD7Service, MagicMock]:
        repo = MagicMock()
        return GAD7Service(repo), repo

    def test_crear_cuestionario_valido_persiste(self) -> None:
        servicio, repo = self._servicio_con_mock()
        cuestionario = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(1)
        )
        repo.crear.return_value = cuestionario
        resultado = servicio.crear_cuestionario("EST001", _respuestas(1))
        repo.crear.assert_called_once()
        assert resultado == cuestionario

    def test_crear_cuestionario_incompleto_lanza_error(self) -> None:
        servicio, _ = self._servicio_con_mock()
        with pytest.raises(CuestionarioIncompletoError):
            servicio.crear_cuestionario("EST001", _respuestas(1, cantidad=3))

    def test_buscar_cuestionario_inexistente_lanza_error(self) -> None:
        servicio, repo = self._servicio_con_mock()
        repo.buscar_por_codigo.return_value = None
        with pytest.raises(EntidadNoEncontradaError):
            servicio.buscar_cuestionario("id-inexistente")

    def test_evaluar_riesgo_severo(self) -> None:
        servicio, repo = self._servicio_con_mock()
        cuestionario = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(3)
        )
        repo.buscar_por_codigo.return_value = cuestionario
        nivel = servicio.evaluar_riesgo(cuestionario.id)
        assert nivel == EstadoRiesgo.SEVERO

    def test_evaluar_riesgo_normal(self) -> None:
        servicio, repo = self._servicio_con_mock()
        cuestionario = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(0)
        )
        repo.buscar_por_codigo.return_value = cuestionario
        nivel = servicio.evaluar_riesgo(cuestionario.id)
        assert nivel == EstadoRiesgo.NORMAL

    def test_eliminar_cuestionario_delega_en_repo(self) -> None:
        servicio, repo = self._servicio_con_mock()
        servicio.eliminar_cuestionario("some-id")
        repo.eliminar.assert_called_once_with("some-id")

    def test_actualizar_respuestas_incompletas_lanza_error(self) -> None:
        servicio, repo = self._servicio_con_mock()
        cuestionario = CuestionarioGAD7(
            codigo_estudiante="EST001", respuestas=_respuestas(1)
        )
        repo.buscar_por_codigo.return_value = cuestionario
        with pytest.raises(CuestionarioIncompletoError):
            servicio.actualizar_respuestas(
                cuestionario.id, _respuestas(2, cantidad=4)
            )


# ── TestGAD7RepositoryJSON (integración) ──────────────────────────────────────

class TestGAD7RepositoryJSONIntegracion:
    """Pruebas de integración del repositorio JSON usando archivos temporales."""

    def test_crud_completo(self, tmp_path: Path) -> None:
        repo = GAD7RepositoryJSON(ruta=tmp_path / "test.json")
        c = CuestionarioGAD7(
            codigo_estudiante="EST999", respuestas=_respuestas(2)
        )
        # Crear
        repo.crear(c)
        assert len(repo.listar()) == 1

        # Buscar
        encontrado = repo.buscar_por_codigo(c.id)
        assert encontrado is not None
        assert encontrado.codigo_estudiante == "EST999"

        # Actualizar
        encontrado.respuestas = _respuestas(3)
        repo.actualizar(encontrado)
        assert repo.buscar_por_codigo(c.id).puntaje_total == 21  # type: ignore[union-attr]

        # Eliminar
        repo.eliminar(c.id)
        assert len(repo.listar()) == 0

    def test_archivo_vacio_retorna_lista_vacia(self, tmp_path: Path) -> None:
        repo = GAD7RepositoryJSON(ruta=tmp_path / "vacio.json")
        assert repo.listar() == []

    def test_eliminar_inexistente_lanza_error(self, tmp_path: Path) -> None:
        repo = GAD7RepositoryJSON(ruta=tmp_path / "test.json")
        with pytest.raises(EntidadNoEncontradaError):
            repo.eliminar("id-fantasma")

    def test_actualizar_inexistente_lanza_error(self, tmp_path: Path) -> None:
        repo = GAD7RepositoryJSON(ruta=tmp_path / "test.json")
        c = CuestionarioGAD7(
            codigo_estudiante="EST000", respuestas=_respuestas(1)
        )
        with pytest.raises(EntidadNoEncontradaError):
            repo.actualizar(c)

    def test_multiples_cuestionarios_mismo_estudiante(
        self, tmp_path: Path
    ) -> None:
        repo = GAD7RepositoryJSON(ruta=tmp_path / "test.json")
        for _ in range(3):
            repo.crear(
                CuestionarioGAD7(
                    codigo_estudiante="EST001", respuestas=_respuestas(1)
                )
            )
        assert len(repo.listar()) == 3
