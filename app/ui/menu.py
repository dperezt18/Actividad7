from app.exceptions import AppError
from app.models.cuestionario_gad7 import CuestionarioGAD7
from app.models.respuesta import Respuesta
from app.services.gad7_service import GAD7Service
from app.ui import mensajes as msg

OPCIONES_VALIDAS = {"0", "1", "2", "3", "4", "5", "6"}

DESCRIPCIONES_RIESGO = {
    "NORMAL": "Sin ansiedad significativa (0-4 pts).",
    "LEVE": "Ansiedad leve — seguimiento recomendado (5-9 pts).",
    "MODERADO": "Ansiedad moderada — considerar intervención (10-14 pts).",
    "SEVERO": "Ansiedad severa — atención prioritaria recomendada (15-21 pts).",
}


class MenuPrincipal:
    """Controlador de la interfaz de consola para el CRUD GAD-7."""

    def __init__(self, servicio: GAD7Service) -> None:
        self._servicio = servicio

    def ejecutar(self) -> None:
        """Bucle principal del menú."""
        print(msg.BIENVENIDA)
        print(msg.TITULO)
        print(msg.SEPARADOR)
        while True:
            print(msg.MENU_PRINCIPAL)
            opcion = input(msg.OPCION).strip()
            if opcion not in OPCIONES_VALIDAS:
                print(msg.ERR_OPCION_INVALIDA)
                continue
            if opcion == "0":
                print("\n  ¡Hasta luego!\n")
                break
            self._despachar(opcion)

    def _despachar(self, opcion: str) -> None:
        acciones = {
            "1": self._registrar,
            "2": self._listar,
            "3": self._buscar,
            "4": self._actualizar,
            "5": self._eliminar,
            "6": self._evaluar_riesgo,
        }
        try:
            acciones[opcion]()
        except AppError as error:
            print(f"\n  Error: {error}")

    def _capturar_respuestas(self) -> list[Respuesta] | None:
        print(msg.CANCELAR)
        print(msg.ESCALA)
        respuestas: list[Respuesta] = []
        for pregunta in msg.PREGUNTAS_GAD7:
            while True:
                entrada = input(f"  {pregunta}: ").strip()
                if entrada.lower() == "cancelar":
                    print(msg.OPERACION_CANCELADA)
                    return None
                if entrada.isdigit() and 0 <= int(entrada) <= 3:
                    respuestas.append(
                        Respuesta(
                            numero_item=len(respuestas) + 1,
                            valor=int(entrada),
                            descripcion_item=pregunta,
                        )
                    )
                    break
                print(msg.ERR_VALOR_INVALIDO)
        return respuestas

    def _registrar(self) -> None:
        print("\n--- REGISTRAR CUESTIONARIO ---")
        codigo = input(msg.CODIGO_ESTUDIANTE).strip()
        if not codigo:
            print(msg.ERR_OPCION_INVALIDA)
            return
        respuestas = self._capturar_respuestas()
        if respuestas is None:
            return
        cuestionario = self._servicio.crear_cuestionario(codigo, respuestas)
        print(msg.OK_CREADO)
        print(f"  ID     : {cuestionario.id}")
        print(f"  Puntaje: {cuestionario.puntaje_total}/21")
        print(f"  Nivel  : {cuestionario.nivel_severidad.value}")

    def _listar(self) -> None:
        print("\n--- LISTADO DE CUESTIONARIOS ---")
        cuestionarios = self._servicio.listar_cuestionarios()
        if not cuestionarios:
            print("  No hay cuestionarios registrados.")
            return
        for c in cuestionarios:
            print(
                f"  {c.id[:8]}...  "
                f"Est: {c.codigo_estudiante:<12}  "
                f"Puntaje: {c.puntaje_total:>2}/21  "
                f"Nivel: {c.nivel_severidad.value:<8}  "
                f"Fecha: {c.fecha_aplicacion.strftime('%Y-%m-%d')}"
            )

    def _buscar(self) -> None:
        print("\n--- BUSCAR CUESTIONARIO ---")
        id_c = input(msg.ID_CUESTIONARIO).strip()
        cuestionario = self._servicio.buscar_cuestionario(id_c)
        self._mostrar_detalle(cuestionario)

    def _mostrar_detalle(self, cuestionario: CuestionarioGAD7) -> None:
        print(f"\n  ID        : {cuestionario.id}")
        print(f"  Estudiante: {cuestionario.codigo_estudiante}")
        print(
            f"  Fecha     : "
            f"{cuestionario.fecha_aplicacion.strftime('%Y-%m-%d %H:%M')}"
        )
        print(f"  Puntaje   : {cuestionario.puntaje_total}/21")
        print(f"  Nivel     : {cuestionario.nivel_severidad.value}")
        print("  Respuestas:")
        for r in cuestionario.respuestas:
            print(f"    [{r.valor}] {r.descripcion_item}")

    def _actualizar(self) -> None:
        print("\n--- ACTUALIZAR CUESTIONARIO ---")
        id_c = input(msg.ID_CUESTIONARIO).strip()
        self._servicio.buscar_cuestionario(id_c)
        print("  Ingrese las nuevas respuestas:")
        nuevas = self._capturar_respuestas()
        if nuevas is None:
            return
        cuestionario = self._servicio.actualizar_respuestas(id_c, nuevas)
        print(msg.OK_ACTUALIZADO)
        print(f"  Nuevo puntaje: {cuestionario.puntaje_total}/21")
        print(f"  Nuevo nivel  : {cuestionario.nivel_severidad.value}")

    def _eliminar(self) -> None:
        print("\n--- ELIMINAR CUESTIONARIO ---")
        id_c = input(msg.ID_CUESTIONARIO).strip()
        confirmacion = (
            input(f"  ¿Confirma eliminar '{id_c[:8]}...'? [s/n]: ")
            .strip()
            .lower()
        )
        if confirmacion != "s":
            print(msg.OPERACION_CANCELADA)
            return
        self._servicio.eliminar_cuestionario(id_c)
        print(msg.OK_ELIMINADO)

    def _evaluar_riesgo(self) -> None:
        print("\n--- EVALUACIÓN DE RIESGO ---")
        id_c = input(msg.ID_CUESTIONARIO).strip()
        nivel = self._servicio.evaluar_riesgo(id_c)
        print(f"\n  Nivel de riesgo: {nivel.value}")
        print(f"  {DESCRIPCIONES_RIESGO[nivel.value]}")
