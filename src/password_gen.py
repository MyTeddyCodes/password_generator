from rich import box, print as rprint
from rich.console import Console
from rich.table import Table
import string
import secrets
from zxcvbn import zxcvbn

console = Console()

table = Table(show_header=True,
              header_style="italic white",
              expand="True",
              box=box.MINIMAL,
              )

table.add_column("Strength", justify="center")
table.add_column("Password", justify="center", ratio=3)


def create_password(length: int,
                    use_uppercase: bool = True,
                    use_numbers: bool = True,
                    use_symbols: bool = True) -> str:
    """
    Generate a secure random password with guaranteed character types.
    """
    # Start with lowercase letters (always included for basic password)
    char_sets = []
    char_sets.append(string.ascii_lowercase)

    if use_uppercase:
        char_sets.append(string.ascii_uppercase)
    if use_numbers:
        char_sets.append(string.digits)
    if use_symbols:
        char_sets.append(string.punctuation)

    # Ensure we have at least one character set
    if not char_sets:
        raise ValueError("At least one character type must be selected")

    # Combine all character sets
    all_chars = ''.join(char_sets)

    # Generate password ensuring at least one character from each selected set
    password = []

    # Add one character from each selected set
    for char_set in char_sets:
        password.append(secrets.choice(char_set))

    # Fill the rest randomly from all characters
    for _ in range(length - len(char_sets)):
        password.append(secrets.choice(all_chars))

    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def cli_password_generator(length: int) -> None:
    if length <= 4:
        rprint("[red]Too short! Try 8 or more.[/]")
        return
    password: str = create_password(length)
    strength: str = cli_strength_highlighting(
        verify_password_strength(password)
    )

    print_password_table(password, strength)


def verify_password_strength(password: str) -> str:

    score: int = get_password_strength_percent(password)
    if score < 50:
        strength = "WEAK (Low Security)"
    elif score <= 75:
        strength = "MEDIUM (Good)"
    else:
        strength = "STRONG (Excellent)"

    return strength


def get_password_strength_percent(password) -> int:
    results = zxcvbn(password)
    score = results['score']  # 0, 1, 2, 3, or 4

    # Map the 0-4 score to a 0-100 percentage
    strength_map = {
        0: 0,   # Too guessable
        1: 25,  # Very guessable
        2: 50,  # Somewhat guessable
        3: 75,  # Safely unguessable
        4: 100  # Very unguessable
    }
    return strength_map[score]


def print_password_table(password: str, strength: str) -> None:
    table.add_row(
        strength,
        password
    )
    console.print(table)


def cli_strength_highlighting(strength: str) -> str:
    if "WEAK" in strength:
        strength: str = f"[red dim]{strength} (Low Security)[/]"
    elif "MEDIUM" in strength:
        strength: str = f"[yellow dim]{strength} (Good)[/]"
    elif "STRONG" in strength:
        strength: str = f"[green dim]{strength} (Excellent)[/]"

    return strength
