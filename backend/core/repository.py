from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List

T = TypeVar('T')
CreateSchema = TypeVar('CreateSchema')
UpdateSchema = TypeVar('UpdateSchema')

class BaseRepository(ABC, Generic[T, CreateSchema, UpdateSchema]):
    @abstractmethod
    def get(self, id: int) -> T:
        pass
    @abstractmethod
    def list(self, *, property_id: int = None) -> List[T]:
        pass
    @abstractmethod
    def create(self, obj_in: CreateSchema) -> T:
        pass
    @abstractmethod
    def update(self, id: int, obj_in: UpdateSchema) -> T:
        pass
    @abstractmethod
    def delete(self, id: int) -> None:
        pass
