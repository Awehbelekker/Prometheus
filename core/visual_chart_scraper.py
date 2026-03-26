"""
Visual Chart Scraper for PROMETHEUS
Scrapes financial charts from various sources and uses Visual AI to learn patterns
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ScrapedChart:
    """A scraped financial chart"""
    chart_id: str
    symbol: str
    source: str  # 'tradingview', 'finviz', 'yahoo', 'stockcharts'
    url: str
    image_path: str
    timeframe: str
    scraped_at: datetime
    visual_analysis: Optional[Dict[str, Any]] = None

class VisualChartScraper:
    """
    Scrapes financial charts from various sources
    Feeds them to Visual AI (LLaVA) for pattern learning
    """
    
    def __init__(self, visual_ai=None):
        self.visual_ai = visual_ai
        self.scraped_charts = []
        self.chart_dir = Path("scraped_charts")
        self.chart_dir.mkdir(exist_ok=True)
        
        # Chart sources
        self.sources = {
            'finviz': 'https://finviz.com/chart.ashx?t={symbol}&ty=c&ta=1&p=d',
            'tradingview': 'https://www.tradingview.com/x/{hash}/',
            'stockcharts': 'https://stockcharts.com/c-sc/sc?s={symbol}&p=D&b=5&g=0&i=0'
        }
        
        logger.info("[VISUAL SCRAPER] Visual Chart Scraper initialized")
    
    async def scrape_chart(
        self,
        symbol: str,
        source: str = 'finviz',
        timeframe: str = 'daily'
    ) -> Optional[ScrapedChart]:
        """
        Scrape a chart for a given symbol
        """
        try:
            # Generate chart URL
            if source == 'finviz':
                url = self.sources['finviz'].format(symbol=symbol)
            elif source == 'stockcharts':
                url = self.sources['stockcharts'].format(symbol=symbol)
            else:
                logger.warning(f"[VISUAL SCRAPER] Unknown source: {source}")
                return None
            
            # Download chart image
            chart_id = hashlib.md5(f"{symbol}_{source}_{datetime.now()}".encode()).hexdigest()[:12]
            image_path = self.chart_dir / f"{symbol}_{chart_id}.png"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        with open(image_path, 'wb') as f:
                            f.write(await response.read())
                        
                        logger.info(f"[VISUAL SCRAPER] Downloaded chart for {symbol} from {source}")
                    else:
                        logger.warning(f"[VISUAL SCRAPER] Failed to download chart for {symbol}: {response.status}")
                        return None
            
            # Create scraped chart record
            chart = ScrapedChart(
                chart_id=chart_id,
                symbol=symbol,
                source=source,
                url=url,
                image_path=str(image_path),
                timeframe=timeframe,
                scraped_at=datetime.now()
            )
            
            # Analyze with Visual AI if available
            if self.visual_ai:
                analysis = await self._analyze_chart_with_visual_ai(chart)
                chart.visual_analysis = analysis
            
            self.scraped_charts.append(chart)
            return chart
            
        except Exception as e:
            logger.error(f"[VISUAL SCRAPER] Error scraping chart for {symbol}: {e}")
            return None
    
    async def _analyze_chart_with_visual_ai(self, chart: ScrapedChart) -> Dict[str, Any]:
        """
        Analyze scraped chart with Visual AI (LLaVA)
        """
        try:
            if not self.visual_ai:
                return {'error': 'Visual AI not available'}
            
            # Prepare context
            context = {
                'symbol': chart.symbol,
                'timeframe': chart.timeframe,
                'source': chart.source,
                'purpose': 'learning_from_scraped_data'
            }
            
            # Analyze with LLaVA
            analysis = await self.visual_ai.analyze_chart(
                chart_path=chart.image_path,
                context=context
            )
            
            logger.info(
                f"[VISUAL SCRAPER] Analyzed {chart.symbol} chart: "
                f"Patterns: {len(analysis.get('patterns', []))}, "
                f"Confidence: {analysis.get('confidence', 0):.2f}"
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"[VISUAL SCRAPER] Error analyzing chart: {e}")
            return {'error': str(e)}
    
    async def scrape_multiple_charts(
        self,
        symbols: List[str],
        source: str = 'finviz'
    ) -> List[ScrapedChart]:
        """
        Scrape charts for multiple symbols
        """
        tasks = [self.scrape_chart(symbol, source) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        charts = [r for r in results if isinstance(r, ScrapedChart)]
        
        logger.info(
            f"[VISUAL SCRAPER] Scraped {len(charts)}/{len(symbols)} charts successfully"
        )
        
        return charts
    
    async def scrape_and_learn_batch(
        self,
        symbols: List[str],
        batch_size: int = 10
    ):
        """
        Scrape charts in batches and learn from them
        """
        logger.info(f"[VISUAL SCRAPER] Starting batch scraping for {len(symbols)} symbols")
        
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            charts = await self.scrape_multiple_charts(batch)
            
            # Learn from this batch
            await self._learn_from_charts(charts)
            
            # Rate limiting
            await asyncio.sleep(2)
        
        logger.info(f"[VISUAL SCRAPER] Batch scraping complete: {len(self.scraped_charts)} total charts")
    
    async def _learn_from_charts(self, charts: List[ScrapedChart]):
        """
        Learn patterns from scraped charts
        """
        for chart in charts:
            if not chart.visual_analysis:
                continue
            
            analysis = chart.visual_analysis
            
            # Extract learnings
            patterns = analysis.get('patterns', [])
            support_levels = analysis.get('support_levels', [])
            resistance_levels = analysis.get('resistance_levels', [])
            trend = analysis.get('trend', 'unknown')
            
            # Log learnings
            if patterns:
                logger.info(
                    f"[VISUAL LEARNING] {chart.symbol}: "
                    f"Detected {len(patterns)} patterns, "
                    f"Trend: {trend}, "
                    f"S/R levels: {len(support_levels)}/{len(resistance_levels)}"
                )
            
            # Store patterns for future reference
            # (This would integrate with the continuous learning engine)
    
    def get_scraping_stats(self) -> Dict[str, Any]:
        """Get statistics about scraped charts"""
        if not self.scraped_charts:
            return {
                'total_charts': 0,
                'message': 'No charts scraped yet'
            }
        
        analyzed = sum(1 for c in self.scraped_charts if c.visual_analysis)
        
        return {
            'total_charts': len(self.scraped_charts),
            'analyzed_charts': analyzed,
            'sources': list(set(c.source for c in self.scraped_charts)),
            'symbols': list(set(c.symbol for c in self.scraped_charts)),
            'latest_scrape': max(c.scraped_at for c in self.scraped_charts)
        }


# Global instance
_visual_chart_scraper = None

def get_visual_chart_scraper(visual_ai=None) -> VisualChartScraper:
    """Get global visual chart scraper instance"""
    global _visual_chart_scraper
    if _visual_chart_scraper is None:
        _visual_chart_scraper = VisualChartScraper(visual_ai)
    return _visual_chart_scraper
