from typing import Optional, Dict, Any, List
from core.utils.time_utils import utc_now

AUDIT_LOGS: List[Dict[str, Any]] = []

def add_audit_log(user_id: str, action: str, details: str, level: str, extra: Optional[Dict[str, Any]] = None):
    entry = {
        'id': f'audit_{len(AUDIT_LOGS)+1:06d}',
        'user_id': user_id,
        'action': action,
        'details': details,
        'level': level,
        'timestamp': utc_now().isoformat().replace('+00:00','Z')
    }
    if extra:
        entry['extra'] = extra
    AUDIT_LOGS.append(entry)
    return entry
