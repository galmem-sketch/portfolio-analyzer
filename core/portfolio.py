from dataclasses import dataclass, field


@dataclass
class AssetEntry:
    ticker: str
    company_name: str
    val: float


@dataclass
class PortfolioConfig:
    entries: list[AssetEntry] = field(default_factory=list)
    mode: str = "1"  # "1" = by value, "2" = by percent
    rf_annual_yield: float = 0.0

    @property
    def has_cash(self) -> bool:
        return any(e.ticker.upper() == 'CASH' for e in self.entries)

    @property
    def stock_tickers(self) -> list[str]:
        return [e.ticker for e in self.entries if e.ticker.upper() != 'CASH']

    def weights(self) -> dict[str, float]:
        """Returns {ticker: weight} normalized to sum=1."""
        total = sum(e.val for e in self.entries)
        if total == 0:
            return {}
        result = {}
        for e in self.entries:
            w = (e.val / total) if self.mode == '1' else (e.val / 100)
            result[e.ticker] = w
        # Normalize
        wsum = sum(result.values())
        if wsum > 0:
            result = {k: v / wsum for k, v in result.items()}
        return result

    def rebuild_from_entries(self, entries: list[AssetEntry]) -> 'PortfolioConfig':
        """Return a new PortfolioConfig with updated entries, same mode/rf."""
        return PortfolioConfig(entries=entries, mode=self.mode, rf_annual_yield=self.rf_annual_yield)
