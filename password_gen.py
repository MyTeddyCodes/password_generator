import string
import secrets

def create_password(length):
    # Combines letters,numbers, and symbols
    chars=string.ascii_letters + string.digits + string.punctuation
    return"".join(secrets.choice(chars) for _ in range(length))

def main():
    print("---Secure Password Generator---")
    try:
        size=int(input("Enter password length:"))
        
        if size<4:
            print("Too short! Try 8 or more.")
        else:
            pwd = create_password(size)

            if size <8:
                strength = "WEAK (Low Security)"
            elif size<=12:
                strength = "MEDIUM (Good)"
            else:
                strength = "STRONG (Excellent)"


            print(f"\nYour Password:{pwd}")
            print(f"Strength:{strength}\n")


    except ValueError:
        print("Error:Please enter a whole number.")


if __name__=="__main__":
    main( )
