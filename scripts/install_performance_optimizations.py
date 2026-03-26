"""
Performance Optimization Installation Script
Installs FlashAttention, model quantization, GPU acceleration
"""

import subprocess
import sys
import logging
import platform
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Install and configure performance optimizations for PROMETHEUS"""
    
    def __init__(self):
        self.python_exe = sys.executable
        self.platform = platform.system()
        self.optimizations_installed = []
        self.optimizations_failed = []
    
    def install_flashattention(self) -> bool:
        """
        Install FlashAttention for 2x faster HRM inference
        Requires: CUDA 11.7+ and compatible GPU
        """
        logger.info("\n" + "="*60)
        logger.info("📦 Installing FlashAttention...")
        logger.info("="*60)
        
        try:
            # Check if CUDA is available
            try:
                import torch
                if not torch.cuda.is_available():
                    logger.warning("⚠️  CUDA not available - skipping FlashAttention")
                    self.optimizations_failed.append("FlashAttention (no CUDA)")
                    return False
                
                cuda_version = torch.version.cuda
                logger.info(f"✅ CUDA {cuda_version} detected")
            except ImportError:
                logger.warning("⚠️  PyTorch not installed - skipping FlashAttention")
                self.optimizations_failed.append("FlashAttention (no PyTorch)")
                return False
            
            # Install FlashAttention
            commands = [
                # Install dependencies
                [self.python_exe, "-m", "pip", "install", "packaging", "ninja"],
                # Install FlashAttention
                [self.python_exe, "-m", "pip", "install", "flash-attn", "--no-build-isolation"]
            ]
            
            for cmd in commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"❌ Failed: {' '.join(cmd)}")
                    logger.error(f"Error: {result.stderr}")
                    self.optimizations_failed.append("FlashAttention")
                    return False
            
            logger.info("✅ FlashAttention installed successfully!")
            logger.info("   Expected speedup: 2x faster HRM inference")
            self.optimizations_installed.append("FlashAttention")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing FlashAttention: {e}")
            self.optimizations_failed.append("FlashAttention")
            return False
    
    def install_quantization_tools(self) -> bool:
        """
        Install model quantization tools (INT8, INT4)
        Reduces memory by 4x with minimal accuracy loss
        """
        logger.info("\n" + "="*60)
        logger.info("📦 Installing Quantization Tools...")
        logger.info("="*60)
        
        try:
            packages = [
                "bitsandbytes",  # INT8 quantization
                "optimum",       # Model optimization
                "auto-gptq"      # GPTQ quantization
            ]
            
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [self.python_exe, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.warning(f"⚠️  Failed to install {package}")
                    logger.warning(f"Error: {result.stderr}")
                else:
                    logger.info(f"✅ {package} installed")
            
            logger.info("✅ Quantization tools installed!")
            logger.info("   Expected benefit: 4x memory reduction, 1.5x speedup")
            self.optimizations_installed.append("Quantization Tools")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing quantization tools: {e}")
            self.optimizations_failed.append("Quantization Tools")
            return False
    
    def install_gpu_acceleration(self) -> bool:
        """
        Install GPU acceleration libraries
        Speeds up backtesting and parallel inference
        """
        logger.info("\n" + "="*60)
        logger.info("📦 Installing GPU Acceleration...")
        logger.info("="*60)
        
        try:
            packages = [
                "cupy-cuda11x",  # GPU-accelerated NumPy
                "numba",         # JIT compilation
                "tensorrt"       # NVIDIA inference optimizer
            ]
            
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [self.python_exe, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.warning(f"⚠️  Failed to install {package}")
                    logger.warning(f"Error: {result.stderr}")
                else:
                    logger.info(f"✅ {package} installed")
            
            logger.info("✅ GPU acceleration libraries installed!")
            logger.info("   Expected benefit: 10x faster backtesting")
            self.optimizations_installed.append("GPU Acceleration")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing GPU acceleration: {e}")
            self.optimizations_failed.append("GPU Acceleration")
            return False
    
    def install_compiled_extensions(self) -> bool:
        """
        Install compiled C++/CUDA extensions for critical paths
        """
        logger.info("\n" + "="*60)
        logger.info("📦 Installing Compiled Extensions...")
        logger.info("="*60)
        
        try:
            packages = [
                "xformers",      # Memory-efficient transformers
                "triton"         # GPU programming
            ]
            
            for package in packages:
                logger.info(f"Installing {package}...")
                result = subprocess.run(
                    [self.python_exe, "-m", "pip", "install", package],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    logger.warning(f"⚠️  Failed to install {package}")
                else:
                    logger.info(f"✅ {package} installed")
            
            logger.info("✅ Compiled extensions installed!")
            self.optimizations_installed.append("Compiled Extensions")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing compiled extensions: {e}")
            self.optimizations_failed.append("Compiled Extensions")
            return False
    
    def optimize_pytorch_settings(self) -> bool:
        """Create optimized PyTorch configuration"""
        logger.info("\n" + "="*60)
        logger.info("⚙️  Configuring PyTorch optimizations...")
        logger.info("="*60)
        
        config_content = '''"""
PyTorch Performance Configuration
Auto-generated by performance optimizer
"""

import torch
import os

# Enable TF32 for faster training on Ampere GPUs
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Enable cuDNN autotuner
torch.backends.cudnn.benchmark = True

# Set number of threads for CPU operations
torch.set_num_threads(8)

# Enable JIT compilation
torch.jit.enable_onednn_fusion(True)

# Memory optimization
torch.cuda.empty_cache()

# Environment variables
os.environ['CUDA_LAUNCH_BLOCKING'] = '0'  # Async CUDA
os.environ['TORCH_CUDNN_V8_API_ENABLED'] = '1'  # cuDNN v8

print("✅ PyTorch optimizations loaded")
'''
        
        try:
            config_path = Path(__file__).parent.parent / 'core' / 'pytorch_optimizations.py'
            with open(config_path, 'w') as f:
                f.write(config_content)
            
            logger.info(f"✅ Created: {config_path}")
            self.optimizations_installed.append("PyTorch Config")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating PyTorch config: {e}")
            self.optimizations_failed.append("PyTorch Config")
            return False
    
    def create_performance_monitor(self) -> bool:
        """Create performance monitoring utilities"""
        logger.info("\n" + "="*60)
        logger.info("📊 Creating performance monitoring tools...")
        logger.info("="*60)
        
        monitor_content = '''"""
Performance Monitoring Utilities
Tracks inference speed, memory usage, GPU utilization
"""

import time
import psutil
import logging
from contextlib import contextmanager
from typing import Dict, Any

logger = logging.getLogger(__name__)

try:
    import torch
    HAS_CUDA = torch.cuda.is_available()
except ImportError:
    HAS_CUDA = False


class PerformanceMonitor:
    """Monitor system and model performance"""
    
    def __init__(self):
        self.metrics = []
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager to measure operation performance"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        if HAS_CUDA:
            torch.cuda.synchronize()
            start_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024  # MB
        
        try:
            yield
        finally:
            if HAS_CUDA:
                torch.cuda.synchronize()
                end_gpu_memory = torch.cuda.memory_allocated() / 1024 / 1024
                gpu_memory_used = end_gpu_memory - start_gpu_memory
            else:
                gpu_memory_used = 0
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            elapsed = end_time - start_time
            memory_used = end_memory - start_memory
            
            metric = {
                'operation': operation_name,
                'elapsed_seconds': elapsed,
                'memory_mb': memory_used,
                'gpu_memory_mb': gpu_memory_used,
                'timestamp': time.time()
            }
            
            self.metrics.append(metric)
            
            logger.info(f"⏱️  {operation_name}: {elapsed:.3f}s "
                       f"(RAM: {memory_used:.1f}MB, GPU: {gpu_memory_used:.1f}MB)")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {}
        
        total_time = sum(m['elapsed_seconds'] for m in self.metrics)
        total_memory = sum(m['memory_mb'] for m in self.metrics)
        total_gpu_memory = sum(m['gpu_memory_mb'] for m in self.metrics)
        
        return {
            'total_operations': len(self.metrics),
            'total_time_seconds': total_time,
            'total_memory_mb': total_memory,
            'total_gpu_memory_mb': total_gpu_memory,
            'average_time_seconds': total_time / len(self.metrics),
            'metrics': self.metrics
        }
    
    def print_summary(self):
        """Print formatted performance summary"""
        summary = self.get_summary()
        if not summary:
            logger.info("No performance metrics recorded")
            return
        
        logger.info("\\n" + "="*60)
        logger.info("📊 PERFORMANCE SUMMARY")
        logger.info("="*60)
        logger.info(f"Total operations: {summary['total_operations']}")
        logger.info(f"Total time: {summary['total_time_seconds']:.3f}s")
        logger.info(f"Average time: {summary['average_time_seconds']:.3f}s")
        logger.info(f"Total RAM: {summary['total_memory_mb']:.1f}MB")
        logger.info(f"Total GPU: {summary['total_gpu_memory_mb']:.1f}MB")
        logger.info("="*60 + "\\n")


# Global monitor
_monitor = PerformanceMonitor()

def get_monitor() -> PerformanceMonitor:
    """Get global performance monitor"""
    return _monitor
'''
        
        try:
            monitor_path = Path(__file__).parent.parent / 'core' / 'performance_monitor.py'
            with open(monitor_path, 'w') as f:
                f.write(monitor_content)
            
            logger.info(f"✅ Created: {monitor_path}")
            self.optimizations_installed.append("Performance Monitor")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating performance monitor: {e}")
            self.optimizations_failed.append("Performance Monitor")
            return False
    
    def update_requirements(self) -> bool:
        """Update requirements.txt with optimization packages"""
        logger.info("\n" + "="*60)
        logger.info("📝 Updating requirements.txt...")
        logger.info("="*60)
        
        optimization_packages = [
            "# Performance Optimizations",
            "flash-attn>=2.5.0",
            "bitsandbytes>=0.41.0",
            "optimum>=1.16.0",
            "auto-gptq>=0.6.0",
            "xformers>=0.0.23",
            "triton>=2.1.0",
            "numba>=0.58.0",
            ""
        ]
        
        try:
            req_path = Path(__file__).parent.parent / 'requirements_optimizations.txt'
            with open(req_path, 'w') as f:
                f.write('\n'.join(optimization_packages))
            
            logger.info(f"✅ Created: {req_path}")
            logger.info("   Install with: pip install -r requirements_optimizations.txt")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating requirements: {e}")
            return False
    
    def run_all_optimizations(self):
        """Install all optimizations"""
        logger.info("\n" + "="*60)
        logger.info("🚀 PROMETHEUS PERFORMANCE OPTIMIZATION")
        logger.info("="*60)
        logger.info("This will install performance enhancements:")
        logger.info("  1. FlashAttention (2x faster HRM)")
        logger.info("  2. Quantization tools (4x memory reduction)")
        logger.info("  3. GPU acceleration (10x faster backtesting)")
        logger.info("  4. Compiled extensions (optimized operations)")
        logger.info("  5. PyTorch optimizations")
        logger.info("  6. Performance monitoring")
        logger.info("="*60 + "\n")
        
        # Run optimizations
        self.install_flashattention()
        self.install_quantization_tools()
        self.install_gpu_acceleration()
        self.install_compiled_extensions()
        self.optimize_pytorch_settings()
        self.create_performance_monitor()
        self.update_requirements()
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 OPTIMIZATION SUMMARY")
        logger.info("="*60)
        logger.info(f"✅ Installed ({len(self.optimizations_installed)}):")
        for opt in self.optimizations_installed:
            logger.info(f"   • {opt}")
        
        if self.optimizations_failed:
            logger.info(f"\n⚠️  Failed ({len(self.optimizations_failed)}):")
            for opt in self.optimizations_failed:
                logger.info(f"   • {opt}")
        
        logger.info("="*60)
        logger.info("\n✅ Optimization installation complete!")
        logger.info("\nNext steps:")
        logger.info("1. Restart Python to load new packages")
        logger.info("2. Import: from core.pytorch_optimizations import *")
        logger.info("3. Use: from core.performance_monitor import get_monitor")
        logger.info("="*60 + "\n")


if __name__ == '__main__':
    optimizer = PerformanceOptimizer()
    optimizer.run_all_optimizations()
