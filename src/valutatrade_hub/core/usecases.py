from decimal import Decimal

from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
    StaleRatesError,
)
from valutatrade_hub.core.models import Portfolio


def buy_currency(
    portfolio: Portfolio, currency: str, amount: Decimal, rate: Decimal
) -> None:
    """Бизнес-логика покупки валюты за USD."""
    currency = currency.upper()

    # 1. Проверяем, есть ли USD кошелек
    try:
        usd_wallet = portfolio.get_wallet("USD")
    except ValueError:
        raise CurrencyNotFoundError("У вас нет кошелька USD для покупки.") from None

    # 2. Проверяем баланс
    cost = amount * rate
    if usd_wallet.balance < cost:
        raise InsufficientFundsError(
            f"Недостаточно USD. Нужно {cost}, есть {usd_wallet.balance}"
        )

    # 3. Списываем USD
    usd_wallet.withdraw(cost)

    # 4. Зачисляем купленную валюту (если кошелька нет — создаем)
    try:
        target_wallet = portfolio.get_wallet(currency)
    except ValueError:
        target_wallet = portfolio.add_currency(currency, balance=0)

    target_wallet.deposit(amount)


def sell_currency(
    portfolio: Portfolio, currency: str, amount: Decimal, rate: Decimal
) -> None:
    """Бизнес-логика продажи валюты за USD."""
    currency = currency.upper()
    if currency == "USD":
        raise CurrencyNotFoundError("Нельзя продать USD за USD.")

    # 1. Проверяем, есть ли кошелек с этой валютой
    try:
        target_wallet = portfolio.get_wallet(currency)
    except ValueError:
        raise CurrencyNotFoundError(
            f"У вас нет кошелька {currency} для продажи."
        ) from None

    # 2. Проверяем хватает ли валюты для продажи
    if target_wallet.balance < amount:
        raise InsufficientFundsError(
            f"Недостаточно {currency}. Нужно {amount}, есть {target_wallet.balance}"
        )

    # 3. Списываем продаваемую валюту
    target_wallet.withdraw(amount)

    # 4. Начисляем USD (если кошелька USD нет — создаем)
    try:
        usd_wallet = portfolio.get_wallet("USD")
    except ValueError:
        usd_wallet = portfolio.add_currency("USD", balance=0)

    revenue = amount * rate
    usd_wallet.deposit(revenue)


def get_rate(rates: dict, currency: str) -> Decimal:
    """Получение актуального курса валюты из кэша с проверкой на наличие."""
    currency = currency.upper()
    if currency not in rates:
        raise StaleRatesError(f"Курс для {currency} отсутствует или устарел.")

    return Decimal(str(rates[currency]))
