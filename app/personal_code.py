"""Personas koda pārbaude (CR-1)."""

import re
from datetime import date

from pydantic_core import PydanticCustomError

_FORMAT = re.compile(r"^\d{6}-?\d{5}$")
_WEIGHTS = (1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
_CENTURIES = {"0": 1800, "1": 1900, "2": 2000}


def normalize_personal_code(value: str) -> str:
    """Atgriež kodu kā 11 ciparus bez defises vai met kļūdu.

    Jaunā formāta kodiem (sākas ar 32) pārbauda tikai formātu.
    Vecā formāta kodiem pārbauda arī dzimšanas datumu un kontrolciparu.
    Kļūdas tekstā ievadīto vērtību neatkārtojam: tā ir personas dati.
    """
    value = value.strip()
    if not value:
        raise PydanticCustomError("missing", "Personal code is required")
    if not _FORMAT.match(value):
        raise ValueError("Invalid personal code format")

    digits = value.replace("-", "")
    if digits.startswith("32"):
        return digits

    century = _CENTURIES.get(digits[6])
    if century is None:
        raise ValueError("Invalid personal code century digit")
    try:
        date(century + int(digits[4:6]), int(digits[2:4]), int(digits[0:2]))
    except ValueError:
        raise ValueError("Invalid personal code date") from None

    total = sum(w * int(d) for w, d in zip(_WEIGHTS, digits))
    if (1101 - total) % 11 != int(digits[10]):
        raise ValueError("Invalid personal code checksum")
    return digits
