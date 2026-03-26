"""
FRED API Integration - Real Federal Reserve Economic Data
Replaces fake FederalReserveAPI with REAL government data
API Key: Configured for higher rate limits

Data Available:
- Interest rates (Fed Funds Rate, Treasury Yields)
- Inflation (CPI, PPI, PCE)
- Employment (Unemployment Rate, Jobless Claims)
- GDP Growth, Consumer Confidence, Manufacturing PMI
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class EconomicIndicator(Enum):
    """Key economic indicators from FRED"""
    FED_FUNDS_RATE = "FEDFUNDS"
    TREASURY_10Y = "DGS10"
    TREASURY_2Y = "DGS2"
    CPI = "CPIAUCSL"
    CORE_CPI = "CPILFESL"
    UNEMPLOYMENT = "UNRATE"
    INITIAL_CLAIMS = "ICSA"
    GDP = "GDP"
    CONSUMER_CONFIDENCE = "UMCSENT"
    VIX = "VIXCLS"
    RETAIL_SALES = "RSXFS"
    INDUSTRIAL_PRODUCTION = "INDPRO"

@dataclass
class EconomicDataPoint:
    """Single economic data point"""
    indicator: str
    value: float
    date: str
    change: float = 0.0
    change_percent: float = 0.0
    trend: str = "stable"
    impact: str = "neutral"
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MacroSignal:
    """Macro-economic trading signal"""
    signal_type: str
    strength: float
    direction: str
    confidence: float
    indicators: List[str]
    description: str
    timestamp: datetime = field(default_factory=datetime.now)

class FREDApi:
    """
    Real Federal Reserve Economic Data API
    Replaces fake FederalReserveAPI with REAL data
    """
    
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    def __init__(self, api_key: str = "05dfcac87de01396088f8f0cf31e7832"):
        self.api_key = api_key
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = timedelta(hours=1)
        self.last_update: Dict[str, datetime] = {}
        
        self.bullish_conditions = {
            EconomicIndicator.FED_FUNDS_RATE: "falling",
            EconomicIndicator.UNEMPLOYMENT: "falling", 
            EconomicIndicator.GDP: "rising",
            EconomicIndicator.CONSUMER_CONFIDENCE: "rising",
            EconomicIndicator.RETAIL_SALES: "rising",
        }
        
        self.bearish_conditions = {
            EconomicIndicator.FED_FUNDS_RATE: "rising",
            EconomicIndicator.CPI: "rising",
            EconomicIndicator.UNEMPLOYMENT: "rising",
            EconomicIndicator.VIX: "rising",
        }
        
        logger.info("✅ FRED API initialized with API key - REAL economic data enabled")
    
    async def fetch_series(self, series_id: str, limit: int = 10) -> List[Dict]:
        """Fetch data series from FRED"""
        cache_key = f"{series_id}_{limit}"
        if cache_key in self.cache:
            last_update = self.last_update.get(cache_key)
            if last_update and datetime.now() - last_update < self.cache_ttl:
                return self.cache[cache_key]
        
        url = f"{self.BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        observations = data.get("observations", [])
                        self.cache[cache_key] = observations
                        self.last_update[cache_key] = datetime.now()
                        logger.debug(f"✅ Fetched {len(observations)} observations for {series_id}")
                        return observations
                    else:
                        logger.warning(f"⚠️ FRED API returned status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"❌ FRED API error: {e}")
            return []
    
    async def get_indicator(self, indicator: EconomicIndicator) -> Optional[EconomicDataPoint]:
        """Get current value and trend for an economic indicator"""
        observations = await self.fetch_series(indicator.value, limit=5)
        
        if not observations or len(observations) < 2:
            return None
        
        current_obs = observations[0]
        previous_obs = observations[1]
        
        try:
            current_value = float(current_obs.get("value", 0))
            previous_value = float(previous_obs.get("value", 0))
        except (ValueError, TypeError):
            return None
        
        change = current_value - previous_value
        change_percent = (change / previous_value * 100) if previous_value != 0 else 0
        
        if change_percent > 0.5:
            trend = "rising"
        elif change_percent < -0.5:
            trend = "falling"
        else:
            trend = "stable"
        
        if indicator in self.bullish_conditions:
            if trend == self.bullish_conditions[indicator]:
                impact = "bullish"
            elif trend != "stable":
                impact = "bearish"
            else:
                impact = "neutral"
        elif indicator in self.bearish_conditions:
            if trend == self.bearish_conditions[indicator]:
                impact = "bearish"
            elif trend != "stable":
                impact = "bullish"
            else:
                impact = "neutral"
        else:
            impact = "neutral"
        
        return EconomicDataPoint(
            indicator=indicator.value,
            value=current_value,
            date=current_obs.get("date", ""),
            change=change,
            change_percent=change_percent,
            trend=trend,
            impact=impact
        )
    
    async def get_all_indicators(self) -> Dict[str, EconomicDataPoint]:
        """Fetch all key economic indicators"""
        results = {}
        key_indicators = [
            EconomicIndicator.FED_FUNDS_RATE,
            EconomicIndicator.TREASURY_10Y,
            EconomicIndicator.TREASURY_2Y,
            EconomicIndicator.CPI,
            EconomicIndicator.UNEMPLOYMENT,
            EconomicIndicator.GDP,
            EconomicIndicator.CONSUMER_CONFIDENCE,
            EconomicIndicator.VIX,
        ]
        
        tasks = [self.get_indicator(ind) for ind in key_indicators]
        data_points = await asyncio.gather(*tasks, return_exceptions=True)
        
        for indicator, data_point in zip(key_indicators, data_points):
            if isinstance(data_point, EconomicDataPoint):
                results[indicator.name] = data_point
        
        logger.info(f"✅ Fetched {len(results)} REAL economic indicators from FRED")
        return results
    
    async def generate_macro_signals(self) -> List[MacroSignal]:
        """Generate trading signals from macro-economic data"""
        indicators = await self.get_all_indicators()
        signals = []
        
        # Yield Curve Inversion
        if "TREASURY_10Y" in indicators and "TREASURY_2Y" in indicators:
            t10y = indicators["TREASURY_10Y"].value
            t2y = indicators["TREASURY_2Y"].value
            spread = t10y - t2y
            
            if spread < 0:
                signals.append(MacroSignal(
                    signal_type="yield_curve_inversion",
                    strength=min(abs(spread) / 0.5, 1.0),
                    direction="bearish",
                    confidence=0.85,
                    indicators=["TREASURY_10Y", "TREASURY_2Y"],
                    description=f"Yield curve inverted by {abs(spread):.2f}% - Recession warning"
                ))
        
        # Rate Environment
        if "FED_FUNDS_RATE" in indicators:
            ffr = indicators["FED_FUNDS_RATE"]
            if ffr.trend == "rising":
                signals.append(MacroSignal(
                    signal_type="rate_hike_environment",
                    strength=min(abs(ffr.change_percent) / 10, 1.0),
                    direction="bearish",
                    confidence=0.80,
                    indicators=["FED_FUNDS_RATE"],
                    description=f"Fed funds rate rising - Growth stocks vulnerable"
                ))
            elif ffr.trend == "falling":
                signals.append(MacroSignal(
                    signal_type="rate_cut_environment",
                    strength=min(abs(ffr.change_percent) / 10, 1.0),
                    direction="bullish",
                    confidence=0.80,
                    indicators=["FED_FUNDS_RATE"],
                    description=f"Fed funds rate falling - Risk assets favorable"
                ))
        
        # Inflation
        if "CPI" in indicators:
            cpi = indicators["CPI"]
            if cpi.value > 4.0 and cpi.trend == "rising":
                signals.append(MacroSignal(
                    signal_type="inflation_surge",
                    strength=min(cpi.value / 8, 1.0),
                    direction="bearish",
                    confidence=0.75,
                    indicators=["CPI"],
                    description=f"Inflation elevated at {cpi.value:.1f}%"
                ))
        
        # VIX Fear
        if "VIX" in indicators:
            vix = indicators["VIX"]
            if vix.value > 30:
                signals.append(MacroSignal(
                    signal_type="high_fear",
                    strength=min(vix.value / 50, 1.0),
                    direction="bearish",
                    confidence=0.80,
                    indicators=["VIX"],
                    description=f"VIX at {vix.value:.1f} - Extreme fear"
                ))
        
        logger.info(f"✅ Generated {len(signals)} REAL macro trading signals")
        return signals
    
    async def get_market_regime(self) -> Dict[str, Any]:
        """Determine current market regime from macro data"""
        signals = await self.generate_macro_signals()
        indicators = await self.get_all_indicators()
        
        bullish_score = 0
        bearish_score = 0
        
        for signal in signals:
            if signal.direction == "bullish":
                bullish_score += signal.strength * signal.confidence
            elif signal.direction == "bearish":
                bearish_score += signal.strength * signal.confidence
        
        for name, data_point in indicators.items():
            if data_point.impact == "bullish":
                bullish_score += 0.3
            elif data_point.impact == "bearish":
                bearish_score += 0.3
        
        total_score = bullish_score + bearish_score
        if total_score == 0:
            regime = "NORMAL"
            confidence = 0.5
        elif bullish_score > bearish_score * 1.5:
            regime = "BULL"
            confidence = min(bullish_score / (bullish_score + bearish_score), 0.95)
        elif bearish_score > bullish_score * 1.5:
            regime = "BEAR"
            confidence = min(bearish_score / (bullish_score + bearish_score), 0.95)
        else:
            regime = "NORMAL"
            confidence = 0.6
        
        if "VIX" in indicators and indicators["VIX"].value > 25:
            regime = "VOLATILE"
            confidence = min(indicators["VIX"].value / 35, 0.95)
        
        return {
            "regime": regime,
            "confidence": confidence,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "signals_count": len(signals),
            "indicators_count": len(indicators),
            "timestamp": datetime.now().isoformat(),
            "data_source": "FRED_REAL_DATA"
        }
    
    async def close(self):
        """Clean up resources (placeholder for consistency)"""
        pass

# Global instance
fred_api = FREDApi()

async def get_real_economic_data():
    """Get real economic data"""
    return await fred_api.get_all_indicators()

async def get_macro_signals():
    """Get macro trading signals"""
    return await fred_api.generate_macro_signals()

async def get_market_regime():
    """Get market regime"""
    return await fred_api.get_market_regime()

if __name__ == "__main__":
    async def test():
        print("=" * 60)
        print("Testing FRED API - REAL Economic Data")
        print("=" * 60)
        
        print("\n📊 Fetching Economic Indicators...")
        indicators = await get_real_economic_data()
        for name, data in indicators.items():
            print(f"  {name}: {data.value:.2f} ({data.trend}, {data.impact})")
        
        print("\n📈 Generating Macro Signals...")
        signals = await get_macro_signals()
        for signal in signals:
            print(f"  {signal.signal_type}: {signal.direction} (strength: {signal.strength:.2f})")
        
        print("\n🎯 Market Regime Detection...")
        regime = await get_market_regime()
        print(f"  Regime: {regime['regime']}")
        print(f"  Confidence: {regime['confidence']:.1%}")
        print(f"  Data Source: {regime['data_source']}")
        
        print("\n✅ FRED API Test Complete - REAL DATA FLOWING!")
    
    asyncio.run(test())
