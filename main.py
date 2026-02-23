from src.password_gen import cli_password_generator
import sys


def main() -> None:
    if (len(sys.argv) > 1):
        password_length_arg: int = int(sys.argv[1])
        cli_password_generator(password_length_arg)
        return

    print("---Secure Password Generator---")
    try:
        size: int = int(input("Enter password length:"))

        cli_password_generator(size)
    except ValueError:
        print("Error:Please enter a whole number.")


if __name__ == "__main__":
    main()
