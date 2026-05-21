"""Punto de entrada del sistema GAD-7.

Selecciona el repositorio (JSON o MySQL) y lanza la interfaz de consola.
"""

from pathlib import Path

from app.repositories.gad7_repository_json import GAD7RepositoryJSON
from app.services.gad7_service import GAD7Service
from app.ui.menu import MenuPrincipal

# ── Configuración MySQL (ajustar credenciales según MySQL Workbench) ──────────
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "Eleanor2025*"
MYSQL_DATABASE = "gad7_db"

USE_MYSQL = True           # False → usa JSON local


def _crear_repositorio():
    if USE_MYSQL:
        from app.repositories.gad7_repository_mysql import GAD7RepositoryMySQL
        return GAD7RepositoryMySQL(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
        )
    return GAD7RepositoryJSON(ruta=Path("data/cuestionarios_gad7.json"))


def main() -> None:
    """Instancia dependencias y arranca la aplicación."""
    repositorio = _crear_repositorio()
    servicio = GAD7Service(repositorio)
    MenuPrincipal(servicio).ejecutar()


if __name__ == "__main__":
    main()
