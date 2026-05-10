from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class TransactionType(Enum):
    EXPENSE = "withdrawal"
    INCOME = "deposit"
    TRANSFER = "transfer"


@dataclass
class Transaction:
    date: date
    raw_label: str
    clean_label: str
    amount: Decimal
    type: TransactionType
    source_name: str
    destination_name: str = ""
    category: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.date, date):
            raise TypeError(f"date must be datetime.date, got {type(self.date)}")
        if not isinstance(self.amount, Decimal) or self.amount < 0:
            raise ValueError(f"amount must be a positive Decimal, got {self.amount!r}")
        if not isinstance(self.type, TransactionType):
            raise TypeError(f"type must be TransactionType, got {type(self.type)}")
        if not self.source_name or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string")
