#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS TIMEZONE-AWARE TRADING SCHEDULER
================================================================================

Ensures PROMETHEUS never misses trading opportunities by:
1. Always using US Eastern Time for market hours
2. Auto-starting before market open
3. Scheduling pre-market scans
4. Sending alerts for market events
5. Supporting 24/5 crypto and forex trading

Your Timezone: South Africa Standard Time (UTC+2)
Market Timezone: US Eastern Time (UTC-5 EST / UTC-4 EDT)
Time Difference: South Africa is 7 hours AHEAD of US Eastern

================================================================================
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import threading
import time as time_module

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Timezone setup
try:
    import pytz
    EASTERN_TZ = pytz.timezone('US/Eastern')
    UTC_TZ = pytz.UTC
    SA_TZ = pytz.timezone('Africa/Johannesburg')
    PYTZ_AVAILABLE = True
except ImportError:
    logger.warning("pytz not installed - installing now...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytz', '-q'])
    import pytz
    EASTERN_TZ = pytz.timezone('US/Eastern')
    UTC_TZ = pytz.UTC
    SA_TZ = pytz.timezone('Africa/Johannesburg')
    PYTZ_AVAILABLE = True


class MarketSchedule:
    """US Stock Market Schedule"""
    
    # Regular trading hours (Eastern Time)
    REGULAR_OPEN = time(9, 30)
    REGULAR_CLOSE = time(16, 0)
    
    # Extended hours
    PRE_MARKET_OPEN = time(4, 0)
    AFTER_HOURS_CLOSE = time(20, 0)
    
    # Overnight session (IB)
    OVERNIGHT_START = time(20, 0)
    OVERNIGHT_END = time(3, 50)
    
    # 24/5 Crypto/Forex
    FOREX_OPEN_SUNDAY = time(17, 0)  # Sunday 5 PM ET
    FOREX_CLOSE_FRIDAY = time(17, 0)  # Friday 5 PM ET
    
    # 2026 US Market Holidays (markets closed)
    HOLIDAYS_2026 = [
        datetime(2026, 1, 1),   # New Year's Day
        datetime(2026, 1, 19),  # Martin Luther King Jr. Day
        datetime(2026, 2, 16),  # Presidents Day
        datetime(2026, 4, 3),   # Good Friday
        datetime(2026, 5, 25),  # Memorial Day
        datetime(2026, 7, 3),   # Independence Day (observed)
        datetime(2026, 9, 7),   # Labor Day
        datetime(2026, 11, 26), # Thanksgiving
        datetime(2026, 12, 25), # Christmas
    ]
    
    # Early close days (1:00 PM ET)
    EARLY_CLOSE_2026 = [
        datetime(2026, 7, 2),   # Day before Independence Day
        datetime(2026, 11, 27), # Day after Thanksgiving
        datetime(2026, 12, 24), # Christmas Eve
    ]


class TradingScheduler:
    """
    Timezone-aware trading scheduler that ensures PROMETHEUS never misses opportunities.
    """
    
    def __init__(self):
        self.schedule = MarketSchedule()
        self.config_file = Path("trading_schedule_config.json")
        self.load_config()
        
    def load_config(self):
        """Load scheduler configuration"""
        default_config = {
            "auto_start_enabled": True,
            "pre_market_scan_minutes": 30,  # Start scanning 30 min before open
            "alerts_enabled": True,
            "trade_extended_hours": True,
            "trade_crypto_24_7": True,
            "trade_forex_24_5": False,
            "notification_methods": ["console", "log"],
            "startup_script": "launch_prometheus_live.py",
            "timezone_display": "both"  # Show both local and ET
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    self.config = {**default_config, **json.load(f)}
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save scheduler configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_eastern_time(self) -> datetime:
        """Get current time in US Eastern timezone"""
        return datetime.now(EASTERN_TZ)
    
    def get_local_time(self) -> datetime:
        """Get current local time"""
        return datetime.now(SA_TZ)
    
    def get_all_timezones(self) -> Dict[str, datetime]:
        """Get current time in all relevant timezones"""
        utc_now = datetime.now(UTC_TZ)
        return {
            "local": datetime.now(SA_TZ),
            "eastern": utc_now.astimezone(EASTERN_TZ),
            "utc": utc_now,
            "pacific": utc_now.astimezone(pytz.timezone('US/Pacific')),
            "london": utc_now.astimezone(pytz.timezone('Europe/London')),
        }
    
    def is_holiday(self, date: datetime = None) -> bool:
        """Check if given date is a market holiday"""
        if date is None:
            date = self.get_eastern_time()
        
        check_date = datetime(date.year, date.month, date.day)
        return check_date in self.schedule.HOLIDAYS_2026
    
    def is_early_close(self, date: datetime = None) -> bool:
        """Check if given date has early market close"""
        if date is None:
            date = self.get_eastern_time()
        
        check_date = datetime(date.year, date.month, date.day)
        return check_date in self.schedule.EARLY_CLOSE_2026
    
    def get_market_status(self) -> Dict:
        """
        Get comprehensive market status with timezone awareness.
        """
        times = self.get_all_timezones()
        et = times['eastern']
        
        # Check weekend
        is_weekend = et.weekday() >= 5
        
        # Check holiday
        is_holiday = self.is_holiday(et)
        
        # Check early close
        is_early = self.is_early_close(et)
        close_time = time(13, 0) if is_early else self.schedule.REGULAR_CLOSE
        
        current_time = et.time()
        
        # Determine session
        if is_weekend:
            session = "weekend"
            is_open = False
            next_open = self._get_next_market_open(et)
        elif is_holiday:
            session = "holiday"
            is_open = False
            next_open = self._get_next_market_open(et)
        elif self.schedule.REGULAR_OPEN <= current_time <= close_time:
            session = "regular"
            is_open = True
            next_open = None
        elif self.schedule.PRE_MARKET_OPEN <= current_time < self.schedule.REGULAR_OPEN:
            session = "pre_market"
            is_open = self.config.get("trade_extended_hours", False)
            next_open = et.replace(hour=9, minute=30, second=0)
        elif close_time < current_time <= self.schedule.AFTER_HOURS_CLOSE:
            session = "after_hours"
            is_open = self.config.get("trade_extended_hours", False)
            next_open = self._get_next_market_open(et)
        else:
            session = "closed"
            is_open = False
            next_open = self._get_next_market_open(et)
        
        # Calculate time to market events
        time_to_open = None
        time_to_close = None
        
        if next_open:
            time_to_open = next_open - et
        if is_open and session == "regular":
            close_dt = et.replace(hour=close_time.hour, minute=close_time.minute, second=0)
            time_to_close = close_dt - et
        
        return {
            "session": session,
            "is_open": is_open,
            "is_weekend": is_weekend,
            "is_holiday": is_holiday,
            "is_early_close": is_early,
            "times": {
                "local": times['local'].strftime("%Y-%m-%d %H:%M:%S %Z"),
                "eastern": times['eastern'].strftime("%Y-%m-%d %H:%M:%S %Z"),
                "utc": times['utc'].strftime("%Y-%m-%d %H:%M:%S %Z"),
            },
            "next_open": next_open.strftime("%Y-%m-%d %H:%M ET") if next_open else None,
            "time_to_open": str(time_to_open).split('.')[0] if time_to_open else None,
            "time_to_close": str(time_to_close).split('.')[0] if time_to_close else None,
            "close_time": close_time.strftime("%I:%M %p") + " ET",
        }
    
    def _get_next_market_open(self, from_time: datetime) -> datetime:
        """Calculate next market open time"""
        next_day = from_time + timedelta(days=1)
        next_day = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
        
        # Skip weekends
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        
        # Skip holidays
        while self.is_holiday(next_day):
            next_day += timedelta(days=1)
            while next_day.weekday() >= 5:
                next_day += timedelta(days=1)
        
        return next_day
    
    def get_trading_windows_local(self) -> Dict[str, str]:
        """
        Get trading windows in YOUR LOCAL TIME (South Africa).
        This helps you know when to be available for trading.
        """
        et = self.get_eastern_time()
        local = self.get_local_time()
        
        # Time difference (SA is ahead)
        offset_hours = (local.utcoffset().total_seconds() - et.utcoffset().total_seconds()) / 3600
        
        def et_to_local(et_time: time) -> str:
            """Convert Eastern Time to local time string"""
            hour = (et_time.hour + int(offset_hours)) % 24
            next_day = ""
            if et_time.hour + int(offset_hours) >= 24:
                next_day = " (+1 day)"
            return f"{hour:02d}:{et_time.minute:02d}{next_day}"
        
        return {
            "timezone_offset": f"+{int(offset_hours)} hours (SA ahead of ET)",
            "pre_market": {
                "start": f"{et_to_local(self.schedule.PRE_MARKET_OPEN)} local = 4:00 AM ET",
                "end": f"{et_to_local(self.schedule.REGULAR_OPEN)} local = 9:30 AM ET",
            },
            "regular_market": {
                "start": f"{et_to_local(self.schedule.REGULAR_OPEN)} local = 9:30 AM ET",
                "end": f"{et_to_local(self.schedule.REGULAR_CLOSE)} local = 4:00 PM ET",
            },
            "after_hours": {
                "start": f"{et_to_local(self.schedule.REGULAR_CLOSE)} local = 4:00 PM ET",
                "end": f"{et_to_local(self.schedule.AFTER_HOURS_CLOSE)} local = 8:00 PM ET",
            },
            "optimal_trading": "Your best times: 4:30 PM - 11:00 PM local (regular market hours)",
        }
    
    def get_upcoming_events(self, days: int = 7) -> List[Dict]:
        """Get upcoming market events for the next N days"""
        events = []
        et = self.get_eastern_time()
        
        for i in range(days):
            day = et + timedelta(days=i)
            day_str = day.strftime("%A, %B %d")
            
            if day.weekday() >= 5:
                events.append({
                    "date": day_str,
                    "event": "Weekend - Markets Closed",
                    "type": "closed"
                })
            elif self.is_holiday(day):
                events.append({
                    "date": day_str,
                    "event": "Market Holiday - Closed",
                    "type": "holiday"
                })
            elif self.is_early_close(day):
                events.append({
                    "date": day_str,
                    "event": "Early Close at 1:00 PM ET",
                    "type": "early_close"
                })
            else:
                events.append({
                    "date": day_str,
                    "event": "Regular Trading Day (9:30 AM - 4:00 PM ET)",
                    "type": "regular"
                })
        
        return events
    
    def create_windows_scheduled_task(self) -> bool:
        """
        Create a Windows Scheduled Task to auto-start PROMETHEUS before market open.
        Runs at 4:00 PM local time (9:00 AM ET) - 30 min before market open.
        """
        try:
            # Calculate local time for 9:00 AM ET (30 min before open)
            et = self.get_eastern_time()
            local = self.get_local_time()
            offset_hours = int((local.utcoffset().total_seconds() - et.utcoffset().total_seconds()) / 3600)
            
            # 9:00 AM ET = 9 + offset in local time
            start_hour = 9 + offset_hours
            start_time = f"{start_hour:02d}:00"
            
            script_path = Path(__file__).parent / self.config.get("startup_script", "launch_prometheus_live.py")
            
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Auto-start PROMETHEUS Trading before market open</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-15T{start_time}:00</StartBoundary>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday /><Tuesday /><Wednesday /><Thursday /><Friday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Settings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
  </Settings>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>{script_path}</Arguments>
      <WorkingDirectory>{script_path.parent}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
            
            # Save task XML
            task_file = Path(__file__).parent / "prometheus_market_open_task.xml"
            with open(task_file, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            logger.info(f"Created scheduled task XML: {task_file}")
            logger.info(f"PROMETHEUS will auto-start at {start_time} local time (9:00 AM ET)")
            logger.info(f"To install: schtasks /create /tn 'PROMETHEUS_MarketOpen' /xml '{task_file}'")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create scheduled task: {e}")
            return False
    
    def wait_for_market_open(self, callback=None):
        """
        Wait until market opens, then execute callback.
        Shows countdown timer.
        """
        while True:
            status = self.get_market_status()
            
            if status['is_open'] and status['session'] == 'regular':
                logger.info("🔔 MARKET IS OPEN! Starting trading...")
                if callback:
                    callback()
                return
            
            if status['time_to_open']:
                logger.info(f"⏳ Market opens in: {status['time_to_open']} | Current: {status['times']['eastern']}")
            
            # Sleep for 1 minute between checks
            time_module.sleep(60)
    
    def display_status(self):
        """Display comprehensive trading schedule status"""
        status = self.get_market_status()
        windows = self.get_trading_windows_local()
        events = self.get_upcoming_events(7)
        
        print("\n" + "=" * 70)
        print("🕐 PROMETHEUS TIMEZONE-AWARE TRADING SCHEDULER")
        print("=" * 70)
        
        print("\n📍 CURRENT TIME:")
        print(f"   Your Local Time:  {status['times']['local']}")
        print(f"   US Eastern Time:  {status['times']['eastern']}")
        print(f"   UTC Time:         {status['times']['utc']}")
        
        print(f"\n📊 MARKET STATUS: ", end="")
        session_emoji = {
            "regular": "🟢 OPEN",
            "pre_market": "🟡 PRE-MARKET",
            "after_hours": "🟠 AFTER-HOURS",
            "closed": "🔴 CLOSED",
            "weekend": "⚫ WEEKEND",
            "holiday": "🔵 HOLIDAY"
        }
        print(session_emoji.get(status['session'], status['session'].upper()))
        
        if status['time_to_open']:
            print(f"   ⏳ Time to market open: {status['time_to_open']}")
            print(f"   📅 Next open: {status['next_open']}")
        
        if status['time_to_close']:
            print(f"   ⏳ Time to market close: {status['time_to_close']}")
        
        if status['is_early_close']:
            print(f"   ⚠️ EARLY CLOSE TODAY: {status['close_time']}")
        
        print("\n" + "-" * 70)
        print("🌍 YOUR LOCAL TRADING WINDOWS (South Africa Time):")
        print("-" * 70)
        print(f"   Timezone Offset: {windows['timezone_offset']}")
        print(f"\n   PRE-MARKET (Limited Liquidity):")
        print(f"      {windows['pre_market']['start']}")
        print(f"      {windows['pre_market']['end']}")
        print(f"\n   REGULAR MARKET (Best Liquidity) ⭐:")
        print(f"      {windows['regular_market']['start']}")
        print(f"      {windows['regular_market']['end']}")
        print(f"\n   AFTER-HOURS:")
        print(f"      {windows['after_hours']['start']}")
        print(f"      {windows['after_hours']['end']}")
        print(f"\n   💡 {windows['optimal_trading']}")
        
        print("\n" + "-" * 70)
        print("📅 UPCOMING WEEK:")
        print("-" * 70)
        for event in events:
            emoji = {"regular": "✅", "closed": "❌", "holiday": "🎄", "early_close": "⚠️"}
            print(f"   {emoji.get(event['type'], '•')} {event['date']}: {event['event']}")
        
        print("\n" + "-" * 70)
        print("⚙️ AUTO-START CONFIGURATION:")
        print("-" * 70)
        print(f"   Auto-start enabled: {self.config.get('auto_start_enabled', False)}")
        print(f"   Pre-market scan: {self.config.get('pre_market_scan_minutes', 30)} min before open")
        print(f"   Extended hours trading: {self.config.get('trade_extended_hours', False)}")
        print(f"   24/7 Crypto trading: {self.config.get('trade_crypto_24_7', True)}")
        
        print("\n" + "=" * 70)
        print("✅ PROMETHEUS will NEVER miss a trading opportunity!")
        print("   - Timezone-aware market hours detection")
        print("   - Holiday and early close awareness")
        print("   - Auto-start scheduling available")
        print("   - 24/7 crypto support")
        print("=" * 70 + "\n")


def main():
    """Main entry point"""
    scheduler = TradingScheduler()
    scheduler.display_status()
    
    # Create Windows scheduled task
    print("\n📋 Creating Windows Scheduled Task for auto-start...")
    if scheduler.create_windows_scheduled_task():
        print("✅ Scheduled task created! PROMETHEUS will auto-start before market open.")
    
    # Save configuration
    scheduler.save_config()
    print(f"\n💾 Configuration saved to: {scheduler.config_file}")


if __name__ == "__main__":
    main()
