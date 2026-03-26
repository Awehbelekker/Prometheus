"""
🕐 MARKET HOURS UTILITIES - TIMEZONE-AWARE
Centralized market hours detection that works on ANY server timezone worldwide.

This module ensures PROMETHEUS always uses US Eastern Time for market hours,
regardless of what timezone the server is running in.

Author: PROMETHEUS Team
Date: 2025-10-13
"""

from datetime import datetime, time
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

# Try to import pytz for proper timezone handling
try:
    import pytz
    PYTZ_AVAILABLE = True
    EASTERN_TZ = pytz.timezone('US/Eastern')
except ImportError:
    PYTZ_AVAILABLE = False
    EASTERN_TZ = None
    logger.warning("[WARNING]️ pytz not available - using UTC offset approximation")

# Market hours in Eastern Time
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Extended hours
PRE_MARKET_OPEN_HOUR = 4
PRE_MARKET_OPEN_MINUTE = 0
AFTER_HOURS_CLOSE_HOUR = 20
AFTER_HOURS_CLOSE_MINUTE = 0

# Overnight trading hours (IB 24/5 support)
OVERNIGHT_START_HOUR = 20  # 8:00 PM
OVERNIGHT_START_MINUTE = 0
OVERNIGHT_END_HOUR = 3     # 3:50 AM (next day)
OVERNIGHT_END_MINUTE = 50


def get_eastern_time() -> datetime:
    """
    Get current time in US Eastern timezone.
    Works on ANY server timezone worldwide.
    
    Returns:
        datetime: Current time in US Eastern timezone
    """
    if PYTZ_AVAILABLE:
        # Proper timezone conversion using pytz
        utc_now = datetime.now(pytz.UTC)
        eastern_now = utc_now.astimezone(EASTERN_TZ)
        return eastern_now
    else:
        # Fallback: Use UTC with offset approximation
        # Eastern Time is UTC-5 (EST) or UTC-4 (EDT)
        # This is approximate and doesn't handle DST perfectly
        from datetime import timezone, timedelta
        utc_now = datetime.now(timezone.utc)
        
        # Simple DST check (March-November is EDT, otherwise EST)
        month = utc_now.month
        if 3 <= month <= 11:  # Approximate EDT period
            offset = timedelta(hours=-4)  # EDT = UTC-4
        else:
            offset = timedelta(hours=-5)  # EST = UTC-5
        
        eastern_now = utc_now + offset
        logger.debug(f"Using UTC offset approximation: {offset}")
        return eastern_now


def is_market_open(include_extended_hours: bool = False) -> bool:
    """
    Check if US stock market is currently open.
    Always uses US Eastern Time regardless of server timezone.
    
    Args:
        include_extended_hours: If True, includes pre-market (4:00 AM) and after-hours (until 8:00 PM)
    
    Returns:
        bool: True if market is open, False otherwise
    """
    try:
        # Get current time in Eastern timezone
        eastern_now = get_eastern_time()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        if eastern_now.weekday() >= 5:  # Saturday or Sunday
            logger.debug(f"[WEEKEND] Weekend in Eastern Time - markets closed (ET: {eastern_now.strftime('%A %I:%M %p')})")
            return False
        
        current_time = eastern_now.time()
        
        if include_extended_hours:
            # Extended hours: 4:00 AM - 8:00 PM ET
            session_start = time(PRE_MARKET_OPEN_HOUR, PRE_MARKET_OPEN_MINUTE)
            session_end = time(AFTER_HOURS_CLOSE_HOUR, AFTER_HOURS_CLOSE_MINUTE)
        else:
            # Regular hours: 9:30 AM - 4:00 PM ET
            session_start = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
            session_end = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
        
        is_open = session_start <= current_time <= session_end
        
        logger.debug(
            f"[MARKET] Market hours check: {'OPEN' if is_open else 'CLOSED'} "
            f"(ET: {eastern_now.strftime('%I:%M %p')}, "
            f"Extended: {include_extended_hours})"
        )
        
        return is_open
        
    except Exception as e:
        logger.error(f"[ERROR] Market hours check failed: {e}")
        return False  # Default to closed on error


def get_market_status() -> Dict[str, any]:
    """
    Get detailed market status information.
    
    Returns:
        Dict with market status details including:
        - is_open: bool
        - session: str ('regular', 'pre_market', 'after_hours', 'closed')
        - eastern_time: str
        - local_time: str
        - next_open: str
        - next_close: str
    """
    try:
        eastern_now = get_eastern_time()
        local_now = datetime.now()
        
        current_time = eastern_now.time()
        is_weekday = eastern_now.weekday() < 5
        
        # Determine session
        session = 'closed'
        is_open = False
        
        if is_weekday:
            market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
            market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
            pre_market_open = time(PRE_MARKET_OPEN_HOUR, PRE_MARKET_OPEN_MINUTE)
            after_hours_close = time(AFTER_HOURS_CLOSE_HOUR, AFTER_HOURS_CLOSE_MINUTE)
            
            if market_open <= current_time <= market_close:
                session = 'regular'
                is_open = True
            elif pre_market_open <= current_time < market_open:
                session = 'pre_market'
                is_open = False  # Pre-market not considered "open" for regular trading
            elif market_close < current_time <= after_hours_close:
                session = 'after_hours'
                is_open = False  # After-hours not considered "open" for regular trading
        
        # Calculate next open/close times
        if is_weekday:
            if current_time < time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE):
                next_open = f"Today at {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} AM ET"
            else:
                next_open = f"Tomorrow at {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} AM ET"
            
            if current_time < time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE):
                next_close = f"Today at {MARKET_CLOSE_HOUR}:00 PM ET"
            else:
                next_close = f"Tomorrow at {MARKET_CLOSE_HOUR}:00 PM ET"
        else:
            # Weekend
            days_until_monday = (7 - eastern_now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 1
            next_open = f"Monday at {MARKET_OPEN_HOUR}:{MARKET_OPEN_MINUTE:02d} AM ET"
            next_close = f"Monday at {MARKET_CLOSE_HOUR}:00 PM ET"
        
        return {
            'is_open': is_open,
            'session': session,
            'eastern_time': eastern_now.strftime('%I:%M:%S %p %Z'),
            'eastern_date': eastern_now.strftime('%A, %B %d, %Y'),
            'local_time': local_now.strftime('%I:%M:%S %p'),
            'local_timezone': local_now.astimezone().tzname() if hasattr(local_now, 'astimezone') else 'Unknown',
            'next_open': next_open,
            'next_close': next_close,
            'is_weekday': is_weekday,
            'weekday_name': eastern_now.strftime('%A')
        }
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get market status: {e}")
        return {
            'is_open': False,
            'session': 'error',
            'eastern_time': 'Unknown',
            'eastern_date': 'Unknown',
            'local_time': datetime.now().strftime('%I:%M:%S %p'),
            'local_timezone': 'Unknown',
            'next_open': 'Unknown',
            'next_close': 'Unknown',
            'is_weekday': False,
            'weekday_name': 'Unknown',
            'error': str(e)
        }


def get_time_until_market_open() -> Tuple[int, int, int]:
    """
    Calculate time remaining until market opens.
    
    Returns:
        Tuple[int, int, int]: (hours, minutes, seconds) until market open
    """
    try:
        eastern_now = get_eastern_time()
        
        # If weekend, calculate to Monday 9:30 AM
        if eastern_now.weekday() >= 5:
            days_until_monday = (7 - eastern_now.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 1
            
            next_open = eastern_now.replace(
                hour=MARKET_OPEN_HOUR,
                minute=MARKET_OPEN_MINUTE,
                second=0,
                microsecond=0
            )
            from datetime import timedelta
            next_open += timedelta(days=days_until_monday)
        else:
            # Weekday - check if before or after market hours
            market_open_time = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)
            current_time = eastern_now.time()
            
            if current_time < market_open_time:
                # Before market open today
                next_open = eastern_now.replace(
                    hour=MARKET_OPEN_HOUR,
                    minute=MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0
                )
            else:
                # After market close - next open is tomorrow
                from datetime import timedelta
                next_open = eastern_now.replace(
                    hour=MARKET_OPEN_HOUR,
                    minute=MARKET_OPEN_MINUTE,
                    second=0,
                    microsecond=0
                ) + timedelta(days=1)
        
        time_diff = next_open - eastern_now
        total_seconds = int(time_diff.total_seconds())
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return (hours, minutes, seconds)
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to calculate time until market open: {e}")
        return (0, 0, 0)


def format_market_status() -> str:
    """
    Get a formatted string with current market status.
    Useful for logging and display.
    
    Returns:
        str: Formatted market status message
    """
    status = get_market_status()
    
    if status['is_open']:
        return (
            f"[OPEN] MARKET OPEN - {status['session'].upper()}\n"
            f"   Eastern Time: {status['eastern_time']}\n"
            f"   Local Time: {status['local_time']} ({status['local_timezone']})\n"
            f"   Closes: {status['next_close']}"
        )
    else:
        hours, minutes, seconds = get_time_until_market_open()
        return (
            f"[CLOSED] MARKET CLOSED - {status['session'].upper()}\n"
            f"   Eastern Time: {status['eastern_time']}\n"
            f"   Local Time: {status['local_time']} ({status['local_timezone']})\n"
            f"   Opens: {status['next_open']}\n"
            f"   Time until open: {hours}h {minutes}m {seconds}s"
        )


def is_overnight_session() -> bool:
    """
    Check if currently in IB overnight trading session (8:00 PM - 3:50 AM ET)

    Returns:
        bool: True if in overnight session, False otherwise
    """
    try:
        eastern_now = get_eastern_time()

        # Saturday - no overnight trading
        if eastern_now.weekday() == 5:
            return False

        # Sunday evening - overnight session starts at 8:00 PM
        if eastern_now.weekday() == 6 and eastern_now.hour >= 20:
            return True

        current_time = eastern_now.time()

        # Overnight hours: 8:00 PM to 3:50 AM (spans midnight)
        overnight_start = time(OVERNIGHT_START_HOUR, OVERNIGHT_START_MINUTE)
        overnight_end = time(OVERNIGHT_END_HOUR, OVERNIGHT_END_MINUTE)

        # Handle overnight spanning midnight
        if current_time >= overnight_start or current_time <= overnight_end:
            return True

        return False

    except Exception as e:
        logger.error(f"[ERROR] Overnight session check failed: {e}")
        return False


def is_ib_trading_hours() -> bool:
    """
    Check if IB trading is available (any session: pre-market, regular, after-hours, or overnight)
    Supports 24/5 trading capability

    Returns:
        bool: True if IB can trade, False otherwise
    """
    try:
        eastern_now = get_eastern_time()

        # Saturday - no trading
        if eastern_now.weekday() == 5:
            return False

        # Sunday - only after 8:00 PM
        if eastern_now.weekday() == 6:
            return eastern_now.hour >= 20

        # Monday-Friday: Check if in any trading session
        current_time = eastern_now.time()

        # Pre-market: 4:00 AM - 9:30 AM
        pre_market_start = time(PRE_MARKET_OPEN_HOUR, PRE_MARKET_OPEN_MINUTE)
        market_open = time(MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE)

        # After-hours: 4:00 PM - 8:00 PM
        market_close = time(MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE)
        after_hours_end = time(AFTER_HOURS_CLOSE_HOUR, AFTER_HOURS_CLOSE_MINUTE)

        # Overnight: 8:00 PM - 3:50 AM
        overnight_start = time(OVERNIGHT_START_HOUR, OVERNIGHT_START_MINUTE)
        overnight_end = time(OVERNIGHT_END_HOUR, OVERNIGHT_END_MINUTE)

        # Check all sessions
        if pre_market_start <= current_time < after_hours_end:
            # Covers pre-market, regular, and after-hours
            return True

        if current_time >= overnight_start or current_time <= overnight_end:
            # Covers overnight session
            return True

        return False

    except Exception as e:
        logger.error(f"[ERROR] IB trading hours check failed: {e}")
        return False


# Convenience function for backward compatibility
def is_market_hours() -> bool:
    """
    Simple check if market is open (regular hours only).
    Alias for is_market_open() for backward compatibility.

    Returns:
        bool: True if market is open, False otherwise
    """
    return is_market_open(include_extended_hours=False)


if __name__ == "__main__":
    # Test the module
    print("=" * 60)
    print("MARKET HOURS UTILITY TEST")
    print("=" * 60)
    print()
    print(format_market_status())
    print()
    print("=" * 60)

