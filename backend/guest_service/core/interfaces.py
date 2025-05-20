from abc import ABC, abstractmethod
from typing import Optional, List
from backend.guest_service.models.guest import Guest
from backend.guest_service.schemas.guest import GuestCreate

class IGuestService(ABC):
    @abstractmethod
    def create_or_update_guest(self, data: GuestCreate) -> Guest:
        pass

    @abstractmethod
    def get_guest_by_id(self, guest_id: int) -> Optional[Guest]:
        pass

    @abstractmethod
    def search_guest(self, query: str) -> List[Guest]:
        pass
