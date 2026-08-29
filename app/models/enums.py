from enum import Enum

class ItemType(str, Enum):
    BOOK = "BOOK"
    MAGAZINE = "MAGAZINE"

class TransactionType(str, Enum):
    ORDER = "ORDER"
    RETURN = "RETURN"

class Genre(str, Enum):
    CRIME = "CRIME"
    FANTASY = "FANTASY"
    FICTION = "FICTION"
    MYTHOLOGY = "MYTHOLOGY"
    NEWS = "NEWS"
    NON_FICTION = "NON-FICTION"
    PROGRAMMING = "PROGRAMMING"
    SCIENCE = "SCIENCE"
