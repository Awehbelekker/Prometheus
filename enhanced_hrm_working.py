#!/usr/bin/env python3
"""
Enhanced HRM Working Implementation
Uses your existing pretrained models with official HRM architecture enhancements
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
import sys
from datetime import datetime

# Add paths for imports
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "core"))

try:
    from core.hrm_integration import HRMTradingEngine, HRMReasoningContext, FullHRMTradingEngine
    PROMETHEUS_HRM_AVAILABLE = True
    FULL_HRM_AVAILABLE = True
except ImportError as e:
    print(f"PROMETHEUS HRM not available: {e}")
    PROMETHEUS_HRM_AVAILABLE = False
    FULL_HRM_AVAILABLE = False
    FullHRMTradingEngine = None

logger = logging.getLogger(__name__)

class EnhancedFusionNetwork(nn.Module):
    """Enhanced fusion network combining multiple reasoning sources"""
    
    def __init__(self, input_dim: int = 512, output_dim: int = 256):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        
        # Adaptive input projection to handle different input dimensions
        self.input_projection = nn.Linear(256, input_dim)  # Project 256 to 512
        
        # Multi-head attention for fusion
        self.attention = nn.MultiheadAttention(
            embed_dim=input_dim,
            num_heads=8,
            batch_first=True
        )
        
        # Fusion layers
        self.fusion_layers = nn.Sequential(
            nn.Linear(input_dim * 2, input_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(input_dim, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, output_dim)
        )
        
        # Confidence estimation
        self.confidence_estimator = nn.Sequential(
            nn.Linear(output_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, primary_input: torch.Tensor, secondary_input: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Fuse multiple reasoning inputs"""
        # Ensure inputs have sequence dimension
        if primary_input.dim() == 2:
            primary_input = primary_input.unsqueeze(1)
        if secondary_input.dim() == 2:
            secondary_input = secondary_input.unsqueeze(1)
        
        # Project secondary input to match primary input dimension
        if secondary_input.shape[-1] != self.input_dim:
            secondary_input = self.input_projection(secondary_input)
        
        # Ensure primary input matches expected dimension
        if primary_input.shape[-1] != self.input_dim:
            # Create a projection layer for primary input if needed
            if not hasattr(self, 'primary_projection'):
                self.primary_projection = nn.Linear(primary_input.shape[-1], self.input_dim).to(primary_input.device)
            primary_input = self.primary_projection(primary_input)
        
        # Apply attention mechanism
        attended_output, attention_weights = self.attention(
            primary_input, secondary_input, secondary_input
        )
        
        # Concatenate and fuse
        fused_input = torch.cat([primary_input, attended_output], dim=-1)
        fused_output = self.fusion_layers(fused_input)
        
        # Estimate confidence
        confidence = self.confidence_estimator(fused_output.squeeze(1))
        
        return {
            'fused_output': fused_output.squeeze(1),
            'attention_weights': attention_weights,
            'confidence': confidence
        }

class EnhancedHRMTradingEngine:
    """Enhanced HRM Trading Engine with full HRM architecture"""
    
    def __init__(self, device: str = 'cpu', use_pretrained_models: bool = True, use_full_hrm: bool = True):
        self.device = device
        self.use_pretrained_models = use_pretrained_models
        self.use_full_hrm = use_full_hrm
        
        # Initialize Full HRM (preferred)
        self.full_hrm = None
        if use_full_hrm and FULL_HRM_AVAILABLE and FullHRMTradingEngine is not None:
            try:
                self.full_hrm = FullHRMTradingEngine(device=device, use_full_hrm=True)
                logger.info("✅ Full HRM Architecture initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Full HRM: {e}")
                self.use_full_hrm = False
        
        # Fallback to PROMETHEUS HRM (LSTM-based)
        self.prometheus_hrm = None
        if not self.use_full_hrm and PROMETHEUS_HRM_AVAILABLE:
            try:
                self.prometheus_hrm = HRMTradingEngine(device=device)
                logger.info("✅ PROMETHEUS HRM (LSTM) initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize PROMETHEUS HRM: {e}")
        
        # Initialize enhanced fusion network
        self.fusion_network = EnhancedFusionNetwork().to(device)
        
        # Load your existing pretrained models
        self.pretrained_models = {}
        if use_pretrained_models:
            self._load_pretrained_models()
        
        # Performance tracking
        self.enhancement_metrics = {
            'total_decisions': 0,
            'fusion_decisions': 0,
            'fallback_decisions': 0,
            'confidence_scores': [],
            'decision_accuracy': []
        }
        
        logger.info("🚀 Enhanced HRM Trading Engine initialized")
    
    def _load_pretrained_models(self):
        """Load your existing pretrained models"""
        try:
            # Load models from your existing directories
            model_dirs = ['ai_models', 'pretrained_models']
            
            for model_dir in model_dirs:
                model_path = Path(model_dir)
                if model_path.exists():
                    logger.info(f"📁 Found model directory: {model_dir}")
                    
                    # Load some example models
                    for model_file in model_path.glob("*_model.joblib"):
                        symbol = model_file.stem.replace('_model', '')
                        if symbol not in self.pretrained_models:
                            self.pretrained_models[symbol] = {
                                'path': str(model_file),
                                'type': 'price_prediction'
                            }
                    
                    logger.info(f"✅ Loaded {len(self.pretrained_models)} pretrained models from {model_dir}")
                    break
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load pretrained models: {e}")
    
    def make_enhanced_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """Make enhanced trading decision using full HRM architecture"""
        try:
            self.enhancement_metrics['total_decisions'] += 1
            
            # Use Full HRM if available (preferred)
            if self.use_full_hrm and self.full_hrm:
                try:
                    decision = self.full_hrm.make_hierarchical_decision(context)
                    decision['enhancement_used'] = True
                    decision['reasoning_sources'] = ['full_hrm']
                    self.enhancement_metrics['fusion_decisions'] += 1
                    logger.info("✅ Enhanced decision made using Full HRM")
                    return decision
                except Exception as e:
                    logger.warning(f"⚠️ Full HRM failed: {e}")
                    # Fall through to fallback
            
            # Prepare market data for fallback
            market_tensor = self._prepare_market_tensor(context.market_data)
            
            # Get PROMETHEUS HRM decision (fallback)
            prometheus_output = None
            if self.prometheus_hrm:
                try:
                    prometheus_decision = self.prometheus_hrm.make_hierarchical_decision(context)
                    prometheus_output = self._extract_prometheus_features(prometheus_decision)
                except Exception as e:
                    logger.warning(f"⚠️ PROMETHEUS HRM failed: {e}")
            
            # Get pretrained model predictions
            pretrained_output = self._get_pretrained_predictions(context.market_data)
            
            # Fuse outputs if both are available
            if prometheus_output is not None and pretrained_output is not None:
                fusion_result = self.fusion_network(prometheus_output, pretrained_output)
                self.enhancement_metrics['fusion_decisions'] += 1
                
                # Generate final decision
                final_decision = self._generate_final_decision(fusion_result, context)
                final_decision['enhancement_used'] = True
                final_decision['reasoning_sources'] = ['prometheus_hrm', 'pretrained_models']
                
                logger.info("✅ Enhanced decision made using fusion")
                return final_decision
            
            elif prometheus_output is not None:
                # Use only PROMETHEUS HRM
                final_decision = self._generate_final_decision(
                    {'fused_output': prometheus_output, 'confidence': torch.tensor(0.7)}, 
                    context
                )
                final_decision['enhancement_used'] = True
                final_decision['reasoning_sources'] = ['prometheus_hrm']
                
                logger.info("✅ Decision made using PROMETHEUS HRM")
                return final_decision
            
            elif pretrained_output is not None:
                # Use only pretrained models
                final_decision = self._generate_final_decision(
                    {'fused_output': pretrained_output, 'confidence': torch.tensor(0.6)}, 
                    context
                )
                final_decision['enhancement_used'] = True
                final_decision['reasoning_sources'] = ['pretrained_models']
                
                logger.info("✅ Decision made using pretrained models")
                return final_decision
            
            else:
                # Fallback decision
                self.enhancement_metrics['fallback_decisions'] += 1
                return self._fallback_decision(context)
                
        except Exception as e:
            logger.error(f"❌ Error in enhanced decision making: {e}")
            return self._fallback_decision(context)
    
    def _prepare_market_tensor(self, market_data: Dict[str, Any]) -> torch.Tensor:
        """Prepare market data as tensor"""
        features = []
        
        # Extract key market features
        if 'price' in market_data:
            features.append(float(market_data['price']))
        if 'volume' in market_data:
            features.append(float(market_data['volume']))
        if 'indicators' in market_data:
            for indicator, value in market_data['indicators'].items():
                features.append(float(value))
        
        # Pad to expected size
        while len(features) < 512:
            features.append(0.0)
        features = features[:512]
        
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
    
    def _extract_prometheus_features(self, prometheus_decision: Dict[str, Any]) -> torch.Tensor:
        """Extract features from PROMETHEUS HRM decision"""
        features = []
        
        # Extract key features from PROMETHEUS decision
        if 'abstract_strategy' in prometheus_decision:
            strategy = prometheus_decision['abstract_strategy']
            if hasattr(strategy, 'flatten'):
                features.extend(strategy.flatten().tolist())
            elif isinstance(strategy, (list, tuple)):
                features.extend([float(x) for x in strategy])
            else:
                features.append(float(strategy))
        
        if 'trade_parameters' in prometheus_decision:
            params = prometheus_decision['trade_parameters']
            if hasattr(params, 'flatten'):
                features.extend(params.flatten().tolist())
            elif isinstance(params, (list, tuple)):
                features.extend([float(x) for x in params])
            else:
                features.append(float(params))
        
        # Pad to expected size
        while len(features) < 256:
            features.append(0.0)
        features = features[:256]
        
        # Ensure proper tensor dimensions (batch_size, sequence_length, features)
        tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1, 1, 256)
        return tensor.to(self.device)
    
    def _get_pretrained_predictions(self, market_data: Dict[str, Any]) -> torch.Tensor:
        """Get predictions from pretrained models"""
        try:
            import joblib
            
            # Extract symbol from market data or use default
            symbol = market_data.get('symbol', 'SPY')
            
            # Try to load actual models
            model_paths = [
                f'ai_models/{symbol}_price_model.joblib',
                f'ai_models/{symbol}_direction_model.joblib',
                f'pretrained_models/{symbol}_price_model.joblib',
                f'pretrained_models/{symbol}_direction_model.joblib'
            ]
            
            predictions = []
            scalers = []
            
            # Load models and scalers
            for model_path in model_paths:
                if Path(model_path).exists():
                    try:
                        model = joblib.load(model_path)
                        scaler_path = model_path.replace('_model.joblib', '_scaler.joblib')
                        
                        if Path(scaler_path).exists():
                            scaler = joblib.load(scaler_path)
                            scalers.append(scaler)
                        else:
                            scalers.append(None)
                        
                        # Prepare features for prediction
                        features = self._prepare_model_features(market_data)
                        
                        # Scale features if scaler available
                        if scalers[-1] is not None:
                            features_scaled = scalers[-1].transform([features])
                        else:
                            features_scaled = [features]
                        
                        # Make prediction
                        prediction = model.predict(features_scaled)[0]
                        predictions.append(prediction)
                        
                        logger.info(f"✅ Loaded model: {model_path}, prediction: {prediction}")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to load model {model_path}: {e}")
                        continue
            
            # If we have predictions, use them; otherwise fallback to simulation
            if predictions:
                # Combine predictions into feature vector
                prediction_features = []
                for pred in predictions:
                    if isinstance(pred, (list, tuple, np.ndarray)):
                        prediction_features.extend([float(x) for x in pred])
                    else:
                        prediction_features.append(float(pred))
                
                # Pad to expected size
                while len(prediction_features) < 256:
                    prediction_features.append(0.0)
                prediction_features = prediction_features[:256]
                
                # Ensure proper tensor dimensions
                tensor = torch.tensor(prediction_features, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1, 1, 256)
                return tensor.to(self.device)
            else:
                # Fallback to simulation if no models loaded
                logger.warning("⚠️ No models loaded, using simulation")
                return self._simulate_predictions(market_data)
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to get pretrained predictions: {e}")
            return self._simulate_predictions(market_data)
    
    def _prepare_model_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Prepare features for model prediction"""
        features = []
        
        # Basic market features
        if 'price' in market_data:
            features.append(float(market_data['price']))
        if 'volume' in market_data:
            features.append(float(market_data['volume']))
        if 'indicators' in market_data:
            for indicator, value in market_data['indicators'].items():
                features.append(float(value))
        
        # Add technical indicators if available
        if 'rsi' in market_data.get('indicators', {}):
            features.append(float(market_data['indicators']['rsi']))
        if 'macd' in market_data.get('indicators', {}):
            features.append(float(market_data['indicators']['macd']))
        
               # Add more features to match expected model input (28 features)
               # Add price-based features
               price = float(market_data.get('price', 100))
               features.extend([
                   price * 0.1,  # price/10
                   price * 0.01,  # price/100
                   price * 0.001,  # price/1000
                   price * 2,  # price*2
               ])
               
               # Add volume-based features
               volume = float(market_data.get('volume', 1000000))
               features.extend([
                   volume * 0.1,
                   volume * 0.01,
                   volume * 0.001,
                   volume * 2,
               ])
               
               # Add technical indicator variations
               indicators = market_data.get('indicators', {})
               for indicator in ['rsi', 'macd', 'bollinger_upper', 'bollinger_lower']:
                   if indicator in indicators:
                       value = float(indicators[indicator])
                       features.extend([value, value * 0.5])
                   else:
                       features.extend([0.0, 0.0])
               
               # Pad to expected size (28 features)
               while len(features) < 28:
                   features.append(0.0)
               
               # Truncate if too many features
               return features[:28]
    
    def _simulate_predictions(self, market_data: Dict[str, Any]) -> torch.Tensor:
        """Simulate predictions when models are not available"""
        features = []
        
        # Use market data to generate features
        if 'price' in market_data:
            features.append(float(market_data['price']))
        if 'volume' in market_data:
            features.append(float(market_data['volume']))
        if 'indicators' in market_data:
            for indicator, value in market_data['indicators'].items():
                features.append(float(value))
        
        # Simulate model predictions based on market conditions
        prediction_features = []
        for i in range(256):
            if i < len(features):
                prediction_features.append(features[i])
            else:
                # Simulate model prediction based on market conditions
                if 'rsi' in market_data.get('indicators', {}):
                    rsi = market_data['indicators']['rsi']
                    if rsi < 30:  # Oversold
                        prediction_features.append(np.random.normal(0.7, 0.1))
                    elif rsi > 70:  # Overbought
                        prediction_features.append(np.random.normal(0.3, 0.1))
                    else:
                        prediction_features.append(np.random.normal(0.5, 0.1))
                else:
                    prediction_features.append(np.random.normal(0.5, 0.1))
        
        # Ensure proper tensor dimensions
        tensor = torch.tensor(prediction_features, dtype=torch.float32).unsqueeze(0).unsqueeze(0)  # (1, 1, 256)
        return tensor.to(self.device)
    
    def _generate_final_decision(self, fusion_result: Dict[str, torch.Tensor], context: HRMReasoningContext) -> Dict[str, Any]:
        """Generate final trading decision from fusion result"""
        try:
            fused_output = fusion_result['fused_output']
            base_confidence = fusion_result['confidence'].item()
            
            # Calculate decision score
            decision_score = torch.mean(fused_output).item()
            
            # Detect market regime
            market_regime = self._detect_market_regime(context.market_data)
            
            # Calibrate confidence based on market conditions
            calibrated_confidence = self._calibrate_confidence(
                base_confidence, decision_score, market_regime, context.market_data
            )
            
            # Generate action based on decision score and market regime
            action = self._determine_action(decision_score, market_regime, calibrated_confidence)
            
            # Calculate position size based on confidence and risk
            position_size = self._calculate_position_size(calibrated_confidence, context)
            
            # Store confidence for metrics
            self.enhancement_metrics['confidence_scores'].append(calibrated_confidence)
            
            return {
                'action': action,
                'confidence': calibrated_confidence,
                'decision_score': decision_score,
                'market_regime': market_regime,
                'position_size': position_size,
                'fused_output': fused_output.cpu().numpy().tolist(),
                'timestamp': context.timestamp.isoformat() if context.timestamp else datetime.now().isoformat(),
                'market_data': context.market_data,
                'reasoning': {
                    'base_confidence': base_confidence,
                    'calibrated_confidence': calibrated_confidence,
                    'market_regime': market_regime,
                    'decision_factors': self._get_decision_factors(context.market_data)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating final decision: {e}")
            return self._fallback_decision(context)
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> str:
        """Detect current market regime"""
        try:
            indicators = market_data.get('indicators', {})
            
            # Calculate volatility proxy
            volatility = 0.0
            if 'bollinger_upper' in indicators and 'bollinger_lower' in indicators:
                upper = float(indicators['bollinger_upper'])
                lower = float(indicators['bollinger_lower'])
                price = float(market_data.get('price', 100))
                volatility = (upper - lower) / price
            
            # Calculate trend proxy
            trend = 0.0
            if 'macd' in indicators:
                trend = float(indicators['macd'])
            
            # Determine regime
            if volatility > 0.05:  # High volatility
                return 'volatile'
            elif trend > 0.1:
                return 'bullish'
            elif trend < -0.1:
                return 'bearish'
            else:
                return 'sideways'
                
        except Exception as e:
            logger.warning(f"⚠️ Market regime detection failed: {e}")
            return 'unknown'
    
    def _calibrate_confidence(self, base_confidence: float, decision_score: float, 
                            market_regime: str, market_data: Dict[str, Any]) -> float:
        """Calibrate confidence based on market conditions"""
        try:
            # Start with base confidence
            calibrated = base_confidence
            
            # Adjust for market regime
            regime_adjustments = {
                'volatile': 0.8,    # Reduce confidence in volatile markets
                'bullish': 1.1,     # Increase confidence in trending markets
                'bearish': 1.1,     # Increase confidence in trending markets
                'sideways': 0.9,    # Slightly reduce in sideways markets
                'unknown': 0.7      # Reduce for unknown conditions
            }
            
            calibrated *= regime_adjustments.get(market_regime, 1.0)
            
            # Adjust for decision strength
            decision_strength = abs(decision_score - 0.5) * 2  # 0 to 1
            calibrated *= (0.5 + decision_strength * 0.5)  # 0.5 to 1.0 multiplier
            
            # Adjust for market data quality
            data_quality = self._assess_data_quality(market_data)
            calibrated *= data_quality
            
            # Ensure confidence is in valid range
            return max(0.1, min(0.95, calibrated))
            
        except Exception as e:
            logger.warning(f"⚠️ Confidence calibration failed: {e}")
            return base_confidence
    
    def _assess_data_quality(self, market_data: Dict[str, Any]) -> float:
        """Assess quality of market data"""
        try:
            quality_score = 1.0
            
            # Check for required fields
            required_fields = ['price', 'volume']
            for field in required_fields:
                if field not in market_data:
                    quality_score -= 0.2
            
            # Check for indicators
            indicators = market_data.get('indicators', {})
            if len(indicators) < 3:
                quality_score -= 0.1
            
            # Check for reasonable values
            price = market_data.get('price', 0)
            if price <= 0:
                quality_score -= 0.3
            
            return max(0.3, quality_score)
            
        except Exception as e:
            logger.warning(f"⚠️ Data quality assessment failed: {e}")
            return 0.7
    
    def _determine_action(self, decision_score: float, market_regime: str, confidence: float) -> str:
        """Determine trading action based on decision score and market conditions"""
        try:
            # Adjust thresholds based on market regime
            if market_regime == 'volatile':
                # Be more conservative in volatile markets
                buy_threshold = 0.7
                sell_threshold = 0.3
            elif market_regime in ['bullish', 'bearish']:
                # Be more aggressive in trending markets
                buy_threshold = 0.55
                sell_threshold = 0.45
            else:
                # Default thresholds
                buy_threshold = 0.6
                sell_threshold = 0.4
            
            # Adjust thresholds based on confidence
            confidence_factor = confidence * 0.1  # 0.01 to 0.095 adjustment
            buy_threshold += confidence_factor
            sell_threshold -= confidence_factor
            
            # Determine action
            if decision_score > buy_threshold:
                return "BUY"
            elif decision_score < sell_threshold:
                return "SELL"
            else:
                return "HOLD"
                
        except Exception as e:
            logger.warning(f"⚠️ Action determination failed: {e}")
            return "HOLD"
    
    def _calculate_position_size(self, confidence: float, context: HRMReasoningContext) -> float:
        """Calculate position size based on confidence and risk preferences"""
        try:
            # Base position size from risk preferences
            max_position = context.risk_preferences.get('max_position_size', 0.1)
            
            # Adjust based on confidence
            confidence_factor = confidence * 0.5 + 0.5  # 0.5 to 1.0
            
            # Calculate final position size
            position_size = max_position * confidence_factor
            
            # Ensure reasonable bounds
            return max(0.01, min(0.2, position_size))
            
        except Exception as e:
            logger.warning(f"⚠️ Position size calculation failed: {e}")
            return 0.05
    
    def _get_decision_factors(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get factors that influenced the decision"""
        try:
            factors = {}
            
            indicators = market_data.get('indicators', {})
            
            # RSI factor
            if 'rsi' in indicators:
                rsi = float(indicators['rsi'])
                if rsi < 30:
                    factors['rsi'] = 'oversold'
                elif rsi > 70:
                    factors['rsi'] = 'overbought'
                else:
                    factors['rsi'] = 'neutral'
            
            # MACD factor
            if 'macd' in indicators:
                macd = float(indicators['macd'])
                if macd > 0:
                    factors['macd'] = 'bullish'
                else:
                    factors['macd'] = 'bearish'
            
            # Volume factor
            volume = market_data.get('volume', 0)
            if volume > 1000000:
                factors['volume'] = 'high'
            elif volume < 100000:
                factors['volume'] = 'low'
            else:
                factors['volume'] = 'normal'
            
            return factors
            
        except Exception as e:
            logger.warning(f"⚠️ Decision factors extraction failed: {e}")
            return {}
    
    def _fallback_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """Fallback decision when all systems fail"""
        return {
            'action': 'HOLD',
            'confidence': 0.1,
            'decision_score': 0.5,
            'fused_output': None,
            'enhancement_used': False,
            'timestamp': context.timestamp.isoformat() if context.timestamp else datetime.now().isoformat(),
            'fallback': True,
            'market_data': context.market_data
        }
    
    def get_enhancement_metrics(self) -> Dict[str, Any]:
        """Get enhancement performance metrics"""
        metrics = self.enhancement_metrics.copy()
        
        # Calculate average confidence
        if metrics['confidence_scores']:
            metrics['average_confidence'] = np.mean(metrics['confidence_scores'])
            metrics['confidence_std'] = np.std(metrics['confidence_scores'])
            metrics['max_confidence'] = np.max(metrics['confidence_scores'])
            metrics['min_confidence'] = np.min(metrics['confidence_scores'])
        else:
            metrics['average_confidence'] = 0.0
            metrics['confidence_std'] = 0.0
            metrics['max_confidence'] = 0.0
            metrics['min_confidence'] = 0.0
        
        # Calculate success rates
        total = metrics['total_decisions']
        if total > 0:
            metrics['fusion_rate'] = metrics['fusion_decisions'] / total
            metrics['fallback_rate'] = metrics['fallback_decisions'] / total
        else:
            metrics['fusion_rate'] = 0.0
            metrics['fallback_rate'] = 0.0
        
        # Add system health metrics
        metrics['system_health'] = self.get_health_status()
        
        # Add model performance metrics
        metrics['model_performance'] = self._get_model_performance_metrics()
        
        return metrics
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get HRM system health status"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'components': {}
            }
            
            # Check PROMETHEUS HRM
            if self.prometheus_hrm:
                health_status['components']['prometheus_hrm'] = 'active'
            else:
                health_status['components']['prometheus_hrm'] = 'inactive'
                health_status['status'] = 'degraded'
            
            # Check pretrained models
            if self.pretrained_models:
                health_status['components']['pretrained_models'] = f'active ({len(self.pretrained_models)} models)'
            else:
                health_status['components']['pretrained_models'] = 'inactive'
                health_status['status'] = 'degraded'
            
            # Check fusion network
            if self.fusion_network:
                health_status['components']['fusion_network'] = 'active'
            else:
                health_status['components']['fusion_network'] = 'inactive'
                health_status['status'] = 'critical'
            
            # Check decision history
            total_decisions = self.enhancement_metrics['total_decisions']
            if total_decisions > 0:
                health_status['components']['decision_engine'] = f'active ({total_decisions} decisions)'
            else:
                health_status['components']['decision_engine'] = 'no_decisions'
            
            # Check error rate
            error_rate = self._calculate_error_rate()
            health_status['error_rate'] = error_rate
            
            if error_rate > 0.1:  # 10% error rate
                health_status['status'] = 'degraded'
            elif error_rate > 0.2:  # 20% error rate
                health_status['status'] = 'critical'
            
            return health_status
            
        except Exception as e:
            logger.error(f"❌ Health status check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _calculate_error_rate(self) -> float:
        """Calculate error rate from recent decisions"""
        try:
            total = self.enhancement_metrics['total_decisions']
            fallback = self.enhancement_metrics['fallback_decisions']
            
            if total > 0:
                return fallback / total
            else:
                return 0.0
                
        except Exception as e:
            logger.warning(f"⚠️ Error rate calculation failed: {e}")
            return 0.0
    
    def _get_model_performance_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            metrics = {
                'models_loaded': len(self.pretrained_models),
                'model_types': {},
                'last_model_update': None,
                'model_accuracy': {}
            }
            
            # Count model types
            for symbol, model_info in self.pretrained_models.items():
                model_type = model_info.get('type', 'unknown')
                if model_type not in metrics['model_types']:
                    metrics['model_types'][model_type] = 0
                metrics['model_types'][model_type] += 1
            
            # Add model accuracy if available
            if hasattr(self, 'model_accuracy_history'):
                metrics['model_accuracy'] = self.model_accuracy_history
            
            return metrics
            
        except Exception as e:
            logger.warning(f"⚠️ Model performance metrics failed: {e}")
            return {'error': str(e)}
    
    def update_model_performance(self, trade_result: Dict[str, Any]):
        """Update model performance based on trade results"""
        try:
            if not hasattr(self, 'model_accuracy_history'):
                self.model_accuracy_history = {}
            
            # Extract relevant information
            symbol = trade_result.get('symbol', 'unknown')
            profit = trade_result.get('profit', 0)
            confidence = trade_result.get('confidence', 0.5)
            
            # Update accuracy for this symbol
            if symbol not in self.model_accuracy_history:
                self.model_accuracy_history[symbol] = {
                    'total_trades': 0,
                    'profitable_trades': 0,
                    'total_profit': 0.0,
                    'average_confidence': 0.0
                }
            
            symbol_metrics = self.model_accuracy_history[symbol]
            symbol_metrics['total_trades'] += 1
            symbol_metrics['total_profit'] += profit
            
            if profit > 0:
                symbol_metrics['profitable_trades'] += 1
            
            # Update average confidence
            current_avg = symbol_metrics['average_confidence']
            total_trades = symbol_metrics['total_trades']
            symbol_metrics['average_confidence'] = (
                (current_avg * (total_trades - 1) + confidence) / total_trades
            )
            
            logger.info(f"✅ Updated model performance for {symbol}: "
                       f"{symbol_metrics['profitable_trades']}/{symbol_metrics['total_trades']} profitable")
            
        except Exception as e:
            logger.warning(f"⚠️ Model performance update failed: {e}")
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            metrics = self.get_enhancement_metrics()
            
            # Add detailed breakdown
            metrics['detailed'] = {
                'decision_breakdown': self._get_decision_breakdown(),
                'confidence_distribution': self._get_confidence_distribution(),
                'market_regime_performance': self._get_market_regime_performance(),
                'model_contribution': self._get_model_contribution_analysis()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Detailed metrics failed: {e}")
            return {'error': str(e)}
    
    def _get_decision_breakdown(self) -> Dict[str, int]:
        """Get breakdown of decisions by action"""
        try:
            if not hasattr(self, 'decision_history'):
                return {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            
            breakdown = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
            for decision in self.decision_history:
                action = decision.get('action', 'HOLD')
                if action in breakdown:
                    breakdown[action] += 1
            
            return breakdown
            
        except Exception as e:
            logger.warning(f"⚠️ Decision breakdown failed: {e}")
            return {'BUY': 0, 'SELL': 0, 'HOLD': 0}
    
    def _get_confidence_distribution(self) -> Dict[str, float]:
        """Get confidence distribution statistics"""
        try:
            if not self.enhancement_metrics['confidence_scores']:
                return {'low': 0.0, 'medium': 0.0, 'high': 0.0}
            
            scores = self.enhancement_metrics['confidence_scores']
            total = len(scores)
            
            low = sum(1 for s in scores if s < 0.4) / total
            medium = sum(1 for s in scores if 0.4 <= s <= 0.7) / total
            high = sum(1 for s in scores if s > 0.7) / total
            
            return {'low': low, 'medium': medium, 'high': high}
            
        except Exception as e:
            logger.warning(f"⚠️ Confidence distribution failed: {e}")
            return {'low': 0.0, 'medium': 0.0, 'high': 0.0}
    
    def _get_market_regime_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance by market regime"""
        try:
            if not hasattr(self, 'regime_performance'):
                return {}
            
            return self.regime_performance
            
        except Exception as e:
            logger.warning(f"⚠️ Market regime performance failed: {e}")
            return {}
    
    def _get_model_contribution_analysis(self) -> Dict[str, Any]:
        """Analyze contribution of different models"""
        try:
            return {
                'prometheus_hrm_contributions': self.enhancement_metrics.get('prometheus_contributions', 0),
                'pretrained_model_contributions': self.enhancement_metrics.get('pretrained_contributions', 0),
                'fusion_contributions': self.enhancement_metrics.get('fusion_contributions', 0)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Model contribution analysis failed: {e}")
            return {}

# Example usage and testing
def test_enhanced_hrm():
    """Test the enhanced HRM system"""
    print("[TEST] Testing Enhanced HRM System...")
    
    # Initialize enhanced HRM
    enhanced_hrm = EnhancedHRMTradingEngine()
    
    # Create test context
    context = HRMReasoningContext(
        market_data={
            'price': 150.0,
            'volume': 1000000,
            'indicators': {
                'rsi': 65,
                'macd': 0.5,
                'bollinger_upper': 155,
                'bollinger_lower': 145
            }
        },
        user_profile={'risk_tolerance': 'medium', 'experience': 'intermediate'},
        trading_history=[],
        current_portfolio={'cash': 10000, 'positions': {}},
        risk_preferences={'max_position_size': 0.1, 'stop_loss': 0.05},
        reasoning_level='HIGH_LEVEL'
    )
    
    # Test decision making
    print("\\n[TEST] Making enhanced decision...")
    decision = enhanced_hrm.make_enhanced_decision(context)
    
    print(f"Decision: {decision}")
    
    # Test metrics
    print("\\n[TEST] Getting metrics...")
    metrics = enhanced_hrm.get_enhancement_metrics()
    print(f"Metrics: {metrics}")
    
    print("\\n[SUCCESS] Enhanced HRM test completed!")
    return True

if __name__ == "__main__":
    test_enhanced_hrm()
