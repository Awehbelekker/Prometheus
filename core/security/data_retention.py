"""
Data Retention and Privacy Compliance Module
Implements GDPR-compliant data retention policies and automated cleanup
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import json

logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Data categories with different retention requirements"""
    ESSENTIAL_USER_DATA = "essential_user_data"  # 7 years (regulatory)
    TRADING_RECORDS = "trading_records"          # 7 years (regulatory)
    AUDIT_LOGS = "audit_logs"                   # 7 years (regulatory)
    SESSION_DATA = "session_data"               # 90 days
    ANALYTICS_DATA = "analytics_data"           # 2 years
    MARKETING_DATA = "marketing_data"           # 2 years (with consent)
    TEMPORARY_DATA = "temporary_data"           # 30 days
    CACHE_DATA = "cache_data"                   # 24 hours

class DataRetentionPolicy:
    """Data retention policy configuration"""
    
    def __init__(self):
        self.policies = {
            DataCategory.ESSENTIAL_USER_DATA: {
                "retention_days": 2555,  # 7 years
                "description": "Essential user profile data required for regulatory compliance",
                "legal_basis": "Regulatory requirement (MiFID II, GDPR Article 6(1)(c))",
                "auto_delete": False,  # Manual review required
                "anonymize_after": 2920  # 8 years - anonymize instead of delete
            },
            DataCategory.TRADING_RECORDS: {
                "retention_days": 2555,  # 7 years
                "description": "Trading transactions and order history",
                "legal_basis": "Regulatory requirement (MiFID II)",
                "auto_delete": False,  # Manual review required
                "anonymize_after": 2920  # 8 years
            },
            DataCategory.AUDIT_LOGS: {
                "retention_days": 2555,  # 7 years
                "description": "Security and compliance audit trails",
                "legal_basis": "Regulatory requirement and legitimate interest",
                "auto_delete": False,  # Manual review required
                "anonymize_after": 2920  # 8 years
            },
            DataCategory.SESSION_DATA: {
                "retention_days": 90,
                "description": "User session logs and activity data",
                "legal_basis": "Legitimate interest (security)",
                "auto_delete": True,
                "anonymize_after": None
            },
            DataCategory.ANALYTICS_DATA: {
                "retention_days": 730,  # 2 years
                "description": "Application usage analytics and performance metrics",
                "legal_basis": "Legitimate interest (service improvement)",
                "auto_delete": True,
                "anonymize_after": None
            },
            DataCategory.MARKETING_DATA: {
                "retention_days": 730,  # 2 years
                "description": "Marketing preferences and communication history",
                "legal_basis": "Consent (GDPR Article 6(1)(a))",
                "auto_delete": True,
                "anonymize_after": None,
                "requires_consent": True
            },
            DataCategory.TEMPORARY_DATA: {
                "retention_days": 30,
                "description": "Temporary files, uploads, and processing data",
                "legal_basis": "Legitimate interest (service provision)",
                "auto_delete": True,
                "anonymize_after": None
            },
            DataCategory.CACHE_DATA: {
                "retention_days": 1,
                "description": "Application cache and temporary storage",
                "legal_basis": "Legitimate interest (performance)",
                "auto_delete": True,
                "anonymize_after": None
            }
        }
    
    def get_retention_period(self, category: DataCategory) -> int:
        """Get retention period in days for a data category"""
        return self.policies[category]["retention_days"]
    
    def should_auto_delete(self, category: DataCategory) -> bool:
        """Check if data category should be automatically deleted"""
        return self.policies[category]["auto_delete"]
    
    def get_policy_info(self, category: DataCategory) -> Dict[str, Any]:
        """Get complete policy information for a data category"""
        return self.policies[category].copy()

class DataRetentionManager:
    """Manages data retention and automated cleanup"""
    
    def __init__(self):
        self.policy = DataRetentionPolicy()
        self.cleanup_log = []
    
    async def schedule_cleanup(self):
        """Schedule automated data cleanup"""
        logger.info("Starting scheduled data cleanup")
        
        cleanup_results = {}
        
        for category in DataCategory:
            try:
                result = await self.cleanup_category(category)
                cleanup_results[category.value] = result
            except Exception as e:
                logger.error(f"Cleanup failed for {category.value}: {e}")
                cleanup_results[category.value] = {"error": str(e)}
        
        # Log cleanup results
        self.cleanup_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "results": cleanup_results
        })
        
        logger.info(f"Data cleanup completed: {cleanup_results}")
        return cleanup_results
    
    async def cleanup_category(self, category: DataCategory) -> Dict[str, Any]:
        """Clean up data for a specific category"""
        policy_info = self.policy.get_policy_info(category)
        retention_days = policy_info["retention_days"]
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        result = {
            "category": category.value,
            "cutoff_date": cutoff_date.isoformat(),
            "records_processed": 0,
            "records_deleted": 0,
            "records_anonymized": 0,
            "auto_delete": policy_info["auto_delete"]
        }
        
        if policy_info["auto_delete"]:
            # Simulate data cleanup (replace with actual database operations)
            result.update(await self._perform_cleanup(category, cutoff_date))
        else:
            # For non-auto-delete categories, just identify records
            result.update(await self._identify_expired_records(category, cutoff_date))
        
        return result
    
    async def _perform_cleanup(self, category: DataCategory, cutoff_date: datetime) -> Dict[str, int]:
        """Perform actual data cleanup"""
        # Mock cleanup operation (replace with actual database operations)
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Simulate finding and deleting records
        mock_records_found = {
            DataCategory.SESSION_DATA: 150,
            DataCategory.ANALYTICS_DATA: 50,
            DataCategory.MARKETING_DATA: 25,
            DataCategory.TEMPORARY_DATA: 200,
            DataCategory.CACHE_DATA: 1000
        }.get(category, 0)
        
        return {
            "records_processed": mock_records_found,
            "records_deleted": mock_records_found,
            "records_anonymized": 0
        }
    
    async def _identify_expired_records(self, category: DataCategory, cutoff_date: datetime) -> Dict[str, int]:
        """Identify expired records that need manual review"""
        # Mock identification (replace with actual database queries)
        await asyncio.sleep(0.1)
        
        mock_records_found = {
            DataCategory.ESSENTIAL_USER_DATA: 5,
            DataCategory.TRADING_RECORDS: 10,
            DataCategory.AUDIT_LOGS: 8
        }.get(category, 0)
        
        return {
            "records_processed": mock_records_found,
            "records_deleted": 0,
            "records_anonymized": 0
        }
    
    async def anonymize_user_data(self, user_id: str) -> Dict[str, Any]:
        """Anonymize user data while preserving regulatory records"""
        logger.info(f"Starting data anonymization for user {user_id}")
        
        anonymization_result = {
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "categories_processed": [],
            "records_anonymized": 0,
            "records_preserved": 0
        }
        
        # Categories that can be anonymized
        anonymizable_categories = [
            DataCategory.SESSION_DATA,
            DataCategory.ANALYTICS_DATA,
            DataCategory.MARKETING_DATA,
            DataCategory.TEMPORARY_DATA
        ]
        
        for category in anonymizable_categories:
            try:
                result = await self._anonymize_category_data(user_id, category)
                anonymization_result["categories_processed"].append({
                    "category": category.value,
                    "records_anonymized": result["anonymized"],
                    "records_preserved": result["preserved"]
                })
                anonymization_result["records_anonymized"] += result["anonymized"]
                anonymization_result["records_preserved"] += result["preserved"]
                
            except Exception as e:
                logger.error(f"Anonymization failed for {category.value}: {e}")
        
        logger.info(f"Data anonymization completed for user {user_id}")
        return anonymization_result
    
    async def _anonymize_category_data(self, user_id: str, category: DataCategory) -> Dict[str, int]:
        """Anonymize data for a specific category"""
        # Mock anonymization (replace with actual database operations)
        await asyncio.sleep(0.1)
        
        # Simulate anonymization process
        mock_records = {
            DataCategory.SESSION_DATA: 20,
            DataCategory.ANALYTICS_DATA: 15,
            DataCategory.MARKETING_DATA: 10,
            DataCategory.TEMPORARY_DATA: 5
        }.get(category, 0)
        
        return {
            "anonymized": mock_records,
            "preserved": 0  # Records that must be preserved for regulatory reasons
        }
    
    def get_retention_summary(self) -> Dict[str, Any]:
        """Get summary of all retention policies"""
        summary = {
            "total_categories": len(DataCategory),
            "auto_delete_categories": 0,
            "manual_review_categories": 0,
            "policies": {}
        }
        
        for category in DataCategory:
            policy_info = self.policy.get_policy_info(category)
            
            if policy_info["auto_delete"]:
                summary["auto_delete_categories"] += 1
            else:
                summary["manual_review_categories"] += 1
            
            summary["policies"][category.value] = {
                "retention_days": policy_info["retention_days"],
                "retention_years": round(policy_info["retention_days"] / 365, 1),
                "auto_delete": policy_info["auto_delete"],
                "legal_basis": policy_info["legal_basis"],
                "description": policy_info["description"]
            }
        
        return summary
    
    def get_cleanup_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent cleanup history"""
        return self.cleanup_log[-limit:] if self.cleanup_log else []

class GDPRComplianceManager:
    """GDPR compliance management"""
    
    def __init__(self):
        self.retention_manager = DataRetentionManager()
    
    async def handle_data_subject_request(self, request_type: str, user_id: str) -> Dict[str, Any]:
        """Handle GDPR data subject requests"""
        logger.info(f"Processing {request_type} request for user {user_id}")
        
        if request_type == "access":
            return await self._handle_access_request(user_id)
        elif request_type == "erasure":
            return await self._handle_erasure_request(user_id)
        elif request_type == "portability":
            return await self._handle_portability_request(user_id)
        elif request_type == "rectification":
            return await self._handle_rectification_request(user_id)
        else:
            raise ValueError(f"Unsupported request type: {request_type}")
    
    async def _handle_access_request(self, user_id: str) -> Dict[str, Any]:
        """Handle right to access request"""
        # Mock data access (replace with actual database queries)
        user_data = {
            "user_id": user_id,
            "personal_data": {
                "profile": {"email": "user@example.com", "name": "John Doe"},
                "trading_history": ["order_1", "order_2"],
                "session_logs": ["session_1", "session_2"]
            },
            "data_categories": [category.value for category in DataCategory],
            "retention_info": self.retention_manager.get_retention_summary()
        }
        
        return {
            "request_type": "access",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": user_data
        }
    
    async def _handle_erasure_request(self, user_id: str) -> Dict[str, Any]:
        """Handle right to erasure request"""
        # Check if user has active regulatory obligations
        has_regulatory_data = await self._check_regulatory_obligations(user_id)
        
        if has_regulatory_data:
            # Anonymize instead of delete
            result = await self.retention_manager.anonymize_user_data(user_id)
            result["action"] = "anonymized"
            result["reason"] = "Regulatory data retention requirements"
        else:
            # Full deletion possible
            result = await self._delete_user_data(user_id)
            result["action"] = "deleted"
        
        return {
            "request_type": "erasure",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result
        }
    
    async def _handle_portability_request(self, user_id: str) -> Dict[str, Any]:
        """Handle right to data portability request"""
        # Export user data in portable format
        portable_data = {
            "user_profile": {"email": "user@example.com", "preferences": {}},
            "trading_data": {"orders": [], "positions": []},
            "export_format": "JSON",
            "export_date": datetime.utcnow().isoformat()
        }
        
        return {
            "request_type": "portability",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "portable_data": portable_data
        }
    
    async def _handle_rectification_request(self, user_id: str) -> Dict[str, Any]:
        """Handle right to rectification request"""
        return {
            "request_type": "rectification",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "ready_for_update",
            "message": "User data ready for rectification"
        }
    
    async def _check_regulatory_obligations(self, user_id: str) -> bool:
        """Check if user has data subject to regulatory retention"""
        # Mock check (replace with actual database query)
        return True  # Assume trading users have regulatory data
    
    async def _delete_user_data(self, user_id: str) -> Dict[str, Any]:
        """Delete all user data"""
        # Mock deletion (replace with actual database operations)
        return {
            "records_deleted": 100,
            "categories_affected": [category.value for category in DataCategory]
        }

# Global instances
retention_manager = DataRetentionManager()
gdpr_manager = GDPRComplianceManager()
