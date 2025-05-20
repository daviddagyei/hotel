# Exceptions for Room Service business logic

class InvalidStatusTransition(Exception):
    pass

class NoAvailableRoom(Exception):
    pass
