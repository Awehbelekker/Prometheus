# multi_tenancy.py
# Multi-tenancy utilities
from typing import Dict, Any

class TenantManager:
    def __init__(self):
        self.tenants: Dict[str, Any] = {}

    def add_tenant(self, tenant_id: str, metadata: Dict[str, Any]):
        self.tenants[tenant_id] = metadata

    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        return self.tenants.get(tenant_id, {})

    def list_tenants(self):
        return list(self.tenants.keys())
