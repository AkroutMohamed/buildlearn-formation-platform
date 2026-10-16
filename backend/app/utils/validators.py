import re

from pydantic import EmailStr, field_validator


def validate_email(value: str) -> str:
    return str(EmailStr(value))


def validate_password(value: str) -> str:
    if len(value) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not re.search(r"[A-Za-z]", value) or not re.search(r"\d", value):
        raise ValueError("Password must contain at least one letter and one number")
    return value


def validate_non_empty(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("Value must not be empty")
    return cleaned


class EmailValidatorMixin:
    _validate_email = field_validator("email")(validate_email)


class PasswordValidatorMixin:
    _validate_password = field_validator("password")(validate_password)