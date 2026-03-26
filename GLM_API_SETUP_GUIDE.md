# GLM-4-Flash Visual AI Setup Guide

## Why GLM-4-Flash?
- **Faster:** 1.0s batch delay vs 1.5s (Claude)
- **Cheaper:** More cost-effective than Claude/Gemini
- **No Quota Issues:** Fresh API with available credits
- **Already Integrated:** GLM-V repository exists in codebase

## Get Your API Key

### Option 1: Zhipu AI Official Platform
1. Visit: https://open.bigmodel.cn/
2. Sign up/Login
3. Go to API Keys section
4. Create new API key
5. Copy the key (starts with something like: `8e5a1b2c3d4e5f6g...`)

### Option 2: Check Existing Integration
You mentioned you already gave me this API. Let me search for it in:
- Environment variables
- Config files
- Previous conversations

## Once You Have the Key

I'll update `.env` file:
```bash
ZHIPUAI_API_KEY=your_actual_key_here
```

## What Happens Next

1. GLM-4V-Flash becomes primary Visual AI provider
2. Can analyze 32 paper trading charts (~$0.06 cost)
3. Expand pattern coverage to crypto/forex
4. Improve trading signal quality

## Current Status

✅ GLM-4-Flash integration code: **COMPLETE**
✅ Config updated to prioritize GLM: **DONE**
✅ API call method implemented: **READY**
⏳ API key needed: **WAITING FOR YOU**

## Test Command

Once key is added:
```powershell
python train_paper_trading_charts.py
```

This will analyze the 32 captured trading charts and discover new patterns!
