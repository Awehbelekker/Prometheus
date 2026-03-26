#!/usr/bin/env python3
"""
Social Trading & Community Features for Prometheus Trading Platform
Advanced community-driven trading with social signals, copy trading, and collaborative analytics
"""

import asyncio
import json
import sqlite3
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import uuid
import numpy as np
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User experience tiers"""
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    PROFESSIONAL = "professional"

class PostType(Enum):
    """Types of social posts"""
    TRADE_IDEA = "trade_idea"
    MARKET_ANALYSIS = "market_analysis"
    EDUCATIONAL = "educational"
    NEWS_DISCUSSION = "news_discussion"
    PERFORMANCE_UPDATE = "performance_update"
    QUESTION = "question"
    POLL = "poll"

class NotificationType(Enum):
    """Types of notifications"""
    NEW_FOLLOWER = "new_follower"
    TRADE_COPIED = "trade_copied"
    POST_LIKED = "post_liked"
    POST_COMMENTED = "post_commented"
    TRADER_POSTED = "trader_posted"
    PERFORMANCE_MILESTONE = "performance_milestone"
    MARKET_ALERT = "market_alert"

@dataclass
class TradingPerformance:
    """Trader performance metrics"""
    user_id: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_return: float
    monthly_return: float
    max_drawdown: float
    sharpe_ratio: float
    avg_trade_duration: float  # in hours
    risk_score: float  # 1-10 scale
    consistency_score: float  # 1-10 scale
    last_updated: datetime

@dataclass
class SocialPost:
    """Social media post in the trading community"""
    post_id: str
    user_id: str
    username: str
    user_tier: UserTier
    post_type: PostType
    title: str
    content: str
    symbols: List[str]  # Related trading symbols
    tags: List[str]
    likes: int
    comments: int
    shares: int
    created_at: datetime
    is_verified: bool  # Verified trader post
    sentiment: float  # -1 to 1
    engagement_score: float

@dataclass
class TradeIdea:
    """Shared trading idea with detailed analysis"""
    idea_id: str
    user_id: str
    username: str
    symbol: str
    action: str  # BUY/SELL
    entry_price: float
    target_price: float
    stop_loss: float
    confidence: float
    timeframe: str
    analysis: str
    risk_level: str  # low/medium/high
    created_at: datetime
    expires_at: datetime
    likes: int
    copies: int
    success_rate: float  # Historical success of this trader's ideas

@dataclass
class CopyTradeSettings:
    """Copy trading configuration"""
    follower_id: str
    trader_id: str
    max_copy_amount: float  # Maximum amount per trade
    risk_multiplier: float  # 0.1 to 2.0
    symbols_filter: List[str]  # Only copy trades for these symbols
    min_confidence: float  # Minimum confidence threshold
    auto_copy: bool
    notifications: bool
    created_at: datetime
    is_active: bool

@dataclass
class TraderRanking:
    """Trader leaderboard ranking"""
    user_id: str
    username: str
    tier: UserTier
    rank: int
    score: float
    monthly_return: float
    win_rate: float
    followers: int
    total_trades: int
    verified: bool

class SocialTradingDatabase:
    """Database manager for social trading features"""
    
    def __init__(self, db_path: str = "social_trading.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize social trading database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User profiles and performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trader_profiles (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                display_name TEXT,
                bio TEXT,
                tier TEXT,
                verified BOOLEAN DEFAULT FALSE,
                followers_count INTEGER DEFAULT 0,
                following_count INTEGER DEFAULT 0,
                total_posts INTEGER DEFAULT 0,
                joined_at TIMESTAMP,
                last_active TIMESTAMP,
                profile_image TEXT,
                cover_image TEXT,
                location TEXT,
                website TEXT
            )
        ''')
        
        # Trading performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_performance (
                user_id TEXT PRIMARY KEY,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                total_return REAL DEFAULT 0.0,
                monthly_return REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                avg_trade_duration REAL DEFAULT 0.0,
                risk_score REAL DEFAULT 5.0,
                consistency_score REAL DEFAULT 5.0,
                last_updated TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Social posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_posts (
                post_id TEXT PRIMARY KEY,
                user_id TEXT,
                post_type TEXT,
                title TEXT,
                content TEXT,
                symbols TEXT,  -- JSON array
                tags TEXT,     -- JSON array
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                created_at TIMESTAMP,
                is_verified BOOLEAN DEFAULT FALSE,
                sentiment REAL DEFAULT 0.0,
                engagement_score REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Trade ideas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trade_ideas (
                idea_id TEXT PRIMARY KEY,
                user_id TEXT,
                symbol TEXT,
                action TEXT,
                entry_price REAL,
                target_price REAL,
                stop_loss REAL,
                confidence REAL,
                timeframe TEXT,
                analysis TEXT,
                risk_level TEXT,
                created_at TIMESTAMP,
                expires_at TIMESTAMP,
                likes INTEGER DEFAULT 0,
                copies INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Copy trading relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copy_trading (
                id TEXT PRIMARY KEY,
                follower_id TEXT,
                trader_id TEXT,
                max_copy_amount REAL,
                risk_multiplier REAL DEFAULT 1.0,
                symbols_filter TEXT,  -- JSON array
                min_confidence REAL DEFAULT 0.0,
                auto_copy BOOLEAN DEFAULT TRUE,
                notifications BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (follower_id) REFERENCES trader_profiles (user_id),
                FOREIGN KEY (trader_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Followers/Following relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_follows (
                follower_id TEXT,
                following_id TEXT,
                created_at TIMESTAMP,
                notifications BOOLEAN DEFAULT TRUE,
                PRIMARY KEY (follower_id, following_id),
                FOREIGN KEY (follower_id) REFERENCES trader_profiles (user_id),
                FOREIGN KEY (following_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Notifications
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                type TEXT,
                title TEXT,
                message TEXT,
                data TEXT,  -- JSON data
                read BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES trader_profiles (user_id)
            )
        ''')
        
        # Leaderboards
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard_cache (
                period TEXT,  -- daily, weekly, monthly, all_time
                user_id TEXT,
                rank INTEGER,
                score REAL,
                updated_at TIMESTAMP,
                PRIMARY KEY (period, user_id)
            )
        ''')
        
        conn.commit()
        conn.close()

class SocialTradingManager:
    """Main manager for social trading features"""
    
    def __init__(self):
        self.db = SocialTradingDatabase()
        self.active_users = {}  # Online users cache
        self.live_notifications = defaultdict(deque)  # Real-time notifications
        
    async def create_trader_profile(self, user_id: str, username: str, 
                                  display_name: str = None, bio: str = None) -> bool:
        """Create a new trader profile"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trader_profiles 
                (user_id, username, display_name, bio, tier, joined_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, username, display_name or username, bio or "",
                  UserTier.NOVICE.value, datetime.now(), datetime.now()))
            
            # Initialize performance record
            cursor.execute('''
                INSERT INTO trading_performance (user_id, last_updated)
                VALUES (?, ?)
            ''', (user_id, datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created trader profile for {username} ({user_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error creating trader profile: {e}")
            return False
    
    async def follow_trader(self, follower_id: str, trader_id: str) -> bool:
        """Follow another trader"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Add follow relationship
            cursor.execute('''
                INSERT OR IGNORE INTO social_follows 
                (follower_id, following_id, created_at)
                VALUES (?, ?, ?)
            ''', (follower_id, trader_id, datetime.now()))
            
            # Update follower counts
            cursor.execute('''
                UPDATE trader_profiles SET followers_count = followers_count + 1
                WHERE user_id = ?
            ''', (trader_id,))
            
            cursor.execute('''
                UPDATE trader_profiles SET following_count = following_count + 1
                WHERE user_id = ?
            ''', (follower_id,))
            
            conn.commit()
            conn.close()
            
            # Send notification
            await self.send_notification(
                trader_id, NotificationType.NEW_FOLLOWER,
                "New Follower", f"You have a new follower!",
                {"follower_id": follower_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error following trader: {e}")
            return False
    
    async def post_trade_idea(self, user_id: str, symbol: str, action: str,
                            entry_price: float, target_price: float, stop_loss: float,
                            confidence: float, timeframe: str, analysis: str,
                            risk_level: str = "medium") -> str:
        """Post a new trade idea"""
        try:
            idea_id = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(hours=24)  # Ideas expire in 24h
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get user's historical success rate
            cursor.execute('''
                SELECT AVG(
                    CASE WHEN result = 'success' THEN 1.0 ELSE 0.0 END
                ) as success_rate
                FROM trade_results WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            success_rate = result[0] if result and result[0] else 0.5
            
            cursor.execute('''
                INSERT INTO trade_ideas 
                (idea_id, user_id, symbol, action, entry_price, target_price, 
                 stop_loss, confidence, timeframe, analysis, risk_level, 
                 created_at, expires_at, success_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (idea_id, user_id, symbol, action, entry_price, target_price,
                  stop_loss, confidence, timeframe, analysis, risk_level,
                  datetime.now(), expires_at, success_rate))
            
            conn.commit()
            conn.close()
            
            # Notify followers
            await self.notify_followers_of_post(user_id, "trade_idea", idea_id)
            
            logger.info(f"Posted trade idea {idea_id} for {symbol}")
            return idea_id
            
        except Exception as e:
            logger.error(f"Error posting trade idea: {e}")
            return ""
    
    async def setup_copy_trading(self, follower_id: str, trader_id: str,
                               max_copy_amount: float, risk_multiplier: float = 1.0,
                               symbols_filter: List[str] = None,
                               min_confidence: float = 0.0) -> bool:
        """Setup copy trading relationship"""
        try:
            copy_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO copy_trading 
                (id, follower_id, trader_id, max_copy_amount, risk_multiplier,
                 symbols_filter, min_confidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (copy_id, follower_id, trader_id, max_copy_amount, risk_multiplier,
                  json.dumps(symbols_filter or []), min_confidence, datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Notify trader
            await self.send_notification(
                trader_id, NotificationType.TRADE_COPIED,
                "Copy Trading Setup", f"Someone is now copying your trades!",
                {"follower_id": follower_id, "max_amount": max_copy_amount}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up copy trading: {e}")
            return False
    
    async def get_social_feed(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get personalized social feed"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get posts from followed traders and own posts
            cursor.execute('''
                SELECT p.*, tp.username, tp.tier, tp.verified
                FROM social_posts p
                JOIN trader_profiles tp ON p.user_id = tp.user_id
                WHERE p.user_id IN (
                    SELECT following_id FROM social_follows WHERE follower_id = ?
                    UNION
                    SELECT ? as user_id
                )
                ORDER BY p.created_at DESC
                LIMIT ?
            ''', (user_id, user_id, limit))
            
            posts = []
            for row in cursor.fetchall():
                post = {
                    'post_id': row[0],
                    'user_id': row[1],
                    'post_type': row[2],
                    'title': row[3],
                    'content': row[4],
                    'symbols': json.loads(row[5] or '[]'),
                    'tags': json.loads(row[6] or '[]'),
                    'likes': row[7],
                    'comments': row[8],
                    'shares': row[9],
                    'created_at': row[10],
                    'is_verified': row[11],
                    'sentiment': row[12],
                    'engagement_score': row[13],
                    'username': row[14],
                    'tier': row[15],
                    'verified': row[16]
                }
                posts.append(post)
            
            conn.close()
            return posts
            
        except Exception as e:
            logger.error(f"Error getting social feed: {e}")
            return []
    
    async def get_trade_ideas_feed(self, user_id: str, symbol: str = None) -> List[Dict[str, Any]]:
        """Get trade ideas feed with filtering"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT ti.*, tp.username, tp.tier, tp.verified
                FROM trade_ideas ti
                JOIN trader_profiles tp ON ti.user_id = tp.user_id
                WHERE ti.expires_at > ?
            '''
            params = [datetime.now()]
            
            if symbol:
                query += ' AND ti.symbol = ?'
                params.append(symbol)
            
            # Prioritize followed traders
            query += '''
                ORDER BY 
                    CASE WHEN ti.user_id IN (
                        SELECT following_id FROM social_follows WHERE follower_id = ?
                    ) THEN 0 ELSE 1 END,
                    ti.confidence DESC,
                    ti.success_rate DESC,
                    ti.created_at DESC
                LIMIT 20
            '''
            params.append(user_id)
            
            cursor.execute(query, params)
            
            ideas = []
            for row in cursor.fetchall():
                idea = {
                    'idea_id': row[0],
                    'user_id': row[1],
                    'symbol': row[2],
                    'action': row[3],
                    'entry_price': row[4],
                    'target_price': row[5],
                    'stop_loss': row[6],
                    'confidence': row[7],
                    'timeframe': row[8],
                    'analysis': row[9],
                    'risk_level': row[10],
                    'created_at': row[11],
                    'expires_at': row[12],
                    'likes': row[13],
                    'copies': row[14],
                    'success_rate': row[15],
                    'username': row[16],
                    'tier': row[17],
                    'verified': row[18]
                }
                ideas.append(idea)
            
            conn.close()
            return ideas
            
        except Exception as e:
            logger.error(f"Error getting trade ideas feed: {e}")
            return []
    
    async def get_leaderboard(self, period: str = "monthly", limit: int = 50) -> List[TraderRanking]:
        """Get trader leaderboard"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Calculate rankings based on period
            if period == "monthly":
                cursor.execute('''
                    SELECT tp.user_id, tp.username, tp.tier, tp.verified,
                           tp.followers_count, perf.monthly_return, perf.win_rate,
                           perf.total_trades,
                           (perf.monthly_return * 0.4 + perf.win_rate * 0.3 + 
                            LOG(tp.followers_count + 1) * 0.2 + 
                            perf.consistency_score * 0.1) as score
                    FROM trader_profiles tp
                    JOIN trading_performance perf ON tp.user_id = perf.user_id
                    WHERE perf.total_trades > 10
                    ORDER BY score DESC
                    LIMIT ?
                ''', (limit,))
            else:
                # Default to total return ranking
                cursor.execute('''
                    SELECT tp.user_id, tp.username, tp.tier, tp.verified,
                           tp.followers_count, perf.total_return, perf.win_rate,
                           perf.total_trades,
                           (perf.total_return * 0.5 + perf.win_rate * 0.3 + 
                            perf.sharpe_ratio * 0.2) as score
                    FROM trader_profiles tp
                    JOIN trading_performance perf ON tp.user_id = perf.user_id
                    WHERE perf.total_trades > 10
                    ORDER BY score DESC
                    LIMIT ?
                ''', (limit,))
            
            rankings = []
            for rank, row in enumerate(cursor.fetchall(), 1):
                ranking = TraderRanking(
                    user_id=row[0],
                    username=row[1],
                    tier=UserTier(row[2]),
                    rank=rank,
                    score=row[8],
                    monthly_return=row[5],
                    win_rate=row[6],
                    followers=row[4],
                    total_trades=row[7],
                    verified=row[3]
                )
                rankings.append(ranking)
            
            conn.close()
            return rankings
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def send_notification(self, user_id: str, notification_type: NotificationType,
                              title: str, message: str, data: Dict[str, Any] = None):
        """Send notification to user"""
        try:
            notification_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications 
                (id, user_id, type, title, message, data, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (notification_id, user_id, notification_type.value, title,
                  message, json.dumps(data or {}), datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Add to live notifications for real-time delivery
            self.live_notifications[user_id].append({
                'id': notification_id,
                'type': notification_type.value,
                'title': title,
                'message': message,
                'data': data,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 50 notifications per user
            if len(self.live_notifications[user_id]) > 50:
                self.live_notifications[user_id].popleft()
                
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
    
    async def notify_followers_of_post(self, user_id: str, post_type: str, post_id: str):
        """Notify followers of new post"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get followers who have notifications enabled
            cursor.execute('''
                SELECT sf.follower_id, tp.username
                FROM social_follows sf
                JOIN trader_profiles tp ON sf.following_id = tp.user_id
                WHERE sf.following_id = ? AND sf.notifications = TRUE
            ''', (user_id,))
            
            username = None
            for row in cursor.fetchall():
                follower_id = row[0]
                if not username:
                    username = row[1]
                
                await self.send_notification(
                    follower_id, NotificationType.TRADER_POSTED,
                    f"New {post_type.replace('_', ' ').title()}",
                    f"{username} shared a new {post_type.replace('_', ' ')}",
                    {"trader_id": user_id, "post_id": post_id, "post_type": post_type}
                )
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error notifying followers: {e}")
    
    async def update_trading_performance(self, user_id: str, performance: TradingPerformance):
        """Update trader's performance metrics"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trading_performance SET
                    total_trades = ?, winning_trades = ?, losing_trades = ?,
                    win_rate = ?, total_return = ?, monthly_return = ?,
                    max_drawdown = ?, sharpe_ratio = ?, avg_trade_duration = ?,
                    risk_score = ?, consistency_score = ?, last_updated = ?
                WHERE user_id = ?
            ''', (performance.total_trades, performance.winning_trades, performance.losing_trades,
                  performance.win_rate, performance.total_return, performance.monthly_return,
                  performance.max_drawdown, performance.sharpe_ratio, performance.avg_trade_duration,
                  performance.risk_score, performance.consistency_score, datetime.now(), user_id))
            
            conn.commit()
            conn.close()
            
            # Check for performance milestones
            await self.check_performance_milestones(user_id, performance)
            
        except Exception as e:
            logger.error(f"Error updating performance: {e}")
    
    async def check_performance_milestones(self, user_id: str, performance: TradingPerformance):
        """Check and notify about performance milestones"""
        milestones = []
        
        if performance.total_trades in [10, 50, 100, 500, 1000]:
            milestones.append(f"{performance.total_trades} trades completed!")
        
        if performance.win_rate >= 0.8:
            milestones.append("80%+ win rate achieved!")
        
        if performance.total_return >= 0.5:
            milestones.append("50%+ total return achieved!")
        
        for milestone in milestones:
            await self.send_notification(
                user_id, NotificationType.PERFORMANCE_MILESTONE,
                "Performance Milestone", milestone,
                {"performance": asdict(performance)}
            )
    
    async def get_copy_trading_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recommended traders to copy"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
            # Get top performing traders not already being copied
            cursor.execute('''
                SELECT tp.user_id, tp.username, tp.tier, tp.verified,
                       tp.followers_count, perf.win_rate, perf.monthly_return,
                       perf.total_trades, perf.risk_score, perf.consistency_score
                FROM trader_profiles tp
                JOIN trading_performance perf ON tp.user_id = perf.user_id
                WHERE tp.user_id != ? 
                  AND tp.user_id NOT IN (
                      SELECT trader_id FROM copy_trading 
                      WHERE follower_id = ? AND is_active = TRUE
                  )
                  AND perf.total_trades > 20
                  AND perf.win_rate > 0.6
                ORDER BY (perf.monthly_return * 0.4 + perf.win_rate * 0.3 + 
                         perf.consistency_score * 0.3) DESC
                LIMIT 10
            ''', (user_id, user_id))
            
            opportunities = []
            for row in cursor.fetchall():
                opportunity = {
                    'user_id': row[0],
                    'username': row[1],
                    'tier': row[2],
                    'verified': row[3],
                    'followers': row[4],
                    'win_rate': row[5],
                    'monthly_return': row[6],
                    'total_trades': row[7],
                    'risk_score': row[8],
                    'consistency_score': row[9],
                    'recommendation_score': row[5] * 0.3 + row[6] * 0.4 + row[9] * 0.3
                }
                opportunities.append(opportunity)
            
            conn.close()
            return opportunities
            
        except Exception as e:
            logger.error(f"Error getting copy trading opportunities: {e}")
            return []

# Global social trading manager
social_manager = SocialTradingManager()

async def demo_social_features():
    """Demo function for social trading features"""
    print("🚀 Prometheus Social Trading Demo")
    
    # Create demo users
    await social_manager.create_trader_profile("user1", "TraderPro", "Professional Trader", "10 years of trading experience")
    await social_manager.create_trader_profile("user2", "TechAnalyst", "Technical Analysis Expert", "Specialized in tech stocks")
    await social_manager.create_trader_profile("user3", "CryptoKing", "Crypto Specialist", "Bitcoin maximalist")
    
    print("[CHECK] Created demo trader profiles")
    
    # Follow relationships
    await social_manager.follow_trader("user2", "user1")
    await social_manager.follow_trader("user3", "user1")
    print("[CHECK] Set up follow relationships")
    
    # Post trade idea
    idea_id = await social_manager.post_trade_idea(
        "user1", "AAPL", "BUY", 150.0, 165.0, 145.0, 0.8, "1w",
        "Strong momentum and positive earnings outlook"
    )
    print(f"[CHECK] Posted trade idea: {idea_id}")
    
    # Setup copy trading
    await social_manager.setup_copy_trading("user2", "user1", 1000.0, 0.5)
    print("[CHECK] Set up copy trading")
    
    # Get social feed
    feed = await social_manager.get_social_feed("user2")
    print(f"[CHECK] Retrieved social feed: {len(feed)} posts")
    
    # Get leaderboard
    leaderboard = await social_manager.get_leaderboard()
    print(f"[CHECK] Retrieved leaderboard: {len(leaderboard)} traders")
    
    print("\n🎉 Social trading demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_social_features())
