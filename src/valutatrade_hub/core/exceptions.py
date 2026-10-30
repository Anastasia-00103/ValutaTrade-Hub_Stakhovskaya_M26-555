
class ValutaTradeError(Exception):
    """Базовое исключение приложения ValutaTrade Hub."""


class ValidationError(ValutaTradeError):
    """Ошибка проверки входных данных."""


class InsufficientFundsError(ValutaTradeError):
    """Недостаточно средств для выполнения операции."""


class CurrencyNotFoundError(ValutaTradeError):
    """Запрашиваемая валюта или кошелёк не найдены."""


class UserAlreadyExistsError(ValutaTradeError):
    """Пользователь с таким именем уже существует."""


class AuthenticationError(ValutaTradeError):
    """Ошибка аутентификации пользователя."""


class InvalidOperationError(ValutaTradeError):
    """Невозможно выполнить запрошенную операцию."""


class StaleRatesError(ValutaTradeError):
    """Курсы валют устарели или не обновлялись."""
