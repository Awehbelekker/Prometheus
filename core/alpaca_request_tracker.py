#!/usr/bin/env python3
"""
🔍 Alpaca Request ID Tracker
PROMETHEUS Trading Platform - Track X-Request-ID for debugging and support
"""

import os
import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import sqlite3
import threading
from pathlib import Path

@dataclass
class AlpacaRequest:
    """Alpaca API request with tracking info"""
    request_id: str
    timestamp: str
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    request_data: Optional[Dict] = None
    response_data: Optional[Dict] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class AlpacaRequestTracker:
    """
    🎯 Track Alpaca API Request IDs for debugging and support
    
    This class provides:
    - Automatic X-Request-ID capture from all Alpaca API calls
    - Request/response logging with performance metrics
    - SQLite database storage for request history
    - Easy retrieval of recent Request IDs for support tickets
    """
    
    def __init__(self, db_path: str = "alpaca_requests.db", max_requests: int = 10000):
        self.db_path = db_path
        self.max_requests = max_requests
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # In-memory cache for recent requests
        self.recent_requests: List[AlpacaRequest] = []
        
    def _init_database(self):
        """Initialize SQLite database for request tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS alpaca_requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        request_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        method TEXT NOT NULL,
                        status_code INTEGER NOT NULL,
                        response_time_ms REAL NOT NULL,
                        request_data TEXT,
                        response_data TEXT,
                        error_message TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster queries
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON alpaca_requests(timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_request_id 
                    ON alpaca_requests(request_id)
                """)
                
                conn.commit()
                self.logger.info("[CHECK] Alpaca request tracking database initialized")
                
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to initialize tracking database: {e}")
    
    def make_tracked_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> requests.Response:
        """
        Make an HTTP request with automatic X-Request-ID tracking
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL for the request
            headers: Request headers
            data: Form data
            json_data: JSON data
            params: URL parameters
            
        Returns:
            requests.Response object with X-Request-ID tracked
        """
        start_time = datetime.now()
        
        # Prepare headers
        if headers is None:
            headers = {}
            
        # Add required Alpaca headers if not present
        if 'APCA-API-KEY-ID' not in headers:
            # Try to get from environment
            api_key = os.getenv("ALPACA_PAPER_KEY") or os.getenv("ALPACA_LIVE_KEY") or os.getenv("APCA_API_KEY_ID")
            if api_key:
                headers['APCA-API-KEY-ID'] = api_key
                
        if 'APCA-API-SECRET-KEY' not in headers:
            api_secret = os.getenv("ALPACA_PAPER_SECRET") or os.getenv("ALPACA_LIVE_SECRET") or os.getenv("APCA_API_SECRET_KEY")
            if api_secret:
                headers['APCA-API-SECRET-KEY'] = api_secret
        
        # Make the request
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                if json_data:
                    response = requests.post(url, headers=headers, json=json_data, params=params)
                else:
                    response = requests.post(url, headers=headers, data=data, params=params)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params)
            elif method.upper() == 'PUT':
                if json_data:
                    response = requests.put(url, headers=headers, json=json_data, params=params)
                else:
                    response = requests.put(url, headers=headers, data=data, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Calculate response time
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Extract X-Request-ID from response headers
            request_id = response.headers.get('X-Request-ID', 'unknown')
            
            # Parse response data if JSON
            response_data = None
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    response_data = response.json()
            except:
                pass
            
            # Create request record
            request_record = AlpacaRequest(
                request_id=request_id,
                timestamp=start_time.isoformat(),
                endpoint=url,
                method=method.upper(),
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                request_data=json_data or data or params,
                response_data=response_data,
                error_message=None if response.status_code < 400 else f"HTTP {response.status_code}"
            )
            
            # Store the request
            self._store_request(request_record)
            
            # Log the request
            status_emoji = "[CHECK]" if response.status_code < 400 else "[ERROR]"
            self.logger.info(
                f"{status_emoji} Alpaca API Call: {method} {url} -> "
                f"{response.status_code} ({response_time_ms:.1f}ms) "
                f"[Request-ID: {request_id}]"
            )
            
            return response
            
        except Exception as e:
            end_time = datetime.now()
            response_time_ms = (end_time - start_time).total_seconds() * 1000
            
            # Create error record
            request_record = AlpacaRequest(
                request_id='error',
                timestamp=start_time.isoformat(),
                endpoint=url,
                method=method.upper(),
                status_code=0,
                response_time_ms=response_time_ms,
                request_data=json_data or data or params,
                response_data=None,
                error_message=str(e)
            )
            
            self._store_request(request_record)
            
            self.logger.error(f"[ERROR] Alpaca API Error: {method} {url} -> {e}")
            raise
    
    def _store_request(self, request: AlpacaRequest):
        """Store request in database and memory cache"""
        with self._lock:
            # Add to memory cache
            self.recent_requests.append(request)
            
            # Keep only recent requests in memory
            if len(self.recent_requests) > 100:
                self.recent_requests = self.recent_requests[-100:]
            
            # Store in database
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO alpaca_requests 
                        (request_id, timestamp, endpoint, method, status_code, 
                         response_time_ms, request_data, response_data, error_message)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        request.request_id,
                        request.timestamp,
                        request.endpoint,
                        request.method,
                        request.status_code,
                        request.response_time_ms,
                        json.dumps(request.request_data) if request.request_data else None,
                        json.dumps(request.response_data) if request.response_data else None,
                        request.error_message
                    ))
                    
                    # Clean up old records if we have too many
                    conn.execute("""
                        DELETE FROM alpaca_requests 
                        WHERE id NOT IN (
                            SELECT id FROM alpaca_requests 
                            ORDER BY created_at DESC 
                            LIMIT ?
                        )
                    """, (self.max_requests,))
                    
                    conn.commit()
                    
            except Exception as e:
                self.logger.error(f"Failed to store request in database: {e}")
    
    def get_recent_requests(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent requests for debugging"""
        with self._lock:
            recent = self.recent_requests[-limit:] if self.recent_requests else []
            return [req.to_dict() for req in reversed(recent)]
    
    def get_request_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get specific request by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT request_id, timestamp, endpoint, method, status_code,
                           response_time_ms, request_data, response_data, error_message
                    FROM alpaca_requests 
                    WHERE request_id = ?
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (request_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'request_id': row[0],
                        'timestamp': row[1],
                        'endpoint': row[2],
                        'method': row[3],
                        'status_code': row[4],
                        'response_time_ms': row[5],
                        'request_data': json.loads(row[6]) if row[6] else None,
                        'response_data': json.loads(row[7]) if row[7] else None,
                        'error_message': row[8]
                    }
        except Exception as e:
            self.logger.error(f"Error retrieving request {request_id}: {e}")
        
        return None
    
    def get_failed_requests(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed requests from the last N hours"""
        try:
            since = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT request_id, timestamp, endpoint, method, status_code,
                           response_time_ms, request_data, response_data, error_message
                    FROM alpaca_requests 
                    WHERE (status_code >= 400 OR error_message IS NOT NULL)
                    AND timestamp >= ?
                    ORDER BY created_at DESC
                """, (since,))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'request_id': row[0],
                        'timestamp': row[1],
                        'endpoint': row[2],
                        'method': row[3],
                        'status_code': row[4],
                        'response_time_ms': row[5],
                        'request_data': json.loads(row[6]) if row[6] else None,
                        'response_data': json.loads(row[7]) if row[7] else None,
                        'error_message': row[8]
                    })
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error retrieving failed requests: {e}")
        
        return []
    
    def generate_support_report(self) -> Dict[str, Any]:
        """Generate a report for Alpaca support with recent Request IDs"""
        recent_requests = self.get_recent_requests(10)
        failed_requests = self.get_failed_requests(24)
        
        # Extract Request IDs for easy copy-paste
        recent_ids = [req['request_id'] for req in recent_requests if req['request_id'] != 'unknown']
        failed_ids = [req['request_id'] for req in failed_requests if req['request_id'] != 'unknown']
        
        return {
            'generated_at': datetime.now().isoformat(),
            'recent_request_ids': recent_ids,
            'failed_request_ids': failed_ids,
            'recent_requests': recent_requests,
            'failed_requests': failed_requests,
            'summary': {
                'total_recent': len(recent_requests),
                'total_failed_24h': len(failed_requests),
                'latest_request_id': recent_ids[0] if recent_ids else None
            }
        }

# Global instance
_request_tracker: Optional[AlpacaRequestTracker] = None

def get_request_tracker() -> AlpacaRequestTracker:
    """Get global request tracker instance"""
    global _request_tracker
    if _request_tracker is None:
        _request_tracker = AlpacaRequestTracker()
    return _request_tracker

# Main function for testing
if __name__ == "__main__":
    # Test the request tracker
    tracker = AlpacaRequestTracker()
    
    # Example of making a tracked request to Alpaca
    try:
        # This would be a real Alpaca API call
        response = tracker.make_tracked_request(
            method="GET",
            url="https://paper-api.alpaca.markets/v2/account",
            headers={
                "APCA-API-KEY-ID": os.getenv("ALPACA_PAPER_KEY", ""),
                "APCA-API-SECRET-KEY": os.getenv("ALPACA_PAPER_SECRET", "")
            }
        )
        
        print(f"[CHECK] Request successful: {response.status_code}")
        print(f"🆔 Request ID: {response.headers.get('X-Request-ID', 'not found')}")
        
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
    
    # Show recent requests
    recent = tracker.get_recent_requests(5)
    print(f"\n📊 Recent requests: {len(recent)}")
    for req in recent:
        print(f"   {req['method']} {req['endpoint']} -> {req['status_code']} [{req['request_id']}]")
    
    # Generate support report
    report = tracker.generate_support_report()
    print(f"\n🎫 Support Report:")
    print(f"   Recent Request IDs: {report['recent_request_ids']}")
    print(f"   Failed in 24h: {len(report['failed_requests'])}")
