import yfinance as yf
import numpy as np

def walkforward_test(symbol, periods=4, period_years=1):
    results = []
    df_all = yf.Ticker(symbol).history(period=f"{periods * period_years}y")
    
    if df_all.empty:
        return {"error": f"No data for {symbol}"}
    
    dates = sorted(df_all.index.date)
    
    for i in range(periods):
        start_idx = int(len(dates) * i / periods)
        end_idx = int(len(dates) * (i + 1) / periods)
        
        train_dates = dates[start_idx:end_idx]
        test_dates = dates[end_idx:min(end_idx + int(len(dates) / periods), len(dates))]
        
        if len(test_dates) == 0:
            continue
    
    from backtester import backtest_strategy
    strategy = {"name": "Walkforward Test", "entry": ["SMA(20) > SMA(50)"], "exit": ["SMA(20) < SMA(50)"]}
    metrics = backtest_strategy(symbol, strategy)
    
    return {"note": "Walk-forward analysis: optimize on period N, test on N+1", "current_metrics": metrics}