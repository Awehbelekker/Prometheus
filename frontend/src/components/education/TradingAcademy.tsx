import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  LinearProgress,
  IconButton,
  Collapse,
  alpha,
  Avatar
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  Lock,
  ExpandMore,
  ExpandLess,
  School,
  TrendingUp,
  Psychology,
  Security,
  Speed
} from '@mui/icons-material';

interface Lesson {
  id: string;
  title: string;
  description: string;
  duration: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  category: string;
  isCompleted: boolean;
  isLocked: boolean;
  progress: number;
  icon: React.ElementType;
}

interface Course {
  id: string;
  title: string;
  description: string;
  totalLessons: number;
  completedLessons: number;
  estimatedTime: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  isEnrolled: boolean;
  lessons: Lesson[];
}

interface TradingAcademyProps {
  userId: string;
  onStartLesson?: (lessonId: string) => void;
  onEnrollCourse?: (courseId: string) => void;
}

const TradingAcademy: React.FC<TradingAcademyProps> = ({
  userId,
  onStartLesson,
  onEnrollCourse
}) => {
  const [expandedCourse, setExpandedCourse] = useState<string | null>(null);

  const courses: Course[] = [
    {
      id: '1',
      title: 'Trading Fundamentals',
      description: 'Learn the basics of trading, market mechanics, and essential concepts.',
      totalLessons: 8,
      completedLessons: 3,
      estimatedTime: '2 hours',
      difficulty: 'Beginner',
      isEnrolled: true,
      lessons: [
        {
          id: '1-1',
          title: 'What is Trading?',
          description: 'Introduction to financial markets and trading concepts.',
          duration: '15 min',
          difficulty: 'Beginner',
          category: 'Basics',
          isCompleted: true,
          isLocked: false,
          progress: 100,
          icon: School
        },
        {
          id: '1-2',
          title: 'Market Types & Instruments',
          description: 'Understanding stocks, bonds, forex, and other financial instruments.',
          duration: '20 min',
          difficulty: 'Beginner',
          category: 'Basics',
          isCompleted: true,
          isLocked: false,
          progress: 100,
          icon: TrendingUp
        },
        {
          id: '1-3',
          title: 'Risk Management Basics',
          description: 'Learn how to protect your capital and manage risk.',
          duration: '25 min',
          difficulty: 'Beginner',
          category: 'Risk',
          isCompleted: true,
          isLocked: false,
          progress: 100,
          icon: Security
        },
        {
          id: '1-4',
          title: 'Technical Analysis Introduction',
          description: 'Understanding charts, patterns, and technical indicators.',
          duration: '30 min',
          difficulty: 'Beginner',
          category: 'Analysis',
          isCompleted: false,
          isLocked: false,
          progress: 0,
          icon: Psychology
        },
        {
          id: '1-5',
          title: 'Order Types & Execution',
          description: 'Market orders, limit orders, and execution strategies.',
          duration: '20 min',
          difficulty: 'Beginner',
          category: 'Execution',
          isCompleted: false,
          isLocked: false,
          progress: 0,
          icon: Speed
        },
        {
          id: '1-6',
          title: 'Trading Psychology',
          description: 'Mastering emotions and developing a trader mindset.',
          duration: '25 min',
          difficulty: 'Beginner',
          category: 'Psychology',
          isCompleted: false,
          isLocked: false,
          progress: 0,
          icon: Psychology
        },
        {
          id: '1-7',
          title: 'Building Your First Strategy',
          description: 'Create and test your first trading strategy.',
          duration: '35 min',
          difficulty: 'Beginner',
          category: 'Strategy',
          isCompleted: false,
          isLocked: false,
          progress: 0,
          icon: TrendingUp
        },
        {
          id: '1-8',
          title: 'Paper Trading Practice',
          description: 'Apply your knowledge with risk-free paper trading.',
          duration: '40 min',
          difficulty: 'Beginner',
          category: 'Practice',
          isCompleted: false,
          isLocked: false,
          progress: 0,
          icon: School
        }
      ]
    },
    {
      id: '2',
      title: 'AI-Powered Trading',
      description: 'Master the use of artificial intelligence in modern trading strategies.',
      totalLessons: 6,
      completedLessons: 0,
      estimatedTime: '3 hours',
      difficulty: 'Intermediate',
      isEnrolled: false,
      lessons: [
        {
          id: '2-1',
          title: 'Introduction to AI Trading',
          description: 'Understanding how AI revolutionizes trading.',
          duration: '25 min',
          difficulty: 'Intermediate',
          category: 'AI Basics',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Psychology
        },
        {
          id: '2-2',
          title: 'Machine Learning in Markets',
          description: 'How ML algorithms analyze market data.',
          duration: '30 min',
          difficulty: 'Intermediate',
          category: 'AI Basics',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: TrendingUp
        },
        {
          id: '2-3',
          title: 'Neural Networks for Trading',
          description: 'Deep learning applications in financial markets.',
          duration: '35 min',
          difficulty: 'Intermediate',
          category: 'AI Advanced',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Psychology
        },
        {
          id: '2-4',
          title: 'Sentiment Analysis',
          description: 'Using AI to analyze market sentiment and news.',
          duration: '30 min',
          difficulty: 'Intermediate',
          category: 'AI Advanced',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Psychology
        },
        {
          id: '2-5',
          title: 'Algorithmic Trading Strategies',
          description: 'Building and deploying AI trading algorithms.',
          duration: '40 min',
          difficulty: 'Intermediate',
          category: 'Strategy',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Speed
        },
        {
          id: '2-6',
          title: 'Risk Management with AI',
          description: 'AI-powered risk assessment and management.',
          duration: '35 min',
          difficulty: 'Intermediate',
          category: 'Risk',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Security
        }
      ]
    },
    {
      id: '3',
      title: 'Advanced Strategies',
      description: 'Master complex trading strategies and market analysis techniques.',
      totalLessons: 5,
      completedLessons: 0,
      estimatedTime: '4 hours',
      difficulty: 'Advanced',
      isEnrolled: false,
      lessons: [
        {
          id: '3-1',
          title: 'Options Trading Strategies',
          description: 'Advanced options strategies for experienced traders.',
          duration: '45 min',
          difficulty: 'Advanced',
          category: 'Options',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: TrendingUp
        },
        {
          id: '3-2',
          title: 'Quantitative Analysis',
          description: 'Mathematical models and quantitative trading.',
          duration: '50 min',
          difficulty: 'Advanced',
          category: 'Quant',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Psychology
        },
        {
          id: '3-3',
          title: 'High-Frequency Trading',
          description: 'Understanding HFT and algorithmic execution.',
          duration: '40 min',
          difficulty: 'Advanced',
          category: 'HFT',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Speed
        },
        {
          id: '3-4',
          title: 'Portfolio Optimization',
          description: 'Advanced portfolio management and optimization.',
          duration: '45 min',
          difficulty: 'Advanced',
          category: 'Portfolio',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: TrendingUp
        },
        {
          id: '3-5',
          title: 'Market Microstructure',
          description: 'Understanding market dynamics and order flow.',
          duration: '50 min',
          difficulty: 'Advanced',
          category: 'Microstructure',
          isCompleted: false,
          isLocked: true,
          progress: 0,
          icon: Psychology
        }
      ]
    }
  ];

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      'Beginner': '#4caf50',
      'Intermediate': '#ff9800',
      'Advanced': '#f44336'
    };
    return colors[difficulty as keyof typeof colors] || '#2196f3';
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      'Basics': '#2196f3',
      'Risk': '#f44336',
      'Analysis': '#9c27b0',
      'Execution': '#ff9800',
      'Psychology': '#4caf50',
      'Strategy': '#00d4ff',
      'Practice': '#795548',
      'AI Basics': '#e91e63',
      'AI Advanced': '#9c27b0',
      'Options': '#ff5722',
      'Quant': '#607d8b',
      'HFT': '#3f51b5',
      'Portfolio': '#009688',
      'Microstructure': '#673ab7'
    };
    return colors[category as keyof typeof colors] || '#2196f3';
  };

  const toggleCourse = (courseId: string) => {
    setExpandedCourse(expandedCourse === courseId ? null : courseId);
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ color: '#00d4ff', fontWeight: 600, mb: 4 }}>
        🎓 Trading Academy
      </Typography>

      <Grid container spacing={3}>
        {courses.map((course) => (
          <Grid item xs={12} key={course.id}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 3,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 8px 25px rgba(0, 212, 255, 0.15)'
              }
            }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Avatar sx={{
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      mr: 2
                    }}>
                      <School />
                    </Avatar>
                    <Box>
                      <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                        {course.title}
                      </Typography>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        {course.description}
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Chip
                      label={course.difficulty}
                      size="small"
                      sx={{
                        backgroundColor: alpha(getDifficultyColor(course.difficulty), 0.2),
                        color: getDifficultyColor(course.difficulty),
                        border: `1px solid ${alpha(getDifficultyColor(course.difficulty), 0.3)}`
                      }}
                    />
                    <IconButton
                      onClick={() => toggleCourse(course.id)}
                      sx={{ color: '#00d4ff' }}
                    >
                      {expandedCourse === course.id ? <ExpandLess /> : <ExpandMore />}
                    </IconButton>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      Progress:
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      {course.completedLessons}/{course.totalLessons} lessons
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      Duration:
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                      {course.estimatedTime}
                    </Typography>
                  </Box>
                </Box>

                <LinearProgress
                  variant="determinate"
                  value={(course.completedLessons / course.totalLessons) * 100}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      borderRadius: 3
                    }
                  }}
                />

                <Collapse in={expandedCourse === course.id}>
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="h6" sx={{ color: '#00d4ff', mb: 2 }}>
                      Lessons
                    </Typography>
                    <Grid container spacing={2}>
                      {course.lessons.map((lesson) => (
                        <Grid item xs={12} sm={6} md={4} key={lesson.id}>
                          <Card sx={{
                            background: lesson.isCompleted 
                              ? 'linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%)'
                              : lesson.isLocked
                                ? 'linear-gradient(135deg, rgba(158, 158, 158, 0.1) 0%, rgba(158, 158, 158, 0.05) 100%)'
                                : 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
                            border: lesson.isCompleted 
                              ? '1px solid rgba(76, 175, 80, 0.3)'
                              : lesson.isLocked
                                ? '1px solid rgba(158, 158, 158, 0.3)'
                                : '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: 2,
                            transition: 'all 0.3s ease',
                            '&:hover': !lesson.isLocked ? {
                              transform: 'translateY(-2px)',
                              boxShadow: '0 4px 12px rgba(0, 212, 255, 0.2)'
                            } : {}
                          }}>
                            <CardContent sx={{ p: 2 }}>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                                {lesson.isCompleted ? (
                                  <CheckCircle sx={{ color: '#4caf50', fontSize: 20, mr: 1 }} />
                                ) : lesson.isLocked ? (
                                  <Lock sx={{ color: '#9e9e9e', fontSize: 20, mr: 1 }} />
                                ) : (
                                  <PlayArrow sx={{ color: '#00d4ff', fontSize: 20, mr: 1 }} />
                                )}
                                <Typography variant="body2" sx={{ 
                                  color: lesson.isLocked ? '#9e9e9e' : 'white',
                                  fontWeight: 600,
                                  flex: 1
                                }}>
                                  {lesson.title}
                                </Typography>
                              </Box>
                              <Typography variant="caption" sx={{ color: '#aaa', mb: 1, display: 'block' }}>
                                {lesson.description}
                              </Typography>
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                                <Chip
                                  label={lesson.category}
                                  size="small"
                                  sx={{
                                    height: 18,
                                    fontSize: '0.7rem',
                                    backgroundColor: alpha(getCategoryColor(lesson.category), 0.2),
                                    color: getCategoryColor(lesson.category),
                                    border: `1px solid ${alpha(getCategoryColor(lesson.category), 0.3)}`
                                  }}
                                />
                                <Typography variant="caption" sx={{ color: '#aaa' }}>
                                  {lesson.duration}
                                </Typography>
                              </Box>
                              {lesson.progress > 0 && (
                                <LinearProgress
                                  variant="determinate"
                                  value={lesson.progress}
                                  sx={{
                                    height: 4,
                                    borderRadius: 2,
                                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                    '& .MuiLinearProgress-bar': {
                                      background: 'linear-gradient(45deg, #4caf50, #8bc34a)',
                                      borderRadius: 2
                                    }
                                  }}
                                />
                              )}
                              {!lesson.isLocked && (
                                <Button
                                  fullWidth
                                  variant="outlined"
                                  size="small"
                                  startIcon={lesson.isCompleted ? <CheckCircle /> : <PlayArrow />}
                                  onClick={() => onStartLesson?.(lesson.id)}
                                  sx={{
                                    mt: 1,
                                    borderColor: lesson.isCompleted ? '#4caf50' : '#00d4ff',
                                    color: lesson.isCompleted ? '#4caf50' : '#00d4ff',
                                    '&:hover': {
                                      borderColor: lesson.isCompleted ? '#4caf50' : '#0099cc',
                                      backgroundColor: lesson.isCompleted 
                                        ? alpha('#4caf50', 0.1) 
                                        : alpha('#00d4ff', 0.1)
                                    }
                                  }}
                                >
                                  {lesson.isCompleted ? 'Review' : 'Start Lesson'}
                                </Button>
                              )}
                            </CardContent>
                          </Card>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </Collapse>

                {!course.isEnrolled && (
                  <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Button
                      variant="contained"
                      onClick={() => onEnrollCourse?.(course.id)}
                      sx={{
                        background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                        '&:hover': {
                          background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
                        }
                      }}
                    >
                      Enroll in Course
                    </Button>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default TradingAcademy;
