"""Personas koda pārbaude (CR-1)."""

import re

from pydantic_core import PydanticCustomError

_FORMAT = re.compile(r"^\d{6}-?\d{5}$")


def normalize_personal_code(value: str) -> str:
    """Atgriež kodu kā 11 ciparus bez defises vai met kļūdu.

    Pārbauda tikai formātu: DDMMYY-NNNNN vai 11 ciparus. Dzimšanas datumu
    un kontrolciparu nepārbauda (jaunajiem kodiem, kas sākas ar 32, to nav).
    Kļūdas tekstā ievadīto vērtību neatkārtojam: tā ir personas dati.
    """
    value = value.strip()
    if not value:
        raise PydanticCustomError("missing", "Personal code is required")
    if not _FORMAT.match(value):
        raise ValueError("Invalid personal code format")
    return value.replace("-", "")
