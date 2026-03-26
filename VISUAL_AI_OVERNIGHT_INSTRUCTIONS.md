# PROMETHEUS Visual AI Overnight Training Guide

## Quick Start

### Option 1: Run Manually Tonight
Just double-click:
```
RUN_VISUAL_AI_OVERNIGHT.bat
```

### Option 2: Schedule Automatic Overnight Training

#### Using Windows Task Scheduler:

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create New Task**
   - Click "Create Task" (not Basic Task)

3. **General Tab**
   - Name: `PROMETHEUS Visual AI Training`
   - Check "Run whether user is logged on or not"
   - Check "Run with highest privileges"

4. **Triggers Tab**
   - Click "New"
   - Begin: On a schedule
   - Daily, Start at: **2:00 AM**
   - Check "Enabled"

5. **Actions Tab**
   - Click "New"
   - Action: Start a program
   - Program: `C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\RUN_VISUAL_AI_OVERNIGHT.bat`
   - Start in: `C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform`

6. **Conditions Tab**
   - Uncheck "Start only if computer is on AC power" (optional)

7. **Settings Tab**
   - Check "Allow task to be run on demand"
   - Check "Stop task if it runs longer than 6 hours"

8. Click **OK** and enter your Windows password

---

## What the Training Does

1. **Checks if it's a good time** (overnight/weekend = low system load)
2. **Pauses Learning Engine** if CPU > 70%
3. **Analyzes charts** with LLaVA vision model
4. **Detects patterns**:
   - Head & Shoulders
   - Double Top/Bottom
   - Bull/Bear Flags
   - Cup & Handle
   - Wedges
   - And 45+ more patterns
5. **Saves results** to `visual_ai_patterns.json`
6. **Resumes Learning Engine** when done

---

## Progress & Results

- **Log file**: `visual_ai_overnight.log`
- **Results**: `visual_ai_patterns.json`
- **Training time**: ~3-5 hours for all 1,320 charts

---

## Quick Test (5 charts only)

To test if Visual AI is working:
```
python VISUAL_AI_OVERNIGHT_TRAINING.py 5
```

---

## Files Created

| File | Purpose |
|------|---------|
| `VISUAL_AI_OVERNIGHT_TRAINING.py` | Main training script |
| `RUN_VISUAL_AI_OVERNIGHT.bat` | Easy launcher |
| `visual_ai_overnight.log` | Training progress log |
| `visual_ai_patterns.json` | Learned patterns database |

---

## Troubleshooting

### Training Too Slow
- Run only overnight when markets closed
- Ensure Ollama is running: `ollama serve`

### Ollama Not Responding
```
taskkill /f /im ollama.exe
ollama serve
```

### Skip Already Analyzed Charts
The script automatically skips charts that were already analyzed.

---

## Integration with Live Trading

Once training completes, the patterns in `visual_ai_patterns.json` are automatically used by the trading system for:
- Confirming entry signals
- Identifying chart patterns
- Trend confirmation
- Support/Resistance awareness
