"""
🚀 REVOLUTIONARY SOCIAL TRADING NETWORK
Connect traders, share strategies, and create trading communities
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum
import random
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)

class UserTier(Enum):
    ROOKIE = "rookie"
    TRADER = "trader"
    EXPERT = "expert"
    MASTER = "master"
    LEGEND = "legend"
    ORACLE = "oracle"

class PostType(Enum):
    TRADE_ALERT = "trade_alert"
    ANALYSIS = "analysis"
    STRATEGY = "strategy"
    NEWS = "news"
    EDUCATION = "education"
    PREDICTION = "prediction"

class FollowType(Enum):
    FOLLOW = "follow"
    COPY_TRADE = "copy_trade"
    MIRROR = "mirror"
    ALERT_ONLY = "alert_only"

@dataclass
class SocialUser:
    """Social trading user profile"""
    user_id: int
    username: str
    display_name: str
    avatar_url: str
    tier: UserTier
    verified: bool = False
    
    # Trading stats
    total_trades: int = 0
    win_rate: float = 0.0
    total_profit: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    
    # Social stats
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    likes_received: int = 0
    comments_received: int = 0
    
    # Influence metrics
    influence_score: float = 0.0
    copy_trader_count: int = 0
    total_aum: float = 0.0  # Assets under management from copiers
    
    # Specializations
    favorite_assets: List[str] = field(default_factory=list)
    trading_style: str = ""
    strategy_description: str = ""
    
    # Performance tracking
    monthly_returns: List[float] = field(default_factory=list)
    risk_score: float = 0.5
    consistency_score: float = 0.5
    
    # Social features
    is_mentor: bool = False
    mentor_rating: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TradingPost:
    """Social trading post"""
    post_id: str
    user_id: int
    post_type: PostType
    title: str
    content: str
    
    # Trading-specific data
    symbol: Optional[str] = None
    action: Optional[str] = None  # buy, sell, hold
    entry_price: Optional[float] = None
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    confidence: Optional[float] = None
    
    # Media attachments
    images: List[str] = field(default_factory=list)
    charts: List[str] = field(default_factory=list)
    
    # Engagement metrics
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Performance tracking (for trade alerts)
    is_closed: bool = False
    actual_profit: Optional[float] = None
    accuracy_score: Optional[float] = None
    
    # Hashtags and mentions
    hashtags: List[str] = field(default_factory=list)
    mentions: List[int] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TradingRoom:
    """Virtual trading room for live discussions"""
    room_id: str
    name: str
    description: str
    creator_id: int
    
    # Room settings
    is_public: bool = True
    requires_approval: bool = False
    max_members: int = 1000
    
    # Member management
    members: Set[int] = field(default_factory=set)
    moderators: Set[int] = field(default_factory=set)
    banned_users: Set[int] = field(default_factory=set)
    
    # Room features
    allow_copy_trading: bool = True
    allow_signals: bool = True
    allow_voice_chat: bool = False
    
    # Room statistics
    total_members: int = 0
    active_traders: int = 0
    total_signals: int = 0
    average_accuracy: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CopyTradeSettings:
    """Copy trading configuration"""
    follower_id: int
    leader_id: int
    follow_type: FollowType
    
    # Copy settings
    copy_percentage: float = 100.0  # % of leader's position size
    max_position_size: float = 1000.0
    stop_copy_on_loss: float = 0.1  # Stop copying if 10% loss
    
    # Asset filters
    allowed_symbols: List[str] = field(default_factory=list)
    blocked_symbols: List[str] = field(default_factory=list)
    
    # Risk management
    max_daily_loss: float = 500.0
    max_open_positions: int = 10
    
    # Performance tracking
    total_copied_trades: int = 0
    successful_trades: int = 0
    total_profit: float = 0.0
    
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

class SocialTradingNetwork:
    """Revolutionary social trading network engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.users: Dict[int, SocialUser] = {}
        self.posts: Dict[str, TradingPost] = {}
        self.trading_rooms: Dict[str, TradingRoom] = {}
        self.copy_trades: Dict[Tuple[int, int], CopyTradeSettings] = {}
        self.follows: Dict[int, Set[int]] = defaultdict(set)  # follower_id -> set of leader_ids
        self.followers: Dict[int, Set[int]] = defaultdict(set)  # leader_id -> set of follower_ids
        
        # Analytics
        self.trending_hashtags: List[str] = []
        self.top_performers: List[int] = []
        self.viral_posts: List[str] = []
        
    async def create_user(self, user_id: int, username: str, display_name: str) -> SocialUser:
        """Create a new social trading user"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        user = SocialUser(
            user_id=user_id,
            username=username,
            display_name=display_name,
            avatar_url=f"/avatars/{username}.jpg",
            tier=UserTier.ROOKIE
        )
        
        self.users[user_id] = user
        logger.info(f"Created social user: {username}")
        return user
    
    async def create_post(self, user_id: int, post_type: PostType, title: str, 
                         content: str, **kwargs) -> TradingPost:
        """Create a new trading post"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        post_id = f"post_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        post = TradingPost(
            post_id=post_id,
            user_id=user_id,
            post_type=post_type,
            title=title,
            content=content,
            **kwargs
        )
        
        # Extract hashtags from content
        post.hashtags = self._extract_hashtags(content)
        
        # Extract mentions from content
        post.mentions = self._extract_mentions(content)
        
        self.posts[post_id] = post
        self.users[user_id].posts_count += 1
        
        # Notify followers
        await self._notify_followers(user_id, post)
        
        logger.info(f"Created post: {title} by user {user_id}")
        return post
    
    async def follow_user(self, follower_id: int, leader_id: int, 
                         follow_type: FollowType = FollowType.FOLLOW) -> bool:
        """Follow another user"""
        if follower_id == leader_id:
            raise ValueError("Cannot follow yourself")
        
        if follower_id not in self.users or leader_id not in self.users:
            raise ValueError("User not found")
        
        # Add to follow relationships
        self.follows[follower_id].add(leader_id)
        self.followers[leader_id].add(follower_id)
        
        # Update counts
        self.users[follower_id].following_count += 1
        self.users[leader_id].followers_count += 1
        
        # If copy trading, create copy trade settings
        if follow_type in [FollowType.COPY_TRADE, FollowType.MIRROR]:
            await self.setup_copy_trading(follower_id, leader_id, follow_type)
        
        logger.info(f"User {follower_id} followed user {leader_id} with type {follow_type.value}")
        return True
    
    async def setup_copy_trading(self, follower_id: int, leader_id: int, 
                               follow_type: FollowType) -> CopyTradeSettings:
        """Setup copy trading between users"""
        copy_settings = CopyTradeSettings(
            follower_id=follower_id,
            leader_id=leader_id,
            follow_type=follow_type
        )
        
        self.copy_trades[(follower_id, leader_id)] = copy_settings
        self.users[leader_id].copy_trader_count += 1
        
        logger.info(f"Setup copy trading: {follower_id} -> {leader_id}")
        return copy_settings
    
    async def create_trading_room(self, creator_id: int, name: str, 
                                description: str, **kwargs) -> TradingRoom:
        """Create a new trading room"""
        room_id = f"room_{creator_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        room = TradingRoom(
            room_id=room_id,
            name=name,
            description=description,
            creator_id=creator_id,
            **kwargs
        )
        
        # Creator is automatically a member and moderator
        room.members.add(creator_id)
        room.moderators.add(creator_id)
        room.total_members = 1
        
        self.trading_rooms[room_id] = room
        logger.info(f"Created trading room: {name}")
        return room
    
    async def join_trading_room(self, user_id: int, room_id: str) -> bool:
        """Join a trading room"""
        if room_id not in self.trading_rooms:
            raise ValueError(f"Trading room {room_id} not found")
        
        room = self.trading_rooms[room_id]
        
        # Check if user is banned
        if user_id in room.banned_users:
            raise ValueError("User is banned from this room")
        
        # Check room capacity
        if len(room.members) >= room.max_members:
            raise ValueError("Room is at maximum capacity")
        
        # Add to room
        room.members.add(user_id)
        room.total_members = len(room.members)
        
        logger.info(f"User {user_id} joined room {room_id}")
        return True
    
    async def execute_copy_trade(self, leader_id: int, trade_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute copy trades when a leader makes a trade"""
        executed_trades = []
        
        # Find all copy traders for this leader
        for (follower_id, leader), copy_settings in self.copy_trades.items():
            if leader != leader_id or not copy_settings.is_active:
                continue
            
            # Check if trade should be copied
            if not await self._should_copy_trade(copy_settings, trade_data):
                continue
            
            # Calculate position size for follower
            follower_position_size = await self._calculate_copy_position_size(
                copy_settings, trade_data
            )
            
            # Create copy trade
            copy_trade_data = {
                **trade_data,
                'user_id': follower_id,
                'quantity': follower_position_size,
                'is_copy_trade': True,
                'copied_from': leader_id,
                'copy_percentage': copy_settings.copy_percentage
            }
            
            executed_trades.append(copy_trade_data)
            
            # Update copy trade statistics
            copy_settings.total_copied_trades += 1
            
        logger.info(f"Executed {len(executed_trades)} copy trades for leader {leader_id}")
        return executed_trades
    
    async def _should_copy_trade(self, copy_settings: CopyTradeSettings, 
                               trade_data: Dict[str, Any]) -> bool:
        """Determine if a trade should be copied"""
        symbol = trade_data.get('symbol', '')
        
        # Check symbol filters
        if copy_settings.allowed_symbols and symbol not in copy_settings.allowed_symbols:
            return False
        
        if symbol in copy_settings.blocked_symbols:
            return False
        
        # Check risk limits
        position_value = trade_data.get('value', 0)
        if position_value > copy_settings.max_position_size:
            return False
        
        # Check daily loss limits
        # This would integrate with the user's trading history
        
        return True
    
    async def _calculate_copy_position_size(self, copy_settings: CopyTradeSettings,
                                          trade_data: Dict[str, Any]) -> float:
        """Calculate the position size for a copy trade"""
        original_quantity = trade_data.get('quantity', 0)
        copy_percentage = copy_settings.copy_percentage / 100.0
        
        copied_quantity = original_quantity * copy_percentage
        
        # Apply maximum position size limit
        max_quantity = copy_settings.max_position_size / trade_data.get('price', 1)
        copied_quantity = min(copied_quantity, max_quantity)
        
        return copied_quantity
    
    async def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from post content"""
        import re
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, content.lower())
        return list(set(hashtags))  # Remove duplicates
    
    async def _extract_mentions(self, content: str) -> List[int]:
        """Extract user mentions from post content"""
        import re
        mention_pattern = r'@(\w+)'
        usernames = re.findall(mention_pattern, content.lower())
        
        # Convert usernames to user IDs
        user_ids = []
        for username in usernames:
            for user_id, user in self.users.items():
                if user.username.lower() == username:
                    user_ids.append(user_id)
                    break
        
        return user_ids
    
    async def _notify_followers(self, user_id: int, post: TradingPost) -> None:
        """Notify followers about new post"""
        followers = self.followers.get(user_id, set())
        
        # This would integrate with notification system
        for follower_id in followers:
            logger.debug(f"Notifying follower {follower_id} about new post from {user_id}")
    
    async def get_feed(self, user_id: int, limit: int = 50) -> List[TradingPost]:
        """Get personalized feed for user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        # Get posts from followed users
        following = self.follows.get(user_id, set())
        feed_posts = []
        
        for post in self.posts.values():
            if post.user_id in following or post.user_id == user_id:
                feed_posts.append(post)
        
        # Sort by engagement and recency
        feed_posts.sort(key=lambda p: (
            p.likes_count + p.comments_count + p.shares_count,
            p.created_at
        ), reverse=True)
        
        return feed_posts[:limit]
    
    async def get_trending_posts(self, limit: int = 20) -> List[TradingPost]:
        """Get trending posts across the platform"""
        all_posts = list(self.posts.values())
        
        # Calculate trending score
        now = datetime.utcnow()
        trending_posts = []
        
        for post in all_posts:
            # Recency factor (posts lose relevance over time)
            hours_old = (now - post.created_at).total_seconds() / 3600
            recency_factor = max(0.1, 1 / (1 + hours_old / 24))  # Decay over 24 hours
            
            # Engagement score
            engagement_score = (
                post.likes_count * 1 +
                post.comments_count * 3 +
                post.shares_count * 5 +
                post.views_count * 0.1
            )
            
            # Trending score
            trending_score = engagement_score * recency_factor
            trending_posts.append((trending_score, post))
        
        # Sort by trending score
        trending_posts.sort(key=lambda x: x[0], reverse=True)
        
        return [post for _, post in trending_posts[:limit]]
    
    async def get_top_traders(self, timeframe: str = "monthly", limit: int = 100) -> List[SocialUser]:
        """Get top performing traders"""
        traders = list(self.users.values())
        
        # Filter out users with insufficient data
        qualified_traders = [
            trader for trader in traders
            if trader.total_trades >= 10 and trader.followers_count >= 1
        ]
        
        # Sort by performance metrics
        if timeframe == "monthly":
            qualified_traders.sort(key=lambda t: (
                t.monthly_returns[-1] if t.monthly_returns else 0,
                t.win_rate,
                t.sharpe_ratio
            ), reverse=True)
        else:
            qualified_traders.sort(key=lambda t: (
                t.total_profit,
                t.win_rate,
                t.sharpe_ratio
            ), reverse=True)
        
        return qualified_traders[:limit]
    
    async def get_user_analytics(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        user = self.users[user_id]
        
        # Get user's posts
        user_posts = [post for post in self.posts.values() if post.user_id == user_id]
        
        # Calculate engagement metrics
        total_likes = sum(post.likes_count for post in user_posts)
        total_comments = sum(post.comments_count for post in user_posts)
        total_shares = sum(post.shares_count for post in user_posts)
        total_views = sum(post.views_count for post in user_posts)
        
        avg_engagement = (total_likes + total_comments + total_shares) / max(len(user_posts), 1)
        
        # Calculate influence metrics
        influence_factors = {
            'followers': user.followers_count * 0.3,
            'engagement': avg_engagement * 0.2,
            'copy_traders': user.copy_trader_count * 0.25,
            'performance': user.win_rate * user.total_profit * 0.15,
            'consistency': user.consistency_score * 0.1
        }
        
        total_influence = sum(influence_factors.values())
        
        return {
            'user_info': {
                'username': user.username,
                'display_name': user.display_name,
                'tier': user.tier.value,
                'verified': user.verified
            },
            'social_metrics': {
                'followers': user.followers_count,
                'following': user.following_count,
                'posts': user.posts_count,
                'total_likes': total_likes,
                'total_comments': total_comments,
                'total_shares': total_shares,
                'total_views': total_views,
                'avg_engagement': avg_engagement
            },
            'trading_metrics': {
                'total_trades': user.total_trades,
                'win_rate': f"{user.win_rate:.1%}",
                'total_profit': f"${user.total_profit:,.2f}",
                'sharpe_ratio': user.sharpe_ratio,
                'max_drawdown': f"{user.max_drawdown:.1%}"
            },
            'influence_metrics': {
                'influence_score': total_influence,
                'copy_traders': user.copy_trader_count,
                'aum': f"${user.total_aum:,.2f}",
                'influence_breakdown': influence_factors
            },
            'specializations': {
                'favorite_assets': user.favorite_assets,
                'trading_style': user.trading_style,
                'risk_score': user.risk_score,
                'consistency_score': user.consistency_score
            }
        }
    
    async def search_users(self, query: str, filters: Dict[str, Any] = None) -> List[SocialUser]:
        """Search for users based on query and filters"""
        results = []
        filters = filters or {}
        
        for user in self.users.values():
            # Text search
            if query.lower() in user.username.lower() or query.lower() in user.display_name.lower():
                # Apply filters
                if filters.get('min_followers') and user.followers_count < filters['min_followers']:
                    continue
                if filters.get('min_win_rate') and user.win_rate < filters['min_win_rate']:
                    continue
                if filters.get('tier') and user.tier != UserTier(filters['tier']):
                    continue
                if filters.get('verified_only') and not user.verified:
                    continue
                
                results.append(user)
        
        # Sort by relevance (followers, influence, etc.)
        results.sort(key=lambda u: (u.influence_score, u.followers_count), reverse=True)
        
        return results
    
    async def get_room_feed(self, room_id: str, limit: int = 50) -> List[TradingPost]:
        """Get feed for a specific trading room"""
        if room_id not in self.trading_rooms:
            raise ValueError(f"Trading room {room_id} not found")
        
        room = self.trading_rooms[room_id]
        room_posts = []
        
        # Get posts from room members
        for post in self.posts.values():
            if post.user_id in room.members:
                room_posts.append(post)
        
        # Sort by recency
        room_posts.sort(key=lambda p: p.created_at, reverse=True)
        
        return room_posts[:limit]
    
    async def update_user_performance(self, user_id: int, trade_result: Dict[str, Any]) -> None:
        """Update user performance metrics after a trade"""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        
        # Update basic stats
        user.total_trades += 1
        
        pnl = trade_result.get('pnl', 0)
        user.total_profit += pnl
        
        if pnl > 0:
            # Update win rate
            winning_trades = user.win_rate * (user.total_trades - 1) + 1
            user.win_rate = winning_trades / user.total_trades
        else:
            # Update win rate
            winning_trades = user.win_rate * (user.total_trades - 1)
            user.win_rate = winning_trades / user.total_trades
        
        # Update tier based on performance
        await self._update_user_tier(user_id)
        
        # Update influence score
        await self._update_influence_score(user_id)
        
        user.last_active = datetime.utcnow()
    
    async def _update_user_tier(self, user_id: int) -> None:
        """Update user tier based on performance"""
        user = self.users[user_id]
        
        # Tier upgrade criteria
        if (user.total_trades >= 1000 and user.win_rate >= 0.8 and 
            user.total_profit >= 100000 and user.followers_count >= 500):
            user.tier = UserTier.ORACLE
        elif (user.total_trades >= 500 and user.win_rate >= 0.75 and 
              user.total_profit >= 50000 and user.followers_count >= 200):
            user.tier = UserTier.LEGEND
        elif (user.total_trades >= 200 and user.win_rate >= 0.7 and 
              user.total_profit >= 20000 and user.followers_count >= 50):
            user.tier = UserTier.MASTER
        elif (user.total_trades >= 100 and user.win_rate >= 0.65 and 
              user.total_profit >= 5000):
            user.tier = UserTier.EXPERT
        elif user.total_trades >= 50 and user.win_rate >= 0.6:
            user.tier = UserTier.TRADER
    
    async def _update_influence_score(self, user_id: int) -> None:
        """Update user influence score"""
        user = self.users[user_id]
        
        # Calculate influence based on multiple factors
        performance_score = (user.win_rate * user.total_profit) / max(user.total_trades, 1)
        social_score = (user.followers_count * 0.5 + user.copy_trader_count * 2)
        engagement_score = (user.likes_received + user.comments_received) / max(user.posts_count, 1)
        
        user.influence_score = (performance_score * 0.4 + social_score * 0.4 + engagement_score * 0.2)

# Global instance
social_network = None

def get_social_network(config: Dict[str, Any] = None) -> SocialTradingNetwork:
    """Get or create the global social network instance"""
    global social_network
    if social_network is None:
        social_network = SocialTradingNetwork(config or {})
    return social_network

# Example usage
async def test_social_network():
    """Test the social trading network"""
    network = get_social_network()
    
    # Create users
    user1 = await network.create_user(1, "alpha_trader", "Alpha Trader")
    user2 = await network.create_user(2, "crypto_guru", "Crypto Guru")
    user3 = await network.create_user(3, "forex_master", "Forex Master")
    
    # Update some performance data
    await network.update_user_performance(1, {"pnl": 1500, "symbol": "BTCUSD"})
    await network.update_user_performance(2, {"pnl": 800, "symbol": "ETHUSD"})
    
    # Create posts
    post1 = await network.create_post(
        1, PostType.TRADE_ALERT, 
        "🚀 BTC Breakout Alert!", 
        "BTC breaking above $45,000 resistance. Long position opened! #btc #crypto #breakout",
        symbol="BTCUSD",
        action="buy",
        entry_price=45000,
        target_price=48000,
        confidence=0.85
    )
    
    # Follow users
    await network.follow_user(2, 1, FollowType.COPY_TRADE)
    await network.follow_user(3, 1, FollowType.FOLLOW)
    
    # Create trading room
    room = await network.create_trading_room(
        1, "Crypto Masters", 
        "Elite crypto trading room for experienced traders"
    )
    
    # Get analytics
    analytics = await network.get_user_analytics(1)
    print("User Analytics:", json.dumps(analytics, indent=2))
    
    # Get trending posts
    trending = await network.get_trending_posts(10)
    print(f"\nTrending Posts: {len(trending)}")
    
    # Get top traders
    top_traders = await network.get_top_traders(limit=5)
    print(f"\nTop Traders: {[t.username for t in top_traders]}")

if __name__ == "__main__":
    asyncio.run(test_social_network())
