"""This module defines the Balancer class"""

from ..portfolio import Portfolio


class Balancer:
    """A abstract rebalancer class."""

    SMALL_MULTIPLIER = 0.0001

    def __init__(self, **options: str) -> None:
        # The targets to balance
        self.targets = options.get("targets")
        if not self.targets:
            raise ValueError("targets must be provided")

        # Portfolio of holdings
        self.portfolio = options.get("portfolio")
        if not self.portfolio:
            raise ValueError("portfolio must be provided")
        self.portfolio.include_empty_targets(self.targets)

        # The transactions config
        self.transactions_config = options.get("transactions_config")
        if not self.transactions_config:
            raise ValueError("transactions config must be provided")

        self.symbols = list(set(self.portfolio.symbols) & \
                            set(self.targets.symbols))
        self._value = None

        self._validate()

    @property
    def value(self) -> float:
        """Total value of the portfolio for the symbols we want to rebalance."""
        if not self._value:
            self._value = 0
            for symbol in self.symbols:
                self._value += self.portfolio.holding(symbol).value
        return self._value

    @property
    def minimum_transaction(self) -> float:
        """The smallest amount that can be purchased (per transaction)."""
        return self.transactions_config.minimum_transaction

    @property
    def maximum_transaction(self) -> float:
        """The greatest amount that can be purchased (per transaction)."""
        return self.transactions_config.maximum_transaction

    def holding(self, symbol: str) -> float:
        """The holding of an investment for the symbol."""
        return self.portfolio.holding(symbol)

    def multiplier(self, symbols: list) -> float:
        """The amount we have to scale all the weights so that they sum up to 1.
        Usually the weighs for all the symbols sum to 1, but not when
        we consider subsets of those symbols.
        """
        multiplier = 0
        for symbol in symbols:
            multiplier += self.targets.weight(symbol)

        if multiplier < self.SMALL_MULTIPLIER:
            return 0

        return 1/multiplier

    def current_total_value(self, symbols: list) -> float:
        """Current value of the portfolio for just these symbols."""
        value = 0
        for symbol in symbols:
            value += self.holding(symbol).value
        return value

    def next_total_value(self, symbols: list) -> float:
        """Current value of just these symbols plus the amount we are spending."""
        return self.transactions_config.amount + self.current_total_value(symbols)

    def run(self) -> "Portfolio":
        """Perform the rebalancing."""
        return Portfolio(self._get_transactions())

    def get_transaction_symbols(self, symbols: list) -> list:
        """The symbols for investments that will be bought or sold."""
        transaction_symbols = []
        multiplier = self.multiplier(symbols)
        next_total_value = self.next_total_value(symbols)

        for symbol in symbols:
            target_weight = self.targets.weight(symbol) * multiplier
            desired_holding = next_total_value * target_weight
            current_holding = self.holding(symbol).value

            # Must meet minimum/maximum purchase
            if "buy" in self._transaction_modes() and \
               desired_holding - current_holding >= self.minimum_transaction:
                transaction_symbols.append(symbol)

            if "sell" in self._transaction_modes() and \
               current_holding - desired_holding >= self.minimum_transaction:
                transaction_symbols.append(symbol)

        return transaction_symbols

    def _transaction_modes(self) -> list:
        # Return a list of transaction types
        raise NotImplementedError

    def _validate(self) -> None:
        if self.transactions_config.balancer_class is not type(self):
            raise ValueError("balancer initialized with wrong class")

    def _get_transactions(self) -> dict:
        # Converge on some symbols eligible for transaction
        transaction_symbols = self.symbols
        prev_symbols = []
        while (set(transaction_symbols) != set(prev_symbols)):
            prev_symbols = transaction_symbols.copy()
            transaction_symbols = self.get_transaction_symbols(prev_symbols)

        multiplier = self.multiplier(transaction_symbols)
        next_value = self.next_total_value(transaction_symbols)
        transactions = {}

        for symbol in self.symbols:
            if symbol in transaction_symbols:
                target_weight = self.targets.weight(symbol) * multiplier
                desired_holding = next_value * target_weight
                holding = self.holding(symbol)

                # Must meet minimums/maximums for transaction to happen
                if "buy" in self._transaction_modes() and \
                   desired_holding >= holding.value + self.minimum_transaction:
                    desired_holding = min(desired_holding,
                                          holding.value + self.maximum_transaction)
                    transactions[symbol] = desired_holding

                if "sell" in self._transaction_modes() and \
                   desired_holding <= holding.value - self.minimum_transaction:
                    desired_holding = max(desired_holding,
                                          holding.value - self.maximum_transaction)
                    transactions[symbol] = desired_holding

            else:
                transactions[symbol] = self.holding(symbol).value

        return transactions
