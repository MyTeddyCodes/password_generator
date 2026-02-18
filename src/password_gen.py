from rich import print, box
from rich.console import Console
from rich.table import Table
import string
import secrets

console = Console()

table = Table(show_header=True,
              header_style="italic white",
              expand="True",
              box=box.MINIMAL,
              )

table.add_column("Strength", justify="center")
table.add_column("Password", justify="center", ratio=3)


def create_password(length):
    # Combines letters,numbers, and symbols
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(chars) for _ in range(length))


def cli_password_generator(length):
    run_password_generator(length)


def run_password_generator(size):

    if size < 4:
        print("[red]Too short! Try 8 or more.[/]")
    else:
        pwd = create_password(size)

        if size < 8:
            strength = "[red dim]WEAK (Low Security)[/]"
        elif size <= 12:
            strength = "[yellow dim]MEDIUM (Good)[/]"
        else:
            strength = "[green dim]STRONG (Excellent)[/]"

        table.add_row(
            strength,
            pwd
        )
        console.print(table)
