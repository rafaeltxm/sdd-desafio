"""normalizar_texto(): os passos da seção 5 da spec."""

import unicodedata


def _conta(caractere: str) -> bool:
    """Letra (categoria `L*`) ou algarismo decimal (`Nd`); o resto é separador."""
    categoria = unicodedata.category(caractere)
    return categoria.startswith("L") or categoria == "Nd"


def normalizar_texto(texto: str) -> str:
    """Normaliza categoria ou fornecedor conforme a seção 5 da spec (DT-004)."""
    texto = unicodedata.normalize("NFD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.category(c).startswith("M"))
    texto = "".join(c if _conta(c) else " " for c in texto)
    return "_".join(texto.split())
