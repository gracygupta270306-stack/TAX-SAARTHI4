import pandas as pd

_current_transactions: pd.DataFrame | None = None


def save_transactions(dataframe: pd.DataFrame) -> None:
    global _current_transactions
    _current_transactions = dataframe.copy()


def get_transactions() -> pd.DataFrame:
    if _current_transactions is None:
        raise ValueError("No transaction data has been uploaded yet.")
    return _current_transactions.copy()
