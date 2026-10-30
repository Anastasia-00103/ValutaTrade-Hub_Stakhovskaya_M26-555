from valutatrade_hub.core.models import User


def main():
    user = User("Anastasia", "password123")

    print("Информация о пользователе:")
    print(user.get_user_info())

    print("\nПроверка пароля:")
    print(user.verify_password("password123"))

    print("\nПроверка неправильного пароля:")
    print(user.verify_password("wrongpassword"))

    print("\nДанные для сохранения:")
    print(user.to_dict())


if __name__ == "__main__":
    main()