class BotError(Exception):
    notify_user = "Ошибка в боте"

    def __init__(
            self,
            text: str = None,
            user_id: int = None,
            chat_id: int = None,
            *args
    ):
        super(BotError, self).__init__(text, args)
        self.text = text
        self.user_id = user_id
        self.chat_id = chat_id

    def __str__(self):
        text = f"{self.__class__.__name__}: {self.text}"
        if self.user_id is not None:
            text += f", by user {self.user_id} "
        if self.chat_id is not None:
            text += f"in chat {self.chat_id}"
        return text

    def __repr__(self):
        return str(self)


class ThreadStopped(BotError):
    notify_user = "Матч закрыт"
