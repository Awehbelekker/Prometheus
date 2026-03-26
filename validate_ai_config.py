#!/usr/bin/env python3
"""
🔍 AI Configuration Validation Script
Validates that PROMETHEUS AI configuration is properly set up for full intelligence
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate environment variables"""
    print("🔍 VALIDATING ENVIRONMENT CONFIGURATION")
    print("=" * 60)
    
    # Load environment
    load_dotenv()
    
    # Check critical environment variables
    env_vars = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'OPENAI_MODEL': os.getenv('OPENAI_MODEL'),
        'THINKMESH_ENABLED': os.getenv('THINKMESH_ENABLED'),
        'GPT_OSS_ENABLED': os.getenv('GPT_OSS_ENABLED'),
    }
    
    print("\n📋 ENVIRONMENT VARIABLES:")
    print("-" * 40)
    
    for var, value in env_vars.items():
        if value:
            if 'API_KEY' in var:
                # Mask API key for security
                masked_value = f"{value[:12]}...{value[-4:]}" if len(value) > 16 else "SET"
                print(f"   [CHECK] {var}: {masked_value}")
            else:
                print(f"   [CHECK] {var}: {value}")
        else:
            print(f"   [ERROR] {var}: NOT SET")
    
    return env_vars

def validate_ai_config():
    """Validate AI configuration loading"""
    print("\n🤖 VALIDATING AI CONFIGURATION")
    print("-" * 40)
    
    try:
        # Import AI config
        from config.ai_config import ai_config_manager, AIProvider
        
        print("   [CHECK] AI config module imported successfully")
        
        # Check available providers
        available_providers = ai_config_manager.get_available_providers()
        print(f"   📊 Available providers: {[p.value for p in available_providers]}")
        
        # Check if real providers are available
        real_providers = [p for p in available_providers if p != AIProvider.MOCK]
        if real_providers:
            print(f"   [CHECK] Real AI providers detected: {[p.value for p in real_providers]}")
            return True
        else:
            print("   [ERROR] Only mock providers available - check API keys")
            return False
            
    except ImportError as e:
        print(f"   [ERROR] Failed to import AI config: {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] AI config validation error: {e}")
        return False

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🔗 TESTING OPENAI CONNECTION")
    print("-" * 40)
    
    try:
        from core.llm_service import LLMService, AIMessage
        
        # Initialize LLM service
        llm_service = LLMService()
        
        # Test simple completion
        test_messages = [
            AIMessage(role="user", content="Say 'AI connection successful' if you can read this.")
        ]
        
        print("   🔄 Testing OpenAI API connection...")
        response = await llm_service.generate_response(
            messages=test_messages,
            model="gpt-4o-mini"
        )
        
        if response.success:
            print(f"   [CHECK] OpenAI connection successful!")
            print(f"   📝 Response: {response.content[:100]}...")
            print(f"   ⏱️ Response time: {response.response_time:.2f}s")
            print(f"   🎯 Tokens used: {response.tokens_used}")
            return True
        else:
            print(f"   [ERROR] OpenAI connection failed: {response.error}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] OpenAI connection test error: {e}")
        return False

def validate_revolutionary_engines():
    """Check Revolutionary Engines status"""
    print("\n[LIGHTNING] VALIDATING REVOLUTIONARY ENGINES")
    print("-" * 40)
    
    try:
        # Check if engines can import AI coordination
        from revolutionary_master_engine import AI_COORDINATION_AVAILABLE
        
        if AI_COORDINATION_AVAILABLE:
            print("   [CHECK] AI Coordination systems available")
        else:
            print("   [WARNING]️ AI Coordination systems not available - running in basic mode")
        
        print("   [CHECK] Revolutionary engines module accessible")
        return True
        
    except ImportError as e:
        print(f"   [ERROR] Revolutionary engines import error: {e}")
        return False
    except Exception as e:
        print(f"   [ERROR] Revolutionary engines validation error: {e}")
        return False

async def main():
    """Main validation function"""
    print("🚀 PROMETHEUS AI CONFIGURATION VALIDATION")
    print("=" * 60)
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Run validation steps
    env_valid = validate_environment()
    config_valid = validate_ai_config()
    engines_valid = validate_revolutionary_engines()
    
    # Test OpenAI connection if config is valid
    openai_valid = False
    if config_valid and env_valid.get('OPENAI_API_KEY'):
        openai_valid = await test_openai_connection()
    
    # Summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    results = {
        "Environment Variables": "[CHECK] PASS" if env_valid.get('OPENAI_API_KEY') else "[ERROR] FAIL",
        "AI Configuration": "[CHECK] PASS" if config_valid else "[ERROR] FAIL", 
        "OpenAI Connection": "[CHECK] PASS" if openai_valid else "[ERROR] FAIL",
        "Revolutionary Engines": "[CHECK] PASS" if engines_valid else "[ERROR] FAIL"
    }
    
    for test, result in results.items():
        print(f"   {test}: {result}")
    
    # Overall status
    all_passed = all("[CHECK]" in result for result in results.values())
    
    print("\n🎯 OVERALL STATUS")
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("[CHECK] PROMETHEUS is ready for full AI intelligence operation")
        print("🤖 Real AI providers are configured and functional")
        print("[LIGHTNING] Revolutionary engines can access AI coordination")
    else:
        print("[WARNING]️ SOME VALIDATIONS FAILED")
        print("[ERROR] PROMETHEUS may not operate at full intelligence")
        print("🔧 Review failed validations above and fix issues")
    
    return all_passed

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n[WARNING]️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        sys.exit(1)
