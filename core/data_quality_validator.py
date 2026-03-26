"""
Data Quality Validator
Validates all incoming data and auto-disables junk sources

Features:
- Score data sources on reliability
- Auto-disable sources producing junk
- Log quality metrics for monitoring
- Track data freshness and accuracy
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Quality metrics for a data source"""
    source_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    empty_responses: int = 0
    stale_data_count: int = 0
    invalid_data_count: int = 0
    average_latency_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    quality_score: float = 1.0  # 0 to 1
    is_enabled: bool = True
    consecutive_failures: int = 0
    response_times: List[float] = field(default_factory=list)


class DataQualityValidator:
    """Validates and scores data quality from all sources"""
    
    # Known junk/fake sources to ALWAYS disable
    KNOWN_JUNK_SOURCES = [
        "FederalReserveAPI",  # Fake - generates random numbers
        "BloombergNewsAPI",  # Fake - generates fake headlines
        "OpenWeatherMapAPI",  # Not relevant to trading
        "FakeNewsGenerator",
        "RandomDataSource",
        "MockMarketData",
    ]
    
    # Minimum quality thresholds
    MIN_QUALITY_SCORE = 0.5
    MAX_CONSECUTIVE_FAILURES = 5
    MAX_STALE_DATA_PERCENT = 0.3
    MAX_EMPTY_RESPONSE_PERCENT = 0.2
    
    # Auto-disable thresholds
    AUTO_DISABLE_QUALITY = 0.3
    AUTO_DISABLE_FAILURES = 10
    
    def __init__(self, config_path: str = "data_quality_config.json"):
        self.config_path = Path(config_path)
        self.metrics: Dict[str, DataQualityMetrics] = {}
        self.disabled_sources: set = set()
        self.validation_rules: Dict[str, Callable] = {}
        
        # Load existing config
        self._load_config()
        
        # Disable known junk sources
        for source in self.KNOWN_JUNK_SOURCES:
            self.disabled_sources.add(source)
            logger.warning(f"⛔ Auto-disabled known junk source: {source}")
        
        logger.info(f"✅ Data Quality Validator initialized")
        logger.info(f"   📊 Tracking {len(self.metrics)} sources")
        logger.info(f"   ⛔ {len(self.disabled_sources)} sources disabled")
    
    def _load_config(self):
        """Load saved configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    data = json.load(f)
                    self.disabled_sources = set(data.get("disabled_sources", []))
                    logger.info(f"📂 Loaded config: {len(self.disabled_sources)} disabled sources")
        except Exception as e:
            logger.warning(f"⚠️ Could not load config: {e}")
    
    def _save_config(self):
        """Save configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump({
                    "disabled_sources": list(self.disabled_sources),
                    "last_updated": datetime.now().isoformat(),
                    "metrics": {
                        name: {
                            "quality_score": m.quality_score,
                            "total_requests": m.total_requests,
                            "is_enabled": m.is_enabled
                        }
                        for name, m in self.metrics.items()
                    }
                }, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️ Could not save config: {e}")
    
    def get_metrics(self, source_name: str) -> DataQualityMetrics:
        """Get or create metrics for a source"""
        if source_name not in self.metrics:
            self.metrics[source_name] = DataQualityMetrics(source_name=source_name)
        return self.metrics[source_name]
    
    def is_source_enabled(self, source_name: str) -> bool:
        """Check if a source is enabled"""
        if source_name in self.disabled_sources:
            return False
        
        metrics = self.get_metrics(source_name)
        return metrics.is_enabled
    
    def record_success(self, source_name: str, latency_ms: float, data_age_seconds: float = 0):
        """Record a successful data fetch"""
        metrics = self.get_metrics(source_name)
        
        metrics.total_requests += 1
        metrics.successful_requests += 1
        metrics.consecutive_failures = 0
        metrics.last_success = datetime.now()
        
        # Track latency
        metrics.response_times.append(latency_ms)
        if len(metrics.response_times) > 100:
            metrics.response_times = metrics.response_times[-100:]
        metrics.average_latency_ms = statistics.mean(metrics.response_times)
        
        # Check for stale data
        if data_age_seconds > 300:  # Older than 5 minutes
            metrics.stale_data_count += 1
        
        # Update quality score
        self._update_quality_score(metrics)
    
    def record_failure(self, source_name: str, error: str = ""):
        """Record a failed data fetch"""
        metrics = self.get_metrics(source_name)
        
        metrics.total_requests += 1
        metrics.failed_requests += 1
        metrics.consecutive_failures += 1
        metrics.last_failure = datetime.now()
        
        # Update quality score
        self._update_quality_score(metrics)
        
        # Check for auto-disable
        if metrics.consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self._disable_source(source_name, f"Too many consecutive failures: {metrics.consecutive_failures}")
        
        logger.warning(f"⚠️ {source_name} failure #{metrics.consecutive_failures}: {error}")
    
    def record_empty_response(self, source_name: str):
        """Record an empty response"""
        metrics = self.get_metrics(source_name)
        
        metrics.total_requests += 1
        metrics.empty_responses += 1
        
        self._update_quality_score(metrics)
    
    def record_invalid_data(self, source_name: str, reason: str = ""):
        """Record invalid/garbage data"""
        metrics = self.get_metrics(source_name)
        
        metrics.total_requests += 1
        metrics.invalid_data_count += 1
        
        self._update_quality_score(metrics)
        
        logger.warning(f"⚠️ Invalid data from {source_name}: {reason}")
    
    def _update_quality_score(self, metrics: DataQualityMetrics):
        """Calculate quality score based on metrics"""
        if metrics.total_requests == 0:
            metrics.quality_score = 1.0
            return
        
        # Success rate (40% weight)
        success_rate = metrics.successful_requests / metrics.total_requests
        
        # Freshness rate (20% weight)
        stale_rate = metrics.stale_data_count / max(metrics.successful_requests, 1)
        freshness_score = 1.0 - min(stale_rate, 1.0)
        
        # Empty response penalty (20% weight)
        empty_rate = metrics.empty_responses / metrics.total_requests
        empty_score = 1.0 - min(empty_rate * 2, 1.0)
        
        # Invalid data penalty (20% weight)
        invalid_rate = metrics.invalid_data_count / metrics.total_requests
        valid_score = 1.0 - min(invalid_rate * 2, 1.0)
        
        # Combined score
        metrics.quality_score = (
            success_rate * 0.4 +
            freshness_score * 0.2 +
            empty_score * 0.2 +
            valid_score * 0.2
        )
        
        # Check for auto-disable
        if metrics.quality_score < self.AUTO_DISABLE_QUALITY and metrics.total_requests >= 10:
            self._disable_source(metrics.source_name, f"Quality score too low: {metrics.quality_score:.2f}")
    
    def _disable_source(self, source_name: str, reason: str):
        """Disable a data source"""
        if source_name in self.disabled_sources:
            return
        
        self.disabled_sources.add(source_name)
        
        if source_name in self.metrics:
            self.metrics[source_name].is_enabled = False
        
        logger.warning(f"⛔ AUTO-DISABLED source '{source_name}': {reason}")
        self._save_config()
    
    def enable_source(self, source_name: str):
        """Re-enable a data source"""
        self.disabled_sources.discard(source_name)
        
        if source_name in self.metrics:
            self.metrics[source_name].is_enabled = True
            self.metrics[source_name].consecutive_failures = 0
        
        logger.info(f"✅ Re-enabled source: {source_name}")
        self._save_config()
    
    def validate_data(self, source_name: str, data: Any) -> Dict[str, Any]:
        """Validate incoming data and return quality report"""
        result = {
            "source": source_name,
            "is_valid": True,
            "quality_score": 1.0,
            "issues": [],
            "data_count": 0
        }
        
        # Check if source is disabled
        if not self.is_source_enabled(source_name):
            result["is_valid"] = False
            result["quality_score"] = 0.0
            result["issues"].append("Source is disabled")
            return result
        
        # Check for None/empty
        if data is None:
            self.record_empty_response(source_name)
            result["is_valid"] = False
            result["quality_score"] = 0.0
            result["issues"].append("Empty response")
            return result
        
        # Check for empty collections
        if isinstance(data, (list, dict)) and len(data) == 0:
            self.record_empty_response(source_name)
            result["is_valid"] = False
            result["quality_score"] = 0.0
            result["issues"].append("Empty collection")
            return result
        
        # Count data points
        if isinstance(data, list):
            result["data_count"] = len(data)
        elif isinstance(data, dict):
            result["data_count"] = len(data.keys())
        
        # Run custom validation rules
        if source_name in self.validation_rules:
            try:
                rule_result = self.validation_rules[source_name](data)
                if not rule_result.get("is_valid", True):
                    result["is_valid"] = False
                    result["issues"].extend(rule_result.get("issues", []))
            except Exception as e:
                result["issues"].append(f"Validation error: {e}")
        
        # Update metrics and get quality score
        metrics = self.get_metrics(source_name)
        result["quality_score"] = metrics.quality_score
        
        return result
    
    def add_validation_rule(self, source_name: str, rule: Callable):
        """Add custom validation rule for a source"""
        self.validation_rules[source_name] = rule
    
    def get_quality_report(self) -> Dict[str, Any]:
        """Get overall data quality report"""
        if not self.metrics:
            return {
                "overall_score": 0.0,
                "total_sources": 0,
                "enabled_sources": 0,
                "disabled_sources": len(self.disabled_sources),
                "sources": {}
            }
        
        enabled_metrics = [m for m in self.metrics.values() if m.is_enabled]
        
        if enabled_metrics:
            overall_score = statistics.mean(m.quality_score for m in enabled_metrics)
        else:
            overall_score = 0.0
        
        return {
            "overall_score": overall_score,
            "total_sources": len(self.metrics),
            "enabled_sources": len(enabled_metrics),
            "disabled_sources": len(self.disabled_sources),
            "disabled_list": list(self.disabled_sources),
            "sources": {
                name: {
                    "quality_score": m.quality_score,
                    "success_rate": m.successful_requests / max(m.total_requests, 1),
                    "is_enabled": m.is_enabled,
                    "total_requests": m.total_requests,
                    "average_latency_ms": m.average_latency_ms
                }
                for name, m in self.metrics.items()
            }
        }
    
    def get_quality_score(self) -> float:
        """Get simple overall quality score"""
        report = self.get_quality_report()
        return report["overall_score"]
    
    def print_report(self):
        """Print quality report"""
        report = self.get_quality_report()
        
        print("\n" + "=" * 60)
        print("📊 DATA QUALITY REPORT")
        print("=" * 60)
        print(f"\n🎯 Overall Quality Score: {report['overall_score']:.2f}/1.00")
        print(f"   ✅ Enabled Sources: {report['enabled_sources']}")
        print(f"   ⛔ Disabled Sources: {report['disabled_sources']}")
        
        if report["disabled_list"]:
            print(f"\n⛔ DISABLED SOURCES (producing junk):")
            for source in report["disabled_list"]:
                print(f"   - {source}")
        
        print(f"\n📈 SOURCE DETAILS:")
        for name, metrics in sorted(report["sources"].items(), 
                                     key=lambda x: x[1]["quality_score"], 
                                     reverse=True):
            status = "✅" if metrics["is_enabled"] else "⛔"
            print(f"   {status} {name}")
            print(f"      Quality: {metrics['quality_score']:.2f} | "
                  f"Success: {metrics['success_rate']:.1%} | "
                  f"Requests: {metrics['total_requests']}")
        
        print("\n" + "=" * 60)


# Global instance
data_quality_validator = DataQualityValidator()


def is_source_enabled(source_name: str) -> bool:
    """Check if source is enabled"""
    return data_quality_validator.is_source_enabled(source_name)


def record_success(source_name: str, latency_ms: float = 0, data_age_seconds: float = 0):
    """Record successful fetch"""
    data_quality_validator.record_success(source_name, latency_ms, data_age_seconds)


def record_failure(source_name: str, error: str = ""):
    """Record failed fetch"""
    data_quality_validator.record_failure(source_name, error)


def validate_data(source_name: str, data: Any) -> Dict[str, Any]:
    """Validate data from source"""
    return data_quality_validator.validate_data(source_name, data)


def get_quality_score() -> float:
    """Get overall quality score"""
    return data_quality_validator.get_quality_score()


def get_quality_report() -> Dict[str, Any]:
    """Get full quality report"""
    return data_quality_validator.get_quality_report()


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Data Quality Validator")
    print("=" * 60)
    
    validator = DataQualityValidator()
    
    # Simulate some data sources
    print("\n📡 Simulating data source activity...")
    
    # Good source
    for i in range(10):
        validator.record_success("FRED_API", latency_ms=150, data_age_seconds=60)
    print("   ✅ FRED_API: 10 successful requests")
    
    # Medium source
    for i in range(7):
        validator.record_success("SEC_EDGAR", latency_ms=300, data_age_seconds=120)
    for i in range(3):
        validator.record_failure("SEC_EDGAR", "Rate limited")
    print("   ⚠️ SEC_EDGAR: 7 success, 3 failures")
    
    # Bad source (should auto-disable)
    for i in range(10):
        validator.record_failure("FakeNewsGenerator", "Returns garbage")
    print("   ❌ FakeNewsGenerator: 10 failures")
    
    # Check known junk sources are disabled
    print("\n⛔ Checking known junk sources:")
    for source in validator.KNOWN_JUNK_SOURCES[:3]:
        enabled = validator.is_source_enabled(source)
        print(f"   {source}: {'❌ Enabled (BAD!)' if enabled else '✅ Disabled'}")
    
    # Print report
    validator.print_report()
    
    print("\n✅ Data Quality Validator Test Complete!")
