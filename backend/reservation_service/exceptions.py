class ReservationError(Exception):
    pass

class RoomUnavailableError(ReservationError):
    pass

class InvalidReservationStatus(ReservationError):
    pass
