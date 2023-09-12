class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ParserUrlException(Exception):
    """Вызывается когда найден неверный URL"""
    pass
