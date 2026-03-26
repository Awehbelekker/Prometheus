@echo off
title D: Drive GPT-OSS Finder
color 0B
cls

echo ======================================================================
echo                  D: DRIVE GPT-OSS FINDER
echo ======================================================================
echo.

if not exist D:\ (
    echo ERROR: D: drive not accessible!
    pause
    exit
)

echo [D: DRIVE CONTENTS]
echo ------------------------------------------------------------------
dir D:\ /b
echo.

echo [SEARCHING FOR GPT/OSS/LLM RELATED FOLDERS]
echo ------------------------------------------------------------------

echo Searching for *gpt*...
dir D:\*gpt* /b /ad 2>nul
dir D:\*GPT* /b /ad 2>nul

echo Searching for *oss*...
dir D:\*oss* /b /ad 2>nul
dir D:\*OSS* /b /ad 2>nul

echo Searching for *llm*...
dir D:\*llm* /b /ad 2>nul
dir D:\*LLM* /b /ad 2>nul

echo Searching for *model*...
dir D:\*model* /b /ad 2>nul
dir D:\*Model* /b /ad 2>nul

echo Searching for *ollama*...
dir D:\*ollama* /b /ad 2>nul
dir D:\*Ollama* /b /ad 2>nul

echo Searching for *hugging*...
dir D:\*hugging* /b /ad 2>nul

echo.
echo [DEEP SEARCH - First Level Subfolders]
echo ------------------------------------------------------------------
for /d %%D in (D:\*) do (
    echo Checking: %%D
    dir "%%D\*gpt*" /b /ad 2>nul
    dir "%%D\*GPT*" /b /ad 2>nul
    dir "%%D\*oss*" /b /ad 2>nul
    dir "%%D\*llm*" /b /ad 2>nul
    dir "%%D\*model*" /b /ad 2>nul
)

echo.
echo ======================================================================
pause
