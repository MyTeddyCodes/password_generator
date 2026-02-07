import string
import secrets
import sys


password_length_arg: int = int(sys.argv[1])


def create_password(length):
    # Combines letters,numbers, and symbols
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(chars) for _ in range(length))


def cli_password_generator(length):
    run_password_generator(length)


def run_password_generator(size):

    if size < 4:
        print("Too short! Try 8 or more.")
    else:
        pwd = create_password(size)

        if size < 8:
            strength = "WEAK (Low Security)"
        elif size <= 12:
            strength = "MEDIUM (Good)"
        else:
            strength = "STRONG (Excellent)"

        print(f"\nYour Password:{pwd}")
        print(f"Strength:{strength}\n")


def main():
    if password_length_arg:
        cli_password_generator(password_length_arg)
        return

    print("---Secure Password Generator---")
    try:
        size = int(input("Enter password length:"))
        run_password_generator(size)
    except ValueError:
        print("Error:Please enter a whole number.")


if __name__ == "__main__":
    main()
