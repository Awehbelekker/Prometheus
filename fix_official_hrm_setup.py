#!/usr/bin/env python3
"""
Fix Official HRM Setup
Installs FlashAttention and configures official HRM to work
"""

import sys
import subprocess
import logging

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_cuda():
    """Check if CUDA is available"""
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            logger.info(f"✅ CUDA Available: {torch.cuda.get_device_name(0)}")
            logger.info(f"   CUDA Version: {torch.version.cuda}")
            return True
        else:
            logger.warning("⚠️ CUDA not available - FlashAttention may not work")
            return False
    except ImportError:
        logger.error("❌ PyTorch not installed")
        return False

def install_flash_attention():
    """Install FlashAttention"""
    logger.info("=" * 80)
    logger.info("INSTALLING FLASHATTENTION FOR OFFICIAL HRM")
    logger.info("=" * 80)
    
    # Check CUDA first
    cuda_available = check_cuda()
    
    if not cuda_available:
        logger.warning("⚠️ CUDA not available")
        logger.warning("   FlashAttention requires CUDA")
        logger.warning("   Attempting installation anyway (may fail)")
    
    try:
        logger.info("Installing flash-attn...")
        logger.info("Note: This may take several minutes and requires CUDA")
        
        # Try installing flash-attn
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "flash-attn", "--no-build-isolation"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            logger.info("✅ FlashAttention installed successfully")
            return True
        else:
            logger.error(f"❌ FlashAttention installation failed:")
            logger.error(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ FlashAttention installation timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error installing FlashAttention: {e}")
        return False

def create_flash_attention_fallback():
    """Create a fallback for FlashAttention if it's not available"""
    logger.info("Creating FlashAttention fallback...")
    
    fallback_code = '''
"""
FlashAttention Fallback
Provides fallback implementation when flash-attn is not available
"""

try:
    from flash_attn import flash_attn_func
    FLASH_ATTN_AVAILABLE = True
except ImportError:
    FLASH_ATTN_AVAILABLE = False
    
    # Fallback implementation using standard attention
    import torch
    import torch.nn.functional as F
    
    def flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None, causal=False):
        """
        Fallback flash attention using standard scaled dot-product attention
        """
        # Use PyTorch's built-in scaled_dot_product_attention if available
        if hasattr(F, 'scaled_dot_product_attention'):
            return F.scaled_dot_product_attention(q, k, v, dropout_p=dropout_p, scale=softmax_scale, is_causal=causal)
        else:
            # Manual implementation
            scale = softmax_scale or (1.0 / (q.size(-1) ** 0.5))
            attn = torch.matmul(q, k.transpose(-2, -1)) * scale
            if causal:
                mask = torch.triu(torch.ones(attn.size(-2), attn.size(-1), device=attn.device), diagonal=1)
                attn = attn.masked_fill(mask.bool(), float('-inf'))
            attn = F.softmax(attn, dim=-1)
            if dropout_p > 0:
                attn = F.dropout(attn, p=dropout_p)
            return torch.matmul(attn, v)
'''
    
    try:
        # Create flash_attn_interface.py in official_hrm
        from pathlib import Path
        official_hrm_path = Path("official_hrm")
        if official_hrm_path.exists():
            fallback_file = official_hrm_path / "flash_attn_interface.py"
            with open(fallback_file, 'w', encoding='utf-8') as f:
                f.write(fallback_code)
            logger.info(f"✅ Created FlashAttention fallback at {fallback_file}")
            return True
        else:
            logger.error("❌ official_hrm directory not found")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to create fallback: {e}")
        return False

def test_hrm_import():
    """Test if HRM can be imported"""
    logger.info("Testing HRM import...")
    
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path("official_hrm").absolute()))
        
        from models.hrm.hrm_act_v1 import (
            HierarchicalReasoningModel_ACTV1,
            HierarchicalReasoningModel_ACTV1Config,
            HierarchicalReasoningModel_ACTV1Carry
        )
        
        logger.info("✅ Official HRM can be imported successfully!")
        return True
    except ImportError as e:
        logger.error(f"❌ HRM import failed: {e}")
        return False

def main():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("FIXING OFFICIAL HRM SETUP")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Try to install FlashAttention
    logger.info("STEP 1: Installing FlashAttention")
    logger.info("-" * 80)
    flash_attn_installed = install_flash_attention()
    
    if not flash_attn_installed:
        logger.info("")
        logger.info("STEP 2: Creating FlashAttention fallback")
        logger.info("-" * 80)
        create_flash_attention_fallback()
    
    # Step 3: Test HRM import
    logger.info("")
    logger.info("STEP 3: Testing HRM Import")
    logger.info("-" * 80)
    hrm_works = test_hrm_import()
    
    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("SETUP SUMMARY")
    logger.info("=" * 80)
    
    if hrm_works:
        logger.info("✅ SUCCESS: Official HRM is now available!")
        logger.info("   Prometheus will use the true HRM instead of LSTM fallback")
    else:
        logger.warning("⚠️ Official HRM still not available")
        logger.warning("   System will continue using LSTM fallback")
        logger.warning("   You may need to:")
        logger.warning("   1. Install CUDA Toolkit")
        logger.warning("   2. Install FlashAttention manually")
        logger.warning("   3. Check official_hrm directory structure")
    
    return hrm_works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

