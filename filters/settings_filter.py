from aiogram.filters import BaseFilter

class Notifications_fiter(BaseFilter):
    def __init__(self, settings) -> None:
        self.notification = settings.notification
        self.first_time = settings.first_time
    
    def __call__(self, what_state_noti: bool, is_first_time) -> bool:
        return self.notification == what_state_noti and self.first_time == is_first_time
    

class Settings():
    def __init__(self,notification:bool,first_time:bool) -> None:
        self.notification = notification
        self.first_time = first_time

