#!/usr/bin/env python3
"""
PROMETHEUS Model Pre-Training System
=====================================
Pre-trains AI models on historical data for better initial performance.
Integrates with existing AI Learning Engine.

Features:
- Pre-train models on 5+ years of historical data
- Multiple model types (price prediction, direction classification, risk assessment)
- Performance validation and metrics
- Model versioning and storage
- Integration with existing ai_learning_engine.py
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report, r2_score
import joblib
import json

# Import existing systems
from core.historical_data_pipeline import get_historical_pipeline
from core.ai_learning_engine import AILearningEngine

logger = logging.getLogger(__name__)


class ModelPreTrainingSystem:
    """
    Pre-train AI models on historical data
    Integrates with existing AILearningEngine
    """
    
    def __init__(self, model_dir: str = "pretrained_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        # Use existing historical data pipeline
        self.pipeline = get_historical_pipeline()
        
        # Storage for trained models and metrics
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        
        # Reference to existing AI Learning Engine
        self.ai_learning_engine = None
        
        logger.info(f"🤖 Model Pre-Training System initialized: {self.model_dir}")
    
    async def pretrain_all_models(
        self,
        symbols: List[str],
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """
        Pre-train all AI models on historical data
        
        Args:
            symbols: List of symbols to train on
            start_date: Start date for training data
            end_date: End date for training data
        
        Returns:
            Performance report
        """
        if start_date is None:
            start_date = datetime.now() - timedelta(days=365*5)  # 5 years
        if end_date is None:
            end_date = datetime.now()
        
        logger.info("🚀 Starting comprehensive model pre-training...")
        logger.info(f"  Symbols: {len(symbols)}")
        logger.info(f"  Date range: {start_date.date()} to {end_date.date()}")
        
        # Step 1: Download historical data (if not already downloaded)
        logger.info("\n📥 Step 1: Ensuring historical data is available...")
        data = await self.pipeline.download_historical_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            interval='1d'
        )
        
        # Step 2: Train price prediction models
        logger.info("\n📊 Step 2: Training price prediction models...")
        price_models = await self._train_price_predictors(data)
        
        # Step 3: Train direction classifiers
        logger.info("\n🎯 Step 3: Training direction classifiers...")
        direction_models = await self._train_direction_classifiers(data)
        
        # Step 4: Save all models
        logger.info("\n💾 Step 4: Saving trained models...")
        await self._save_all_models()
        
        # Step 5: Generate report
        logger.info("\n📋 Step 5: Generating performance report...")
        report = self._generate_report()
        
        # Step 6: Integrate with existing AI Learning Engine
        logger.info("\n🔗 Step 6: Integrating with AI Learning Engine...")
        await self._integrate_with_ai_engine()
        
        logger.info("\n[CHECK] Model pre-training complete!")
        logger.info(f"  Total models trained: {len(self.models)}")
        logger.info(f"  Models saved to: {self.model_dir}")
        
        return report
    
    async def _train_price_predictors(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Train price prediction models (regression)"""
        models = {}
        
        for symbol, df in data.items():
            try:
                logger.info(f"  Training price predictor for {symbol}...")
                
                # Calculate features
                df_features = await self.pipeline.calculate_features(df)
                
                # Prepare training data
                X, y = await self.pipeline.prepare_training_data(
                    df_features,
                    target_type='return'
                )
                
                if len(X) < 100:
                    logger.warning(f"    [WARNING]️ Insufficient data for {symbol}, skipping")
                    continue
                
                # Split data (80/20, no shuffle for time series)
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train RandomForest model
                model = RandomForestRegressor(
                    n_estimators=200,
                    max_depth=15,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    random_state=42,
                    n_jobs=-1
                )
                
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                
                # Predictions
                y_pred = model.predict(X_test_scaled)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                
                logger.info(f"    [CHECK] Train R²: {train_score:.3f}, Test R²: {test_score:.3f}, RMSE: {rmse:.4f}")
                
                # Store model and scaler
                model_key = f"{symbol}_price"
                self.models[model_key] = model
                self.scalers[model_key] = scaler
                
                # Store metrics
                self.performance_metrics[model_key] = {
                    'model_type': 'price_prediction',
                    'symbol': symbol,
                    'train_r2': float(train_score),
                    'test_r2': float(test_score),
                    'rmse': float(rmse),
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features': X.shape[1]
                }
                
                models[symbol] = model
                
            except Exception as e:
                logger.error(f"    [ERROR] Error training {symbol}: {e}")
        
        return models
    
    async def _train_direction_classifiers(
        self,
        data: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Train direction classification models"""
        models = {}
        
        for symbol, df in data.items():
            try:
                logger.info(f"  Training direction classifier for {symbol}...")
                
                # Calculate features
                df_features = await self.pipeline.calculate_features(df)
                
                # Prepare training data
                X, y = await self.pipeline.prepare_training_data(
                    df_features,
                    target_type='direction'
                )
                
                if len(X) < 100:
                    logger.warning(f"    [WARNING]️ Insufficient data for {symbol}, skipping")
                    continue
                
                # Split data
                split_idx = int(len(X) * 0.8)
                X_train, X_test = X[:split_idx], X[split_idx:]
                y_train, y_test = y[:split_idx], y[split_idx:]
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train GradientBoosting model
                model = GradientBoostingClassifier(
                    n_estimators=200,
                    learning_rate=0.1,
                    max_depth=8,
                    min_samples_split=10,
                    min_samples_leaf=5,
                    random_state=42
                )
                
                model.fit(X_train_scaled, y_train)
                
                # Evaluate
                train_acc = model.score(X_train_scaled, y_train)
                test_acc = model.score(X_test_scaled, y_test)
                
                logger.info(f"    [CHECK] Train Acc: {train_acc:.3f}, Test Acc: {test_acc:.3f}")
                
                # Store model and scaler
                model_key = f"{symbol}_direction"
                self.models[model_key] = model
                self.scalers[model_key] = scaler
                
                # Store metrics
                self.performance_metrics[model_key] = {
                    'model_type': 'direction_classification',
                    'symbol': symbol,
                    'train_accuracy': float(train_acc),
                    'test_accuracy': float(test_acc),
                    'train_samples': len(X_train),
                    'test_samples': len(X_test),
                    'features': X.shape[1]
                }
                
                models[symbol] = model
                
            except Exception as e:
                logger.error(f"    [ERROR] Error training {symbol}: {e}")
        
        return models
    
    async def _save_all_models(self):
        """Save all trained models and scalers"""
        for model_key, model in self.models.items():
            model_path = self.model_dir / f"{model_key}_model.joblib"
            joblib.dump(model, model_path)
            logger.info(f"  💾 Saved: {model_key}_model.joblib")
        
        for scaler_key, scaler in self.scalers.items():
            scaler_path = self.model_dir / f"{scaler_key}_scaler.joblib"
            joblib.dump(scaler, scaler_path)
            logger.info(f"  💾 Saved: {scaler_key}_scaler.joblib")
        
        # Save performance metrics
        metrics_path = self.model_dir / "performance_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(self.performance_metrics, f, indent=2)
        logger.info(f"  💾 Saved: performance_metrics.json")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(self.models),
            'models_by_type': {},
            'average_performance': {},
            'metrics': self.performance_metrics
        }
        
        # Group by model type
        price_models = [k for k in self.models.keys() if '_price' in k]
        direction_models = [k for k in self.models.keys() if '_direction' in k]
        
        report['models_by_type'] = {
            'price_prediction': len(price_models),
            'direction_classification': len(direction_models)
        }
        
        # Calculate average performance
        if price_models:
            avg_test_r2 = np.mean([
                self.performance_metrics[k]['test_r2']
                for k in price_models
            ])
            report['average_performance']['price_test_r2'] = float(avg_test_r2)
        
        if direction_models:
            avg_test_acc = np.mean([
                self.performance_metrics[k]['test_accuracy']
                for k in direction_models
            ])
            report['average_performance']['direction_test_accuracy'] = float(avg_test_acc)
        
        return report
    
    async def _integrate_with_ai_engine(self):
        """Integrate pre-trained models with existing AI Learning Engine"""
        try:
            # Copy pre-trained models to AI Learning Engine's model directory
            ai_model_dir = Path("ai_models")
            ai_model_dir.mkdir(exist_ok=True)
            
            # Copy models
            for model_file in self.model_dir.glob("*.joblib"):
                target_file = ai_model_dir / model_file.name
                import shutil
                shutil.copy(model_file, target_file)
                logger.info(f"  🔗 Copied {model_file.name} to AI Learning Engine")
            
            logger.info("  [CHECK] Integration with AI Learning Engine complete")
            
        except Exception as e:
            logger.error(f"  [ERROR] Error integrating with AI Learning Engine: {e}")


# Global instance
_pretraining_system = None

def get_pretraining_system() -> ModelPreTrainingSystem:
    """Get global pre-training system instance"""
    global _pretraining_system
    if _pretraining_system is None:
        _pretraining_system = ModelPreTrainingSystem()
    return _pretraining_system
