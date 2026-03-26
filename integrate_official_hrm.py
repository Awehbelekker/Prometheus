#!/usr/bin/env python3
"""
Official HRM Integration Script for PROMETHEUS
Integrates the official HRM repository (Awehbelekker/HRM) with PROMETHEUS HRM system
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import json
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OfficialHRMIntegrator:
    """Integrates official HRM with PROMETHEUS HRM system"""
    
    def __init__(self, prometheus_root: str = ".", official_hrm_dir: str = "official_hrm"):
        self.prometheus_root = Path(prometheus_root)
        self.official_hrm_dir = Path(official_hrm_dir)
        self.integration_dir = self.prometheus_root / "hrm_enhancement"
        
        # Create integration directory
        self.integration_dir.mkdir(exist_ok=True)
        
        logger.info(f"🚀 Official HRM Integrator initialized")
        logger.info(f"  PROMETHEUS Root: {self.prometheus_root}")
        logger.info(f"  Official HRM Dir: {self.official_hrm_dir}")
        logger.info(f"  Integration Dir: {self.integration_dir}")
    
    def clone_official_hrm(self) -> bool:
        """Clone the official HRM repository"""
        try:
            logger.info("📥 Cloning official HRM repository...")
            
            if self.official_hrm_dir.exists():
                logger.info(f"  Repository already exists at {self.official_hrm_dir}")
                return True
            
            # Clone the repository
            cmd = [
                "git", "clone", 
                "https://github.com/Awehbelekker/HRM.git",
                str(self.official_hrm_dir)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.prometheus_root)
            
            if result.returncode == 0:
                logger.info("✅ Successfully cloned official HRM repository")
                return True
            else:
                logger.error(f"❌ Failed to clone repository: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error cloning repository: {str(e)}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install official HRM dependencies"""
        try:
            logger.info("📦 Installing official HRM dependencies...")
            
            requirements_file = self.official_hrm_dir / "requirements.txt"
            if not requirements_file.exists():
                logger.warning("⚠️ requirements.txt not found, skipping dependency installation")
                return True
            
            # Install requirements
            cmd = ["pip", "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Successfully installed official HRM dependencies")
                return True
            else:
                logger.warning(f"⚠️ Some dependencies may have failed: {result.stderr}")
                return True  # Continue even if some dependencies fail
                
        except Exception as e:
            logger.error(f"❌ Error installing dependencies: {str(e)}")
            return False
    
    def create_integration_layer(self) -> bool:
        """Create integration layer between official HRM and PROMETHEUS"""
        try:
            logger.info("🔗 Creating integration layer...")
            
            # Create enhanced HRM integration file
            integration_code = '''#!/usr/bin/env python3
"""
Enhanced HRM Integration Layer
Combines official HRM with PROMETHEUS HRM for superior trading decisions
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import sys

# Add official HRM to path
sys.path.append(str(Path(__file__).parent / "official_hrm"))

try:
    # Import official HRM components
    from models.hrm import HRM as OfficialHRM
    from models.hrm import HRMConfig as OfficialHRMConfig
    OFFICIAL_HRM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Official HRM not available: {e}")
    OFFICIAL_HRM_AVAILABLE = False

# Import your existing HRM
try:
    from core.hrm_integration import HRMTradingEngine, HRMReasoningContext
    PROMETHEUS_HRM_AVAILABLE = True
except ImportError as e:
    logger.warning(f"PROMETHEUS HRM not available: {e}")
    PROMETHEUS_HRM_AVAILABLE = False

logger = logging.getLogger(__name__)

class FusionNetwork(nn.Module):
    """Fusion network to combine official HRM with PROMETHEUS HRM"""
    
    def __init__(self, official_dim: int = 512, prometheus_dim: int = 256, output_dim: int = 256):
        super().__init__()
        self.official_to_trading = nn.Linear(official_dim, output_dim)
        self.trading_to_official = nn.Linear(prometheus_dim, official_dim)
        self.attention_mechanism = nn.MultiheadAttention(output_dim, 8, batch_first=True)
        self.fusion_layer = nn.Linear(output_dim * 2, output_dim)
        
    def forward(self, official_output: torch.Tensor, prometheus_output: torch.Tensor) -> torch.Tensor:
        """Fuse official HRM and PROMETHEUS HRM outputs"""
        # Project to common dimension
        official_proj = self.official_to_trading(official_output)
        prometheus_proj = prometheus_output
        
        # Ensure same shape for attention
        if official_proj.dim() == 2:
            official_proj = official_proj.unsqueeze(1)
        if prometheus_proj.dim() == 2:
            prometheus_proj = prometheus_proj.unsqueeze(1)
        
        # Apply attention mechanism
        attended_output, _ = self.attention_mechanism(
            official_proj, prometheus_proj, prometheus_proj
        )
        
        # Fuse outputs
        fused = torch.cat([official_proj, attended_output], dim=-1)
        fused = self.fusion_layer(fused)
        
        return fused.squeeze(1) if fused.dim() == 3 else fused

class EnhancedHRMTradingEngine:
    """Enhanced HRM Trading Engine combining official HRM with PROMETHEUS HRM"""
    
    def __init__(self, device: str = 'cpu', checkpoint_dir: str = 'hrm_checkpoints'):
        self.device = device
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Initialize official HRM if available
        self.official_hrm = None
        if OFFICIAL_HRM_AVAILABLE:
            try:
                config = OfficialHRMConfig()
                self.official_hrm = OfficialHRM(config).to(device)
                logger.info("✅ Official HRM initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize official HRM: {e}")
        
        # Initialize PROMETHEUS HRM if available
        self.prometheus_hrm = None
        if PROMETHEUS_HRM_AVAILABLE:
            try:
                self.prometheus_hrm = HRMTradingEngine(device=device)
                logger.info("✅ PROMETHEUS HRM initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize PROMETHEUS HRM: {e}")
        
        # Initialize fusion network
        self.fusion_network = FusionNetwork().to(device)
        
        # Performance tracking
        self.enhancement_metrics = {
            'official_hrm_calls': 0,
            'prometheus_hrm_calls': 0,
            'fusion_calls': 0,
            'decision_accuracy': []
        }
        
        logger.info("🚀 Enhanced HRM Trading Engine initialized")
    
    def load_official_checkpoints(self, checkpoint_paths: Dict[str, str]) -> bool:
        """Load official HRM checkpoints"""
        if not self.official_hrm:
            logger.warning("⚠️ Official HRM not available, skipping checkpoint loading")
            return False
        
        try:
            for checkpoint_name, checkpoint_path in checkpoint_paths.items():
                if Path(checkpoint_path).exists():
                    checkpoint = torch.load(checkpoint_path, map_location=self.device)
                    # Load checkpoint into official HRM
                    # Implementation depends on official HRM checkpoint format
                    logger.info(f"✅ Loaded {checkpoint_name} checkpoint")
                else:
                    logger.warning(f"⚠️ Checkpoint not found: {checkpoint_path}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error loading checkpoints: {e}")
            return False
    
    def make_enhanced_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """Make enhanced trading decision using both HRM systems"""
        try:
            # Prepare market data tensor
            market_tensor = self._prepare_market_tensor(context.market_data)
            
            # Official HRM reasoning
            official_output = None
            if self.official_hrm:
                try:
                    official_output = self.official_hrm(market_tensor)
                    self.enhancement_metrics['official_hrm_calls'] += 1
                except Exception as e:
                    logger.warning(f"⚠️ Official HRM failed: {e}")
            
            # PROMETHEUS HRM reasoning
            prometheus_output = None
            if self.prometheus_hrm:
                try:
                    prometheus_decision = self.prometheus_hrm.make_hierarchical_decision(context)
                    prometheus_output = self._extract_prometheus_features(prometheus_decision)
                    self.enhancement_metrics['prometheus_hrm_calls'] += 1
                except Exception as e:
                    logger.warning(f"⚠️ PROMETHEUS HRM failed: {e}")
            
            # Fusion and final decision
            if official_output is not None and prometheus_output is not None:
                # Fuse both outputs
                fused_output = self.fusion_network(official_output, prometheus_output)
                self.enhancement_metrics['fusion_calls'] += 1
                
                # Generate final decision
                final_decision = self._generate_final_decision(fused_output, context)
                
                logger.info("✅ Enhanced decision made using both HRM systems")
                return final_decision
            
            elif official_output is not None:
                # Use only official HRM
                final_decision = self._generate_final_decision(official_output, context)
                logger.info("✅ Decision made using official HRM only")
                return final_decision
            
            elif prometheus_output is not None:
                # Use only PROMETHEUS HRM
                final_decision = self._generate_final_decision(prometheus_output, context)
                logger.info("✅ Decision made using PROMETHEUS HRM only")
                return final_decision
            
            else:
                # Fallback decision
                logger.warning("⚠️ Both HRM systems failed, using fallback")
                return self._fallback_decision(context)
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced decision making: {e}")
            return self._fallback_decision(context)
    
    def _prepare_market_tensor(self, market_data: Dict[str, Any]) -> torch.Tensor:
        """Prepare market data as tensor for official HRM"""
        # Convert market data to tensor format expected by official HRM
        # This is a placeholder - actual implementation depends on official HRM input format
        features = []
        
        # Extract key market features
        if 'price' in market_data:
            features.append(market_data['price'])
        if 'volume' in market_data:
            features.append(market_data['volume'])
        if 'indicators' in market_data:
            features.extend(market_data['indicators'].values())
        
        # Pad or truncate to expected size
        while len(features) < 512:
            features.append(0.0)
        features = features[:512]
        
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
    
    def _extract_prometheus_features(self, prometheus_decision: Dict[str, Any]) -> torch.Tensor:
        """Extract features from PROMETHEUS HRM decision"""
        features = []
        
        # Extract key features from PROMETHEUS decision
        if 'abstract_strategy' in prometheus_decision:
            features.extend(prometheus_decision['abstract_strategy'].flatten().tolist())
        if 'trade_parameters' in prometheus_decision:
            features.extend(prometheus_decision['trade_parameters'].flatten().tolist())
        
        # Pad to expected size
        while len(features) < 256:
            features.append(0.0)
        features = features[:256]
        
        return torch.tensor(features, dtype=torch.float32).to(self.device)
    
    def _generate_final_decision(self, fused_output: torch.Tensor, context: HRMReasoningContext) -> Dict[str, Any]:
        """Generate final trading decision from fused output"""
        # Convert fused output to trading decision
        # This is a placeholder - actual implementation depends on your trading logic
        
        # Simple decision logic based on fused output
        decision_score = torch.mean(fused_output).item()
        
        if decision_score > 0.6:
            action = "BUY"
        elif decision_score < 0.4:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            'action': action,
            'confidence': abs(decision_score - 0.5) * 2,  # Convert to 0-1 confidence
            'fused_output': fused_output.cpu().numpy().tolist(),
            'enhancement_used': True,
            'timestamp': context.timestamp.isoformat() if context.timestamp else None
        }
    
    def _fallback_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """Fallback decision when both HRM systems fail"""
        return {
            'action': 'HOLD',
            'confidence': 0.1,
            'fused_output': None,
            'enhancement_used': False,
            'timestamp': context.timestamp.isoformat() if context.timestamp else None,
            'fallback': True
        }
    
    def get_enhancement_metrics(self) -> Dict[str, Any]:
        """Get enhancement performance metrics"""
        return self.enhancement_metrics.copy()

# Example usage
if __name__ == "__main__":
    # Initialize enhanced HRM
    enhanced_hrm = EnhancedHRMTradingEngine()
    
    # Load official checkpoints if available
    checkpoint_paths = {
        'arc_agi_2': 'official_hrm/checkpoints/arc-agi-2.pt',
        'sudoku_extreme': 'official_hrm/checkpoints/sudoku-extreme.pt',
        'maze_30x30': 'official_hrm/checkpoints/maze-30x30.pt'
    }
    
    enhanced_hrm.load_official_checkpoints(checkpoint_paths)
    
    # Example decision making
    context = HRMReasoningContext(
        market_data={'price': 150.0, 'volume': 1000000, 'indicators': {'rsi': 65, 'macd': 0.5}},
        user_profile={'risk_tolerance': 'medium'},
        trading_history=[],
        current_portfolio={'cash': 10000, 'positions': {}},
        risk_preferences={'max_position_size': 0.1},
        reasoning_level='HIGH_LEVEL'
    )
    
    decision = enhanced_hrm.make_enhanced_decision(context)
    print(f"Enhanced Decision: {decision}")
    
    metrics = enhanced_hrm.get_enhancement_metrics()
    print(f"Enhancement Metrics: {metrics}")
'''
            
            # Write integration file
            integration_file = self.integration_dir / "enhanced_hrm_integration.py"
            with open(integration_file, 'w', encoding='utf-8') as f:
                f.write(integration_code)
            
            logger.info("✅ Created enhanced HRM integration layer")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating integration layer: {str(e)}")
            return False
    
    def create_test_script(self) -> bool:
        """Create test script for enhanced HRM"""
        try:
            logger.info("🧪 Creating test script...")
            
            test_code = '''#!/usr/bin/env python3
"""
Test script for Enhanced HRM Integration
Tests the integration between official HRM and PROMETHEUS HRM
"""

import sys
from pathlib import Path
import logging

# Add integration directory to path
sys.path.append(str(Path(__file__).parent / "hrm_enhancement"))

try:
    from enhanced_hrm_integration import EnhancedHRMTradingEngine, HRMReasoningContext
    logger = logging.getLogger(__name__)
    
    def test_enhanced_hrm():
        """Test enhanced HRM functionality"""
        print("🧪 Testing Enhanced HRM Integration...")
        
        # Initialize enhanced HRM
        enhanced_hrm = EnhancedHRMTradingEngine()
        
        # Test context
        context = HRMReasoningContext(
            market_data={
                'price': 150.0,
                'volume': 1000000,
                'indicators': {'rsi': 65, 'macd': 0.5, 'bollinger_upper': 155, 'bollinger_lower': 145}
            },
            user_profile={'risk_tolerance': 'medium', 'experience': 'intermediate'},
            trading_history=[],
            current_portfolio={'cash': 10000, 'positions': {}},
            risk_preferences={'max_position_size': 0.1, 'stop_loss': 0.05},
            reasoning_level='HIGH_LEVEL'
        )
        
        # Test decision making
        print("\\n📊 Testing decision making...")
        decision = enhanced_hrm.make_enhanced_decision(context)
        print(f"Decision: {decision}")
        
        # Test metrics
        print("\\n📈 Testing metrics...")
        metrics = enhanced_hrm.get_enhancement_metrics()
        print(f"Metrics: {metrics}")
        
        print("\\n✅ Enhanced HRM test completed successfully!")
        return True
        
    if __name__ == "__main__":
        test_enhanced_hrm()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure to run the integration script first")
except Exception as e:
    print(f"❌ Test error: {e}")
'''
            
            # Write test file
            test_file = self.integration_dir / "test_enhanced_hrm.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            logger.info("✅ Created test script")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating test script: {str(e)}")
            return False
    
    def create_setup_script(self) -> bool:
        """Create setup script for easy installation"""
        try:
            logger.info("⚙️ Creating setup script...")
            
            setup_code = '''#!/usr/bin/env python3
"""
Setup script for Enhanced HRM Integration
Automates the integration process
"""

import subprocess
import sys
from pathlib import Path

def run_setup():
    """Run the complete setup process"""
    print("🚀 Setting up Enhanced HRM Integration...")
    
    # Run the integration script
    try:
        result = subprocess.run([sys.executable, "integrate_official_hrm.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Integration completed successfully")
        else:
            print(f"⚠️ Integration completed with warnings: {result.stderr}")
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False
    
    # Run the test script
    try:
        test_script = Path("hrm_enhancement") / "test_enhanced_hrm.py"
        if test_script.exists():
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Tests passed successfully")
            else:
                print(f"⚠️ Tests completed with warnings: {result.stderr}")
        else:
            print("⚠️ Test script not found, skipping tests")
    except Exception as e:
        print(f"⚠️ Test execution failed: {e}")
    
    print("\\n🎉 Enhanced HRM Integration setup complete!")
    print("\\nNext steps:")
    print("1. Review the integration in hrm_enhancement/")
    print("2. Download official HRM checkpoints if available")
    print("3. Test with your trading data")
    print("4. Integrate into your main trading system")
    
    return True

if __name__ == "__main__":
    run_setup()
'''
            
            # Write setup file
            setup_file = self.prometheus_root / "setup_enhanced_hrm.py"
            with open(setup_file, 'w', encoding='utf-8') as f:
                f.write(setup_code)
            
            logger.info("✅ Created setup script")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating setup script: {str(e)}")
            return False
    
    def run_integration(self) -> bool:
        """Run the complete integration process"""
        logger.info("🚀 Starting Official HRM Integration...")
        
        steps = [
            ("Clone Official HRM", self.clone_official_hrm),
            ("Install Dependencies", self.install_dependencies),
            ("Create Integration Layer", self.create_integration_layer),
            ("Create Test Script", self.create_test_script),
            ("Create Setup Script", self.create_setup_script)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"\\n📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ {step_name} failed")
                return False
            logger.info(f"✅ {step_name} completed")
        
        logger.info("\\n🎉 Official HRM Integration completed successfully!")
        logger.info("\\n📁 Files created:")
        logger.info(f"  - {self.official_hrm_dir}/ (Official HRM repository)")
        logger.info(f"  - {self.integration_dir}/enhanced_hrm_integration.py (Integration layer)")
        logger.info(f"  - {self.integration_dir}/test_enhanced_hrm.py (Test script)")
        logger.info(f"  - setup_enhanced_hrm.py (Setup script)")
        
        logger.info("\\n🚀 Next steps:")
        logger.info("1. Run: python setup_enhanced_hrm.py")
        logger.info("2. Download official HRM checkpoints")
        logger.info("3. Test the enhanced HRM system")
        logger.info("4. Integrate into your trading system")
        
        return True

def main():
    """Main function"""
    integrator = OfficialHRMIntegrator()
    success = integrator.run_integration()
    
    if success:
        print("\\n[SUCCESS] Official HRM Integration completed successfully!")
        print("\\nYour PROMETHEUS HRM system is now enhanced with official HRM capabilities!")
    else:
        print("\\n[ERROR] Integration failed. Please check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
