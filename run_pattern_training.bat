@echo off
cd /d "%~dp0"
echo Starting Pattern Training...
python extended_pattern_training.py
echo Training Complete!
pause
