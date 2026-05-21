BIENVENIDA = "╔══════════════════════════════════════════╗"
TITULO = "║      SISTEMA GAD-7 — CRUD ANSIEDAD       ║"
SEPARADOR = "╚══════════════════════════════════════════╝"

MENU_PRINCIPAL = """
┌──────────────── MENÚ PRINCIPAL ──────────────────┐
│  1. Registrar nuevo cuestionario                 │
│  2. Listar todos los cuestionarios               │
│  3. Buscar cuestionario por ID                   │
│  4. Actualizar respuestas de cuestionario        │
│  5. Eliminar cuestionario                        │
│  6. Evaluar nivel de riesgo                      │
│  0. Salir                                        │
└──────────────────────────────────────────────────┘"""

OPCION = "Seleccione una opción: "
CODIGO_ESTUDIANTE = "Código del estudiante: "
ID_CUESTIONARIO = "ID del cuestionario: "
CANCELAR = "  (escriba 'cancelar' para volver al menú)"

PREGUNTAS_GAD7 = [
    "1. Sentirse nervioso/a, ansioso/a o muy alterado/a",
    "2. No poder dejar de preocuparse o controlar la preocupación",
    "3. Preocuparse demasiado por cosas diferentes",
    "4. Dificultad para relajarse",
    "5. Estar tan inquieto/a que es difícil mantenerse sentado/a",
    "6. Molestarse o ponerse irritable fácilmente",
    "7. Sentir miedo como si algo terrible fuera a pasar",
]

ESCALA = "  Escala: [0] Nunca  [1] Varios días  [2] Más de la mitad  [3] Casi siempre\n"

ERR_OPCION_INVALIDA = "  Opción no válida. Intente de nuevo."
ERR_VALOR_INVALIDO = "  Ingrese un número entre 0 y 3."
ERR_NO_ENCONTRADO = "  No se encontró el cuestionario indicado."
OK_CREADO = "  ✔ Cuestionario registrado exitosamente."
OK_ACTUALIZADO = "  ✔ Cuestionario actualizado exitosamente."
OK_ELIMINADO = "  ✔ Cuestionario eliminado exitosamente."
OPERACION_CANCELADA = "  Operación cancelada."
