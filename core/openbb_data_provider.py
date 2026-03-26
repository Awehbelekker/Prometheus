"""
OpenBB Platform Integration for PROMETHEUS
Unified access to 350+ financial datasets via a single SDK.

OpenBB replaces the fragmented patchwork of:
  yfinance, Alpha Vantage, Polygon, CoinGecko, FRED, SEC EDGAR
with one consistent API. 34K+ GitHub stars, AGPL-3.0 license.

Install: pip install openbb
Docs: https://docs.openbb.co/

This adapter coexists with existing data sources — it does NOT remove them.
It adds a unified layer that PROMETHEUS can optionally prefer.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Lazy import
_obb = None


def _get_obb():
    """Lazy-load OpenBB to avoid import cost when not needed."""
    global _obb
    if _obb is not None:
        return _obb

    try:
        from openbb import obb
        _obb = obb
        logger.info("OpenBB Platform loaded successfully")
        return _obb
    except ImportError:
        logger.warning("OpenBB not installed. Run: pip install openbb")
        return None


class OpenBBDataProvider:
    """
    Unified market data provider using OpenBB Platform.

    Provides a single interface for:
      - Equities (historical prices, fundamentals, news)
      - Crypto (prices, on-chain data)
      - Economic data (FRED, Treasury, CPI, GDP)
      - Options chains
      - ETFs and mutual funds
      - Technical indicators
      - News and sentiment
      - SEC filings
    """

    def __init__(self):
        self.obb = _get_obb()
        self.available = self.obb is not None
        self._configure_providers()

    def _configure_providers(self):
        """Set up data provider credentials from env vars."""
        if not self.available:
            return

        # OpenBB supports per-provider API keys via its settings
        provider_keys = {
            'polygon': os.getenv('POLYGON_API_KEY') or os.getenv('POLYGON_ACCESS_KEY_ID', ''),
            'alpha_vantage': os.getenv('ALPHA_VANTAGE_API_KEY', ''),
            'fred': os.getenv('FRED_API_KEY', ''),
            'fmp': os.getenv('FMP_API_KEY', ''),  # Financial Modeling Prep
            'intrinio': os.getenv('INTRINIO_API_KEY', ''),
            'tiingo': os.getenv('TIINGO_API_KEY', ''),
            'newsapi': os.getenv('NEWSAPI_KEY', ''),
        }

        configured = [k for k, v in provider_keys.items() if v]
        if configured:
            logger.info(f"OpenBB providers with API keys: {configured}")

    # ------------------------------------------------------------------
    # Equity data
    # ------------------------------------------------------------------

    def get_stock_price(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        interval: str = '1d',
        provider: str = 'yfinance',
    ) -> Optional[Any]:
        """
        Fetch historical stock price data.

        Args:
            symbol: Ticker symbol (e.g. 'AAPL')
            start_date: Start date (YYYY-MM-DD). Default: 1 year ago.
            end_date: End date (YYYY-MM-DD). Default: today.
            interval: '1m', '5m', '15m', '1h', '1d', '1W', '1M'
            provider: 'yfinance', 'polygon', 'alpha_vantage', 'fmp', etc.

        Returns:
            OpenBB OBBject with .to_df() method, or None on error.
        """
        if not self.available:
            return None

        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        try:
            result = self.obb.equity.price.historical(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                interval=interval,
                provider=provider,
            )
            logger.info(f"OpenBB: fetched {symbol} price data ({provider})")
            return result
        except Exception as exc:
            logger.error(f"OpenBB stock price fetch failed ({symbol}): {exc}")
            return None

    def get_stock_quote(self, symbol: str, provider: str = 'yfinance') -> Optional[Dict]:
        """Get real-time quote."""
        if not self.available:
            return None
        try:
            result = self.obb.equity.price.quote(symbol=symbol, provider=provider)
            return result.to_dict() if hasattr(result, 'to_dict') else None
        except Exception as exc:
            logger.error(f"OpenBB quote failed ({symbol}): {exc}")
            return None

    def get_fundamentals(self, symbol: str, provider: str = 'yfinance') -> Optional[Dict]:
        """Get company fundamentals (balance sheet, income stmt, ratios)."""
        if not self.available:
            return None
        try:
            profile = self.obb.equity.profile(symbol=symbol, provider=provider)
            return profile.to_dict() if hasattr(profile, 'to_dict') else None
        except Exception as exc:
            logger.error(f"OpenBB fundamentals failed ({symbol}): {exc}")
            return None

    # ------------------------------------------------------------------
    # Crypto data
    # ------------------------------------------------------------------

    def get_crypto_price(
        self,
        symbol: str = 'BTC',
        vs_currency: str = 'USD',
        start_date: Optional[str] = None,
        provider: str = 'yfinance',
    ) -> Optional[Any]:
        """Fetch crypto price history."""
        if not self.available:
            return None

        # Map to yfinance format if needed
        yf_symbol = f"{symbol}-{vs_currency}" if provider == 'yfinance' else symbol

        if not start_date:
            start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

        try:
            result = self.obb.crypto.price.historical(
                symbol=yf_symbol,
                start_date=start_date,
                provider=provider,
            )
            return result
        except Exception as exc:
            logger.error(f"OpenBB crypto price failed ({symbol}): {exc}")
            return None

    # ------------------------------------------------------------------
    # Economic data (replaces FRED integration)
    # ------------------------------------------------------------------

    def get_economic_indicator(
        self,
        series_id: str = 'GDP',
        provider: str = 'fred',
        start_date: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Fetch economic data series (GDP, CPI, unemployment, etc.).

        Common series_ids: GDP, CPIAUCSL, UNRATE, FEDFUNDS, DGS10, T10Y2Y
        """
        if not self.available:
            return None

        if not start_date:
            start_date = (datetime.now() - timedelta(days=365 * 5)).strftime('%Y-%m-%d')

        try:
            result = self.obb.economy.fred_series(
                symbol=series_id,
                start_date=start_date,
                provider=provider,
            )
            return result
        except Exception as exc:
            logger.error(f"OpenBB economic data failed ({series_id}): {exc}")
            return None

    def get_treasury_rates(self, provider: str = 'fred') -> Optional[Any]:
        """Get current Treasury yield curve."""
        if not self.available:
            return None
        try:
            return self.obb.fixedincome.rate.treasury(provider=provider)
        except Exception as exc:
            logger.error(f"OpenBB treasury rates failed: {exc}")
            return None

    # ------------------------------------------------------------------
    # News and sentiment
    # ------------------------------------------------------------------

    def get_news(
        self,
        query: str = '',
        symbols: Optional[List[str]] = None,
        limit: int = 20,
        provider: str = 'benzinga',
    ) -> Optional[List[Dict]]:
        """Fetch financial news."""
        if not self.available:
            return None
        try:
            kwargs: Dict[str, Any] = {'limit': limit, 'provider': provider}
            if symbols:
                kwargs['symbol'] = ','.join(symbols)

            result = self.obb.news.world(**kwargs)
            if hasattr(result, 'to_df'):
                return result.to_df().to_dict('records')
            return None
        except Exception as exc:
            logger.error(f"OpenBB news failed: {exc}")
            return None

    # ------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------

    def get_options_chain(self, symbol: str, provider: str = 'yfinance') -> Optional[Any]:
        """Fetch options chain for a symbol."""
        if not self.available:
            return None
        try:
            return self.obb.derivatives.options.chains(symbol=symbol, provider=provider)
        except Exception as exc:
            logger.error(f"OpenBB options chain failed ({symbol}): {exc}")
            return None

    # ------------------------------------------------------------------
    # Technical analysis
    # ------------------------------------------------------------------

    def add_technical_indicators(self, df, indicators: Optional[List[str]] = None):
        """
        Add technical indicators to a DataFrame using OpenBB's TA module.

        Args:
            df: DataFrame with OHLCV data
            indicators: List of indicator names. Default: RSI, MACD, SMA_20, Bollinger.
        """
        if not self.available:
            return df

        if indicators is None:
            indicators = ['rsi', 'macd', 'sma', 'bbands']

        try:
            for ind in indicators:
                if ind == 'rsi':
                    result = self.obb.technical.rsi(data=df, length=14)
                    if hasattr(result, 'to_df'):
                        df['rsi'] = result.to_df()['RSI_14'].values
                elif ind == 'macd':
                    result = self.obb.technical.macd(data=df)
                    if hasattr(result, 'to_df'):
                        macd_df = result.to_df()
                        df['macd'] = macd_df.iloc[:, 0].values
                elif ind == 'sma':
                    for period in [20, 50]:
                        result = self.obb.technical.sma(data=df, length=period)
                        if hasattr(result, 'to_df'):
                            df[f'sma_{period}'] = result.to_df().iloc[:, 0].values
                elif ind == 'bbands':
                    result = self.obb.technical.bbands(data=df)
                    if hasattr(result, 'to_df'):
                        bb_df = result.to_df()
                        for col in bb_df.columns:
                            df[f'bb_{col.lower()}'] = bb_df[col].values
        except Exception as exc:
            logger.warning(f"OpenBB TA indicator error: {exc}")

        return df

    # ------------------------------------------------------------------
    # SEC filings (replaces sec_edgar_api.py)
    # ------------------------------------------------------------------

    def get_sec_filings(
        self,
        symbol: str,
        filing_type: str = '10-K',
        limit: int = 5,
        provider: str = 'sec',
    ) -> Optional[List[Dict]]:
        """Fetch SEC filings for a company."""
        if not self.available:
            return None
        try:
            result = self.obb.equity.fundamental.filings(
                symbol=symbol,
                type=filing_type,
                limit=limit,
                provider=provider,
            )
            if hasattr(result, 'to_df'):
                return result.to_df().to_dict('records')
            return None
        except Exception as exc:
            logger.error(f"OpenBB SEC filings failed ({symbol}): {exc}")
            return None

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> Dict[str, Any]:
        return {
            'available': self.available,
            'version': 'N/A',  # Would need openbb.__version__
            'description': 'Unified financial data platform (350+ datasets)',
        }


# Singleton accessor
_openbb_provider: Optional[OpenBBDataProvider] = None


def get_openbb_provider() -> OpenBBDataProvider:
    """Get global OpenBB data provider instance."""
    global _openbb_provider
    if _openbb_provider is None:
        _openbb_provider = OpenBBDataProvider()
    return _openbb_provider
