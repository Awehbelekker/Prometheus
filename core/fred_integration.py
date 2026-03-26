"""
FRED (Federal Reserve Economic Data) Integration for PROMETHEUS
Provides macroeconomic data for market regime detection

FRED API is FREE with no rate limits!
Get your API key at: https://fred.stlouisfed.org/docs/api/api_key.html
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import asyncio
from dataclasses import dataclass
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EconomicIndicator(Enum):
    """Key economic indicators"""
    # Interest Rates
    FED_FUNDS_RATE = "DFF"  # Federal Funds Rate
    TREASURY_10Y = "DGS10"  # 10-Year Treasury Rate
    TREASURY_2Y = "DGS2"  # 2-Year Treasury Rate
    
    # Inflation
    CPI = "CPIAUCSL"  # Consumer Price Index
    PCE = "PCE"  # Personal Consumption Expenditures
    
    # Employment
    UNEMPLOYMENT = "UNRATE"  # Unemployment Rate
    NONFARM_PAYROLLS = "PAYEMS"  # Nonfarm Payrolls
    
    # GDP & Growth
    GDP = "GDP"  # Gross Domestic Product
    GDP_GROWTH = "A191RL1Q225SBEA"  # Real GDP Growth Rate
    
    # Market Indicators
    VIX = "VIXCLS"  # VIX Volatility Index
    SP500 = "SP500"  # S&P 500 Index
    
    # Money Supply
    M2 = "M2SL"  # M2 Money Supply


@dataclass
class EconomicData:
    """Economic data point"""
    indicator: str
    value: float
    date: datetime
    units: str
    frequency: str


@dataclass
class MarketRegime:
    """Market regime classification"""
    regime_type: str  # "bull", "bear", "neutral", "volatile"
    confidence: float  # 0.0 to 1.0
    indicators: Dict[str, float]
    reasoning: str
    timestamp: datetime


class FREDIntegration:
    """
    FRED (Federal Reserve Economic Data) Integration
    
    Features:
    - Real-time economic indicators
    - Market regime detection
    - Recession probability
    - Yield curve analysis
    - Inflation tracking
    
    FREE API with no rate limits!
    """
    
    def __init__(self):
        self.api_key = os.getenv("FRED_API_KEY", "")
        self.base_url = "https://api.stlouisfed.org/fred"
        self.enabled = bool(self.api_key and self.api_key != "your_fred_api_key_here")
        
        # Cache for economic data
        self.data_cache: Dict[str, EconomicData] = {}
        self.cache_duration = timedelta(hours=24)  # Economic data updates daily
        self.last_cache_update: Dict[str, datetime] = {}
        
        if self.enabled:
            logger.info("[CHECK] FRED integration enabled")
            logger.info(f"   API Key: {self.api_key[:8]}...{self.api_key[-4:]}")
            logger.info("   Rate Limit: UNLIMITED (FREE)")
        else:
            logger.warning("[WARNING]️ FRED integration disabled (no API key)")
            logger.info("   Get FREE API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
    
    async def get_indicator(
        self,
        indicator: EconomicIndicator,
        days_back: int = 30
    ) -> Optional[EconomicData]:
        """
        Get latest value for an economic indicator
        
        Args:
            indicator: Economic indicator to fetch
            days_back: How many days of history to consider
            
        Returns:
            EconomicData object or None
        """
        if not self.enabled:
            return None
        
        # Check cache
        cache_key = indicator.value
        if cache_key in self.data_cache:
            last_update = self.last_cache_update.get(cache_key)
            if last_update and datetime.now() - last_update < self.cache_duration:
                logger.debug(f"📊 Using cached data for {indicator.name}")
                return self.data_cache[cache_key]
        
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Build API request
            url = f"{self.base_url}/series/observations"
            params = {
                "series_id": indicator.value,
                "api_key": self.api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1,
                "observation_start": start_date.strftime("%Y-%m-%d"),
                "observation_end": end_date.strftime("%Y-%m-%d")
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        observations = data.get("observations", [])
                        
                        if observations:
                            obs = observations[0]
                            
                            # Parse value (handle "." for missing data)
                            value_str = obs.get("value", ".")
                            if value_str == ".":
                                logger.warning(f"[WARNING]️ No data available for {indicator.name}")
                                return None
                            
                            economic_data = EconomicData(
                                indicator=indicator.name,
                                value=float(value_str),
                                date=datetime.strptime(obs.get("date"), "%Y-%m-%d"),
                                units=data.get("units", ""),
                                frequency=data.get("frequency", "")
                            )
                            
                            # Update cache
                            self.data_cache[cache_key] = economic_data
                            self.last_cache_update[cache_key] = datetime.now()
                            
                            logger.info(f"📊 {indicator.name}: {economic_data.value} ({economic_data.date.date()})")
                            return economic_data
                        else:
                            logger.warning(f"[WARNING]️ No observations for {indicator.name}")
                            return None
                    else:
                        logger.error(f"[ERROR] FRED API error: {response.status}")
                        return None
        
        except Exception as e:
            logger.error(f"[ERROR] Error fetching {indicator.name}: {e}")
            return None
    
    async def get_yield_curve_spread(self) -> Optional[float]:
        """
        Calculate yield curve spread (10Y - 2Y)
        Negative spread often predicts recession
        
        Returns:
            Spread in percentage points or None
        """
        treasury_10y = await self.get_indicator(EconomicIndicator.TREASURY_10Y)
        treasury_2y = await self.get_indicator(EconomicIndicator.TREASURY_2Y)
        
        if treasury_10y and treasury_2y:
            spread = treasury_10y.value - treasury_2y.value
            logger.info(f"📊 Yield Curve Spread: {spread:.2f}%")
            
            if spread < 0:
                logger.warning("[WARNING]️ INVERTED YIELD CURVE - Recession risk!")
            
            return spread
        
        return None
    
    async def detect_market_regime(self) -> Optional[MarketRegime]:
        """
        Detect current market regime based on economic indicators
        
        Returns:
            MarketRegime object or None
        """
        if not self.enabled:
            return None
        
        try:
            # Fetch key indicators
            indicators = {}
            
            # Interest rates
            fed_funds = await self.get_indicator(EconomicIndicator.FED_FUNDS_RATE)
            if fed_funds:
                indicators["fed_funds_rate"] = fed_funds.value
            
            # Yield curve
            yield_spread = await self.get_yield_curve_spread()
            if yield_spread is not None:
                indicators["yield_curve_spread"] = yield_spread
            
            # Volatility
            vix = await self.get_indicator(EconomicIndicator.VIX)
            if vix:
                indicators["vix"] = vix.value
            
            # Unemployment
            unemployment = await self.get_indicator(EconomicIndicator.UNEMPLOYMENT)
            if unemployment:
                indicators["unemployment"] = unemployment.value
            
            # Analyze regime
            regime_type = "neutral"
            confidence = 0.5
            reasoning_parts = []
            
            # Check for recession signals
            if yield_spread is not None and yield_spread < 0:
                regime_type = "bear"
                confidence += 0.2
                reasoning_parts.append("Inverted yield curve")
            
            # Check volatility
            if vix and vix.value > 30:
                regime_type = "volatile"
                confidence += 0.15
                reasoning_parts.append(f"High VIX ({vix.value:.1f})")
            elif vix and vix.value < 15:
                if regime_type != "bear":
                    regime_type = "bull"
                confidence += 0.1
                reasoning_parts.append(f"Low VIX ({vix.value:.1f})")
            
            # Check unemployment
            if unemployment and unemployment.value < 4.0:
                if regime_type == "neutral":
                    regime_type = "bull"
                confidence += 0.1
                reasoning_parts.append(f"Low unemployment ({unemployment.value:.1f}%)")
            elif unemployment and unemployment.value > 6.0:
                regime_type = "bear"
                confidence += 0.15
                reasoning_parts.append(f"High unemployment ({unemployment.value:.1f}%)")
            
            # Check interest rates
            if fed_funds and fed_funds.value > 5.0:
                confidence += 0.05
                reasoning_parts.append(f"High rates ({fed_funds.value:.2f}%)")
            
            reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Neutral indicators"
            confidence = min(confidence, 1.0)
            
            regime = MarketRegime(
                regime_type=regime_type,
                confidence=confidence,
                indicators=indicators,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
            logger.info(f"📊 Market Regime: {regime_type.upper()} (confidence: {confidence:.2f})")
            logger.info(f"   Reasoning: {reasoning}")
            
            return regime
        
        except Exception as e:
            logger.error(f"[ERROR] Error detecting market regime: {e}")
            return None
    
    async def get_recession_probability(self) -> Optional[float]:
        """
        Estimate recession probability based on economic indicators
        
        Returns:
            Probability from 0.0 to 1.0 or None
        """
        regime = await self.detect_market_regime()
        
        if not regime:
            return None
        
        # Simple recession probability model
        probability = 0.0
        
        # Inverted yield curve is strong predictor
        if "yield_curve_spread" in regime.indicators:
            spread = regime.indicators["yield_curve_spread"]
            if spread < 0:
                probability += 0.4  # 40% base probability
                probability += min(abs(spread) * 0.1, 0.3)  # Up to 30% more
        
        # High unemployment
        if "unemployment" in regime.indicators:
            unemployment = regime.indicators["unemployment"]
            if unemployment > 5.0:
                probability += (unemployment - 5.0) * 0.05
        
        # High volatility
        if "vix" in regime.indicators:
            vix = regime.indicators["vix"]
            if vix > 25:
                probability += (vix - 25) * 0.01
        
        probability = min(probability, 1.0)
        
        logger.info(f"📊 Recession Probability: {probability*100:.1f}%")
        
        return probability
    
    def get_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "enabled": self.enabled,
            "cache_size": len(self.data_cache),
            "cached_indicators": list(self.data_cache.keys()),
            "rate_limit": "UNLIMITED (FREE)"
        }


# Global instance
_fred_instance: Optional[FREDIntegration] = None


def get_fred() -> FREDIntegration:
    """Get or create the global FRED instance"""
    global _fred_instance
    if _fred_instance is None:
        _fred_instance = FREDIntegration()
    return _fred_instance


# Example usage
async def test_fred():
    """Test the FRED integration"""
    fred = get_fred()
    
    if not fred.enabled:
        print("[ERROR] FRED not enabled (no API key)")
        print("Get FREE API key at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return
    
    print("[CHECK] FRED enabled")
    print(f"Status: {fred.get_status()}")
    
    # Test key indicators
    print("\n📊 Fetching key economic indicators...")
    
    fed_funds = await fred.get_indicator(EconomicIndicator.FED_FUNDS_RATE)
    if fed_funds:
        print(f"  Federal Funds Rate: {fed_funds.value}%")
    
    unemployment = await fred.get_indicator(EconomicIndicator.UNEMPLOYMENT)
    if unemployment:
        print(f"  Unemployment Rate: {unemployment.value}%")
    
    vix = await fred.get_indicator(EconomicIndicator.VIX)
    if vix:
        print(f"  VIX: {vix.value}")
    
    # Test yield curve
    print("\n📊 Analyzing yield curve...")
    spread = await fred.get_yield_curve_spread()
    if spread is not None:
        print(f"  Yield Curve Spread (10Y-2Y): {spread:.2f}%")
        if spread < 0:
            print("  [WARNING]️ INVERTED - Recession risk!")
    
    # Test market regime
    print("\n📊 Detecting market regime...")
    regime = await fred.detect_market_regime()
    if regime:
        print(f"  Regime: {regime.regime_type.upper()}")
        print(f"  Confidence: {regime.confidence:.2f}")
        print(f"  Reasoning: {regime.reasoning}")
    
    # Test recession probability
    print("\n📊 Calculating recession probability...")
    recession_prob = await fred.get_recession_probability()
    if recession_prob is not None:
        print(f"  Recession Probability: {recession_prob*100:.1f}%")


if __name__ == "__main__":
    asyncio.run(test_fred())

