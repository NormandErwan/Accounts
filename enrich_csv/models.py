from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class TransactionType(Enum):
    EXPENSE = "Dépense"
    INCOME = "Revenu"
    TRANSFER = "Virement"


FIREFLY_TYPE_MAP: dict[TransactionType, str] = {
    TransactionType.EXPENSE: "withdrawal",
    TransactionType.INCOME: "deposit",
    TransactionType.TRANSFER: "transfer",
}


@dataclass
class Transaction:
    date: date
    raw_label: str
    clean_label: str
    amount: Decimal
    type: TransactionType
    source_account: str
    merchant_name: str = ""
    category: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.date, date):
            raise TypeError(f"date must be datetime.date, got {type(self.date)}")
        if not isinstance(self.amount, Decimal) or self.amount < 0:
            raise ValueError(f"amount must be a positive Decimal, got {self.amount!r}")
        if not isinstance(self.type, TransactionType):
            raise TypeError(f"type must be TransactionType, got {type(self.type)}")
        if not self.source_account or not self.source_account.strip():
            raise ValueError("source_account must be a non-empty string")
