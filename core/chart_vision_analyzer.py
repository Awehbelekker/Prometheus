"""
PROMETHEUS Chart Vision Analyzer — Multi-Timeframe Edition
Uses llava (7b/13b) via Ollama to perform visual analysis of candlestick charts.

Generates candlestick charts with technical indicators using mplfinance,
then sends the rendered image to the vision model for pattern recognition.

Capabilities:
- Multi-timeframe analysis (recent intraday, swing, and daily views)
- Candlestick pattern detection (doji, hammer, engulfing, etc.)
- Support/resistance level identification
- Trend direction analysis with strength scoring
- Chart formation recognition (head-and-shoulders, double-top, etc.)
- VWAP + Volume overlay for institutional-level context
- Structured prompting for reliable, parseable AI output
- Optional cloud-vision second opinion (Gemini / GPT-4o / Claude)
"""

import asyncio
import aiohttp
import base64
import io
import json
import logging
import os
import re
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server use
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplfinance as mpf
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_BASE_URL = os.getenv(
    "GPT_OSS_API_ENDPOINT",
    os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
).strip().strip("'\"")

# GPU-aware vision model selection (use better models when GPU available)
try:
    from gpu_detector import detect_gpu_backend
    _gpu_info = detect_gpu_backend()
    if _gpu_info.get("available") and _gpu_info.get("backend") in ("CUDA", "DirectML"):
        VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:13b")
    else:
        VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")
except Exception:
    VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava:7b")

# Vision requests take longer — model must process the image
VISION_TIMEOUT = int(os.getenv("OLLAMA_VISION_TIMEOUT", "120"))

# Chart rendering settings — 1024×768 effective output
CHART_WIDTH = 14    # inches
CHART_HEIGHT = 10   # inches
CHART_DPI = 120     # 14×120=1680px wide, 10×120=1200px tall
CHART_STYLE = "charles"

# Multi-timeframe slicing defaults
# When the caller provides a single DataFrame we slice it ourselves.
# "recent" = last 20 bars, "swing" = last 60, "full" = everything
MTF_RECENT_BARS = 20
MTF_SWING_BARS = 60

# Cloud consensus — enable when an API key is available
CLOUD_CONSENSUS_ENABLED = bool(
    os.getenv("GOOGLE_AI_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("ZHIPUAI_API_KEY")
    or os.getenv("ANTHROPIC_API_KEY")
)


class ChartVisionAnalyzer:
    """
    AI-powered chart visual analysis using Ollama llava:7b.

    Renders professional candlestick charts with volume and technical
    overlays, then uses the vision model to identify patterns that
    are difficult to detect with purely numerical analysis.
    """

    # Cache TTL: how long a vision result stays valid (seconds)
    CACHE_TTL = int(os.getenv("VISION_CACHE_TTL", "300"))  # 5 minutes default

    def __init__(self):
        self.ollama_url = OLLAMA_BASE_URL.rstrip("/")
        self.vision_model = VISION_MODEL
        self.session: Optional[aiohttp.ClientSession] = None
        self.is_connected = False
        self._model_available = False
        # Result cache: {symbol: {"result": dict, "timestamp": float}}
        self._cache: Dict[str, Dict] = {}
        # Background analysis tracking
        self._pending: Dict[str, asyncio.Task] = {}
        self._analysis_count = 0
        self._cache_hits = 0

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self):
        """Check Ollama connectivity and llava model availability."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=VISION_TIMEOUT)
        )
        try:
            async with self.session.get(f"{self.ollama_url}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = [m["name"] for m in data.get("models", [])]
                    self._model_available = any(
                        self.vision_model in m for m in models
                    )
                    self.is_connected = True
                    if self._model_available:
                        logger.info(
                            f"Chart Vision Analyzer ready - model: {self.vision_model}"
                        )
                    else:
                        logger.warning(
                            f"Vision model {self.vision_model} not found. "
                            f"Available: {models}"
                        )
        except Exception as e:
            logger.warning(f"Ollama not reachable for vision: {e}")

    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.close()
            self.session = None

    def is_available(self) -> bool:
        """Check if the vision analyzer is ready."""
        return self.is_connected and self._model_available

    # ------------------------------------------------------------------
    # Main analysis method (multi-timeframe)
    # ------------------------------------------------------------------

    async def analyze_chart(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Multi-timeframe chart analysis.

        Slices *price_data* into up to 3 views (recent, swing, full),
        renders each with VWAP + Bollinger overlays, sends to the vision
        model, and merges the per-timeframe verdicts into a single result.

        If cloud consensus is enabled, a second opinion is requested for
        BUY/SELL signals with confidence >= 0.65.
        """
        if not self.is_available():
            return self._fallback_analysis(symbol, price_data)

        # Check cache first
        cached = self.get_cached(symbol)
        if cached:
            logger.info(f"Chart Vision cache hit for {symbol}")
            return cached

        try:
            self._analysis_count += 1

            # --- Build indicator overlays if none supplied ----------------
            indicators = self._auto_indicators(price_data, indicators)

            # --- Slice into timeframes ------------------------------------
            frames = self._slice_timeframes(price_data)

            # --- Analyze each timeframe -----------------------------------
            tf_results: List[Tuple[str, Dict[str, Any]]] = []
            for label, tf_df in frames:
                tf_indicators = self._auto_indicators(tf_df, None)
                chart_bytes = self._render_chart(symbol, tf_df, tf_indicators, label)
                if not chart_bytes:
                    continue
                b64_image = base64.b64encode(chart_bytes).decode("utf-8")
                prompt = self._build_vision_prompt(symbol, label, len(tf_df))
                raw = await self._ollama_vision_generate(prompt, b64_image)
                parsed = self._parse_vision_response(raw, symbol)
                parsed["timeframe"] = label
                tf_results.append((label, parsed))

            if not tf_results:
                return self._fallback_analysis(symbol, price_data)

            # --- Merge timeframe results ----------------------------------
            result = self._merge_timeframe_results(tf_results, symbol)
            result["source"] = "llava-vision-mtf"
            result["model"] = self.vision_model
            result["timeframes_analyzed"] = [label for label, _ in tf_results]

            # --- Optional cloud consensus ---------------------------------
            if CLOUD_CONSENSUS_ENABLED and result.get("confidence", 0) >= 0.65:
                result = await self._cloud_consensus(symbol, price_data, indicators, result)

            self._store_cache(symbol, result)
            return result

        except Exception as e:
            logger.debug(f"Chart vision analysis failed for {symbol}: {e}")
            return self._fallback_analysis(symbol, price_data)

    # ------------------------------------------------------------------
    # Helpers: indicator auto-computation & timeframe slicing
    # ------------------------------------------------------------------

    @staticmethod
    def _auto_indicators(
        df: pd.DataFrame, provided: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Auto-compute SMA-20, SMA-50, Bollinger Bands and VWAP."""
        if provided:
            return provided
        if len(df) < 20:
            return None
        close_col = "Close" if "Close" in df.columns else "close"
        vol_col = "Volume" if "Volume" in df.columns else "volume"
        if close_col not in df.columns:
            return None
        close = df[close_col]
        indicators: Dict[str, Any] = {}
        indicators["SMA-20"] = close.rolling(20).mean()
        if len(df) >= 50:
            indicators["SMA-50"] = close.rolling(50).mean()
        sma20 = indicators["SMA-20"]
        std20 = close.rolling(20).std()
        indicators["BB-Upper"] = sma20 + (std20 * 2)
        indicators["BB-Lower"] = sma20 - (std20 * 2)
        # VWAP (cumulative for the visible window)
        if vol_col in df.columns:
            high_col = "High" if "High" in df.columns else "high"
            low_col = "Low" if "Low" in df.columns else "low"
            if high_col in df.columns and low_col in df.columns:
                typical = (df[high_col] + df[low_col] + df[close_col]) / 3
                cum_vol = df[vol_col].cumsum()
                cum_tp_vol = (typical * df[vol_col]).cumsum()
                vwap = cum_tp_vol / cum_vol.replace(0, np.nan)
                indicators["VWAP"] = vwap
        return indicators

    def _slice_timeframes(
        self, df: pd.DataFrame
    ) -> List[Tuple[str, pd.DataFrame]]:
        """Slice a single DataFrame into recent / swing / full views."""
        frames: List[Tuple[str, pd.DataFrame]] = []
        n = len(df)
        if n >= MTF_SWING_BARS + 10:
            frames.append(("recent", df.iloc[-MTF_RECENT_BARS:]))
            frames.append(("swing", df.iloc[-MTF_SWING_BARS:]))
            frames.append(("full", df))
        elif n >= MTF_RECENT_BARS + 5:
            frames.append(("recent", df.iloc[-MTF_RECENT_BARS:]))
            frames.append(("full", df))
        else:
            frames.append(("full", df))
        return frames

    # ------------------------------------------------------------------
    # Chart rendering
    # ------------------------------------------------------------------

    def _render_chart(
        self,
        symbol: str,
        df: pd.DataFrame,
        indicators: Optional[Dict[str, Any]] = None,
        timeframe_label: str = "",
    ) -> Optional[bytes]:
        """
        Render a candlestick chart with volume and optional indicators.

        Returns PNG bytes or None on failure.
        """
        try:
            # Ensure proper column names for mplfinance
            df = df.copy()

            # Normalize column names
            col_map = {}
            for col in df.columns:
                lower = col.lower()
                if lower == "open":
                    col_map[col] = "Open"
                elif lower == "high":
                    col_map[col] = "High"
                elif lower == "low":
                    col_map[col] = "Low"
                elif lower == "close":
                    col_map[col] = "Close"
                elif lower == "volume":
                    col_map[col] = "Volume"
            if col_map:
                df = df.rename(columns=col_map)

            # Ensure DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                if "Date" in df.columns:
                    df["Date"] = pd.to_datetime(df["Date"])
                    df = df.set_index("Date")
                elif "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    df = df.set_index("date")
                else:
                    df.index = pd.to_datetime(df.index)

            # Build additional plot overlays for indicators
            addplots = []
            if indicators:
                colors = ["#00BFFF", "#FF6347", "#32CD32", "#FFD700", "#FF69B4"]
                ci = 0
                for name, series in indicators.items():
                    if series is not None and isinstance(series, (pd.Series, list)):
                        if isinstance(series, list):
                            series = pd.Series(series, index=df.index[: len(series)])
                        # Align series to df index
                        series = series.reindex(df.index)
                        if series.notna().sum() > 0:
                            addplots.append(
                                mpf.make_addplot(
                                    series,
                                    color=colors[ci % len(colors)],
                                    width=1.2,
                                )
                            )
                            ci += 1

            # Use a professional dark style
            mc = mpf.make_marketcolors(
                up="#26a69a",
                down="#ef5350",
                edge="inherit",
                wick="inherit",
                volume={"up": "#26a69a", "down": "#ef5350"},
            )
            style = mpf.make_mpf_style(
                marketcolors=mc,
                facecolor="#1e1e2f",
                edgecolor="#1e1e2f",
                gridcolor="#2d2d44",
                gridstyle="--",
                gridaxis="both",
                y_on_right=True,
            )

            # Render to buffer
            buf = io.BytesIO()
            kwargs = {
                "type": "candle",
                "volume": "Volume" in df.columns,
                "style": style,
                "title": f"\n{symbol} — {timeframe_label.upper()} ({len(df)} bars)" if timeframe_label else f"\n{symbol} — Candlestick Chart",
                "figsize": (CHART_WIDTH, CHART_HEIGHT),
                "savefig": {
                    "fname": buf,
                    "dpi": CHART_DPI,
                    "bbox_inches": "tight",
                    "facecolor": "#1e1e2f",
                },
                "warn_too_much_data": 500,
            }
            if addplots:
                kwargs["addplot"] = addplots

            mpf.plot(df, **kwargs)
            buf.seek(0)
            chart_bytes = buf.read()
            buf.close()

            # Close all matplotlib figures to free memory
            plt.close("all")

            logger.debug(
                f"Chart rendered for {symbol}: {len(chart_bytes)} bytes, "
                f"{len(df)} candles"
            )
            return chart_bytes

        except Exception as e:
            logger.error(f"Chart rendering failed for {symbol}: {e}")
            plt.close("all")
            return None

    # ------------------------------------------------------------------
    # Vision prompt
    # ------------------------------------------------------------------

    def _build_vision_prompt(self, symbol: str, timeframe: str = "", num_bars: int = 0) -> str:
        """Structured prompt — asks specific yes/no + categorical questions."""
        tf_desc = {
            "recent": "the most recent 20 candles (short-term momentum)",
            "swing": "the last 60 candles (swing-trade horizon)",
            "full": f"the full history ({num_bars} candles)" if num_bars else "the full chart",
        }.get(timeframe, "the chart")

        return (
            f"You are a senior quantitative analyst examining a professional "
            f"candlestick chart for **{symbol}** showing {tf_desc}.\n"
            f"The chart includes: price candles, volume bars, SMA-20 (blue), "
            f"SMA-50 (red), Bollinger Bands (green), and VWAP (gold) if data is available.\n\n"

            f"Answer EACH question below with ONLY the specified format.\n\n"

            f"Q1  BULLISH_ENGULFING present in last 5 candles?  YES / NO\n"
            f"Q2  BEARISH_ENGULFING present in last 5 candles?  YES / NO\n"
            f"Q3  HAMMER or INVERTED_HAMMER visible?            YES / NO\n"
            f"Q4  DOJI visible in last 3 candles?               YES / NO\n"
            f"Q5  SHOOTING_STAR visible?                        YES / NO\n"
            f"Q6  MORNING_STAR or EVENING_STAR pattern?         YES / NO  (which one?)\n"
            f"Q7  Any multi-candle FORMATION?  Name it or NONE.\n"
            f"    (double top, double bottom, head-and-shoulders, triangle, wedge, flag, cup-and-handle)\n"
            f"Q8  TREND direction?  STRONG_UPTREND / UPTREND / SIDEWAYS / DOWNTREND / STRONG_DOWNTREND\n"
            f"Q9  Is VOLUME confirming the trend?  YES / NO\n"
            f"Q10 Is price ABOVE or BELOW the VWAP line?  ABOVE / BELOW / NO_VWAP\n"
            f"Q11 RECOMMENDATION?  BUY / SELL / HOLD\n"
            f"Q12 CONFIDENCE (0.00 – 1.00)?\n"
            f"Q13 One-sentence REASONING.\n\n"

            f"NOW output ONLY valid JSON (no markdown fences):\n"
            f'{{"bullish_engulfing": true/false, "bearish_engulfing": true/false, '
            f'"hammer": true/false, "doji": true/false, "shooting_star": true/false, '
            f'"morning_evening_star": "MORNING_STAR" or "EVENING_STAR" or "NONE", '
            f'"formation": "name or NONE", '
            f'"trend": "strong_uptrend/uptrend/sideways/downtrend/strong_downtrend", '
            f'"volume_confirms": true/false, '
            f'"price_vs_vwap": "ABOVE/BELOW/NO_VWAP", '
            f'"recommendation": "BUY/SELL/HOLD", '
            f'"confidence": 0.75, '
            f'"reasoning": "..."}}'
        )

    # ------------------------------------------------------------------
    # Ollama vision API call
    # ------------------------------------------------------------------

    def get_cached(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Return cached result if still valid, else None."""
        entry = self._cache.get(symbol)
        if entry and (time.monotonic() - entry["timestamp"]) < self.CACHE_TTL:
            self._cache_hits += 1
            logger.debug(f"Cache hit for {symbol} (age {time.monotonic() - entry['timestamp']:.0f}s)")
            return entry["result"]
        return None

    def _store_cache(self, symbol: str, result: Dict[str, Any]):
        """Store a result in cache."""
        self._cache[symbol] = {"result": result, "timestamp": time.monotonic()}
        # Evict old entries if cache grows too large
        if len(self._cache) > 200:
            oldest = min(self._cache, key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest]

    def cache_stats(self) -> Dict[str, int]:
        """Return cache statistics."""
        valid = sum(1 for e in self._cache.values()
                    if (time.monotonic() - e["timestamp"]) < self.CACHE_TTL)
        return {
            "total_analyses": self._analysis_count,
            "cache_hits": self._cache_hits,
            "cached_symbols": valid,
            "cache_size": len(self._cache),
        }

    async def _ollama_vision_generate(
        self,
        prompt: str,
        b64_image: str,
        max_tokens: int = 500,
        temperature: float = 0.3,
    ) -> str:
        """Send an image + prompt to Ollama llava and return the response text."""
        # Ollama runs its own inference on GPU — only skip if system memory
        # is critically exhausted (not CPU, since llava uses GPU)
        try:
            import psutil
            mem = psutil.virtual_memory()
            if mem.percent > 95:
                logger.debug("Memory critically low (>95%), skipping chart vision")
                return ""
        except Exception:
            pass
        if self.session is None:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=VISION_TIMEOUT)
            )

        url = f"{self.ollama_url}/api/generate"
        payload = {
            "model": self.vision_model,
            "prompt": prompt,
            "images": [b64_image],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with self.session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("response", "")
            else:
                text = await resp.text()
                raise RuntimeError(
                    f"Ollama vision API error {resp.status}: {text[:200]}"
                )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _parse_vision_response(
        self, response: str, symbol: str
    ) -> Dict[str, Any]:
        """Parse the vision model's structured JSON (or fall back to keyword scan)."""
        parsed = self._extract_json(response)
        if parsed:
            # Normalise recommendation
            rec = str(parsed.get("recommendation", "HOLD")).upper().strip()
            if rec not in ("BUY", "SELL", "HOLD"):
                rec = "HOLD"
            parsed["recommendation"] = rec
            parsed["confidence"] = min(
                max(float(parsed.get("confidence", 0.6)), 0.0), 1.0
            )
            # Convert structured boolean pattern fields → patterns list
            patterns = parsed.get("patterns", [])
            if not patterns:
                patterns = []
            _bool_map = {
                "bullish_engulfing": "Bullish Engulfing",
                "bearish_engulfing": "Bearish Engulfing",
                "hammer": "Hammer",
                "doji": "Doji",
                "shooting_star": "Shooting Star",
            }
            for key, label in _bool_map.items():
                if parsed.get(key) is True and label not in patterns:
                    patterns.append(label)
            me_star = str(parsed.get("morning_evening_star", "NONE")).upper()
            if me_star == "MORNING_STAR" and "Morning Star" not in patterns:
                patterns.append("Morning Star")
            elif me_star == "EVENING_STAR" and "Evening Star" not in patterns:
                patterns.append("Evening Star")
            formation = str(parsed.get("formation", "NONE"))
            formations = parsed.get("formations", [])
            if formation.upper() != "NONE" and formation not in formations:
                formations.append(formation)
            parsed["patterns"] = patterns
            parsed["formations"] = formations
            return parsed

        # Heuristic fallback: scan text for keywords
        upper = (response or "").upper()
        trend = "sideways"
        rec = "HOLD"
        confidence = 0.55

        if any(w in upper for w in ("UPTREND", "BULLISH", "ASCENDING", "BREAKOUT")):
            trend = "uptrend"; rec = "BUY"; confidence = 0.65
        elif any(w in upper for w in ("DOWNTREND", "BEARISH", "DESCENDING", "BREAKDOWN")):
            trend = "downtrend"; rec = "SELL"; confidence = 0.63

        patterns = []
        for kw in [
            "DOJI", "HAMMER", "ENGULFING", "SHOOTING STAR", "MORNING STAR",
            "EVENING STAR", "SPINNING TOP", "MARUBOZU", "HARAMI",
            "HEAD AND SHOULDERS", "DOUBLE TOP", "DOUBLE BOTTOM",
            "TRIANGLE", "WEDGE", "FLAG", "PENNANT", "CUP AND HANDLE",
        ]:
            if kw in upper:
                patterns.append(kw.title())

        return {
            "patterns": patterns, "formations": [], "trend": trend,
            "support_level": "N/A", "resistance_level": "N/A",
            "volume_pattern": "stable", "recommendation": rec,
            "confidence": confidence,
            "reasoning": response[:200] if response else f"Vision analysis for {symbol}",
        }

    @staticmethod
    def _extract_json(text: str) -> Optional[Dict[str, Any]]:
        """Extract the first JSON object from text."""
        if not text:
            return None
        try:
            return json.loads(text.strip())
        except (json.JSONDecodeError, ValueError):
            pass
        match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                pass
        return None


    # ------------------------------------------------------------------
    # Multi-timeframe merger
    # ------------------------------------------------------------------

    @staticmethod
    def _merge_timeframe_results(
        tf_results: List[Tuple[str, Dict[str, Any]]], symbol: str
    ) -> Dict[str, Any]:
        """Combine per-timeframe vision results into one verdict.

        Priority: "recent" for pattern detection, "full" for trend,
        weighted-average for confidence.  If recommendations conflict
        across timeframes the result defaults to HOLD.
        """
        all_patterns: List[str] = []
        all_formations: List[str] = []
        recs: List[str] = []
        confs: List[float] = []
        reasonings: List[str] = []
        trend = "sideways"
        vol_pattern = "stable"
        support = "N/A"
        resistance = "N/A"

        # Weights: recent=3, swing=2, full=1
        _w = {"recent": 3.0, "swing": 2.0, "full": 1.0}

        for label, r in tf_results:
            w = _w.get(label, 1.0)
            all_patterns.extend(r.get("patterns", []))
            all_formations.extend(r.get("formations", []))
            recs.append(r.get("recommendation", "HOLD"))
            confs.append(r.get("confidence", 0.5) * w)
            reasonings.append(f"[{label}] {r.get('reasoning', '')[:60]}")
            if label == "full":
                trend = r.get("trend", trend)
                support = r.get("support_level", support)
                resistance = r.get("resistance_level", resistance)
            if label == "recent":
                vol_pattern = r.get("volume_pattern", vol_pattern)
                # Recent trend overrides if strong
                rt = r.get("trend", "")
                if "strong" in rt.lower():
                    trend = rt

        # De-duplicate patterns
        seen: set = set()
        unique_patterns = []
        for p in all_patterns:
            pl = p.lower()
            if pl not in seen:
                seen.add(pl)
                unique_patterns.append(p)

        # Consensus recommendation
        buy_votes = sum(1 for r in recs if r == "BUY")
        sell_votes = sum(1 for r in recs if r == "SELL")
        total = len(recs)
        if buy_votes > total / 2:
            final_rec = "BUY"
        elif sell_votes > total / 2:
            final_rec = "SELL"
        elif buy_votes == sell_votes and buy_votes > 0:
            final_rec = "HOLD"  # conflicting signals → stay out
        else:
            final_rec = max(set(recs), key=recs.count) if recs else "HOLD"

        total_weight = sum(_w.get(label, 1.0) for label, _ in tf_results) or 1.0
        avg_conf = sum(confs) / total_weight

        return {
            "patterns": unique_patterns,
            "formations": list(set(all_formations)),
            "trend": trend,
            "support_level": support,
            "resistance_level": resistance,
            "volume_pattern": vol_pattern,
            "recommendation": final_rec,
            "confidence": round(min(max(avg_conf, 0.0), 1.0), 3),
            "reasoning": " | ".join(reasonings)[:300],
        }

    # ------------------------------------------------------------------
    # Cloud consensus (second opinion)
    # ------------------------------------------------------------------

    async def _cloud_consensus(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        indicators: Optional[Dict[str, Any]],
        local_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Ask cloud vision for a second opinion on BUY/SELL signals.

        If the cloud agrees with the local model, confidence gets a boost.
        If they disagree, confidence is reduced and recommendation may
        flip to HOLD.
        """
        try:
            from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig

            cloud = CloudVisionAnalyzer(CloudVisionConfig())
            if not cloud.api_available:
                return local_result

            # Render chart to a temp file (CloudVisionAnalyzer needs a path)
            chart_bytes = self._render_chart(symbol, price_data, indicators, "consensus")
            if not chart_bytes:
                return local_result

            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.write(chart_bytes)
            tmp.close()

            cloud_result = cloud.analyze_chart(tmp.name, symbol, "1D")
            os.unlink(tmp.name)

            # Map cloud signal to BUY/SELL/HOLD
            cloud_signal = "HOLD"
            if hasattr(cloud_result, "trend_direction"):
                cd = str(cloud_result.trend_direction).lower()
                if "bull" in cd:
                    cloud_signal = "BUY"
                elif "bear" in cd:
                    cloud_signal = "SELL"

            local_rec = local_result["recommendation"]
            if cloud_signal == local_rec:
                # Agreement → boost confidence by 10%
                local_result["confidence"] = min(local_result["confidence"] * 1.10, 0.95)
                local_result["cloud_consensus"] = "AGREE"
            else:
                # Disagreement → reduce confidence, maybe flip to HOLD
                local_result["confidence"] *= 0.80
                if local_result["confidence"] < 0.55:
                    local_result["recommendation"] = "HOLD"
                local_result["cloud_consensus"] = f"DISAGREE (cloud={cloud_signal})"

            logger.info(
                f"☁️ Cloud consensus for {symbol}: local={local_rec}, "
                f"cloud={cloud_signal} → {local_result['cloud_consensus']}"
            )

        except Exception as e:
            logger.debug(f"Cloud consensus skipped for {symbol}: {e}")
            local_result["cloud_consensus"] = "SKIPPED"

        return local_result

    # ------------------------------------------------------------------
    # Fallback (no vision model available)
    # ------------------------------------------------------------------

    def _fallback_analysis(
        self, symbol: str, df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Simple numerical fallback when vision model is unavailable."""
        try:
            close = df["Close"] if "Close" in df.columns else df["close"]
            recent = close.iloc[-5:]
            older = close.iloc[-20:-5] if len(close) >= 20 else close.iloc[:5]

            recent_avg = recent.mean()
            older_avg = older.mean()

            if recent_avg > older_avg * 1.02:
                trend = "uptrend"
                rec = "BUY"
                conf = 0.60
            elif recent_avg < older_avg * 0.98:
                trend = "downtrend"
                rec = "SELL"
                conf = 0.58
            else:
                trend = "sideways"
                rec = "HOLD"
                conf = 0.50

            return {
                "patterns": [],
                "formations": [],
                "trend": trend,
                "support_level": f"{close.min():.2f}",
                "resistance_level": f"{close.max():.2f}",
                "volume_pattern": "stable",
                "recommendation": rec,
                "confidence": conf,
                "reasoning": f"Numerical fallback: {symbol} {trend}",
                "source": "numerical-fallback",
                "model": "none",
            }
        except Exception:
            return {
                "patterns": [],
                "formations": [],
                "trend": "unknown",
                "support_level": "N/A",
                "resistance_level": "N/A",
                "volume_pattern": "unknown",
                "recommendation": "HOLD",
                "confidence": 0.40,
                "reasoning": f"Unable to analyze {symbol}",
                "source": "error-fallback",
                "model": "none",
            }

    # ------------------------------------------------------------------
    # Convenience: fetch data and analyze in one call
    # ------------------------------------------------------------------

    async def analyze_symbol(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
    ) -> Dict[str, Any]:
        """
        Fetch price data for a symbol and run visual chart analysis.

        Uses yfinance to download OHLCV data, then renders and analyzes.
        """
        try:
            import yfinance as yf

            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                return {
                    "patterns": [],
                    "trend": "unknown",
                    "recommendation": "HOLD",
                    "confidence": 0.0,
                    "reasoning": f"No data available for {symbol}",
                    "source": "no-data",
                    "model": "none",
                }

            # Build indicator overlays if we have enough data
            indicators = {}
            if len(df) >= 20:
                indicators["SMA-20"] = df["Close"].rolling(20).mean()
            if len(df) >= 50:
                indicators["SMA-50"] = df["Close"].rolling(50).mean()

            return await self.analyze_chart(symbol, df, indicators)

        except Exception as e:
            logger.error(f"analyze_symbol failed for {symbol}: {e}")
            return {
                "patterns": [],
                "trend": "unknown",
                "recommendation": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Failed to fetch data for {symbol}: {e}",
                "source": "error",
                "model": "none",
            }


# ==================================================================
# Singleton access
# ==================================================================

_chart_analyzer: Optional[ChartVisionAnalyzer] = None


async def get_chart_vision_analyzer() -> ChartVisionAnalyzer:
    """Get or create the global chart vision analyzer instance."""
    global _chart_analyzer
    if _chart_analyzer is None:
        _chart_analyzer = ChartVisionAnalyzer()
        await _chart_analyzer.initialize()
    return _chart_analyzer


async def cleanup_chart_vision_analyzer():
    """Clean up the global analyzer instance."""
    global _chart_analyzer
    if _chart_analyzer:
        await _chart_analyzer.close()
        _chart_analyzer = None
