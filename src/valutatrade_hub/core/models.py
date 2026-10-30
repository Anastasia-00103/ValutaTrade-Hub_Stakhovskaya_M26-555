import hashlib
import secrets
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

#Создаем класс User

class User:
    """Модель пользователя системы ValutaTrade Hub."""

    def __init__(self, username: str, password: str):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым.")

        if not isinstance(password, str) or len(password) < 8:
            raise ValueError(
                "Пароль должен содержать не менее 8 символов."
            )

        self.__user_id = str(uuid.uuid4())
        self.__username = username.strip()
        self.__salt = secrets.token_hex(16)
        self.__password_hash = self._hash_password(password)
        self.__registered_at = datetime.now(UTC)

    def _hash_password(self, password: str) -> str:
        """Создаёт SHA-256 хеш пароля с солью."""
        return hashlib.sha256(
            (self.__salt + password).encode("utf-8")
        ).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Проверяет правильность пароля."""
        return self.__password_hash == self._hash_password(password)

    @property
    def username(self) -> str:
        """Возвращает имя пользователя."""
        return self.__username

    @property
    def user_id(self) -> str:
        """Возвращает идентификатор пользователя."""
        return self.__user_id

    def get_user_info(self) -> dict:
        """Возвращает информацию о пользователе без пароля."""
        return {
            "user_id": self.__user_id,
            "username": self.__username,
            "registered_at": self.__registered_at.isoformat(),
        }

    def to_dict(self) -> dict:
        """Подготавливает пользователя для сохранения в JSON."""
        return {
            "user_id": self.__user_id,
            "username": self.__username,
            "salt": self.__salt,
            "password_hash": self.__password_hash,
            "registered_at": self.__registered_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Восстанавливает пользователя из словаря."""
        user = cls.__new__(cls)
        user.__user_id = data["user_id"]
        user.__username = data["username"]
        user.__salt = data["salt"]
        user.__password_hash = data["password_hash"]
        user.__registered_at = datetime.fromisoformat(
            data["registered_at"]
        )
        return user
    
#Создаем класс Wallet

class Wallet:
    """Модель валютного кошелька пользователя."""

    def __init__(self, currency: str, balance=0):
        if not isinstance(currency, str):
            raise TypeError("Валюта должна быть строкой.")

        currency = currency.strip().upper()

        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("Код валюты должен состоять из 3 букв.")

        self.__currency = currency

        try:
            self.__balance = Decimal(str(balance))
        except InvalidOperation:
            raise ValueError("Некорректное значение баланса.") from None

        if not self.__balance.is_finite() or self.__balance < 0:
            raise ValueError("Баланс не может быть отрицательным.")

    @property
    def currency(self) -> str:
        """Возвращает код валюты."""
        return self.__currency

    @property
    def balance(self) -> Decimal:
        """Возвращает текущий баланс."""
        return self.__balance

    def deposit(self, amount) -> None:
        """Пополняет кошелёк."""
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise ValueError("Некорректная сумма пополнения.") from None

        if not amount.is_finite() or amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной.")

        self.__balance += amount

    def withdraw(self, amount) -> None:
        """Списывает деньги с кошелька."""
        try:
            amount = Decimal(str(amount))
        except InvalidOperation:
            raise ValueError("Некорректная сумма списания.") from None

        if not amount.is_finite() or amount <= 0:
            raise ValueError("Сумма списания должна быть положительной.")

        if amount > self.__balance:
            raise ValueError("Недостаточно средств на кошельке.")

        self.__balance -= amount

    def get_balance_info(self) -> dict:
        """Возвращает информацию о кошельке."""
        return {
            "currency": self.__currency,
            "balance": str(self.__balance),
        }
    
#Создаем модель Portfolio


class Portfolio:
    """Модель валютного портфеля пользователя."""

    def __init__(self, user: User):
        if not isinstance(user, User):
            raise TypeError("Портфель должен принадлежать пользователю.")

        self.__user = user
        self.__wallets = {}

    @property
    def user(self) -> User:
        """Возвращает владельца портфеля."""
        return self.__user

    @property
    def wallets(self) -> dict:
        """Возвращает копию словаря кошельков."""
        return deepcopy(self.__wallets)

    def add_currency(self, currency: str, balance=0) -> Wallet:
        """Добавляет новый валютный кошелёк."""
        currency = currency.strip().upper()

        if currency in self.__wallets:
            raise ValueError(f"Кошелёк {currency} уже существует.")

        wallet = Wallet(currency, balance)
        self.__wallets[currency] = wallet
        return wallet

    def get_wallet(self, currency: str) -> Wallet:
        """Возвращает кошелёк по коду валюты."""
        currency = currency.strip().upper()

        if currency not in self.__wallets:
            raise ValueError(f"Кошелёк {currency} не найден.")

        return self.__wallets[currency]

#расчёт общей стоимости портфеля


    def get_total_value(
        self,
        base: str = "USD",
        rates: dict | None = None,
    ) -> Decimal:
        """Рассчитывает общую стоимость портфеля в базовой валюте."""
        base = base.strip().upper()

        if rates is None:
            rates = {}

        total = Decimal(0)

        for currency, wallet in self.__wallets.items():
            if currency == base:
                total += wallet.balance
            else:
                rate = rates.get(currency)

                if rate is None:
                    raise ValueError(
                        f"Отсутствует курс для валюты {currency}."
                    )

                rate = Decimal(str(rate))

                if not rate.is_finite() or rate <= 0:
                    raise ValueError(
                        f"Некорректный курс валюты {currency}."
                    )

                total += wallet.balance * rate

        return total
