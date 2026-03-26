"""Auto-run backtest learning in Full Suite mode"""
import sys
sys.path.insert(0, '.')

# Import and run directly with option 4 (Full Suite)
from run_continuous_learning_backtest import ContinuousLearningBacktest

learner = ContinuousLearningBacktest(initial_capital=10000.0)
learner.run_extended_backtest_suite(years_list=[10, 20, 50])
