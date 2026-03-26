# Alpaca Credentials Setup

## Current Status

❌ **Alpaca API credentials NOT FOUND**

The system checked for these variable names:

- `ALPACA_LIVE_KEY` / `ALPACA_LIVE_API_KEY` / `ALPACA_API_KEY` / `APCA_API_KEY_ID` / `ALPACA_KEY`
- `ALPACA_LIVE_SECRET` / `ALPACA_LIVE_SECRET_KEY` / `ALPACA_SECRET_KEY` / `APCA_API_SECRET_KEY` / `ALPACA_SECRET`

**None were found in environment variables.**

---

## Solution: Add to .env File

### Step 1: Get Your Alpaca API Keys

1. Go to: https://app.alpaca.markets/
2. Log in to your account
3. Go to: **Dashboard** → **API Keys**
4. Copy your:
   - **API Key ID**
   - **Secret Key**

### Step 2: Add to .env File

Edit the `.env` file in the project root and add:

```env

# Alpaca API Credentials (for crypto trading 24/7)

ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here

# OR use these names (both work)

ALPACA_LIVE_KEY=your_api_key_here
ALPACA_LIVE_SECRET=your_secret_key_here

```

**Important**: Replace `your_api_key_here` and `your_secret_key_here` with your actual keys!

### Step 3: Restart Prometheus

After adding credentials, restart:

```powershell

python full_system_restart.py

```

---

## Alternative: Paper Trading

If you want to use Alpaca Paper Trading (free, no real money):

1. Get paper trading keys from: https://app.alpaca.markets/paper/dashboard/overview
2. Add to `.env`:

   ```env

   ALPACA_API_KEY=your_paper_api_key
   ALPACA_SECRET_KEY=your_paper_secret

   ```
```text

3. The system will automatically use paper trading if configured

---

## Verification

After adding credentials, verify with:

```powershell

python fix_alpaca_credentials.py

```

Expected output:

```
```text
[OK] Alpaca credentials found!
   API Key: ALPACA_API_KEY
   Secret: ALPACA_SECRET_KEY

```

---

## Note

**Alpaca is OPTIONAL** - The system can trade on:

- ✅ Interactive Brokers (stocks, options, forex) - Already configured
- ⚠️ Alpaca (crypto 24/7) - Needs credentials

If you don't use Alpaca, the system will work fine with just IB.

---

## Quick Reference

**Required Variables** (choose one set):

- `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` (recommended)
- OR `ALPACA_LIVE_KEY` and `ALPACA_LIVE_SECRET`

**After adding**: Restart Prometheus to load new credentials.

