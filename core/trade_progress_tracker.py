#!/usr/bin/env python3
"""
Trade Progress Tracking System
Comprehensive tracking and visualization of trade progress for users
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import numpy as np
import pandas as pd
from core.persistence_manager import get_persistence_manager

logger = logging.getLogger(__name__)

@dataclass
class TradeProgress:
    """Detailed trade progress information"""
    trade_id: str
    user_id: str
    symbol: str
    side: str
    entry_price: float
    current_price: float
    quantity: float
    unrealized_pnl: float
    realized_pnl: float
    total_pnl: float
    pnl_percentage: float
    duration: timedelta
    status: str
    milestones: List[Dict[str, Any]]
    price_alerts: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    ai_insights: List[str]
    risk_metrics: Dict[str, float]

@dataclass
class PortfolioProgress:
    """Overall portfolio progress"""
    user_id: str
    total_value: float
    total_pnl: float
    total_pnl_percentage: float
    active_trades_count: int
    completed_trades_count: int
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    daily_pnl: List[Dict[str, Any]]
    sector_allocation: Dict[str, float]
    risk_exposure: Dict[str, float]

@dataclass
class TradeMilestone:
    """Trade milestone or achievement"""
    milestone_id: str
    trade_id: str
    milestone_type: str  # 'profit_target', 'stop_loss', 'time_based', 'price_level'
    description: str
    achieved_at: datetime
    price_at_achievement: float
    pnl_at_achievement: float
    significance: str  # 'minor', 'major', 'critical'

class TradeProgressTracker:
    """
    Comprehensive trade progress tracking system
    Provides detailed insights and visualizations for user trades
    """
    
    def __init__(self):
        self.persistence = get_persistence_manager()
        self.active_trackers: Dict[str, TradeProgress] = {}
        self.portfolio_trackers: Dict[str, PortfolioProgress] = {}
        self.milestones: Dict[str, List[TradeMilestone]] = {}
        self.is_tracking = False
        
        # Load existing progress data
        self._load_existing_progress()
    
    def _load_existing_progress(self):
        """Load existing progress data from database"""
        try:
            # Load active trade progress
            progress_data = self.persistence.load_system_state('trade_progress')
            if progress_data:
                for data in progress_data:
                    progress = TradeProgress(**data)
                    self.active_trackers[progress.trade_id] = progress
            
            # Load portfolio progress
            portfolio_data = self.persistence.load_system_state('portfolio_progress')
            if portfolio_data:
                for data in portfolio_data:
                    portfolio = PortfolioProgress(**data)
                    self.portfolio_trackers[portfolio.user_id] = portfolio
            
            logger.info(f"Loaded progress for {len(self.active_trackers)} trades and {len(self.portfolio_trackers)} portfolios")
            
        except Exception as e:
            logger.error(f"Failed to load existing progress: {e}")
    
    async def start_tracking(self):
        """Start the trade progress tracking system"""
        if self.is_tracking:
            logger.warning("Trade progress tracking is already running")
            return
        
        self.is_tracking = True
        logger.info("Starting trade progress tracking...")
        
        # Start tracking tasks
        asyncio.create_task(self._progress_updater())
        asyncio.create_task(self._milestone_detector())
        asyncio.create_task(self._portfolio_analyzer())
        asyncio.create_task(self._alert_manager())
        
        logger.info("Trade progress tracking started successfully")
    
    async def stop_tracking(self):
        """Stop the trade progress tracking system"""
        logger.info("Stopping trade progress tracking...")
        self.is_tracking = False
        
        # Save all progress data
        await self._save_all_progress()
        
        logger.info("Trade progress tracking stopped")
    
    async def add_trade_tracking(self, trade_data: Dict[str, Any]) -> str:
        """Add a new trade to progress tracking"""
        try:
            trade_id = trade_data['trade_id']
            
            # Create initial progress tracking
            progress = TradeProgress(
                trade_id=trade_id,
                user_id=trade_data['user_id'],
                symbol=trade_data['symbol'],
                side=trade_data['side'],
                entry_price=trade_data['entry_price'],
                current_price=trade_data['entry_price'],
                quantity=trade_data['quantity'],
                unrealized_pnl=0.0,
                realized_pnl=0.0,
                total_pnl=0.0,
                pnl_percentage=0.0,
                duration=timedelta(0),
                status='active',
                milestones=[],
                price_alerts=[],
                performance_metrics={},
                ai_insights=[],
                risk_metrics={}
            )
            
            self.active_trackers[trade_id] = progress
            
            # Initialize milestones
            await self._initialize_trade_milestones(trade_data)
            
            # Update portfolio tracking
            await self._update_portfolio_tracking(trade_data['user_id'])
            
            logger.info(f"Started tracking progress for trade {trade_id}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to add trade tracking: {e}")
            raise
    
    async def _initialize_trade_milestones(self, trade_data: Dict[str, Any]):
        """Initialize milestones for a new trade"""
        try:
            trade_id = trade_data['trade_id']
            entry_price = trade_data['entry_price']
            
            milestones = []
            
            # Price-based milestones
            if trade_data['side'] == 'buy':
                # Profit targets
                for pct in [5, 10, 20, 50]:
                    target_price = entry_price * (1 + pct / 100)
                    milestone = TradeMilestone(
                        milestone_id=f"{trade_id}_profit_{pct}",
                        trade_id=trade_id,
                        milestone_type='profit_target',
                        description=f"{pct}% profit target",
                        achieved_at=None,
                        price_at_achievement=target_price,
                        pnl_at_achievement=0.0,
                        significance='minor' if pct <= 10 else 'major'
                    )
                    milestones.append(milestone)
                
                # Stop loss levels
                for pct in [5, 10, 15]:
                    stop_price = entry_price * (1 - pct / 100)
                    milestone = TradeMilestone(
                        milestone_id=f"{trade_id}_stop_{pct}",
                        trade_id=trade_id,
                        milestone_type='stop_loss',
                        description=f"{pct}% stop loss",
                        achieved_at=None,
                        price_at_achievement=stop_price,
                        pnl_at_achievement=0.0,
                        significance='critical'
                    )
                    milestones.append(milestone)
            
            else:  # sell
                # Similar logic for sell trades
                for pct in [5, 10, 20, 50]:
                    target_price = entry_price * (1 - pct / 100)
                    milestone = TradeMilestone(
                        milestone_id=f"{trade_id}_profit_{pct}",
                        trade_id=trade_id,
                        milestone_type='profit_target',
                        description=f"{pct}% profit target",
                        achieved_at=None,
                        price_at_achievement=target_price,
                        pnl_at_achievement=0.0,
                        significance='minor' if pct <= 10 else 'major'
                    )
                    milestones.append(milestone)
            
            # Time-based milestones
            time_milestones = [
                ('1_hour', timedelta(hours=1), 'minor'),
                ('1_day', timedelta(days=1), 'minor'),
                ('1_week', timedelta(weeks=1), 'major'),
                ('1_month', timedelta(days=30), 'major')
            ]
            
            for name, duration, significance in time_milestones:
                milestone = TradeMilestone(
                    milestone_id=f"{trade_id}_time_{name}",
                    trade_id=trade_id,
                    milestone_type='time_based',
                    description=f"Trade held for {name.replace('_', ' ')}",
                    achieved_at=None,
                    price_at_achievement=0.0,
                    pnl_at_achievement=0.0,
                    significance=significance
                )
                milestones.append(milestone)
            
            # Store milestones
            self.milestones[trade_id] = milestones
            
        except Exception as e:
            logger.error(f"Failed to initialize trade milestones: {e}")
    
    async def update_trade_progress(self, trade_id: str, current_price: float, timestamp: datetime):
        """Update progress for a specific trade"""
        try:
            if trade_id not in self.active_trackers:
                return
            
            progress = self.active_trackers[trade_id]
            
            # Update basic metrics
            progress.current_price = current_price
            progress.duration = timestamp - datetime.fromisoformat(
                self.persistence.load_user_trades(progress.user_id)[0]['created_at']
            )
            
            # Calculate P&L
            if progress.side == 'buy':
                progress.unrealized_pnl = (current_price - progress.entry_price) * progress.quantity
            else:  # sell
                progress.unrealized_pnl = (progress.entry_price - current_price) * progress.quantity
            
            progress.total_pnl = progress.unrealized_pnl + progress.realized_pnl
            progress.pnl_percentage = (progress.total_pnl / (progress.entry_price * progress.quantity)) * 100
            
            # Update performance metrics
            progress.performance_metrics = await self._calculate_performance_metrics(progress)
            
            # Update risk metrics
            progress.risk_metrics = await self._calculate_risk_metrics(progress)
            
            # Generate AI insights
            progress.ai_insights = await self._generate_ai_insights(progress)
            
            # Check for milestone achievements
            await self._check_milestone_achievements(trade_id, current_price, timestamp)
            
            # Save progress
            await self._save_trade_progress(progress)
            
        except Exception as e:
            logger.error(f"Failed to update trade progress for {trade_id}: {e}")
    
    async def _calculate_performance_metrics(self, progress: TradeProgress) -> Dict[str, float]:
        """Calculate detailed performance metrics for a trade"""
        try:
            metrics = {}
            
            # Basic metrics
            metrics['return_percentage'] = progress.pnl_percentage
            metrics['return_absolute'] = progress.total_pnl
            metrics['duration_hours'] = progress.duration.total_seconds() / 3600
            
            # Risk-adjusted metrics
            entry_value = progress.entry_price * progress.quantity
            metrics['risk_reward_ratio'] = abs(progress.total_pnl) / (entry_value * 0.02)  # Assuming 2% risk
            
            # Efficiency metrics
            if progress.duration.total_seconds() > 0:
                metrics['pnl_per_hour'] = progress.total_pnl / (progress.duration.total_seconds() / 3600)
                metrics['return_per_day'] = (progress.pnl_percentage / max(1, progress.duration.days)) if progress.duration.days > 0 else progress.pnl_percentage
            
            # Volatility metrics (would need price history)
            metrics['price_volatility'] = 0.0  # Placeholder
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate performance metrics: {e}")
            return {}
    
    async def _calculate_risk_metrics(self, progress: TradeProgress) -> Dict[str, float]:
        """Calculate risk metrics for a trade"""
        try:
            metrics = {}
            
            # Position size risk
            entry_value = progress.entry_price * progress.quantity
            metrics['position_size'] = entry_value
            
            # Drawdown risk
            max_favorable = max(0, progress.total_pnl) if progress.total_pnl >= 0 else 0
            current_drawdown = max_favorable - progress.total_pnl
            metrics['current_drawdown'] = current_drawdown
            metrics['max_drawdown_pct'] = (current_drawdown / entry_value) * 100 if entry_value > 0 else 0
            
            # Time risk
            metrics['time_exposure_hours'] = progress.duration.total_seconds() / 3600
            
            # Price risk (distance from entry)
            price_change_pct = abs(progress.current_price - progress.entry_price) / progress.entry_price * 100
            metrics['price_deviation_pct'] = price_change_pct
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate risk metrics: {e}")
            return {}
    
    async def _generate_ai_insights(self, progress: TradeProgress) -> List[str]:
        """Generate AI-powered insights for a trade"""
        try:
            insights = []
            
            # Performance insights
            if progress.pnl_percentage > 10:
                insights.append(f"🎉 Excellent performance! Trade is up {progress.pnl_percentage:.1f}%")
            elif progress.pnl_percentage > 5:
                insights.append(f"📈 Good progress! Trade is up {progress.pnl_percentage:.1f}%")
            elif progress.pnl_percentage < -5:
                insights.append(f"[WARNING]️ Trade is down {abs(progress.pnl_percentage):.1f}%. Consider risk management.")
            
            # Duration insights
            if progress.duration.days > 7:
                insights.append(f"⏰ Long-term position held for {progress.duration.days} days")
            elif progress.duration.total_seconds() < 3600:
                insights.append("[LIGHTNING] Short-term position - consider scalping strategy")
            
            # Risk insights
            if progress.risk_metrics.get('max_drawdown_pct', 0) > 10:
                insights.append("🔴 High drawdown detected - consider position sizing")
            
            # Volatility insights
            price_deviation = progress.risk_metrics.get('price_deviation_pct', 0)
            if price_deviation > 15:
                insights.append(f"📊 High volatility: {price_deviation:.1f}% price movement")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate AI insights: {e}")
            return []
    
    async def _check_milestone_achievements(self, trade_id: str, current_price: float, timestamp: datetime):
        """Check if any milestones have been achieved"""
        try:
            if trade_id not in self.milestones:
                return
            
            progress = self.active_trackers[trade_id]
            milestones = self.milestones[trade_id]
            
            for milestone in milestones:
                if milestone.achieved_at is not None:
                    continue  # Already achieved
                
                achieved = False
                
                if milestone.milestone_type == 'profit_target':
                    if progress.side == 'buy' and current_price >= milestone.price_at_achievement:
                        achieved = True
                    elif progress.side == 'sell' and current_price <= milestone.price_at_achievement:
                        achieved = True
                
                elif milestone.milestone_type == 'stop_loss':
                    if progress.side == 'buy' and current_price <= milestone.price_at_achievement:
                        achieved = True
                    elif progress.side == 'sell' and current_price >= milestone.price_at_achievement:
                        achieved = True
                
                elif milestone.milestone_type == 'time_based':
                    # Extract duration from milestone_id
                    if '1_hour' in milestone.milestone_id and progress.duration >= timedelta(hours=1):
                        achieved = True
                    elif '1_day' in milestone.milestone_id and progress.duration >= timedelta(days=1):
                        achieved = True
                    elif '1_week' in milestone.milestone_id and progress.duration >= timedelta(weeks=1):
                        achieved = True
                    elif '1_month' in milestone.milestone_id and progress.duration >= timedelta(days=30):
                        achieved = True
                
                if achieved:
                    milestone.achieved_at = timestamp
                    milestone.price_at_achievement = current_price
                    milestone.pnl_at_achievement = progress.total_pnl
                    
                    # Add to progress milestones
                    progress.milestones.append({
                        'type': milestone.milestone_type,
                        'description': milestone.description,
                        'achieved_at': timestamp.isoformat(),
                        'price': current_price,
                        'pnl': progress.total_pnl,
                        'significance': milestone.significance
                    })
                    
                    logger.info(f"Milestone achieved for trade {trade_id}: {milestone.description}")
            
        except Exception as e:
            logger.error(f"Failed to check milestone achievements: {e}")
    
    async def _progress_updater(self):
        """Background task to update trade progress"""
        while self.is_tracking:
            try:
                # Update progress for all active trades
                for trade_id in list(self.active_trackers.keys()):
                    # Get latest trade data
                    trade_data = self.persistence.load_user_trades("", status='active')
                    trade = next((t for t in trade_data if t['trade_id'] == trade_id), None)
                    
                    if trade:
                        await self.update_trade_progress(
                            trade_id,
                            trade['current_price'],
                            datetime.fromisoformat(trade['last_updated'])
                        )
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Progress updater error: {e}")
                await asyncio.sleep(60)
    
    async def _milestone_detector(self):
        """Background task to detect milestone achievements"""
        while self.is_tracking:
            try:
                # Check milestones for all active trades
                for trade_id in self.active_trackers.keys():
                    if trade_id in self.milestones:
                        progress = self.active_trackers[trade_id]
                        await self._check_milestone_achievements(
                            trade_id,
                            progress.current_price,
                            datetime.now()
                        )
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Milestone detector error: {e}")
                await asyncio.sleep(300)
    
    async def _portfolio_analyzer(self):
        """Background task to analyze portfolio progress"""
        while self.is_tracking:
            try:
                # Update portfolio progress for all users
                users = set(progress.user_id for progress in self.active_trackers.values())
                
                for user_id in users:
                    await self._update_portfolio_tracking(user_id)
                
                await asyncio.sleep(900)  # Update every 15 minutes
                
            except Exception as e:
                logger.error(f"Portfolio analyzer error: {e}")
                await asyncio.sleep(900)
    
    async def _update_portfolio_tracking(self, user_id: str):
        """Update portfolio tracking for a user"""
        try:
            # Get all user trades
            active_trades = self.persistence.load_user_trades(user_id, status='active')
            completed_trades = self.persistence.load_user_trades(user_id, status='completed')
            
            # Calculate portfolio metrics
            total_value = sum(trade['quantity'] * trade['current_price'] for trade in active_trades)
            total_pnl = sum(trade['pnl'] for trade in active_trades + completed_trades)
            
            # Calculate win rate
            profitable_trades = len([t for t in completed_trades if t['pnl'] > 0])
            win_rate = profitable_trades / len(completed_trades) if completed_trades else 0
            
            # Calculate average win/loss
            wins = [t['pnl'] for t in completed_trades if t['pnl'] > 0]
            losses = [t['pnl'] for t in completed_trades if t['pnl'] < 0]
            
            avg_win = np.mean(wins) if wins else 0
            avg_loss = abs(np.mean(losses)) if losses else 0
            
            # Calculate profit factor
            total_wins = sum(wins) if wins else 0
            total_losses = abs(sum(losses)) if losses else 1
            profit_factor = total_wins / total_losses if total_losses > 0 else 0
            
            # Create portfolio progress
            portfolio = PortfolioProgress(
                user_id=user_id,
                total_value=total_value,
                total_pnl=total_pnl,
                total_pnl_percentage=(total_pnl / total_value * 100) if total_value > 0 else 0,
                active_trades_count=len(active_trades),
                completed_trades_count=len(completed_trades),
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                profit_factor=profit_factor,
                sharpe_ratio=0.0,  # Would need more data to calculate
                max_drawdown=0.0,  # Would need historical data
                daily_pnl=[],      # Would track daily P&L changes
                sector_allocation={},  # Would analyze by sector
                risk_exposure={}   # Would calculate risk metrics
            )
            
            self.portfolio_trackers[user_id] = portfolio
            
        except Exception as e:
            logger.error(f"Failed to update portfolio tracking for {user_id}: {e}")
    
    async def _alert_manager(self):
        """Background task to manage alerts and notifications"""
        while self.is_tracking:
            try:
                # Check for alert conditions
                for progress in self.active_trackers.values():
                    await self._check_alert_conditions(progress)
                
                await asyncio.sleep(180)  # Check every 3 minutes
                
            except Exception as e:
                logger.error(f"Alert manager error: {e}")
                await asyncio.sleep(180)
    
    async def _check_alert_conditions(self, progress: TradeProgress):
        """Check if any alert conditions are met"""
        try:
            alerts = []
            
            # P&L alerts
            if progress.pnl_percentage > 20:
                alerts.append({
                    'type': 'profit_alert',
                    'message': f"🎉 {progress.symbol} is up {progress.pnl_percentage:.1f}%!",
                    'urgency': 'high'
                })
            elif progress.pnl_percentage < -10:
                alerts.append({
                    'type': 'loss_alert',
                    'message': f"[WARNING]️ {progress.symbol} is down {abs(progress.pnl_percentage):.1f}%",
                    'urgency': 'high'
                })
            
            # Time alerts
            if progress.duration.days >= 7:
                alerts.append({
                    'type': 'time_alert',
                    'message': f"⏰ {progress.symbol} has been held for {progress.duration.days} days",
                    'urgency': 'medium'
                })
            
            # Add alerts to progress
            for alert in alerts:
                if alert not in progress.price_alerts:
                    progress.price_alerts.append(alert)
            
        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")
    
    async def _save_trade_progress(self, progress: TradeProgress):
        """Save trade progress to database"""
        try:
            # Save to persistence layer
            progress_data = asdict(progress)
            # Convert timedelta to string for JSON serialization
            progress_data['duration'] = str(progress.duration)
            
            # Save individual trade progress
            self.persistence.save_system_state(f'trade_progress_{progress.trade_id}', progress_data)
            
        except Exception as e:
            logger.error(f"Failed to save trade progress: {e}")
    
    async def _save_all_progress(self):
        """Save all progress data to database"""
        try:
            # Save all trade progress
            all_progress = [asdict(progress) for progress in self.active_trackers.values()]
            for progress_data in all_progress:
                progress_data['duration'] = str(progress_data['duration'])
            
            self.persistence.save_system_state('trade_progress', all_progress)
            
            # Save all portfolio progress
            all_portfolios = [asdict(portfolio) for portfolio in self.portfolio_trackers.values()]
            self.persistence.save_system_state('portfolio_progress', all_portfolios)
            
            logger.info("All progress data saved")
            
        except Exception as e:
            logger.error(f"Failed to save all progress: {e}")
    
    def get_trade_progress(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """Get progress for a specific trade"""
        try:
            if trade_id in self.active_trackers:
                progress = self.active_trackers[trade_id]
                progress_dict = asdict(progress)
                progress_dict['duration'] = str(progress.duration)
                return progress_dict
            return None
        except Exception as e:
            logger.error(f"Failed to get trade progress: {e}")
            return None
    
    def get_user_portfolio_progress(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get portfolio progress for a user"""
        try:
            if user_id in self.portfolio_trackers:
                return asdict(self.portfolio_trackers[user_id])
            return None
        except Exception as e:
            logger.error(f"Failed to get portfolio progress: {e}")
            return None
    
    def get_user_trade_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trade summary for a user"""
        try:
            user_trades = [
                progress for progress in self.active_trackers.values()
                if progress.user_id == user_id
            ]
            
            portfolio = self.portfolio_trackers.get(user_id)
            
            summary = {
                'user_id': user_id,
                'active_trades': len(user_trades),
                'total_pnl': sum(trade.total_pnl for trade in user_trades),
                'best_performing_trade': None,
                'worst_performing_trade': None,
                'recent_milestones': [],
                'portfolio_metrics': asdict(portfolio) if portfolio else None
            }
            
            # Find best and worst performing trades
            if user_trades:
                best_trade = max(user_trades, key=lambda t: t.pnl_percentage)
                worst_trade = min(user_trades, key=lambda t: t.pnl_percentage)
                
                summary['best_performing_trade'] = {
                    'trade_id': best_trade.trade_id,
                    'symbol': best_trade.symbol,
                    'pnl_percentage': best_trade.pnl_percentage
                }
                
                summary['worst_performing_trade'] = {
                    'trade_id': worst_trade.trade_id,
                    'symbol': worst_trade.symbol,
                    'pnl_percentage': worst_trade.pnl_percentage
                }
                
                # Get recent milestones
                all_milestones = []
                for trade in user_trades:
                    all_milestones.extend(trade.milestones)
                
                # Sort by achievement time and get recent ones
                recent_milestones = sorted(
                    all_milestones,
                    key=lambda m: m.get('achieved_at', ''),
                    reverse=True
                )[:5]
                
                summary['recent_milestones'] = recent_milestones
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get user trade summary: {e}")
            return {}

# Global trade progress tracker instance
trade_progress_tracker = None

def get_trade_progress_tracker() -> TradeProgressTracker:
    """Get the global trade progress tracker instance"""
    global trade_progress_tracker
    if trade_progress_tracker is None:
        trade_progress_tracker = TradeProgressTracker()
    return trade_progress_tracker
