from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """Contrato genérico para repositorios de acceso a datos (patrón DAO)."""

    @abstractmethod
    def crear(self, entidad: T) -> T:
        """Persiste una nueva entidad y la retorna."""

    @abstractmethod
    def listar(self) -> List[T]:
        """Retorna todas las entidades almacenadas."""

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> Optional[T]:
        """Busca una entidad por su identificador único."""

    @abstractmethod
    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad existente y la retorna."""

    @abstractmethod
    def eliminar(self, codigo: str) -> None:
        """Elimina la entidad con el identificador dado."""
