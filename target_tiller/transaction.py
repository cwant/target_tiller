"""This module defines the Transaction class"""

class Transaction:
    """This will hold the information needed to perform a transaction."""

    def __init__(self, symbol: str, action: str, amount: float) -> None:
        self._symbol = symbol
        self._action = action
        self._amount = amount

    @property
    def symbol(self) -> str:
        """The symbol of the security in the transaction."""
        return self._symbol

    @property
    def action(self) -> str:
        """The action to perform in the transaction: "Buy", "Sell", or "Hold"."""
        return self._action

    @property
    def amount(self) -> float:
        """The amount of cash in the transaction."""
        return self._amount

    def dump(self) -> dict:
        """Return a hash representing this object."""
        return {"symbol": self._symbol,
                "action": self._action,
                "amount": self._amount}

    # Meh, I don't like that I'm only defining these to make tests easier
    def __eq__(self, other: "Transaction") -> bool:
        if isinstance(other, Transaction):
            return \
                [self.symbol, self.action, self.amount] == \
                [other.symbol, other.action, other.amount]
        return NotImplemented

    def __hash__(self) -> hash:
        return hash((self.symbol, self.action, self.amount))

    def __repr__(self) -> str:
        return f"Transaction('{self.symbol}', '{self.action}', {self.amount})"
