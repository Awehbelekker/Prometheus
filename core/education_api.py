"""
Education API module for MASS Framework
Handles skill assessment, learning paths, group projects, and gamification
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio
import random

class SkillLevel(Enum):
    BEGINNER = "beginner"
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ProjectStatus(Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"

@dataclass
class UserSkills:
    programming_fundamentals: int = 0
    problem_solving: int = 0
    advanced_concepts: int = 0
    collaboration: int = 0
    creativity: int = 0

@dataclass
class LearningPreferences:
    learning_style: str = ""  # visual, hands-on, reading, collaborative
    preferred_pace: str = "normal"  # slow, normal, fast
    difficulty_preference: str = "adaptive"  # easy, adaptive, challenging

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    icon: str
    xp_reward: int
    unlocked_at: Optional[datetime] = None

@dataclass
class LearningPath:
    id: str
    name: str
    description: str
    lessons: List[str]
    estimated_duration: int  # in minutes
    skill_requirements: Dict[str, int]
    skill_rewards: Dict[str, int]

@dataclass
class GroupProject:
    id: str
    name: str
    description: str
    project_type: str
    status: ProjectStatus
    members: List[str]
    max_members: int
    due_date: datetime
    progress: int
    tasks: List[Dict[str, Any]]
    created_by: str
    created_at: datetime

@dataclass
class EducationUser:
    user_id: str
    username: str
    email: str
    skill_level: SkillLevel
    skills: UserSkills
    learning_preferences: LearningPreferences
    xp: int = 0
    level: int = 1
    achievements: List[Achievement] = None
    current_lessons: List[str] = None
    completed_lessons: List[str] = None
    groups: List[str] = None
    streak_days: int = 0
    last_activity: Optional[datetime] = None

    def __post_init__(self):
        if self.achievements is None:
            self.achievements = []
        if self.current_lessons is None:
            self.current_lessons = []
        if self.completed_lessons is None:
            self.completed_lessons = []
        if self.groups is None:
            self.groups = []

class EducationAPI:
    def __init__(self):
        self.users: Dict[str, EducationUser] = {}
        self.projects: Dict[str, GroupProject] = {}
        self.achievements_catalog: Dict[str, Achievement] = {}
        self.learning_paths: Dict[str, LearningPath] = {}
        self.ai_responses: Dict[str, List[str]] = {}
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the education system with default data"""
        self._create_achievements()
        self._create_learning_paths()
        self._create_ai_responses()

    def _create_achievements(self):
        """Create the achievements catalog"""
        achievements = [
            Achievement("first_code", "First Code", "Wrote your first line of code", "🎯", 25),
            Achievement("problem_solver", "Problem Solver", "Solved 10 coding challenges", "🧩", 50),
            Achievement("streak_master", "Streak Master", "Maintained 7-day learning streak", "🔥", 100),
            Achievement("team_player", "Team Player", "Completed first group project", "👥", 75),
            Achievement("mentor", "Mentor", "Helped 5 other students", "🎓", 150),
            Achievement("creative_coder", "Creative Coder", "Built an original project", "🎨", 200),
            Achievement("debugging_detective", "Debugging Detective", "Fixed 20 bugs", "🕵️", 125),
            Achievement("algorithm_master", "Algorithm Master", "Mastered sorting algorithms", "[LIGHTNING]", 175),
        ]
        
        for achievement in achievements:
            self.achievements_catalog[achievement.id] = achievement

    def _create_learning_paths(self):
        """Create learning path templates"""
        paths = {
            "python_basics": LearningPath(
                id="python_basics",
                name="Python Programming Fundamentals",
                description="Learn Python from scratch with hands-on projects",
                lessons=["variables", "data_types", "control_structures", "functions", "classes", "file_handling"],
                estimated_duration=480,  # 8 hours
                skill_requirements={},
                skill_rewards={"programming_fundamentals": 40, "problem_solving": 20}
            ),
            "web_development": LearningPath(
                id="web_development",
                name="Web Development with HTML, CSS, JavaScript",
                description="Build modern web applications from frontend to backend",
                lessons=["html_basics", "css_styling", "javascript_fundamentals", "dom_manipulation", "apis", "frameworks"],
                estimated_duration=720,  # 12 hours
                skill_requirements={"programming_fundamentals": 30},
                skill_rewards={"programming_fundamentals": 30, "creativity": 40}
            ),
            "game_development": LearningPath(
                id="game_development",
                name="Game Development with Python",
                description="Create engaging games using Python and Pygame",
                lessons=["pygame_intro", "sprites", "collision_detection", "game_loops", "scoring", "levels"],
                estimated_duration=600,  # 10 hours
                skill_requirements={"programming_fundamentals": 40},
                skill_rewards={"creativity": 50, "problem_solving": 30}
            )
        }
        
        self.learning_paths.update(paths)

    def _create_ai_responses(self):
        """Create AI tutor response templates"""
        self.ai_responses = {
            "encouragement": [
                "Great job! You're making excellent progress!",
                "Keep it up! Programming takes practice, and you're doing fantastic!",
                "I can see you're really getting the hang of this!",
                "Your problem-solving skills are improving every day!",
                "Don't give up! Every expert was once a beginner!"
            ],
            "help_with_errors": [
                "No worries! Errors are part of learning. Let's figure this out together.",
                "That's a common mistake! Here's how to fix it...",
                "Great question! Let me break this down for you step by step.",
                "I see what happened here. This is actually a great learning opportunity!",
                "Debugging is a skill in itself. You're building that muscle!"
            ],
            "concept_explanation": [
                "Think of it this way: variables are like labeled boxes where you store things.",
                "Functions are like recipes - they take ingredients (parameters) and create something new!",
                "Loops are perfect when you need to repeat something multiple times efficiently.",
                "Classes are blueprints for creating objects with similar properties and behaviors.",
                "APIs are like waiters - they take your request and bring back what you need!"
            ],
            "project_suggestions": [
                "Based on your progress, you might enjoy building a simple calculator!",
                "How about creating a guessing game? It's fun and teaches important concepts!",
                "A to-do list app would be perfect for practicing what you've learned!",
                "Consider building a simple weather app using APIs!",
                "A basic text-based adventure game could be really engaging!"
            ]
        }

    async def assess_user_skills(self, user_id: str, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process skill assessment and create personalized learning path"""
        try:
            # Extract assessment responses
            experience_level = assessment_data.get("experienceLevel", "beginner")
            programming_knowledge = assessment_data.get("programmingKnowledge", [])
            code_challenge = assessment_data.get("codeChallenge", "")
            learning_style = assessment_data.get("learningStyle", ["hands-on"])

            # Calculate skill levels
            skills = self._calculate_skills(experience_level, programming_knowledge, code_challenge)
            
            # Create learning preferences
            preferences = LearningPreferences(
                learning_style=learning_style[0] if learning_style else "hands-on",
                preferred_pace="normal",
                difficulty_preference="adaptive"
            )

            # Create or update user
            if user_id not in self.users:
                self.users[user_id] = EducationUser(
                    user_id=user_id,
                    username=f"User_{user_id}",
                    email=f"user_{user_id}@example.com",
                    skill_level=SkillLevel(experience_level),
                    skills=skills,
                    learning_preferences=preferences,
                    xp=0,
                    level=1
                )
            else:
                user = self.users[user_id]
                user.skills = skills
                user.learning_preferences = preferences
                user.skill_level = SkillLevel(experience_level)

            # Generate personalized learning path
            learning_path = self._generate_learning_path(user_id)
            
            # Award assessment completion achievement
            await self._award_achievement(user_id, "first_code")

            return {
                "success": True,
                "user_skills": asdict(skills),
                "learning_path": learning_path,
                "recommended_next_steps": self._get_next_steps(user_id),
                "xp_earned": 50
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _calculate_skills(self, experience_level: str, knowledge: List[str], code_challenge: str) -> UserSkills:
        """Calculate user skills based on assessment"""
        base_skills = {
            "beginner": UserSkills(15, 10, 5, 10, 5),
            "novice": UserSkills(35, 25, 15, 20, 15),
            "intermediate": UserSkills(60, 50, 35, 40, 30),
            "advanced": UserSkills(85, 75, 65, 60, 50)
        }
        
        skills = base_skills.get(experience_level, base_skills["beginner"])
        
        # Bonus for programming knowledge
        knowledge_bonus = len(knowledge) * 3
        skills.programming_fundamentals = min(100, skills.programming_fundamentals + knowledge_bonus)
        
        # Bonus for code challenge completion
        if code_challenge and len(code_challenge) > 50 and "def" in code_challenge:
            skills.problem_solving += 15
            skills.programming_fundamentals += 10
            
        # Ensure no skill exceeds 100
        skills.programming_fundamentals = min(100, skills.programming_fundamentals)
        skills.problem_solving = min(100, skills.problem_solving)
        skills.advanced_concepts = min(100, skills.advanced_concepts)
        skills.collaboration = min(100, skills.collaboration)
        skills.creativity = min(100, skills.creativity)
        
        return skills

    def _generate_learning_path(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized learning path based on user skills"""
        user = self.users.get(user_id)
        if not user:
            return []

        path_steps = []
        
        # Determine appropriate starting path
        if user.skills.programming_fundamentals < 30:
            path_steps.extend([
                {"title": "Programming Fundamentals", "description": "Learn variables, data types, and basic syntax", "duration": 60},
                {"title": "Control Structures", "description": "Master if statements, loops, and conditional logic", "duration": 45},
                {"title": "Functions & Methods", "description": "Write reusable code with functions", "duration": 50},
                {"title": "First Project", "description": "Build a simple calculator app", "duration": 90}
            ])
        elif user.skills.programming_fundamentals < 60:
            path_steps.extend([
                {"title": "Advanced Functions", "description": "Learn about parameters, return values, and scope", "duration": 40},
                {"title": "Data Structures", "description": "Work with lists, dictionaries, and arrays", "duration": 55},
                {"title": "Error Handling", "description": "Debug code and handle exceptions", "duration": 35},
                {"title": "Web Development Basics", "description": "Create your first web application", "duration": 120}
            ])
        else:
            path_steps.extend([
                {"title": "Object-Oriented Programming", "description": "Master classes, objects, and inheritance", "duration": 70},
                {"title": "Algorithm Design", "description": "Learn sorting, searching, and optimization", "duration": 85},
                {"title": "Database Integration", "description": "Connect your apps to databases", "duration": 65},
                {"title": "Full-Stack Project", "description": "Build a complete web application", "duration": 180}
            ])

        return path_steps

    def _get_next_steps(self, user_id: str) -> List[str]:
        """Get recommended next steps for user"""
        user = self.users.get(user_id)
        if not user:
            return []

        steps = []
        
        if user.skills.programming_fundamentals < 50:
            steps.append("Complete Python Fundamentals course")
        if user.skills.creativity < 30:
            steps.append("Try building a creative project")
        if user.skills.collaboration < 40:
            steps.append("Join a group project")
        if len(user.completed_lessons) == 0:
            steps.append("Start with your first lesson")
            
        return steps[:3]  # Return top 3 recommendations

    async def _award_achievement(self, user_id: str, achievement_id: str) -> bool:
        """Award achievement to user"""
        user = self.users.get(user_id)
        achievement = self.achievements_catalog.get(achievement_id)
        
        if not user or not achievement:
            return False
            
        # Check if already unlocked
        if any(a.id == achievement_id for a in user.achievements):
            return False
            
        # Award achievement
        new_achievement = Achievement(
            id=achievement.id,
            name=achievement.name,
            description=achievement.description,
            icon=achievement.icon,
            xp_reward=achievement.xp_reward,
            unlocked_at=datetime.now()
        )
        
        user.achievements.append(new_achievement)
        user.xp += achievement.xp_reward
        
        # Check for level up
        new_level = (user.xp // 100) + 1
        if new_level > user.level:
            user.level = new_level
            
        return True

    async def create_group_project(self, project_data: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Create a new group project"""
        try:
            project_id = f"project_{len(self.projects) + 1}_{int(datetime.now().timestamp())}"
            
            project = GroupProject(
                id=project_id,
                name=project_data["name"],
                description=project_data["description"],
                project_type=project_data["type"],
                status=ProjectStatus.PLANNING,
                members=[creator_id],
                max_members=int(project_data["teamSize"]),
                due_date=datetime.fromisoformat(project_data["dueDate"]),
                progress=0,
                tasks=self._generate_project_tasks(project_data["type"]),
                created_by=creator_id,
                created_at=datetime.now()
            )
            
            self.projects[project_id] = project
            
            # Add project to user's groups
            if creator_id in self.users:
                self.users[creator_id].groups.append(project_id)
            
            # Award achievement for creating first project
            await self._award_achievement(creator_id, "team_player")
            
            return {
                "success": True,
                "project_id": project_id,
                "project": asdict(project)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _generate_project_tasks(self, project_type: str) -> List[Dict[str, Any]]:
        """Generate appropriate tasks based on project type"""
        task_templates = {
            "web-app": [
                {"title": "Set up project structure", "description": "Create folders and initial files", "completed": False},
                {"title": "Design UI mockups", "description": "Create wireframes and design layouts", "completed": False},
                {"title": "Implement frontend", "description": "Build HTML, CSS, and JavaScript", "completed": False},
                {"title": "Set up backend", "description": "Create server and API endpoints", "completed": False},
                {"title": "Connect frontend to backend", "description": "Integrate API calls", "completed": False},
                {"title": "Testing and debugging", "description": "Test all features and fix bugs", "completed": False}
            ],
            "game": [
                {"title": "Set up game window", "description": "Initialize game display and settings", "completed": False},
                {"title": "Create game objects", "description": "Design player, enemies, and items", "completed": False},
                {"title": "Implement game mechanics", "description": "Add movement, collision detection", "completed": False},
                {"title": "Add scoring system", "description": "Track and display player score", "completed": False},
                {"title": "Create levels", "description": "Design multiple game levels", "completed": False},
                {"title": "Polish and test", "description": "Add sound, effects, and test gameplay", "completed": False}
            ],
            "ai-ml": [
                {"title": "Data collection", "description": "Gather and prepare training data", "completed": False},
                {"title": "Exploratory data analysis", "description": "Analyze and visualize data patterns", "completed": False},
                {"title": "Model selection", "description": "Choose appropriate ML algorithm", "completed": False},
                {"title": "Model training", "description": "Train and tune the model", "completed": False},
                {"title": "Model evaluation", "description": "Test model performance", "completed": False},
                {"title": "Deployment preparation", "description": "Prepare model for production use", "completed": False}
            ]
        }
        
        return task_templates.get(project_type, task_templates["web-app"])

    async def join_project(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Allow user to join an existing project"""
        try:
            project = self.projects.get(project_id)
            user = self.users.get(user_id)
            
            if not project or not user:
                return {"success": False, "error": "Project or user not found"}
                
            if len(project.members) >= project.max_members:
                return {"success": False, "error": "Project is full"}
                
            if user_id in project.members:
                return {"success": False, "error": "User already in project"}
                
            # Add user to project
            project.members.append(user_id)
            user.groups.append(project_id)
            
            # Change project status to active if it has enough members
            if len(project.members) >= 2 and project.status == ProjectStatus.PLANNING:
                project.status = ProjectStatus.ACTIVE
            
            return {
                "success": True,
                "message": "Successfully joined project",
                "project": asdict(project)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_ai_tutor_response(self, user_id: str, message: str) -> Dict[str, Any]:
        """Generate AI tutor response based on user message and context"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
                
            # Analyze message intent
            message_lower = message.lower()
            response_type = "general"
            
            if any(word in message_lower for word in ["error", "bug", "wrong", "broken", "help"]):
                response_type = "help_with_errors"
            elif any(word in message_lower for word in ["what", "how", "why", "explain"]):
                response_type = "concept_explanation"
            elif any(word in message_lower for word in ["project", "build", "create", "make"]):
                response_type = "project_suggestions"
            elif any(word in message_lower for word in ["good", "great", "done", "finished"]):
                response_type = "encouragement"
            
            # Select appropriate response
            responses = self.ai_responses.get(response_type, self.ai_responses["encouragement"])
            base_response = random.choice(responses)
            
            # Personalize response based on user data
            personalized_response = self._personalize_response(base_response, user, message)
            
            return {
                "success": True,
                "response": personalized_response,
                "suggestions": self._get_learning_suggestions(user, message)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _personalize_response(self, base_response: str, user: EducationUser, message: str) -> str:
        """Personalize AI response based on user context"""
        # Add user's name and level context
        personalized = base_response
        
        if user.level > 1:
            personalized += f" I can see you've reached Level {user.level} - that's impressive progress!"
            
        if user.streak_days > 0:
            personalized += f" Keep up that {user.streak_days}-day learning streak!"
            
        return personalized

    def _get_learning_suggestions(self, user: EducationUser, message: str) -> List[str]:
        """Get contextual learning suggestions"""
        suggestions = []
        
        if "variable" in message.lower():
            suggestions.append("Try creating different types of variables (strings, numbers, booleans)")
            suggestions.append("Practice using variables in mathematical operations")
            
        elif "function" in message.lower():
            suggestions.append("Write a function that takes parameters and returns a value")
            suggestions.append("Try creating functions that call other functions")
            
        elif "loop" in message.lower():
            suggestions.append("Practice with both for loops and while loops")
            suggestions.append("Try nested loops for more complex patterns")
            
        else:
            # General suggestions based on skill level
            if user.skills.programming_fundamentals < 50:
                suggestions.append("Focus on mastering the basics before moving to advanced topics")
                suggestions.append("Try building small projects to practice what you've learned")
            else:
                suggestions.append("Consider joining a group project to practice collaboration")
                suggestions.append("Challenge yourself with algorithm problems")
                
        return suggestions[:2]  # Return top 2 suggestions

    async def update_user_progress(self, user_id: str, lesson_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user progress when they complete a lesson or activity"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
                
            # Add to completed lessons
            if lesson_id not in user.completed_lessons:
                user.completed_lessons.append(lesson_id)
                
            # Remove from current lessons
            if lesson_id in user.current_lessons:
                user.current_lessons.remove(lesson_id)
                
            # Award XP and update skills
            xp_earned = completion_data.get("xp", 25)
            user.xp += xp_earned
            
            # Update streak
            user.last_activity = datetime.now()
            if self._is_consecutive_day(user):
                user.streak_days += 1
            else:
                user.streak_days = 1
                
            # Check for achievements
            achievements_earned = await self._check_achievements(user_id)
            
            # Update skill levels based on lesson content
            self._update_skills_from_lesson(user, lesson_id, completion_data)
            
            return {
                "success": True,
                "xp_earned": xp_earned,
                "total_xp": user.xp,
                "new_level": (user.xp // 100) + 1,
                "achievements_earned": achievements_earned,
                "streak_days": user.streak_days
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_consecutive_day(self, user: EducationUser) -> bool:
        """Check if user activity is on consecutive day"""
        if not user.last_activity:
            return True
            
        yesterday = datetime.now() - timedelta(days=1)
        return user.last_activity.date() == yesterday.date()

    async def _check_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Check and award new achievements"""
        user = self.users.get(user_id)
        if not user:
            return []
            
        new_achievements = []
        
        # Check streak achievement
        if user.streak_days >= 7:
            if await self._award_achievement(user_id, "streak_master"):
                new_achievements.append(asdict(self.achievements_catalog["streak_master"]))
                
        # Check lesson completion achievements
        if len(user.completed_lessons) >= 10:
            if await self._award_achievement(user_id, "problem_solver"):
                new_achievements.append(asdict(self.achievements_catalog["problem_solver"]))
                
        return new_achievements

    def _update_skills_from_lesson(self, user: EducationUser, lesson_id: str, completion_data: Dict[str, Any]):
        """Update user skills based on lesson completion"""
        # Map lesson types to skill improvements
        skill_mappings = {
            "variables": {"programming_fundamentals": 5},
            "data_types": {"programming_fundamentals": 5},
            "control_structures": {"programming_fundamentals": 7, "problem_solving": 3},
            "functions": {"programming_fundamentals": 8, "problem_solving": 5},
            "classes": {"advanced_concepts": 10, "programming_fundamentals": 5},
            "debugging": {"problem_solving": 8},
            "algorithms": {"problem_solving": 10, "advanced_concepts": 5},
            "web_design": {"creativity": 8, "programming_fundamentals": 3},
            "team_project": {"collaboration": 10, "creativity": 5}
        }
        
        # Apply skill improvements
        for lesson_type, skill_gains in skill_mappings.items():
            if lesson_type in lesson_id.lower():
                for skill, gain in skill_gains.items():
                    current_value = getattr(user.skills, skill)
                    setattr(user.skills, skill, min(100, current_value + gain))
                break

    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user dashboard data"""
        try:
            user = self.users.get(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
                
            # Get user's projects
            user_projects = []
            for project_id in user.groups:
                project = self.projects.get(project_id)
                if project:
                    user_projects.append(asdict(project))
                    
            # Get learning recommendations
            recommendations = self._get_learning_recommendations(user)
            
            # Get peer data (simulated)
            peers = self._get_peer_data(user_id)
            
            return {
                "success": True,
                "user": asdict(user),
                "projects": user_projects,
                "recommendations": recommendations,
                "peers": peers,
                "global_stats": {
                    "total_users": len(self.users),
                    "active_projects": len([p for p in self.projects.values() if p.status == ProjectStatus.ACTIVE]),
                    "completed_projects": len([p for p in self.projects.values() if p.status == ProjectStatus.COMPLETED])
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_learning_recommendations(self, user: EducationUser) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations"""
        recommendations = []
        
        # Skill-based recommendations
        if user.skills.programming_fundamentals < 50:
            recommendations.append({
                "type": "lesson",
                "title": "Master Programming Basics",
                "description": "Strengthen your foundation with core programming concepts",
                "priority": "high"
            })
            
        if user.skills.collaboration < 30:
            recommendations.append({
                "type": "project",
                "title": "Join a Group Project",
                "description": "Develop teamwork skills while building something cool",
                "priority": "medium"
            })
            
        if user.skills.creativity < 40:
            recommendations.append({
                "type": "challenge",
                "title": "Creative Coding Challenge",
                "description": "Build something unique and express your creativity",
                "priority": "medium"
            })
            
        return recommendations[:3]  # Return top 3

    def _get_peer_data(self, user_id: str) -> List[Dict[str, Any]]:
        """Get peer learning data (simulated for demo)"""
        return [
            {"name": "Maya Johnson", "level": 4, "status": "online", "current_lesson": "Functions"},
            {"name": "Ryan Kim", "level": 2, "status": "away", "current_lesson": "Variables"},
            {"name": "Sarah Lee", "level": 5, "status": "online", "current_lesson": "Classes"},
            {"name": "Emma Harris", "level": 3, "status": "offline", "current_lesson": "Loops"}
        ]

# Global instance
education_api = EducationAPI()
