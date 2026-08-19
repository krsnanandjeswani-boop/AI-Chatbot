import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "strategy_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS strategies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        symbol TEXT,
        parameters TEXT,
        metrics TEXT,
        market_regime TEXT,
        notes TEXT,
        date_tested TEXT,
        sharpe REAL,
        max_drawdown REAL,
        cagr REAL
    )""")
    conn.commit()
    conn.close()

def save_strategy(strategy, metrics, regime="unknown", notes=""):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Support portfolio/basket strategies: store universe in symbol field
    universe = strategy.get("universe", [])
    if isinstance(universe, list) and len(universe) > 0:
        symbol_field = "+".join(universe)
    else:
        symbol_field = metrics.get("symbol", "")

    # Prefer validation verdict metrics if present (nested report)
    if "in_sample_metrics" in metrics:
        is_metrics = metrics.get("in_sample_metrics", {})
    else:
        is_metrics = metrics

    c.execute("""INSERT INTO strategies 
        (name, symbol, parameters, metrics, market_regime, notes, date_tested, sharpe, max_drawdown, cagr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            strategy.get("name", "unnamed"),
            symbol_field,
            json.dumps(strategy),
            json.dumps(metrics),
            regime,
            notes,
            datetime.now().isoformat(),
            is_metrics.get("sharpe", 0),
            is_metrics.get("max_drawdown", 0),
            is_metrics.get("cagr", 0)
        ))
    conn.commit()
    conn.close()

def query_strategies(sharpe_gt=0, dd_gt=-100, regime="all"):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = "SELECT * FROM strategies WHERE sharpe >= ?"
    params = [sharpe_gt]
    
    if regime != "all":
        query += " AND market_regime = ?"
        params.append(regime)
    
    query += " ORDER BY date_tested DESC"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    return [
        {"name": r[1], "symbol": r[2], "parameters": json.loads(r[3]), 
         "metrics": json.loads(r[4]), "regime": r[5], "notes": r[6]}
        for r in rows if float(r[8] or 0) >= dd_gt
    ]