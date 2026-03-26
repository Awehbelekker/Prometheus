@echo off
title PROMETHEUS - Broker Status Check
color 0E
cls

echo ======================================================================
echo              PROMETHEUS BROKER CONFIGURATION STATUS
echo ======================================================================
echo.

echo [BROKER API KEYS - From .env File]
echo ------------------------------------------------------------------
for /f "tokens=1,2 delims==" %%a in ('type .env ^| findstr /i "ALPACA IB_"') do (
    echo   %%a: %%b
)

echo.
echo [TRADING SCRIPTS AVAILABLE]
echo ------------------------------------------------------------------
echo.
echo   INTERNAL PAPER TRADING (No Real Orders):
if exist prometheus_active_trading_session.py (
    echo     [OK] prometheus_active_trading_session.py
    echo         - Uses: SIMULATED trades only (no broker connection)
    echo         - Good for: Testing AI signals without real money
)
if exist paper_trading_with_all_ai_systems.py (
    echo     [OK] paper_trading_with_all_ai_systems.py  
    echo         - Uses: SIMULATED trades only
)

echo.
echo   LIVE TRADING WITH REAL BROKERS:
if exist improved_dual_broker_trading.py (
    echo     [OK] improved_dual_broker_trading.py
    echo         - Uses: ALPACA ^(Live^) + INTERACTIVE BROKERS ^(Live^)
    echo         - Executes REAL orders with real money!
)
if exist final_dual_broker_fixed.py (
    echo     [OK] final_dual_broker_fixed.py
    echo         - Uses: DUAL BROKER ^(Alpaca + IB^)
)
if exist dual_broker_live_trading.py (
    echo     [OK] dual_broker_live_trading.py
    echo         - Uses: DUAL BROKER LIVE
)

echo.
echo ======================================================================
echo                    RECOMMENDATION
echo ======================================================================
echo.
echo   FOR SIMULATED TESTING:
echo     python prometheus_active_trading_session.py
echo.
echo   FOR LIVE TRADING WITH REAL BROKERS:
echo     python improved_dual_broker_trading.py
echo.
echo   NOTE: Your .env shows ALPACA_PAPER_TRADING=false
echo         This means Alpaca is configured for LIVE trading!
echo.
echo ======================================================================
pause
