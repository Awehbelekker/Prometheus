"""
Database Security Module
Provides SQL injection protection and secure database operations
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

class SQLInjectionProtector:
    """SQL injection protection and query sanitization"""
    
    def __init__(self):
        # Comprehensive SQL injection patterns
        self.dangerous_patterns = [
            # Basic SQL injection patterns
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
            r"(\b(UNION|JOIN)\b.*\b(SELECT|FROM)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            
            # Comment patterns
            r"(--|#|/\*|\*/)",
            r"(\bxp_\w+)",
            r"(\bsp_\w+)",
            
            # Time-based injection
            r"(\b(WAITFOR|DELAY|SLEEP)\b)",
            r"(\b(BENCHMARK|PG_SLEEP)\b)",
            
            # Union-based injection
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\bUNION\b.*\bALL\b.*\bSELECT\b)",
            
            # Boolean-based injection
            r"(\b(TRUE|FALSE)\b.*\b(AND|OR)\b)",
            r"(\d+\s*=\s*\d+)",
            r"(['\"].*['\"].*=.*['\"].*['\"])",
            
            # Function-based injection
            r"(\b(CAST|CONVERT|CHAR|ASCII|SUBSTRING)\b)",
            r"(\b(CONCAT|GROUP_CONCAT|STRING_AGG)\b)",
            r"(\b(VERSION|USER|DATABASE|SCHEMA)\b\s*\(\s*\))",
            
            # Error-based injection
            r"(\b(EXTRACTVALUE|UPDATEXML|XMLTYPE)\b)",
            r"(\b(EXP|FLOOR|RAND)\b.*\b(FROM|WHERE)\b)",
            
            # Stacked queries
            r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER))",
            
            # Hex encoding attempts
            r"(0x[0-9a-fA-F]+)",
            
            # LDAP injection
            r"(\*\)|\(\|)",
            
            # NoSQL injection patterns
            r"(\$where|\$ne|\$gt|\$lt|\$regex)",
            
            # Advanced patterns
            r"(\b(LOAD_FILE|INTO\s+OUTFILE|INTO\s+DUMPFILE)\b)",
            r"(\b(INFORMATION_SCHEMA|MYSQL\.USER|PG_USER)\b)",
            r"(\b(SYSOBJECTS|SYSCOLUMNS|SYSTABLES)\b)"
        ]
        
        # Compile patterns for better performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            for pattern in self.dangerous_patterns
        ]
        
        # Allowed characters for different input types
        self.allowed_patterns = {
            'alphanumeric': re.compile(r'^[a-zA-Z0-9_]+$'),
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'numeric': re.compile(r'^\d+(\.\d+)?$'),
            'symbol': re.compile(r'^[A-Z]{1,10}$'),  # Stock symbols
            'uuid': re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
        }
    
    def is_sql_injection_attempt(self, input_string: str) -> bool:
        """Check if input contains SQL injection patterns"""
        if not input_string:
            return False
        
        # Convert to string if not already
        input_str = str(input_string).strip()
        
        # Check against all patterns
        for pattern in self.compiled_patterns:
            if pattern.search(input_str):
                logger.warning(f"SQL injection pattern detected: {input_str[:100]}")
                return True
        
        return False
    
    def sanitize_input(self, input_value: Any, input_type: str = 'general') -> str:
        """Sanitize input based on type"""
        if input_value is None:
            return ""
        
        input_str = str(input_value).strip()
        
        # Remove null bytes
        input_str = input_str.replace('\x00', '')
        
        # Type-specific validation
        if input_type in self.allowed_patterns:
            if not self.allowed_patterns[input_type].match(input_str):
                raise ValueError(f"Invalid {input_type} format: {input_str}")
        
        # General sanitization
        if input_type == 'general':
            # Remove dangerous characters
            dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '*', '?']
            for char in dangerous_chars:
                input_str = input_str.replace(char, '')
        
        # Length limits
        max_lengths = {
            'email': 254,
            'symbol': 10,
            'alphanumeric': 50,
            'general': 1000
        }
        
        max_length = max_lengths.get(input_type, 1000)
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
        
        return input_str
    
    def validate_query_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize query parameters"""
        sanitized_params = {}
        
        for key, value in params.items():
            # Validate parameter name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
                raise ValueError(f"Invalid parameter name: {key}")
            
            # Check for SQL injection in value
            if self.is_sql_injection_attempt(str(value)):
                raise ValueError(f"SQL injection attempt detected in parameter: {key}")
            
            sanitized_params[key] = value
        
        return sanitized_params

class SecureDatabase:
    """Secure database operations with SQL injection protection"""
    
    def __init__(self, session: Session):
        self.session = session
        self.protector = SQLInjectionProtector()
    
    def execute_safe_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a parameterized query safely"""
        try:
            # Validate parameters
            if params:
                params = self.protector.validate_query_parameters(params)
            
            # Use parameterized query
            result = self.session.execute(text(query), params or {})
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def safe_select(self, table: str, columns: List[str], where_clause: str = "", 
                   params: Optional[Dict[str, Any]] = None) -> Any:
        """Perform a safe SELECT query"""
        # Validate table and column names
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid table name: {table}")
        
        for column in columns:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                raise ValueError(f"Invalid column name: {column}")
        
        # Build query
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM {table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return self.execute_safe_query(query, params)
    
    def safe_insert(self, table: str, data: Dict[str, Any]) -> Any:
        """Perform a safe INSERT query"""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Validate column names and data
        validated_data = {}
        for column, value in data.items():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                raise ValueError(f"Invalid column name: {column}")
            
            # Check for SQL injection in value
            if self.protector.is_sql_injection_attempt(str(value)):
                raise ValueError(f"SQL injection attempt detected in data for column: {column}")
            
            validated_data[column] = value
        
        # Build parameterized query
        columns = list(validated_data.keys())
        placeholders = [f":{col}" for col in columns]
        
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
        
        return self.execute_safe_query(query, validated_data)
    
    def safe_update(self, table: str, data: Dict[str, Any], where_clause: str, 
                   where_params: Optional[Dict[str, Any]] = None) -> Any:
        """Perform a safe UPDATE query"""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Validate and prepare update data
        validated_data = {}
        set_clauses = []
        
        for column, value in data.items():
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                raise ValueError(f"Invalid column name: {column}")
            
            if self.protector.is_sql_injection_attempt(str(value)):
                raise ValueError(f"SQL injection attempt detected in data for column: {column}")
            
            set_clauses.append(f"{column} = :{column}")
            validated_data[column] = value
        
        # Combine with where parameters
        all_params = validated_data.copy()
        if where_params:
            where_params = self.protector.validate_query_parameters(where_params)
            all_params.update(where_params)
        
        # Build query
        query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"
        
        return self.execute_safe_query(query, all_params)
    
    def safe_delete(self, table: str, where_clause: str, 
                   where_params: Optional[Dict[str, Any]] = None) -> Any:
        """Perform a safe DELETE query"""
        # Validate table name
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid table name: {table}")
        
        # Validate where parameters
        if where_params:
            where_params = self.protector.validate_query_parameters(where_params)
        
        # Build query
        query = f"DELETE FROM {table} WHERE {where_clause}"
        
        return self.execute_safe_query(query, where_params)

# Global protector instance
sql_protector = SQLInjectionProtector()

def validate_input(input_value: Any, input_type: str = 'general') -> str:
    """Global function to validate and sanitize input"""
    return sql_protector.sanitize_input(input_value, input_type)

def check_sql_injection(input_value: Any) -> bool:
    """Global function to check for SQL injection"""
    return sql_protector.is_sql_injection_attempt(str(input_value))

def create_secure_db(session: Session) -> SecureDatabase:
    """Factory function to create secure database instance"""
    return SecureDatabase(session)
