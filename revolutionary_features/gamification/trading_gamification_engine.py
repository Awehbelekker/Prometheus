"""
🎮 REVOLUTIONARY GAMIFICATION SYSTEM
Transform trading into an addictive, engaging gaming experience
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from enum import Enum
import random
import math

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    TRADING_MILESTONE = "trading_milestone"
    PROFIT_ACHIEVEMENT = "profit_achievement"
    CONSISTENCY_AWARD = "consistency_award"
    RISK_MANAGEMENT = "risk_management"
    LEARNING_PROGRESS = "learning_progress"
    SOCIAL_ACHIEVEMENT = "social_achievement"
    SPECIAL_EVENT = "special_event"
    LEGENDARY_FEAT = "legendary_feat"

class BadgeRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"

class TradingLevel(Enum):
    NOVICE_TRADER = 1
    APPRENTICE_TRADER = 2
    SKILLED_TRADER = 3
    EXPERT_TRADER = 4
    MASTER_TRADER = 5
    GRANDMASTER_TRADER = 6
    LEGENDARY_TRADER = 7
    MYTHICAL_TRADER = 8
    GODLIKE_TRADER = 9
    PROMETHEUS_INCARNATE = 10

@dataclass
class TradingBadge:
    """Trading achievement badge with beautiful design"""
    badge_id: str
    name: str
    description: str
    rarity: BadgeRarity
    icon: str  # SVG or emoji
    color_scheme: Dict[str, str]
    unlock_criteria: Dict[str, Any]
    xp_reward: int
    monetary_bonus: float  # Bonus for achieving this
    special_abilities: List[str] = field(default_factory=list)
    earned_at: Optional[datetime] = None
    is_unlocked: bool = False

@dataclass
class TradingQuest:
    """Daily/Weekly trading quests for engagement"""
    quest_id: str
    title: str
    description: str
    quest_type: str  # daily, weekly, monthly, special
    difficulty: str  # easy, medium, hard, legendary
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    xp_reward: int
    time_limit: timedelta
    created_at: datetime
    expires_at: datetime
    is_completed: bool = False
    progress: float = 0.0

@dataclass
class TradingStreak:
    """Trading streak tracking for motivation"""
    streak_type: str  # profitable_days, trading_days, perfect_weeks
    current_streak: int
    longest_streak: int
    streak_multiplier: float
    last_update: datetime
    bonus_active: bool = False

@dataclass
class PlayerStats:
    """Comprehensive player statistics and progression"""
    user_id: int
    level: TradingLevel
    total_xp: int
    current_level_xp: int
    xp_to_next_level: int
    
    # Trading statistics
    total_trades: int
    profitable_trades: int
    win_rate: float
    total_profit: float
    largest_win: float
    largest_loss: float
    
    # Achievements
    badges_earned: List[TradingBadge] = field(default_factory=list)
    quests_completed: int = 0
    streaks: Dict[str, TradingStreak] = field(default_factory=dict)
    
    # Social features
    reputation_score: int = 1000
    followers: int = 0
    following: int = 0
    
    # Special abilities unlocked
    abilities: List[str] = field(default_factory=list)
    
    # Performance multipliers from achievements
    profit_multiplier: float = 1.0
    xp_multiplier: float = 1.0
    fee_discount: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

class TradingGamificationEngine:
    """Revolutionary gamification system for trading"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.player_stats: Dict[int, PlayerStats] = {}
        self.badges = self._initialize_badges()
        self.daily_quests = self._initialize_daily_quests()
        self.level_requirements = self._initialize_level_requirements()
        
    def _initialize_badges(self) -> Dict[str, TradingBadge]:
        """Initialize all available trading badges"""
        badges = {}
        
        # Profit Achievement Badges
        badges["first_profit"] = TradingBadge(
            badge_id="first_profit",
            name="First Blood 💰",
            description="Your first profitable trade! The journey begins.",
            rarity=BadgeRarity.COMMON,
            icon="💰",
            color_scheme={"primary": "#4CAF50", "secondary": "#81C784"},
            unlock_criteria={"profitable_trades": 1},
            xp_reward=100,
            monetary_bonus=10.0
        )
        
        badges["profit_hunter"] = TradingBadge(
            badge_id="profit_hunter",
            name="Profit Hunter 🎯",
            description="100 profitable trades! You're getting the hang of this.",
            rarity=BadgeRarity.UNCOMMON,
            icon="🎯",
            color_scheme={"primary": "#2196F3", "secondary": "#64B5F6"},
            unlock_criteria={"profitable_trades": 100},
            xp_reward=500,
            monetary_bonus=100.0,
            special_abilities=["reduced_fees_5percent"]
        )
        
        badges["profit_master"] = TradingBadge(
            badge_id="profit_master",
            name="Profit Master 👑",
            description="1000 profitable trades! You're becoming a true master.",
            rarity=BadgeRarity.RARE,
            icon="👑",
            color_scheme={"primary": "#FF9800", "secondary": "#FFB74D"},
            unlock_criteria={"profitable_trades": 1000},
            xp_reward=2000,
            monetary_bonus=500.0,
            special_abilities=["reduced_fees_10percent", "priority_execution"]
        )
        
        badges["profit_legend"] = TradingBadge(
            badge_id="profit_legend",
            name="Profit Legend [LIGHTNING]",
            description="5000 profitable trades! You're legendary!",
            rarity=BadgeRarity.LEGENDARY,
            icon="[LIGHTNING]",
            color_scheme={"primary": "#9C27B0", "secondary": "#BA68C8"},
            unlock_criteria={"profitable_trades": 5000},
            xp_reward=10000,
            monetary_bonus=2500.0,
            special_abilities=["reduced_fees_15percent", "priority_execution", "bonus_multiplier_1_1x"]
        )
        
        # Consistency Badges
        badges["week_warrior"] = TradingBadge(
            badge_id="week_warrior",
            name="Week Warrior 📅",
            description="Profitable for 7 consecutive days!",
            rarity=BadgeRarity.UNCOMMON,
            icon="📅",
            color_scheme={"primary": "#795548", "secondary": "#A1887F"},
            unlock_criteria={"profitable_streak_days": 7},
            xp_reward=300,
            monetary_bonus=50.0
        )
        
        badges["month_champion"] = TradingBadge(
            badge_id="month_champion",
            name="Month Champion 🏆",
            description="Profitable for 30 consecutive days! Incredible consistency!",
            rarity=BadgeRarity.EPIC,
            icon="🏆",
            color_scheme={"primary": "#FF5722", "secondary": "#FF8A65"},
            unlock_criteria={"profitable_streak_days": 30},
            xp_reward=1500,
            monetary_bonus=300.0,
            special_abilities=["streak_multiplier_1_2x"]
        )
        
        # Risk Management Badges
        badges["risk_master"] = TradingBadge(
            badge_id="risk_master",
            name="Risk Master 🛡️",
            description="Maximum 2% loss per trade for 100 trades!",
            rarity=BadgeRarity.RARE,
            icon="🛡️",
            color_scheme={"primary": "#607D8B", "secondary": "#90A4AE"},
            unlock_criteria={"max_loss_per_trade": 0.02, "trades_with_good_risk": 100},
            xp_reward=800,
            monetary_bonus=200.0,
            special_abilities=["risk_bonus_5percent"]
        )
        
        # Learning Badges
        badges["ai_student"] = TradingBadge(
            badge_id="ai_student",
            name="AI Student 🎓",
            description="Follow AI recommendations for 50 trades!",
            rarity=BadgeRarity.COMMON,
            icon="🎓",
            color_scheme={"primary": "#3F51B5", "secondary": "#7986CB"},
            unlock_criteria={"ai_recommended_trades": 50},
            xp_reward=250,
            monetary_bonus=25.0
        )
        
        # Social Badges
        badges["influencer"] = TradingBadge(
            badge_id="influencer",
            name="Trading Influencer 🌟",
            description="100 followers! Your trading attracts attention.",
            rarity=BadgeRarity.EPIC,
            icon="🌟",
            color_scheme={"primary": "#E91E63", "secondary": "#F06292"},
            unlock_criteria={"followers": 100},
            xp_reward=1000,
            monetary_bonus=100.0,
            special_abilities=["social_bonus_multiplier"]
        )
        
        # Legendary Achievements
        badges["prometheus_heir"] = TradingBadge(
            badge_id="prometheus_heir",
            name="Prometheus Heir 🔥",
            description="$1M total profit! You've mastered the fire of trading!",
            rarity=BadgeRarity.MYTHICAL,
            icon="🔥",
            color_scheme={"primary": "#FF6F00", "secondary": "#FFB300"},
            unlock_criteria={"total_profit": 1000000},
            xp_reward=50000,
            monetary_bonus=10000.0,
            special_abilities=["all_fees_waived", "vip_status", "profit_multiplier_1_5x"]
        )
        
        return badges
    
    def _initialize_daily_quests(self) -> List[TradingQuest]:
        """Initialize daily trading quests"""
        quest_templates = [
            {
                "title": "Daily Profit Hunter",
                "description": "Make 3 profitable trades today",
                "difficulty": "easy",
                "objectives": [{"type": "profitable_trades", "target": 3}],
                "xp_reward": 150,
                "rewards": {"bonus_cash": 25.0}
            },
            {
                "title": "Risk Management Master",
                "description": "Keep all losses under 1% today",
                "difficulty": "medium",
                "objectives": [{"type": "max_loss_percentage", "target": 0.01}],
                "xp_reward": 200,
                "rewards": {"bonus_cash": 50.0, "fee_discount": 0.1}
            },
            {
                "title": "Volume Warrior",
                "description": "Execute $10,000 in total trading volume",
                "difficulty": "hard",
                "objectives": [{"type": "trading_volume", "target": 10000}],
                "xp_reward": 300,
                "rewards": {"bonus_cash": 100.0, "xp_multiplier": 1.2}
            },
            {
                "title": "AI Synergy",
                "description": "Follow AI recommendations for 5 trades",
                "difficulty": "easy",
                "objectives": [{"type": "ai_recommended_trades", "target": 5}],
                "xp_reward": 100,
                "rewards": {"bonus_cash": 20.0}
            },
            {
                "title": "Perfect Trader",
                "description": "Achieve 100% win rate with minimum 5 trades",
                "difficulty": "legendary",
                "objectives": [
                    {"type": "win_rate", "target": 1.0},
                    {"type": "minimum_trades", "target": 5}
                ],
                "xp_reward": 1000,
                "rewards": {"bonus_cash": 500.0, "special_badge": "daily_perfection"}
            }
        ]
        
        quests = []
        for i, template in enumerate(quest_templates):
            quest = TradingQuest(
                quest_id=f"daily_{i}_{datetime.utcnow().strftime('%Y%m%d')}",
                title=template["title"],
                description=template["description"],
                quest_type="daily",
                difficulty=template["difficulty"],
                objectives=template["objectives"],
                rewards=template["rewards"],
                xp_reward=template["xp_reward"],
                time_limit=timedelta(days=1),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=1)
            )
            quests.append(quest)
            
        return quests
    
    def _initialize_level_requirements(self) -> Dict[TradingLevel, int]:
        """Initialize XP requirements for each level"""
        return {
            TradingLevel.NOVICE_TRADER: 0,
            TradingLevel.APPRENTICE_TRADER: 1000,
            TradingLevel.SKILLED_TRADER: 3000,
            TradingLevel.EXPERT_TRADER: 7000,
            TradingLevel.MASTER_TRADER: 15000,
            TradingLevel.GRANDMASTER_TRADER: 30000,
            TradingLevel.LEGENDARY_TRADER: 60000,
            TradingLevel.MYTHICAL_TRADER: 100000,
            TradingLevel.GODLIKE_TRADER: 200000,
            TradingLevel.PROMETHEUS_INCARNATE: 500000
        }
    
    async def initialize_player(self, user_id: int) -> PlayerStats:
        """Initialize a new player in the gamification system"""
        if user_id in self.player_stats:
            return self.player_stats[user_id]
        
        player = PlayerStats(
            user_id=user_id,
            level=TradingLevel.NOVICE_TRADER,
            total_xp=0,
            current_level_xp=0,
            xp_to_next_level=1000,
            total_trades=0,
            profitable_trades=0,
            win_rate=0.0,
            total_profit=0.0,
            largest_win=0.0,
            largest_loss=0.0
        )
        
        # Initialize streaks
        player.streaks = {
            "profitable_days": TradingStreak(
                streak_type="profitable_days",
                current_streak=0,
                longest_streak=0,
                streak_multiplier=1.0,
                last_update=datetime.utcnow()
            ),
            "trading_days": TradingStreak(
                streak_type="trading_days",
                current_streak=0,
                longest_streak=0,
                streak_multiplier=1.0,
                last_update=datetime.utcnow()
            )
        }
        
        self.player_stats[user_id] = player
        logger.info(f"Initialized player {user_id} in gamification system")
        return player
    
    async def process_trade_completion(self, user_id: int, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process completed trade for gamification rewards"""
        player = await self.initialize_player(user_id)
        
        # Extract trade information
        profit = trade_data.get('pnl', 0.0)
        trade_value = trade_data.get('value', 0.0)
        is_profitable = profit > 0
        loss_percentage = abs(profit / trade_value) if trade_value > 0 and profit < 0 else 0
        
        # Update player statistics
        player.total_trades += 1
        if is_profitable:
            player.profitable_trades += 1
            player.total_profit += profit
            if profit > player.largest_win:
                player.largest_win = profit
        else:
            if abs(profit) > abs(player.largest_loss):
                player.largest_loss = profit
        
        player.win_rate = player.profitable_trades / player.total_trades
        
        # Calculate base XP reward
        base_xp = 10  # Base XP per trade
        if is_profitable:
            base_xp += 20  # Bonus for profitable trades
            base_xp += int(profit * 0.1)  # XP based on profit amount
        
        # Apply multipliers
        total_xp = int(base_xp * player.xp_multiplier)
        
        # Award XP
        await self.award_xp(user_id, total_xp)
        
        # Update streaks
        await self.update_streaks(user_id, is_profitable)
        
        # Check for achievements
        achievements = await self.check_achievements(user_id)
        
        # Check quest progress
        quest_progress = await self.update_quest_progress(user_id, trade_data)
        
        # Generate rewards summary
        rewards = {
            "xp_earned": total_xp,
            "new_achievements": achievements,
            "quest_progress": quest_progress,
            "streak_bonuses": await self.calculate_streak_bonuses(user_id),
            "level_up": await self.check_level_up(user_id),
            "monetary_bonus": await self.calculate_monetary_bonus(user_id, trade_data)
        }
        
        player.last_updated = datetime.utcnow()
        
        logger.info(f"Processed trade for player {user_id}: {rewards}")
        return rewards
    
    async def award_xp(self, user_id: int, xp_amount: int) -> bool:
        """Award XP to a player"""
        if user_id not in self.player_stats:
            await self.initialize_player(user_id)
        
        player = self.player_stats[user_id]
        player.total_xp += xp_amount
        player.current_level_xp += xp_amount
        
        logger.info(f"Awarded {xp_amount} XP to player {user_id}")
        return True
    
    async def check_level_up(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Check if player leveled up and handle level up"""
        player = self.player_stats[user_id]
        current_level_value = player.level.value
        
        # Find the highest level the player qualifies for
        for level in TradingLevel:
            required_xp = self.level_requirements[level]
            if player.total_xp >= required_xp and level.value > current_level_value:
                player.level = level
                
                # Calculate XP for next level
                next_level_xp = float('inf')
                for next_level in TradingLevel:
                    if next_level.value == level.value + 1:
                        next_level_xp = self.level_requirements[next_level]
                        break
                
                player.xp_to_next_level = next_level_xp - player.total_xp if next_level_xp != float('inf') else 0
                player.current_level_xp = player.total_xp - required_xp
                
                # Level up rewards
                level_rewards = await self.calculate_level_up_rewards(level)
                
                logger.info(f"Player {user_id} leveled up to {level.name}!")
                
                return {
                    "new_level": level.name,
                    "level_number": level.value,
                    "rewards": level_rewards,
                    "xp_to_next": player.xp_to_next_level
                }
        
        return None
    
    async def calculate_level_up_rewards(self, level: TradingLevel) -> Dict[str, Any]:
        """Calculate rewards for leveling up"""
        base_cash_reward = level.value * 100
        special_abilities = []
        
        # Special abilities unlocked at certain levels
        if level.value >= 3:
            special_abilities.append("advanced_analytics")
        if level.value >= 5:
            special_abilities.append("ai_strategy_builder")
        if level.value >= 7:
            special_abilities.append("vip_support")
        if level.value >= 9:
            special_abilities.append("exclusive_signals")
        
        return {
            "cash_bonus": base_cash_reward,
            "special_abilities": special_abilities,
            "fee_discount": min(0.25, level.value * 0.02),  # Up to 25% fee discount
            "title": f"{level.name.replace('_', ' ').title()}"
        }
    
    async def check_achievements(self, user_id: int) -> List[Dict[str, Any]]:
        """Check if player unlocked any new achievements"""
        player = self.player_stats[user_id]
        new_achievements = []
        
        for badge_id, badge in self.badges.items():
            # Skip if already unlocked
            if any(b.badge_id == badge_id for b in player.badges_earned):
                continue
            
            # Check unlock criteria
            criteria_met = True
            for criterion, target in badge.unlock_criteria.items():
                if criterion == "profitable_trades" and player.profitable_trades < target:
                    criteria_met = False
                elif criterion == "total_profit" and player.total_profit < target:
                    criteria_met = False
                elif criterion == "followers" and player.followers < target:
                    criteria_met = False
                # Add more criteria checks as needed
            
            if criteria_met:
                # Unlock the badge
                badge.is_unlocked = True
                badge.earned_at = datetime.utcnow()
                player.badges_earned.append(badge)
                
                # Award XP and bonus
                await self.award_xp(user_id, badge.xp_reward)
                
                # Apply special abilities
                for ability in badge.special_abilities:
                    if ability not in player.abilities:
                        player.abilities.append(ability)
                        await self.apply_special_ability(user_id, ability)
                
                new_achievements.append({
                    "badge": {
                        "id": badge.badge_id,
                        "name": badge.name,
                        "description": badge.description,
                        "rarity": badge.rarity.value,
                        "icon": badge.icon,
                        "color_scheme": badge.color_scheme
                    },
                    "rewards": {
                        "xp": badge.xp_reward,
                        "cash_bonus": badge.monetary_bonus,
                        "special_abilities": badge.special_abilities
                    }
                })
                
                logger.info(f"Player {user_id} unlocked achievement: {badge.name}")
        
        return new_achievements
    
    async def apply_special_ability(self, user_id: int, ability: str) -> None:
        """Apply special ability effects to player"""
        player = self.player_stats[user_id]
        
        if ability == "reduced_fees_5percent":
            player.fee_discount = max(player.fee_discount, 0.05)
        elif ability == "reduced_fees_10percent":
            player.fee_discount = max(player.fee_discount, 0.10)
        elif ability == "reduced_fees_15percent":
            player.fee_discount = max(player.fee_discount, 0.15)
        elif ability == "bonus_multiplier_1_1x":
            player.profit_multiplier = max(player.profit_multiplier, 1.1)
        elif ability == "profit_multiplier_1_5x":
            player.profit_multiplier = max(player.profit_multiplier, 1.5)
        elif ability == "streak_multiplier_1_2x":
            for streak in player.streaks.values():
                streak.streak_multiplier = max(streak.streak_multiplier, 1.2)
        elif ability == "all_fees_waived":
            player.fee_discount = 1.0  # 100% fee discount
        
        logger.info(f"Applied special ability {ability} to player {user_id}")
    
    async def update_streaks(self, user_id: int, is_profitable: bool) -> None:
        """Update player's trading streaks"""
        player = self.player_stats[user_id]
        today = datetime.utcnow().date()
        
        # Update trading days streak
        trading_streak = player.streaks["trading_days"]
        if trading_streak.last_update.date() < today:
            trading_streak.current_streak += 1
            trading_streak.longest_streak = max(trading_streak.longest_streak, trading_streak.current_streak)
            trading_streak.last_update = datetime.utcnow()
        
        # Update profitable days streak
        profitable_streak = player.streaks["profitable_days"]
        if is_profitable:
            if profitable_streak.last_update.date() < today:
                profitable_streak.current_streak += 1
                profitable_streak.longest_streak = max(profitable_streak.longest_streak, profitable_streak.current_streak)
                profitable_streak.last_update = datetime.utcnow()
        else:
            # Reset profitable streak on losing day
            profitable_streak.current_streak = 0
    
    async def update_quest_progress(self, user_id: int, trade_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Update progress on active quests"""
        # This would be implemented to track quest progress
        # For now, return empty list
        return []
    
    async def calculate_streak_bonuses(self, user_id: int) -> Dict[str, Any]:
        """Calculate bonuses from active streaks"""
        player = self.player_stats[user_id]
        bonuses = {}
        
        for streak_type, streak in player.streaks.items():
            if streak.current_streak > 0:
                bonus_amount = streak.current_streak * 10 * streak.streak_multiplier
                bonuses[streak_type] = {
                    "streak_length": streak.current_streak,
                    "bonus_amount": bonus_amount,
                    "multiplier": streak.streak_multiplier
                }
        
        return bonuses
    
    async def calculate_monetary_bonus(self, user_id: int, trade_data: Dict[str, Any]) -> float:
        """Calculate monetary bonus based on achievements and streaks"""
        player = self.player_stats[user_id]
        
        # Base bonus from profit multiplier
        profit = trade_data.get('pnl', 0.0)
        bonus = 0.0
        
        if profit > 0:
            bonus = profit * (player.profit_multiplier - 1.0)
        
        # Add streak bonuses
        streak_bonuses = await self.calculate_streak_bonuses(user_id)
        for streak_data in streak_bonuses.values():
            bonus += streak_data["bonus_amount"]
        
        return bonus
    
    async def get_player_dashboard(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive player dashboard data"""
        player = await self.initialize_player(user_id)
        
        # Get recent achievements
        recent_badges = sorted(
            [b for b in player.badges_earned if b.earned_at],
            key=lambda x: x.earned_at,
            reverse=True
        )[:5]
        
        # Get active quests
        active_quests = [q for q in self.daily_quests if not q.is_completed]
        
        return {
            "player_info": {
                "level": player.level.name.replace('_', ' ').title(),
                "level_number": player.level.value,
                "total_xp": player.total_xp,
                "xp_to_next_level": player.xp_to_next_level,
                "reputation_score": player.reputation_score
            },
            "trading_stats": {
                "total_trades": player.total_trades,
                "win_rate": f"{player.win_rate:.1%}",
                "total_profit": f"${player.total_profit:,.2f}",
                "largest_win": f"${player.largest_win:,.2f}",
                "largest_loss": f"${player.largest_loss:,.2f}"
            },
            "achievements": {
                "total_badges": len(player.badges_earned),
                "recent_badges": [
                    {
                        "name": b.name,
                        "icon": b.icon,
                        "rarity": b.rarity.value,
                        "earned_at": b.earned_at.isoformat() if b.earned_at else None
                    }
                    for b in recent_badges
                ]
            },
            "streaks": {
                streak_type: {
                    "current": streak.current_streak,
                    "longest": streak.longest_streak,
                    "multiplier": streak.streak_multiplier
                }
                for streak_type, streak in player.streaks.items()
            },
            "active_quests": [
                {
                    "title": q.title,
                    "description": q.description,
                    "progress": f"{q.progress:.0%}",
                    "xp_reward": q.xp_reward,
                    "time_remaining": str(q.expires_at - datetime.utcnow()).split('.')[0]
                }
                for q in active_quests[:3]  # Show top 3
            ],
            "special_abilities": player.abilities,
            "multipliers": {
                "profit_multiplier": f"{player.profit_multiplier:.1f}x",
                "xp_multiplier": f"{player.xp_multiplier:.1f}x",
                "fee_discount": f"{player.fee_discount:.0%}"
            }
        }
    
    async def get_leaderboard(self, leaderboard_type: str = "total_profit", limit: int = 100) -> List[Dict[str, Any]]:
        """Get trading leaderboard"""
        players = list(self.player_stats.values())
        
        if leaderboard_type == "total_profit":
            players.sort(key=lambda p: p.total_profit, reverse=True)
        elif leaderboard_type == "win_rate":
            players.sort(key=lambda p: p.win_rate, reverse=True)
        elif leaderboard_type == "total_xp":
            players.sort(key=lambda p: p.total_xp, reverse=True)
        elif leaderboard_type == "level":
            players.sort(key=lambda p: p.level.value, reverse=True)
        
        leaderboard = []
        for i, player in enumerate(players[:limit]):
            leaderboard.append({
                "rank": i + 1,
                "user_id": player.user_id,
                "level": player.level.name.replace('_', ' ').title(),
                "total_profit": player.total_profit,
                "win_rate": player.win_rate,
                "total_xp": player.total_xp,
                "badges_count": len(player.badges_earned),
                "reputation": player.reputation_score
            })
        
        return leaderboard

# Global instance
gamification_engine = None

def get_gamification_engine(config: Dict[str, Any] = None) -> TradingGamificationEngine:
    """Get or create the global gamification engine instance"""
    global gamification_engine
    if gamification_engine is None:
        gamification_engine = TradingGamificationEngine(config or {})
    return gamification_engine

# Example usage
async def test_gamification_system():
    """Test the gamification system"""
    engine = get_gamification_engine()
    
    # Initialize a player
    player = await engine.initialize_player(1)
    print(f"Initialized player: {player.level.name}")
    
    # Simulate some trades
    for i in range(10):
        trade_data = {
            "pnl": random.uniform(-50, 150),
            "value": 1000,
            "is_ai_recommended": random.choice([True, False])
        }
        
        rewards = await engine.process_trade_completion(1, trade_data)
        print(f"Trade {i+1} rewards: {rewards}")
    
    # Get player dashboard
    dashboard = await engine.get_player_dashboard(1)
    print(f"\nPlayer Dashboard: {json.dumps(dashboard, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_gamification_system())
