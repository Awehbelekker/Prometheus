# audit_log.py
# Audit logging for user actions and system events
import time
from typing import List, Dict, Any

class AuditLogManager:
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_event(self, user_id: str, action: str, details: Dict[str, Any], tenant_id: str = "default"):
        self.logs.append({
            "timestamp": time.time(),
            "user_id": user_id,
            "action": action,
            "details": details,
            "tenant_id": tenant_id
        })
        print(f"AUDIT: {user_id} {action} {details} (tenant={tenant_id})")

    def get_logs(self, tenant_id: str = None) -> List[Dict[str, Any]]:
        if tenant_id:
            return [log for log in self.logs if log["tenant_id"] == tenant_id]
        return self.logs
