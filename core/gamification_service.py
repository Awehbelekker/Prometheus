"""
🎮 PROMETHEUS Trading Platform - Gamification Service
Comprehensive gamification system for Standard Users (Tier 1)
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from core.models import GamificationProgress, User, UserPermissions
from core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class BadgeType(Enum):
    # Basic Trading Badges
    FIRST_TRADE = "first_trade"
    PROFITABLE_WEEK = "profitable_week"
    TRADING_STREAK = "trading_streak"
    RISK_MANAGER = "risk_manager"
    DIVERSIFIED_PORTFOLIO = "diversified_portfolio"
    PAPER_MILLIONAIRE = "paper_millionaire"
    CONSISTENT_TRADER = "consistent_trader"
    MARKET_ANALYST = "market_analyst"

    # Advanced Engagement Badges
    SPEED_TRADER = "speed_trader"
    NIGHT_OWL = "night_owl"
    EARLY_BIRD = "early_bird"
    WEEKEND_WARRIOR = "weekend_warrior"
    VOLATILITY_MASTER = "volatility_master"
    SECTOR_SPECIALIST = "sector_specialist"
    MOMENTUM_HUNTER = "momentum_hunter"
    VALUE_INVESTOR = "value_investor"
    SWING_TRADER = "swing_trader"
    DAY_TRADER = "day_trader"

    # Social & Learning Badges
    MENTOR = "mentor"
    STUDENT = "student"
    COMMUNITY_LEADER = "community_leader"
    STRATEGY_CREATOR = "strategy_creator"
    PATTERN_SPOTTER = "pattern_spotter"
    NEWS_TRADER = "news_trader"
    TECHNICAL_ANALYST = "technical_analyst"
    FUNDAMENTAL_ANALYST = "fundamental_analyst"

    # Achievement Badges
    COMEBACK_KING = "comeback_king"
    DIAMOND_HANDS = "diamond_hands"
    PROFIT_TAKER = "profit_taker"
    LOSS_CUTTER = "loss_cutter"
    PORTFOLIO_BUILDER = "portfolio_builder"
    MARKET_TIMER = "market_timer"

class AchievementType(Enum):
    BEGINNER_TRADER = "beginner_trader"
    INTERMEDIATE_TRADER = "intermediate_trader"
    ADVANCED_TRADER = "advanced_trader"
    EXPERT_TRADER = "expert_trader"
    MASTER_TRADER = "master_trader"
    LEGENDARY_TRADER = "legendary_trader"

@dataclass
class Badge:
    """Trading badge definition"""
    type: BadgeType
    name: str
    description: str
    icon: str
    xp_reward: int
    rarity: str  # common, rare, epic, legendary

@dataclass
class Achievement:
    """Trading achievement definition"""
    type: AchievementType
    name: str
    description: str
    requirements: Dict[str, Any]
    xp_reward: int
    badge_reward: Optional[BadgeType] = None

@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    user_id: str
    username: str
    level: int
    xp_points: int
    total_trades: int
    best_daily_return: float
    trading_streak: int
    rank: int
    badges_count: int = 0
    favorite_sector: str = ""
    trading_style: str = ""
    win_rate: float = 0.0

@dataclass
class SocialFeature:
    """Social gamification feature"""
    feature_type: str  # follow, like, comment, share
    user_id: str
    target_user_id: str
    content: str = ""
    timestamp: datetime = None

@dataclass
class TradingChallenge:
    """Weekly/Monthly trading challenges"""
    challenge_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    participants: List[str]
    leaderboard: List[Dict[str, Any]]

class GamificationService:
    """Comprehensive gamification service for standard users"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.badges = self._initialize_badges()
        self.achievements = self._initialize_achievements()
        self.active_challenges = {}
        self.user_learning_data = {}  # AI learning from user movements

        logger.info("🎮 Enhanced Gamification Service initialized with AI learning")

    def _initialize_badges(self) -> Dict[BadgeType, Badge]:
        """Initialize all available badges"""
        return {
            BadgeType.FIRST_TRADE: Badge(
                type=BadgeType.FIRST_TRADE,
                name="First Steps",
                description="Executed your first trade",
                icon="🚀",
                xp_reward=100,
                rarity="common"
            ),
            BadgeType.PROFITABLE_WEEK: Badge(
                type=BadgeType.PROFITABLE_WEEK,
                name="Weekly Winner",
                description="Achieved positive returns for a full week",
                icon="📈",
                xp_reward=250,
                rarity="rare"
            ),
            BadgeType.TRADING_STREAK: Badge(
                type=BadgeType.TRADING_STREAK,
                name="Streak Master",
                description="Maintained a 10-day trading streak",
                icon="🔥",
                xp_reward=500,
                rarity="epic"
            ),
            BadgeType.RISK_MANAGER: Badge(
                type=BadgeType.RISK_MANAGER,
                name="Risk Guardian",
                description="Never exceeded 5% daily loss limit",
                icon="🛡️",
                xp_reward=300,
                rarity="rare"
            ),
            BadgeType.DIVERSIFIED_PORTFOLIO: Badge(
                type=BadgeType.DIVERSIFIED_PORTFOLIO,
                name="Diversification Expert",
                description="Held positions in 10+ different sectors",
                icon="🌐",
                xp_reward=400,
                rarity="epic"
            ),
            BadgeType.PAPER_MILLIONAIRE: Badge(
                type=BadgeType.PAPER_MILLIONAIRE,
                name="Paper Millionaire",
                description="Reached $1,000,000 in paper trading portfolio",
                icon="💎",
                xp_reward=1000,
                rarity="legendary"
            ),
            BadgeType.CONSISTENT_TRADER: Badge(
                type=BadgeType.CONSISTENT_TRADER,
                name="Consistency King",
                description="Achieved positive returns 20 days in a row",
                icon="👑",
                xp_reward=750,
                rarity="epic"
            ),
            BadgeType.MARKET_ANALYST: Badge(
                type=BadgeType.MARKET_ANALYST,
                name="Market Oracle",
                description="Correctly predicted market direction 80% of the time",
                icon="🔮",
                xp_reward=600,
                rarity="epic"
            ),
            # Enhanced engagement badges
            BadgeType.SPEED_TRADER: Badge(
                type=BadgeType.SPEED_TRADER,
                name="Lightning Fast",
                description="Executed 50 trades in under 1 hour",
                icon="[LIGHTNING]",
                xp_reward=300,
                rarity="rare"
            ),
            BadgeType.NIGHT_OWL: Badge(
                type=BadgeType.NIGHT_OWL,
                name="Night Owl Trader",
                description="Made profitable trades after midnight 10 times",
                icon="🦉",
                xp_reward=200,
                rarity="common"
            ),
            BadgeType.COMEBACK_KING: Badge(
                type=BadgeType.COMEBACK_KING,
                name="Comeback King",
                description="Recovered from 20% loss to break even",
                icon="👑",
                xp_reward=800,
                rarity="legendary"
            ),
            BadgeType.DIAMOND_HANDS: Badge(
                type=BadgeType.DIAMOND_HANDS,
                name="Diamond Hands",
                description="Held a position through 15% volatility and stayed profitable",
                icon="💎",
                xp_reward=500,
                rarity="epic"
            )
        }

    def _initialize_achievements(self) -> Dict[AchievementType, Achievement]:
        """Initialize all available achievements"""
        return {
            AchievementType.BEGINNER_TRADER: Achievement(
                type=AchievementType.BEGINNER_TRADER,
                name="Beginner Trader",
                description="Complete 10 trades and earn your first badge",
                requirements={"total_trades": 10, "badges_earned": 1},
                xp_reward=200,
                badge_reward=BadgeType.FIRST_TRADE
            ),
            AchievementType.INTERMEDIATE_TRADER: Achievement(
                type=AchievementType.INTERMEDIATE_TRADER,
                name="Intermediate Trader",
                description="Reach Level 5 and earn 3 badges",
                requirements={"level": 5, "badges_earned": 3},
                xp_reward=500
            ),
            AchievementType.ADVANCED_TRADER: Achievement(
                type=AchievementType.ADVANCED_TRADER,
                name="Advanced Trader",
                description="Reach Level 10 and maintain 15% portfolio growth",
                requirements={"level": 10, "portfolio_growth": 0.15},
                xp_reward=1000
            ),
            AchievementType.EXPERT_TRADER: Achievement(
                type=AchievementType.EXPERT_TRADER,
                name="Expert Trader",
                description="Reach Level 20 and earn 10 badges",
                requirements={"level": 20, "badges_earned": 10},
                xp_reward=2000
            ),
            AchievementType.MASTER_TRADER: Achievement(
                type=AchievementType.MASTER_TRADER,
                name="Master Trader",
                description="Reach Level 50 and achieve 50% portfolio growth",
                requirements={"level": 50, "portfolio_growth": 0.50},
                xp_reward=5000
            ),
            AchievementType.LEGENDARY_TRADER: Achievement(
                type=AchievementType.LEGENDARY_TRADER,
                name="Legendary Trader",
                description="Reach Level 100 and become a Paper Millionaire",
                requirements={"level": 100, "portfolio_value": 1000000},
                xp_reward=10000,
                badge_reward=BadgeType.PAPER_MILLIONAIRE
            )
        }

    async def award_xp(self, user_id: str, xp_amount: int, reason: str) -> Dict[str, Any]:
        """Award XP points to user and check for level ups"""
        try:
            with self.db_manager.get_session() as session:
                progress = session.query(GamificationProgress).filter_by(user_id=user_id).first()
                
                if not progress:
                    # Create new gamification progress
                    progress = GamificationProgress(
                        user_id=user_id,
                        xp_points=xp_amount,
                        level=1,
                        badges_earned=json.dumps([]),
                        achievements_unlocked=json.dumps([])
                    )
                    session.add(progress)
                else:
                    progress.xp_points += xp_amount
                    progress.last_activity = datetime.utcnow()
                
                # Calculate new level
                old_level = progress.level
                new_level = self._calculate_level(progress.xp_points)
                level_up = new_level > old_level
                
                if level_up:
                    progress.level = new_level
                
                session.commit()
                
                result = {
                    "success": True,
                    "xp_awarded": xp_amount,
                    "total_xp": progress.xp_points,
                    "level": new_level,
                    "level_up": level_up,
                    "reason": reason
                }
                
                if level_up:
                    result["level_up_rewards"] = await self._check_level_rewards(user_id, new_level)
                
                logger.info(f"[CHECK] Awarded {xp_amount} XP to user {user_id} for {reason}")
                return result
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to award XP: {e}")
            return {"success": False, "error": str(e)}

    async def award_badge(self, user_id: str, badge_type: BadgeType) -> Dict[str, Any]:
        """Award a badge to user"""
        try:
            with self.db_manager.get_session() as session:
                progress = session.query(GamificationProgress).filter_by(user_id=user_id).first()
                
                if not progress:
                    return {"success": False, "error": "User gamification progress not found"}
                
                # Check if badge already earned
                badges_earned = json.loads(progress.badges_earned or "[]")
                if badge_type.value in badges_earned:
                    return {"success": False, "error": "Badge already earned"}
                
                # Award badge
                badges_earned.append(badge_type.value)
                progress.badges_earned = json.dumps(badges_earned)
                
                # Award XP for badge
                badge = self.badges[badge_type]
                progress.xp_points += badge.xp_reward
                progress.level = self._calculate_level(progress.xp_points)
                progress.last_activity = datetime.utcnow()
                
                session.commit()
                
                logger.info(f"🏆 Awarded badge {badge_type.value} to user {user_id}")
                
                return {
                    "success": True,
                    "badge": {
                        "type": badge_type.value,
                        "name": badge.name,
                        "description": badge.description,
                        "icon": badge.icon,
                        "rarity": badge.rarity
                    },
                    "xp_reward": badge.xp_reward,
                    "total_badges": len(badges_earned)
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to award badge: {e}")
            return {"success": False, "error": str(e)}

    async def get_leaderboard(self, limit: int = 50) -> List[LeaderboardEntry]:
        """Get gamification leaderboard"""
        try:
            with self.db_manager.get_session() as session:
                # Query top users by XP
                results = session.query(
                    GamificationProgress.user_id,
                    GamificationProgress.xp_points,
                    GamificationProgress.level,
                    GamificationProgress.total_trades,
                    GamificationProgress.best_daily_return,
                    GamificationProgress.trading_streak,
                    User.username
                ).join(User, GamificationProgress.user_id == User.id)\
                .order_by(GamificationProgress.xp_points.desc())\
                .limit(limit).all()
                
                leaderboard = []
                for rank, result in enumerate(results, 1):
                    leaderboard.append(LeaderboardEntry(
                        user_id=result.user_id,
                        username=result.username,
                        level=result.level,
                        xp_points=result.xp_points,
                        total_trades=result.total_trades,
                        best_daily_return=result.best_daily_return,
                        trading_streak=result.trading_streak,
                        rank=rank
                    ))
                
                return leaderboard
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to get leaderboard: {e}")
            return []

    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's gamification progress"""
        try:
            with self.db_manager.get_session() as session:
                progress = session.query(GamificationProgress).filter_by(user_id=user_id).first()
                
                if not progress:
                    return {"success": False, "error": "User progress not found"}
                
                badges_earned = json.loads(progress.badges_earned or "[]")
                achievements_unlocked = json.loads(progress.achievements_unlocked or "[]")
                
                # Calculate XP needed for next level
                current_xp = progress.xp_points
                next_level_xp = self._xp_for_level(progress.level + 1)
                xp_to_next_level = next_level_xp - current_xp
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "level": progress.level,
                    "xp_points": progress.xp_points,
                    "xp_to_next_level": xp_to_next_level,
                    "total_trades": progress.total_trades,
                    "trading_streak": progress.trading_streak,
                    "best_daily_return": progress.best_daily_return,
                    "badges_earned": [self.badges[BadgeType(badge)] for badge in badges_earned if badge in [b.value for b in BadgeType]],
                    "achievements_unlocked": achievements_unlocked,
                    "leaderboard_rank": progress.leaderboard_rank,
                    "last_activity": progress.last_activity.isoformat() if progress.last_activity else None
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to get user progress: {e}")
            return {"success": False, "error": str(e)}

    def _calculate_level(self, xp_points: int) -> int:
        """Calculate level based on XP points"""
        # Level formula: Level = floor(sqrt(XP / 100))
        # Level 1: 100 XP, Level 2: 400 XP, Level 3: 900 XP, etc.
        import math
        return max(1, int(math.sqrt(xp_points / 100)))

    def _xp_for_level(self, level: int) -> int:
        """Calculate XP required for a specific level"""
        return level * level * 100

    async def _check_level_rewards(self, user_id: str, level: int) -> List[Dict[str, Any]]:
        """Check and award level-up rewards"""
        rewards = []
        
        # Level milestone rewards
        if level == 5:
            rewards.append({"type": "badge", "badge": BadgeType.CONSISTENT_TRADER})
        elif level == 10:
            rewards.append({"type": "xp_bonus", "amount": 500})
        elif level == 25:
            rewards.append({"type": "badge", "badge": BadgeType.MARKET_ANALYST})
        elif level == 50:
            rewards.append({"type": "badge", "badge": BadgeType.PAPER_MILLIONAIRE})
        
        return rewards

    async def track_user_movement(self, user_id: str, action_type: str, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track user movement and learn from behavior - integrates with existing AI learning engine"""
        try:
            # Import existing AI learning engine
            from core.ai_learning_engine import get_ai_learning_engine

            # Get AI learning engine instance
            ai_engine = get_ai_learning_engine()

            # Track the movement in AI engine
            await ai_engine.record_user_action(user_id, action_type, action_data)

            # Update user learning data for gamification
            if user_id not in self.user_learning_data:
                self.user_learning_data[user_id] = {
                    "total_actions": 0,
                    "trading_patterns": {},
                    "preferred_times": [],
                    "risk_tolerance": 0.5,
                    "learning_progress": 0.0
                }

            # Update learning data
            self.user_learning_data[user_id]["total_actions"] += 1
            self.user_learning_data[user_id]["learning_progress"] = min(1.0,
                self.user_learning_data[user_id]["total_actions"] / 1000.0)

            # Check for automatic badge awards based on AI learning
            badges_awarded = await self._check_ai_learning_badges(user_id, action_type, action_data)

            # Award XP for engagement
            xp_reward = self._calculate_engagement_xp(action_type, action_data)
            if xp_reward > 0:
                await self.award_xp(user_id, xp_reward, f"Engagement: {action_type}")

            logger.info(f"🧠 Tracked user movement: {user_id} - {action_type}")

            return {
                "success": True,
                "action_tracked": action_type,
                "xp_awarded": xp_reward,
                "badges_awarded": badges_awarded,
                "learning_progress": self.user_learning_data[user_id]["learning_progress"]
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to track user movement: {e}")
            return {"success": False, "error": str(e)}

    async def _check_ai_learning_badges(self, user_id: str, action_type: str, action_data: Dict[str, Any]) -> List[str]:
        """Check for badges based on AI learning patterns"""
        badges_awarded = []

        try:
            # Speed trading detection
            if action_type == "trade_executed" and action_data.get("execution_time", 0) < 5:
                if await self._check_speed_trading_pattern(user_id):
                    result = await self.award_badge(user_id, BadgeType.SPEED_TRADER)
                    if result.get("success"):
                        badges_awarded.append("speed_trader")

            # Night owl detection
            if action_type == "trade_executed":
                from datetime import datetime
                current_hour = datetime.now().hour
                if 22 <= current_hour or current_hour <= 6:
                    if await self._check_night_trading_pattern(user_id):
                        result = await self.award_badge(user_id, BadgeType.NIGHT_OWL)
                        if result.get("success"):
                            badges_awarded.append("night_owl")

            # Diamond hands detection
            if action_type == "position_held" and action_data.get("volatility", 0) > 0.15:
                if action_data.get("still_profitable", False):
                    result = await self.award_badge(user_id, BadgeType.DIAMOND_HANDS)
                    if result.get("success"):
                        badges_awarded.append("diamond_hands")

            return badges_awarded

        except Exception as e:
            logger.error(f"[ERROR] Failed to check AI learning badges: {e}")
            return []

    def _calculate_engagement_xp(self, action_type: str, action_data: Dict[str, Any]) -> int:
        """Calculate XP reward based on engagement type"""
        xp_rewards = {
            "trade_executed": 10,
            "market_analysis": 5,
            "portfolio_check": 2,
            "strategy_created": 25,
            "position_held": 3,
            "risk_managed": 15,
            "learning_completed": 20,
            "social_interaction": 8
        }

        base_xp = xp_rewards.get(action_type, 1)

        # Bonus XP for quality actions
        if action_data.get("profitable", False):
            base_xp *= 2
        if action_data.get("risk_managed", False):
            base_xp += 5

        return base_xp

    async def _check_speed_trading_pattern(self, user_id: str) -> bool:
        """Check if user has speed trading pattern (50 trades in 1 hour)"""
        # This would integrate with the existing AI learning engine
        # For now, return a simple check
        return self.user_learning_data.get(user_id, {}).get("total_actions", 0) > 50

    async def _check_night_trading_pattern(self, user_id: str) -> bool:
        """Check if user has night trading pattern (10 profitable night trades)"""
        # This would integrate with the existing AI learning engine
        return self.user_learning_data.get(user_id, {}).get("total_actions", 0) > 20

    async def create_daily_challenge(self, challenge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create daily trading challenge to increase engagement"""
        try:
            challenge_id = f"daily_{datetime.now().strftime('%Y%m%d')}"

            challenge = TradingChallenge(
                challenge_id=challenge_id,
                name=challenge_data.get("name", "Daily Trading Challenge"),
                description=challenge_data.get("description", "Complete today's trading objectives"),
                start_date=datetime.now(),
                end_date=datetime.now() + timedelta(days=1),
                requirements=challenge_data.get("requirements", {"trades": 5, "profit": 0.02}),
                rewards=challenge_data.get("rewards", {"xp": 500, "badge": None}),
                participants=[],
                leaderboard=[]
            )

            self.active_challenges[challenge_id] = challenge

            logger.info(f"🎯 Created daily challenge: {challenge_id}")

            return {
                "success": True,
                "challenge_id": challenge_id,
                "challenge": challenge
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to create daily challenge: {e}")
            return {"success": False, "error": str(e)}

# Global service instance
gamification_service = None

def get_gamification_service() -> GamificationService:
    """Get global gamification service instance"""
    global gamification_service
    if gamification_service is None:
        from core.database_manager import db_manager
        gamification_service = GamificationService(db_manager)
    return gamification_service
