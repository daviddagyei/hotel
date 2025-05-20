class INotificationService:
    def create_notification(self, notification_in):
        raise NotImplementedError
    def get_notification(self, notif_id):
        raise NotImplementedError
    def list_notifications(self, recipient, property_id=None):
        raise NotImplementedError
    def mark_as_read(self, notif_id):
        raise NotImplementedError
