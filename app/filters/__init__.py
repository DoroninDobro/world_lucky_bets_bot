from aiogram import Dispatcher


def setup(dispatcher: Dispatcher):
    from .admin import IsAdminFilter

    text_messages = [
        dispatcher.message_handlers,
        dispatcher.edited_message_handlers,
        dispatcher.callback_query_handlers,
    ]
    dispatcher.filters_factory.bind(IsAdminFilter, event_handlers=text_messages)
