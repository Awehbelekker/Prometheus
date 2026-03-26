"""
🎮 GAMIFICATION ENGINE
Achievement system, leaderboards, progress tracking, and educational challenges
"""

import sqlite3
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import math

logger = logging.getLogger(__name__)

class AchievementType(Enum):
    """Types of achievements"""
    TRADING_MILESTONE = "trading_milestone"
    PROFIT_TARGET = "profit_target"
    CONSISTENCY = "consistency"
    RISK_MANAGEMENT = "risk_management"
    LEARNING = "learning"
    SOCIAL = "social"
    SPECIAL_EVENT = "special_event"

class BadgeRarity(Enum):
    """Badge rarity levels"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Achievement:
    """Achievement definition"""
    achievement_id: str
    name: str
    description: str
    achievement_type: AchievementType
    rarity: BadgeRarity
    requirements: Dict[str, Any]
    rewards: Dict[str, Any]
    icon: str
    points: int
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class UserAchievement:
    """User's earned achievement"""
    user_achievement_id: str
    user_id: str
    achievement_id: str
    earned_at: datetime
    progress_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.progress_data is None:
            self.progress_data = {}

@dataclass
class UserProgress:
    """User's overall progress and stats"""
    user_id: str
    level: int
    experience_points: int
    total_achievements: int
    trading_sessions: int
    total_trades: int
    total_profit_loss: float
    best_session_return: float
    current_streak: int
    longest_streak: int
    skill_ratings: Dict[str, float]
    last_updated: datetime = None

    def __post_init__(self):
        if self.skill_ratings is None:
            self.skill_ratings = {
                "risk_management": 0.0,
                "market_analysis": 0.0,
                "timing": 0.0,
                "portfolio_management": 0.0,
                "consistency": 0.0
            }
        if self.last_updated is None:
            self.last_updated = datetime.now()

@dataclass
class LeaderboardEntry:
    """Leaderboard entry"""
    user_id: str
    username: str
    rank: int
    score: float
    metric_type: str  # 'profit', 'consistency', 'achievements', etc.
    period: str  # 'daily', 'weekly', 'monthly', 'all_time'
    additional_data: Dict[str, Any] = None

class GamificationEngine:
    """
    🎮 GAMIFICATION ENGINE
    Manages achievements, leaderboards, progress tracking, and educational challenges
    """
    
    def __init__(self, db_path: str = "gamification.db"):
        self.db_path = db_path
        self._init_database()
        self._create_default_achievements()
        logger.info("🎮 Gamification Engine initialized")

    def _init_database(self):
        """Initialize gamification database"""
        with sqlite3.connect(self.db_path) as conn:
            # Achievements table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    achievement_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    achievement_type TEXT NOT NULL,
                    rarity TEXT NOT NULL,
                    requirements TEXT NOT NULL,  -- JSON
                    rewards TEXT NOT NULL,  -- JSON
                    icon TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User achievements table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    user_achievement_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    achievement_id TEXT NOT NULL,
                    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    progress_data TEXT,  -- JSON
                    FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id)
                )
            """)
            
            # User progress table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id TEXT PRIMARY KEY,
                    level INTEGER DEFAULT 1,
                    experience_points INTEGER DEFAULT 0,
                    total_achievements INTEGER DEFAULT 0,
                    trading_sessions INTEGER DEFAULT 0,
                    total_trades INTEGER DEFAULT 0,
                    total_profit_loss REAL DEFAULT 0.0,
                    best_session_return REAL DEFAULT 0.0,
                    current_streak INTEGER DEFAULT 0,
                    longest_streak INTEGER DEFAULT 0,
                    skill_ratings TEXT,  -- JSON
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Leaderboards table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leaderboards (
                    entry_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    rank INTEGER NOT NULL,
                    score REAL NOT NULL,
                    metric_type TEXT NOT NULL,
                    period TEXT NOT NULL,
                    additional_data TEXT,  -- JSON
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Educational challenges table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS educational_challenges (
                    challenge_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,  -- JSON
                    rewards TEXT NOT NULL,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User challenge progress table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_challenge_progress (
                    progress_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    challenge_id TEXT NOT NULL,
                    status TEXT DEFAULT 'not_started',  -- 'not_started', 'in_progress', 'completed'
                    progress_data TEXT,  -- JSON
                    completed_at TIMESTAMP,
                    FOREIGN KEY (challenge_id) REFERENCES educational_challenges (challenge_id)
                )
            """)
            
            conn.commit()
            logger.info("[CHECK] Gamification database initialized")

    def _create_default_achievements(self):
        """Create default achievements"""
        default_achievements = [
            Achievement(
                achievement_id="first_trade",
                name="First Steps",
                description="Complete your first paper trade",
                achievement_type=AchievementType.TRADING_MILESTONE,
                rarity=BadgeRarity.COMMON,
                requirements={"trades_completed": 1},
                rewards={"experience_points": 100, "title": "Novice Trader"},
                icon="🎯",
                points=100
            ),
            Achievement(
                achievement_id="profitable_session",
                name="In the Green",
                description="Complete a profitable trading session",
                achievement_type=AchievementType.PROFIT_TARGET,
                rarity=BadgeRarity.COMMON,
                requirements={"session_profit": 0.01},  # 1% profit
                rewards={"experience_points": 250, "title": "Profit Maker"},
                icon="💚",
                points=250
            ),
            Achievement(
                achievement_id="week_warrior",
                name="Week Warrior",
                description="Complete a full week trading session",
                achievement_type=AchievementType.TRADING_MILESTONE,
                rarity=BadgeRarity.UNCOMMON,
                requirements={"session_hours": 168},  # 1 week
                rewards={"experience_points": 500, "title": "Endurance Trader"},
                icon="[LIGHTNING]",
                points=500
            ),
            Achievement(
                achievement_id="risk_master",
                name="Risk Master",
                description="Maintain max drawdown under 2% for 100 trades",
                achievement_type=AchievementType.RISK_MANAGEMENT,
                rarity=BadgeRarity.RARE,
                requirements={"trades_with_low_drawdown": 100, "max_drawdown": 0.02},
                rewards={"experience_points": 1000, "title": "Risk Master"},
                icon="🛡️",
                points=1000
            ),
            Achievement(
                achievement_id="consistency_king",
                name="Consistency King",
                description="Achieve positive returns for 7 consecutive sessions",
                achievement_type=AchievementType.CONSISTENCY,
                rarity=BadgeRarity.EPIC,
                requirements={"consecutive_profitable_sessions": 7},
                rewards={"experience_points": 2000, "title": "Consistency King"},
                icon="👑",
                points=2000
            ),
            Achievement(
                achievement_id="legendary_trader",
                name="Legendary Trader",
                description="Achieve 50% return in a single session",
                achievement_type=AchievementType.PROFIT_TARGET,
                rarity=BadgeRarity.LEGENDARY,
                requirements={"session_return": 0.50},  # 50% return
                rewards={"experience_points": 5000, "title": "Legendary Trader"},
                icon="🏆",
                points=5000
            )
        ]
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                for achievement in default_achievements:
                    # Check if achievement already exists
                    cursor = conn.execute(
                        "SELECT achievement_id FROM achievements WHERE achievement_id = ?",
                        (achievement.achievement_id,)
                    )
                    if cursor.fetchone():
                        continue
                    
                    # Insert new achievement
                    conn.execute("""
                        INSERT INTO achievements (
                            achievement_id, name, description, achievement_type, rarity,
                            requirements, rewards, icon, points
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        achievement.achievement_id,
                        achievement.name,
                        achievement.description,
                        achievement.achievement_type.value,
                        achievement.rarity.value,
                        json.dumps(achievement.requirements),
                        json.dumps(achievement.rewards),
                        achievement.icon,
                        achievement.points
                    ))
                
                conn.commit()
                logger.info("[CHECK] Default achievements created")
                
        except Exception as e:
            logger.error(f"Failed to create default achievements: {e}")

    def get_user_progress(self, user_id: str) -> Optional[UserProgress]:
        """Get user's progress and stats"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM user_progress WHERE user_id = ?
                """, (user_id,))

                row = cursor.fetchone()
                if not row:
                    # Create new user progress
                    return self._create_user_progress(user_id)

                return UserProgress(
                    user_id=row['user_id'],
                    level=row['level'],
                    experience_points=row['experience_points'],
                    total_achievements=row['total_achievements'],
                    trading_sessions=row['trading_sessions'],
                    total_trades=row['total_trades'],
                    total_profit_loss=row['total_profit_loss'],
                    best_session_return=row['best_session_return'],
                    current_streak=row['current_streak'],
                    longest_streak=row['longest_streak'],
                    skill_ratings=json.loads(row['skill_ratings']),
                    last_updated=datetime.fromisoformat(row['last_updated'])
                )

        except Exception as e:
            logger.error(f"Failed to get user progress: {e}")
            return None

    def _create_user_progress(self, user_id: str) -> UserProgress:
        """Create initial user progress"""
        progress = UserProgress(user_id=user_id)

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_progress (
                        user_id, level, experience_points, total_achievements,
                        trading_sessions, total_trades, total_profit_loss,
                        best_session_return, current_streak, longest_streak, skill_ratings
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    progress.user_id,
                    progress.level,
                    progress.experience_points,
                    progress.total_achievements,
                    progress.trading_sessions,
                    progress.total_trades,
                    progress.total_profit_loss,
                    progress.best_session_return,
                    progress.current_streak,
                    progress.longest_streak,
                    json.dumps(progress.skill_ratings)
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to create user progress: {e}")

        return progress

    def update_trading_session(self, user_id: str, session_data: Dict[str, Any]) -> List[Achievement]:
        """Update user progress after trading session and check for achievements"""
        try:
            progress = self.get_user_progress(user_id)
            if not progress:
                return []

            # Update progress stats
            progress.trading_sessions += 1
            progress.total_trades += session_data.get('trades_count', 0)
            session_pnl = session_data.get('profit_loss', 0.0)
            progress.total_profit_loss += session_pnl

            # Update best session return
            session_return = session_data.get('return_percentage', 0.0)
            if session_return > progress.best_session_return:
                progress.best_session_return = session_return

            # Update streak
            if session_pnl > 0:
                progress.current_streak += 1
                if progress.current_streak > progress.longest_streak:
                    progress.longest_streak = progress.current_streak
            else:
                progress.current_streak = 0

            # Update skill ratings based on session performance
            self._update_skill_ratings(progress, session_data)

            # Save updated progress
            self._save_user_progress(progress)

            # Check for new achievements
            new_achievements = self._check_achievements(user_id, progress, session_data)

            # Award experience points for achievements
            for achievement in new_achievements:
                progress.experience_points += achievement.points
                progress.total_achievements += 1

            # Update level based on experience
            new_level = self._calculate_level(progress.experience_points)
            if new_level > progress.level:
                progress.level = new_level
                logger.info(f"🎉 User {user_id} leveled up to level {new_level}!")

            # Save final progress
            self._save_user_progress(progress)

            return new_achievements

        except Exception as e:
            logger.error(f"Failed to update trading session: {e}")
            return []

    def _update_skill_ratings(self, progress: UserProgress, session_data: Dict[str, Any]):
        """Update user skill ratings based on session performance"""
        try:
            # Risk management skill
            max_drawdown = session_data.get('max_drawdown', 1.0)
            if max_drawdown < 0.05:  # Less than 5% drawdown
                progress.skill_ratings['risk_management'] = min(100.0, progress.skill_ratings['risk_management'] + 2.0)
            elif max_drawdown > 0.20:  # More than 20% drawdown
                progress.skill_ratings['risk_management'] = max(0.0, progress.skill_ratings['risk_management'] - 1.0)

            # Consistency skill
            if session_data.get('profit_loss', 0) > 0:
                progress.skill_ratings['consistency'] = min(100.0, progress.skill_ratings['consistency'] + 1.0)

            # Portfolio management skill
            trades_count = session_data.get('trades_count', 0)
            if trades_count > 0:
                avg_trade_size = session_data.get('avg_trade_size', 0)
                if 0.01 <= avg_trade_size <= 0.10:  # Good position sizing
                    progress.skill_ratings['portfolio_management'] = min(100.0, progress.skill_ratings['portfolio_management'] + 1.5)

            # Market analysis skill (based on win rate)
            win_rate = session_data.get('win_rate', 0.5)
            if win_rate > 0.6:
                progress.skill_ratings['market_analysis'] = min(100.0, progress.skill_ratings['market_analysis'] + 2.0)
            elif win_rate < 0.4:
                progress.skill_ratings['market_analysis'] = max(0.0, progress.skill_ratings['market_analysis'] - 1.0)

            # Timing skill (based on session duration vs performance)
            session_hours = session_data.get('session_hours', 1)
            return_per_hour = session_data.get('return_percentage', 0) / session_hours
            if return_per_hour > 0.1:  # Good return per hour
                progress.skill_ratings['timing'] = min(100.0, progress.skill_ratings['timing'] + 1.0)

        except Exception as e:
            logger.error(f"Failed to update skill ratings: {e}")

    def _calculate_level(self, experience_points: int) -> int:
        """Calculate user level based on experience points"""
        # Level formula: level = floor(sqrt(experience_points / 100)) + 1
        return int(math.sqrt(experience_points / 100)) + 1

    def _save_user_progress(self, progress: UserProgress):
        """Save user progress to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE user_progress SET
                        level = ?, experience_points = ?, total_achievements = ?,
                        trading_sessions = ?, total_trades = ?, total_profit_loss = ?,
                        best_session_return = ?, current_streak = ?, longest_streak = ?,
                        skill_ratings = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    progress.level,
                    progress.experience_points,
                    progress.total_achievements,
                    progress.trading_sessions,
                    progress.total_trades,
                    progress.total_profit_loss,
                    progress.best_session_return,
                    progress.current_streak,
                    progress.longest_streak,
                    json.dumps(progress.skill_ratings),
                    progress.user_id
                ))
                conn.commit()

        except Exception as e:
            logger.error(f"Failed to save user progress: {e}")

    def _check_achievements(self, user_id: str, progress: UserProgress, session_data: Dict[str, Any]) -> List[Achievement]:
        """Check if user earned any new achievements"""
        new_achievements = []

        try:
            # Get all achievements
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM achievements")
                all_achievements = cursor.fetchall()

                # Get user's existing achievements
                cursor = conn.execute("""
                    SELECT achievement_id FROM user_achievements WHERE user_id = ?
                """, (user_id,))
                earned_achievement_ids = {row['achievement_id'] for row in cursor.fetchall()}

                # Check each achievement
                for ach_row in all_achievements:
                    if ach_row['achievement_id'] in earned_achievement_ids:
                        continue  # Already earned

                    achievement = Achievement(
                        achievement_id=ach_row['achievement_id'],
                        name=ach_row['name'],
                        description=ach_row['description'],
                        achievement_type=AchievementType(ach_row['achievement_type']),
                        rarity=BadgeRarity(ach_row['rarity']),
                        requirements=json.loads(ach_row['requirements']),
                        rewards=json.loads(ach_row['rewards']),
                        icon=ach_row['icon'],
                        points=ach_row['points']
                    )

                    # Check if requirements are met
                    if self._check_achievement_requirements(achievement, progress, session_data):
                        new_achievements.append(achievement)
                        self._award_achievement(user_id, achievement)

        except Exception as e:
            logger.error(f"Failed to check achievements: {e}")

        return new_achievements

    def _check_achievement_requirements(self, achievement: Achievement, progress: UserProgress, session_data: Dict[str, Any]) -> bool:
        """Check if achievement requirements are met"""
        try:
            req = achievement.requirements

            # Trading milestone achievements
            if achievement.achievement_type == AchievementType.TRADING_MILESTONE:
                if 'trades_completed' in req:
                    return progress.total_trades >= req['trades_completed']
                if 'session_hours' in req:
                    return session_data.get('session_hours', 0) >= req['session_hours']

            # Profit target achievements
            elif achievement.achievement_type == AchievementType.PROFIT_TARGET:
                if 'session_profit' in req:
                    return session_data.get('return_percentage', 0) >= req['session_profit']
                if 'session_return' in req:
                    return session_data.get('return_percentage', 0) >= req['session_return']

            # Consistency achievements
            elif achievement.achievement_type == AchievementType.CONSISTENCY:
                if 'consecutive_profitable_sessions' in req:
                    return progress.current_streak >= req['consecutive_profitable_sessions']

            # Risk management achievements
            elif achievement.achievement_type == AchievementType.RISK_MANAGEMENT:
                if 'max_drawdown' in req and 'trades_with_low_drawdown' in req:
                    # This would need more complex tracking - simplified for now
                    return (session_data.get('max_drawdown', 1.0) <= req['max_drawdown'] and
                            progress.total_trades >= req['trades_with_low_drawdown'])

            return False

        except Exception as e:
            logger.error(f"Failed to check achievement requirements: {e}")
            return False

    def _award_achievement(self, user_id: str, achievement: Achievement):
        """Award achievement to user"""
        try:
            user_achievement = UserAchievement(
                user_achievement_id=str(uuid.uuid4()),
                user_id=user_id,
                achievement_id=achievement.achievement_id,
                earned_at=datetime.now()
            )

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_achievements (
                        user_achievement_id, user_id, achievement_id, progress_data
                    ) VALUES (?, ?, ?, ?)
                """, (
                    user_achievement.user_achievement_id,
                    user_achievement.user_id,
                    user_achievement.achievement_id,
                    json.dumps(user_achievement.progress_data)
                ))
                conn.commit()

            logger.info(f"🏆 Achievement awarded: {achievement.name} to {user_id}")

        except Exception as e:
            logger.error(f"Failed to award achievement: {e}")

# Global instance
gamification_engine = GamificationEngine()
