from abc import ABC, abstractmethod

class BaseService(ABC):
    @abstractmethod
    def validate(self, *args, **kwargs):
        pass
