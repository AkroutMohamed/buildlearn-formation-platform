import getpass
import re
import sys
from pathlib import Path

# Ensure backend/ is available for imports when running:
# python scripts/create_admin.py
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.utils.hash import hash_password


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_email(email: str) -> str:
    email = email.strip()

    if not EMAIL_RE.match(email):
        raise ValueError("Please provide a valid email address.")

    return email


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    return password


def prompt_nonempty(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"{label} cannot be empty.")


def prompt_password() -> str:
    while True:
        value = getpass.getpass("Password: ")

        if not value:
            print("Password cannot be empty.")
            continue

        try:
            return validate_password(value)
        except ValueError as exc:
            print(exc)


def main() -> int:
    print("BuildLearn — Admin Bootstrap")
    print("This creates an administrator account.\n")

    first_name = prompt_nonempty("First name")
    last_name = prompt_nonempty("Last name")
    email = validate_email(prompt_nonempty("Email"))
    password = prompt_password()

    db = SessionLocal()

    try:
        repository = UserRepository(db)

        existing = repository.get_by_email(email)

        if existing:
            print(
                f"\nAborted: an account with email '{email}' already exists."
            )
            return 1

        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,
        )

        repository.create(user)

        print(f"\nAdmin account created successfully for {email}.")
        return 0

    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())