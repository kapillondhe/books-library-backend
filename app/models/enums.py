from enum import Enum

class ItemType(str, Enum):
    BOOK = "BOOK"
    MAGAZINE = "MAGAZINE"

class TransactionType(str, Enum):
    ORDER = "ORDER"
    RETURN = "RETURN"
