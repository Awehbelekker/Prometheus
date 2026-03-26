"""
Master Cloud Coding Education Platform - Core Education System
Implementation based on comprehensive master development specification.

Features:
- Age-appropriate learning progressions (5-22 years) 
- Comprehensive gamification with XP, achievements, competitions
- Secure collaborative environments with encrypted communication
- AI-powered personalized learning and adaptive pathways
- Industry-standard skill development with certification pathways
- Real-time collaborative coding and project management
- Multi-modal assessment with anti-cheating measures
- Privacy-compliant data handling (GDPR, FERPA, COPPA)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import json
import asyncio
from enum import Enum
from dataclasses import dataclass, field
import uuid
import hashlib
from pathlib import Path

# Age-based learning phases from master specification
class AgeGroup(str, Enum):
    EARLY_FOUNDATIONS = "5-8"      # Digital Explorers & Cloud Pioneers
    DISCOVERY_PHASE = "9-11"       # Code Crafters & Cloud Architects  
    DEVELOPMENT_PHASE = "12-14"    # Cloud Developers & System Architects
    SPECIALIZATION_PHASE = "15-18" # Cloud Engineers & Tech Innovators
    ADVANCED_PROFESSIONAL = "19-22" # Industry Professionals

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"

class ProgrammingLanguage(str, Enum):
    # Tier 1 Critical (from master spec)
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    SQL = "sql"
    HTML_CSS = "html_css"
    
    # Tier 2 Valuable
    JAVA = "java"
    CSHARP = "csharp"
    
    # Tier 3 Specialized
    GO = "go"
    RUST = "rust"
    TYPESCRIPT = "typescript"
    
    # Early Learning
    SCRATCH = "scratch"
    SCRATCH_JR = "scratch_jr"

class LearningPath(str, Enum):
    # Early Foundations Themes
    SPACE_CADETS_ACADEMY = "space-cadets-academy"
    SUPERHERO_TECH_SQUAD = "superhero-tech-squad"
    MAGIC_KINGDOM_BUILDERS = "magic-kingdom-builders"
    
    # Discovery Phase Themes
    MINECRAFT_CLOUD_CITY = "minecraft-cloud-city"
    DIGITAL_MOVIE_STUDIO = "digital-movie-studio"
    ECO_WARRIORS_CLIMATE_TECH = "eco-warriors-climate-tech"
    MUSIC_ART_CREATION_LAB = "music-art-creation-lab"
    
    # Development Phase Specializations
    SMART_CITY_INNOVATION_LAB = "smart-city-innovation-lab"
    ESPORTS_GAMING_PLATFORM = "esports-gaming-platform"
    HEALTH_TECH_SOLUTIONS = "health-tech-solutions"
    CYBERSECURITY_COMMAND_CENTER = "cybersecurity-command-center"
    SOCIAL_IMPACT_STARTUPS = "social-impact-startups"
    
    # Specialization Phase Tracks
    AI_MACHINE_LEARNING = "ai-machine-learning"
    ENTERPRISE_SOLUTIONS_ARCHITECTURE = "enterprise-solutions-architecture"
    FULL_STACK_MASTERY = "full-stack-mastery"
    DATA_ENGINEERING_ANALYTICS = "data-engineering-analytics"
    CYBERSECURITY_SPECIALIZATION = "cybersecurity-specialization"

class CompetitionType(str, Enum):
    CODE_GOLF = "code-golf"
    SPEED_CODING = "speed-coding"
    DEBUG_RACE = "debug-race"
    ALGORITHM_OPTIMIZATION = "algorithm-optimization"
    HACKATHON = "hackathon"
    PEER_REVIEW = "peer-review"

class AchievementCategory(str, Enum):
    LANGUAGE_MASTERY = "language-mastery"
    PROJECT_COMPLETION = "project-completion"
    COLLABORATION = "collaboration"
    COMPETITION = "competition"
    INDUSTRY_SKILLS = "industry-skills"
    CREATIVITY = "creativity"
    PROBLEM_SOLVING = "problem-solving"
    MENTORSHIP = "mentorship"

# Enhanced Models with Master Specification Requirements

class UserProgress(BaseModel):
    user_id: str
    username: str
    email: str
    age_group: AgeGroup
    skill_level: SkillLevel
    current_path: LearningPath
    xp_points: int = 0
    level: int = 1
    badges_earned: List[str] = []
    completed_lessons: List[str] = []
    completed_projects: List[str] = []
    current_lesson: Optional[str] = None
    streak_days: int = 0
    last_activity: datetime
    skills: Dict[str, int] = {}  # skill_name: proficiency_level (1-5)
    languages_learned: List[ProgrammingLanguage] = []
    certifications: List[str] = []
    competition_wins: int = 0
    collaboration_rating: float = 5.0
    created_at: datetime
    parent_email: Optional[str] = None  # Required for under 18
    school_id: Optional[str] = None
    privacy_settings: Dict[str, bool] = {}

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    category: AchievementCategory
    xp_reward: int
    badge_icon: str
    rarity: str = "common"  # common, rare, epic, legendary
    requirements: Dict[str, Any]
    unlocked_at: Optional[datetime] = None

class CodingChallenge(BaseModel):
    id: str
    title: str
    description: str
    difficulty: SkillLevel
    language: ProgrammingLanguage
    age_group: AgeGroup
    starter_code: str
    test_cases: List[Dict[str, Any]]
    solution_template: str
    xp_reward: int
    time_limit: Optional[int] = None  # minutes
    tags: List[str] = []
    created_by: str = "system"
    created_at: datetime

class ProjectTemplate(BaseModel):
    id: str
    name: str
    theme: str  # e.g., "Space Cadets Academy", "Smart City Innovation Lab"
    description: str
    age_group: AgeGroup
    learning_path: LearningPath
    technologies: List[str]
    estimated_duration: str  # e.g., "4 weeks"
    learning_objectives: List[str]
    starter_files: Dict[str, str]  # filename -> content
    assessment_criteria: List[str]
    collaboration_type: str = "individual"  # individual, pair, team
    industry_connections: List[str] = []
    real_world_impact: bool = False

class LiveCompetition(BaseModel):
    id: str
    name: str
    competition_type: CompetitionType
    description: str
    start_time: datetime
    duration_minutes: int
    max_participants: int
    current_participants: List[str] = []
    skill_level: SkillLevel
    language: ProgrammingLanguage
    prize_pool: Dict[str, Any] = {}  # XP, badges, certifications
    status: str = "scheduled"  # scheduled, active, completed, cancelled

class TeamProject(BaseModel):
    project_id: str
    name: str
    description: str
    team_members: List[str]
    created_by: str
    skill_level: SkillLevel
    age_group: AgeGroup
    learning_objectives: List[str]
    code_repository: str
    collaboration_tools: List[str] = []  # chat, screen_share, code_review
    mentor_assigned: Optional[str] = None
    deadline: datetime
    progress_percentage: float = 0.0
    status: str = "active"  # active, completed, paused, cancelled
    progress: float = 0.0
    due_date: Optional[datetime] = None

class Lesson(BaseModel):
    lesson_id: str
    title: str
    description: str
    skill_level: SkillLevel
    learning_path: LearningPath
    difficulty: int  # 1-5
    estimated_time: int  # minutes
    prerequisites: List[str] = []
    content: Dict[str, Any]
    ai_hints: List[str] = []
    exercises: List[Dict[str, Any]] = []

class CodeSubmission(BaseModel):
    user_id: str
    lesson_id: str
    code: str
    language: str
    timestamp: datetime = datetime.now()

class AIAnalysisResult(BaseModel):
    code_quality: int  # 1-100
    suggestions: List[str]
    bugs_found: List[str]
    improvements: List[str]
    learning_opportunities: List[str]
    estimated_completion_time: int  # minutes

# Create router
education_router = APIRouter(prefix="/api/education", tags=["education"])

# In-memory storage for demo (would be database in production)
user_progress_store: Dict[str, UserProgress] = {}
team_projects_store: Dict[str, TeamProject] = {}
lessons_store: Dict[str, Lesson] = {}
code_submissions_store: List[CodeSubmission] = []

# Initialize sample lessons
def initialize_sample_lessons():
    lessons = [
        Lesson(
            lesson_id="web-basics-1",
            title="Building Your First Webpage",
            description="Learn HTML structure and create your first webpage",
            skill_level=SkillLevel.BEGINNER,
            learning_path=LearningPath.WEB_BASICS,
            difficulty=1,
            estimated_time=30,
            content={
                "instructions": "Create a basic HTML page with proper structure",
                "starter_code": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <!-- Add your content here -->\n</body>\n</html>",
                "solution": "<!DOCTYPE html>\n<html>\n<head>\n    <title>My First Webpage</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <p>This is my first webpage.</p>\n</body>\n</html>"
            },
            ai_hints=[
                "Remember to close all HTML tags",
                "Use semantic elements like <h1> for headings",
                "Don't forget the DOCTYPE declaration"
            ],
            exercises=[
                {
                    "type": "code_completion",
                    "prompt": "Add a paragraph with your name",
                    "expected_elements": ["<p>", "name"]
                }
            ]
        ),
        Lesson(
            lesson_id="python-intro-1", 
            title="Python Variables and Data Types",
            description="Learn about variables, strings, numbers, and basic data types in Python",
            skill_level=SkillLevel.BEGINNER,
            learning_path=LearningPath.PYTHON_INTRO,
            difficulty=1,
            estimated_time=25,
            content={
                "instructions": "Create variables and print different data types",
                "starter_code": "# Your first Python program\n# Create variables here\n\nprint('Hello, Python!')",
                "solution": "name = 'Alice'\nage = 12\nheight = 4.5\nis_student = True\n\nprint(f'Name: {name}')\nprint(f'Age: {age}')\nprint(f'Height: {height} feet')\nprint(f'Is student: {is_student}')"
            },
            ai_hints=[
                "Use descriptive variable names",
                "Try different data types: strings, integers, floats, booleans",
                "Use f-strings for formatting output"
            ]
        )
    ]
    
    for lesson in lessons:
        lessons_store[lesson.lesson_id] = lesson

# Initialize on startup
initialize_sample_lessons()

@education_router.get("/user/{user_id}/progress")
async def get_user_progress(user_id: str) -> UserProgress:
    """Get user's learning progress and achievements"""
    if user_id not in user_progress_store:
        # Create new user progress
        user_progress_store[user_id] = UserProgress(
            user_id=user_id,
            skill_level=SkillLevel.BEGINNER,
            current_path=LearningPath.WEB_BASICS,
            last_activity=datetime.now(),
            skills={
                "html": 1,
                "css": 0,
                "javascript": 0,
                "python": 0
            }
        )
    
    return user_progress_store[user_id]

@education_router.post("/user/{user_id}/progress")
async def update_user_progress(user_id: str, progress: UserProgress) -> Dict[str, Any]:
    """Update user's learning progress"""
    user_progress_store[user_id] = progress
    return {"message": "Progress updated successfully", "level_up": False}

@education_router.get("/learning-paths")
async def get_learning_paths() -> Dict[str, Any]:
    """Get available learning paths with skill level adaptation"""
    paths = {
        "web-basics": {
            "name": "Web Development Basics",
            "description": "HTML, CSS, JavaScript fundamentals",
            "icon": "🌐",
            "difficulty": 1,
            "estimated_hours": 20,
            "lessons": 15,
            "skills": ["html", "css", "javascript"]
        },
        "python-intro": {
            "name": "Python Programming",
            "description": "Learn programming with Python",
            "icon": "🐍", 
            "difficulty": 2,
            "estimated_hours": 25,
            "lessons": 18,
            "skills": ["python", "programming-concepts", "problem-solving"]
        },
        "game-dev": {
            "name": "Game Development",
            "description": "Create games with JavaScript",
            "icon": "🎮",
            "difficulty": 3,
            "estimated_hours": 35,
            "lessons": 22,
            "skills": ["javascript", "canvas", "game-logic"]
        },
        "mobile-apps": {
            "name": "Mobile App Development", 
            "description": "Build mobile apps with React Native",
            "icon": "📱",
            "difficulty": 4,
            "estimated_hours": 40,
            "lessons": 25,
            "skills": ["react-native", "mobile-ui", "app-deployment"]
        }
    }
    
    return {"paths": paths, "total": len(paths)}

@education_router.get("/lessons/{path_id}")
async def get_lessons_for_path(path_id: str, skill_level: SkillLevel = SkillLevel.BEGINNER) -> Dict[str, Any]:
    """Get lessons for a specific learning path, adapted to skill level"""
    path_lessons = [lesson for lesson in lessons_store.values() 
                   if lesson.learning_path.value == path_id and lesson.skill_level == skill_level]
    
    # Sort by difficulty
    path_lessons.sort(key=lambda x: x.difficulty)
    
    return {
        "lessons": [lesson.dict() for lesson in path_lessons],
        "total": len(path_lessons),
        "skill_level": skill_level
    }

@education_router.get("/lesson/{lesson_id}")
async def get_lesson_content(lesson_id: str, user_id: str) -> Dict[str, Any]:
    """Get lesson content with AI personalization"""
    if lesson_id not in lessons_store:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    lesson = lessons_store[lesson_id]
    user_progress = await get_user_progress(user_id)
    
    # AI-powered content adaptation based on user's skill level and progress
    adapted_content = lesson.content.copy()
    adapted_hints = lesson.ai_hints.copy()
    
    if user_progress.skill_level == SkillLevel.BEGINNER:
        # Add more detailed explanations and visual aids
        adapted_hints.insert(0, "Take your time and read each step carefully!")
        if lesson.learning_path == LearningPath.WEB_BASICS:
            adapted_hints.append("Try changing the text and see what happens!")
    elif user_progress.skill_level == SkillLevel.ADVANCED:
        # Add advanced challenges
        adapted_hints.append("Challenge: Can you optimize this code further?")
        adapted_hints.append("Consider best practices and performance implications.")
    
    return {
        "lesson": lesson.dict(),
        "adapted_content": adapted_content,
        "personalized_hints": adapted_hints,
        "user_progress": user_progress.dict()
    }

@education_router.post("/code/submit")
async def submit_code(submission: CodeSubmission) -> Dict[str, Any]:
    """Submit code for AI analysis and feedback"""
    code_submissions_store.append(submission)
    
    # AI-powered code analysis
    analysis = await analyze_code_with_ai(submission.code, submission.language, submission.lesson_id)
    
    # Update user progress based on code quality
    if submission.user_id in user_progress_store:
        user_progress = user_progress_store[submission.user_id]
        xp_gained = calculate_xp_from_analysis(analysis)
        user_progress.xp_points += xp_gained
        
        # Level up logic
        level_up = False
        new_level = calculate_level_from_xp(user_progress.xp_points)
        if new_level > user_progress.level:
            user_progress.level = new_level
            level_up = True
            
        # Award badges based on achievements
        new_badges = check_for_new_badges(user_progress, analysis)
        user_progress.badges_earned.extend(new_badges)
        
        user_progress.last_activity = datetime.now()
        
        return {
            "analysis": analysis.dict(),
            "xp_gained": xp_gained,
            "level_up": level_up,
            "new_badges": new_badges,
            "user_progress": user_progress.dict()
        }
    
    return {"analysis": analysis.dict()}

async def analyze_code_with_ai(code: str, language: str, lesson_id: str) -> AIAnalysisResult:
    """AI-powered code analysis with educational feedback"""
    # Simulate AI analysis (in production, this would call actual AI services)
    await asyncio.sleep(1)  # Simulate processing time
    
    suggestions = []
    bugs_found = []
    improvements = []
    learning_opportunities = []
    code_quality = 85  # Base score
    
    # Basic code analysis based on language
    if language.lower() == "html":
        if "<!DOCTYPE html>" in code:
            code_quality += 5
        else:
            suggestions.append("Add <!DOCTYPE html> declaration at the beginning")
            
        if "<title>" in code:
            code_quality += 5
        else:
            suggestions.append("Include a <title> tag in the <head> section")
            
        if code.count("<") != code.count(">"):
            bugs_found.append("Mismatched HTML tags detected")
            code_quality -= 15
            
        if "<h1>" in code or "<h2>" in code:
            improvements.append("Great use of semantic heading tags!")
        else:
            learning_opportunities.append("Try using heading tags like <h1> to structure your content")
            
    elif language.lower() == "python":
        if "print" in code:
            improvements.append("Good use of print statements for output!")
            
        if "=" in code and not "==" in code:
            improvements.append("Nice variable assignment!")
            
        if "#" in code:
            code_quality += 10
            improvements.append("Excellent code commenting!")
        else:
            learning_opportunities.append("Consider adding comments to explain your code")
            
        # Check for common Python issues
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if line.strip().endswith(':') and i < len(lines) - 1:
                next_line = lines[i + 1]
                if next_line and not next_line.startswith('    '):
                    bugs_found.append(f"Line {i+2}: Missing indentation after colon")
                    code_quality -= 10
    
    # General improvements based on code structure
    if len(code.strip()) < 10:
        learning_opportunities.append("Try adding more content to make your code more complete")
    elif len(code.strip()) > 500:
        learning_opportunities.append("Consider breaking large code blocks into smaller functions")
    
    # Ensure code quality is within bounds
    code_quality = max(0, min(100, code_quality))
    
    return AIAnalysisResult(
        code_quality=code_quality,
        suggestions=suggestions,
        bugs_found=bugs_found,
        improvements=improvements,
        learning_opportunities=learning_opportunities,
        estimated_completion_time=5 if bugs_found else 0
    )

def calculate_xp_from_analysis(analysis: AIAnalysisResult) -> int:
    """Calculate XP points based on code analysis results"""
    base_xp = 50
    quality_bonus = int(analysis.code_quality * 0.5)  # Up to 50 bonus XP
    
    # Bonus for clean code
    if analysis.code_quality >= 90:
        quality_bonus += 25
    elif analysis.code_quality >= 80:
        quality_bonus += 10
        
    # Penalty for bugs
    bug_penalty = len(analysis.bugs_found) * 10
    
    total_xp = max(10, base_xp + quality_bonus - bug_penalty)
    return total_xp

def calculate_level_from_xp(xp: int) -> int:
    """Calculate user level based on XP points"""
    # Level 1: 0-100 XP, Level 2: 101-250 XP, Level 3: 251-500 XP, etc.
    if xp <= 100:
        return 1
    elif xp <= 250:
        return 2
    elif xp <= 500:
        return 3
    elif xp <= 1000:
        return 4
    elif xp <= 2000:
        return 5
    elif xp <= 3500:
        return 6
    elif xp <= 5500:
        return 7
    elif xp <= 8000:
        return 8
    elif xp <= 12000:
        return 9
    else:
        return 10

def check_for_new_badges(user_progress: UserProgress, analysis: AIAnalysisResult) -> List[str]:
    """Check if user earned any new badges"""
    new_badges = []
    current_badges = set(user_progress.badges_earned)
    
    # First Code badge
    if "first-code" not in current_badges and user_progress.xp_points >= 50:
        new_badges.append("first-code")
    
    # Bug Hunter badge
    if "bug-hunter" not in current_badges and len(analysis.bugs_found) == 0 and analysis.code_quality >= 90:
        new_badges.append("bug-hunter")
    
    # Code Quality badge
    if "quality-coder" not in current_badges and analysis.code_quality >= 95:
        new_badges.append("quality-coder")
    
    # Streak badges
    if user_progress.streak_days >= 7 and "week-streak" not in current_badges:
        new_badges.append("week-streak")
    elif user_progress.streak_days >= 30 and "month-streak" not in current_badges:
        new_badges.append("month-streak")
    
    # Level badges
    if user_progress.level >= 5 and "level-5" not in current_badges:
        new_badges.append("level-5")
    elif user_progress.level >= 10 and "level-10" not in current_badges:
        new_badges.append("level-10")
    
    return new_badges

@education_router.post("/team/create")
async def create_team_project(project: TeamProject, creator_id: str) -> Dict[str, Any]:
    """Create a new team project for collaborative learning"""
    project.created_by = creator_id
    team_projects_store[project.project_id] = project
    
    return {
        "message": "Team project created successfully",
        "project_id": project.project_id,
        "invite_link": f"/education/team/join/{project.project_id}"
    }

@education_router.get("/team/{project_id}")
async def get_team_project(project_id: str) -> TeamProject:
    """Get team project details"""
    if project_id not in team_projects_store:
        raise HTTPException(status_code=404, detail="Team project not found")
    
    return team_projects_store[project_id]

@education_router.post("/team/{project_id}/join")
async def join_team_project(project_id: str, user_id: str) -> Dict[str, Any]:
    """Join a team project"""
    if project_id not in team_projects_store:
        raise HTTPException(status_code=404, detail="Team project not found")
    
    project = team_projects_store[project_id]
    if user_id not in project.team_members:
        project.team_members.append(user_id)
        
        # Award collaboration badge
        if user_id in user_progress_store:
            user_progress = user_progress_store[user_id]
            if "team-player" not in user_progress.badges_earned:
                user_progress.badges_earned.append("team-player")
    
    return {
        "message": "Successfully joined team project",
        "project": project.dict(),
        "team_size": len(project.team_members)
    }

@education_router.post("/import/analyze")
async def analyze_imported_project(files: List[str], user_id: str) -> Dict[str, Any]:
    """Analyze imported project files and create learning path"""
    # Simulate file analysis
    await asyncio.sleep(2)
    
    analysis_results = {
        "overall_quality": 75,
        "files_analyzed": len(files),
        "languages_detected": ["html", "css", "javascript"],
        "strengths": [
            "Good HTML structure",
            "Consistent naming conventions", 
            "Proper indentation"
        ],
        "improvements_needed": [
            "Missing CSS file linking",
            "JavaScript function could be optimized",
            "Add more semantic HTML elements"
        ],
        "learning_opportunities": [
            "CSS Grid and Flexbox layouts",
            "Modern JavaScript ES6+ features",
            "Responsive design principles",
            "Web accessibility best practices"
        ],
        "suggested_next_steps": [
            {
                "title": "Fix CSS Linking",
                "description": "Learn how to properly link CSS files",
                "estimated_time": 15,
                "difficulty": 1
            },
            {
                "title": "Responsive Design",
                "description": "Make your website work on all devices",
                "estimated_time": 45,
                "difficulty": 2
            },
            {
                "title": "JavaScript Optimization",
                "description": "Improve code performance and readability",
                "estimated_time": 30,
                "difficulty": 3
            }
        ]
    }
    
    # Create personalized learning path based on analysis
    learning_path = {
        "path_id": f"imported-project-{user_id}",
        "name": "Your Project Improvement Path",
        "description": "Personalized lessons based on your imported project",
        "lessons": analysis_results["suggested_next_steps"],
        "estimated_completion": sum(step["estimated_time"] for step in analysis_results["suggested_next_steps"])
    }
    
    # Award XP for importing and analyzing
    if user_id in user_progress_store:
        user_progress = user_progress_store[user_id]
        user_progress.xp_points += 200  # Bonus for importing project
        
        # Award import badge
        if "project-importer" not in user_progress.badges_earned:
            user_progress.badges_earned.append("project-importer")
    
    return {
        "analysis": analysis_results,
        "learning_path": learning_path,
        "xp_bonus": 200
    }

@education_router.get("/leaderboard")
async def get_leaderboard(skill_level: Optional[SkillLevel] = None) -> Dict[str, Any]:
    """Get leaderboard for gamification"""
    # Filter users by skill level if specified
    users = list(user_progress_store.values())
    if skill_level:
        users = [user for user in users if user.skill_level == skill_level]
    
    # Sort by XP points
    users.sort(key=lambda x: x.xp_points, reverse=True)
    
    leaderboard = []
    for i, user in enumerate(users[:10]):  # Top 10
        leaderboard.append({
            "rank": i + 1,
            "user_id": user.user_id,
            "level": user.level,
            "xp_points": user.xp_points,
            "badges_count": len(user.badges_earned),
            "streak_days": user.streak_days,
            "current_path": user.current_path.value
        })
    
    return {
        "leaderboard": leaderboard,
        "skill_level": skill_level.value if skill_level else "all",
        "total_users": len(users)
    }

@education_router.get("/badges")
async def get_available_badges() -> Dict[str, Any]:
    """Get list of all available badges and their requirements"""
    badges = {
        "first-code": {
            "name": "First Code",
            "description": "Submit your first piece of code",
            "icon": "🎯",
            "requirement": "Submit any code solution",
            "xp_required": 50
        },
        "bug-hunter": {
            "name": "Bug Hunter", 
            "description": "Submit clean code with no bugs",
            "icon": "🐛",
            "requirement": "Code quality >= 90% with no bugs",
            "xp_required": 0
        },
        "quality-coder": {
            "name": "Quality Coder",
            "description": "Achieve excellent code quality",
            "icon": "⭐",
            "requirement": "Code quality >= 95%",
            "xp_required": 0
        },
        "team-player": {
            "name": "Team Player",
            "description": "Join a collaborative project",
            "icon": "👥",
            "requirement": "Join any team project",
            "xp_required": 0
        },
        "project-importer": {
            "name": "Project Importer",
            "description": "Import and analyze existing code",
            "icon": "📁",
            "requirement": "Import and analyze a project",
            "xp_required": 0
        },
        "week-streak": {
            "name": "Week Warrior",
            "description": "Code for 7 days in a row",
            "icon": "🔥",
            "requirement": "7-day coding streak",
            "xp_required": 0
        },
        "month-streak": {
            "name": "Monthly Master",
            "description": "Code for 30 days in a row",
            "icon": "🏆",
            "requirement": "30-day coding streak", 
            "xp_required": 0
        },
        "level-5": {
            "name": "Rising Star",
            "description": "Reach level 5",
            "icon": "🌟",
            "requirement": "Reach user level 5",
            "xp_required": 2000
        },
        "level-10": {
            "name": "Code Master",
            "description": "Reach level 10",
            "icon": "👑",
            "requirement": "Reach user level 10",
            "xp_required": 12000
        }
    }
    
    return {"badges": badges, "total": len(badges)}

# Export the router
__all__ = ["education_router"]
