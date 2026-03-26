#!/usr/bin/env python3
"""
🔥 PROMETHEUS MASTER BENCHMARK SUITE 🔥
Complete testing of ALL systems across ALL levels after ALL enhancements

Benchmarks:
1. CORE SYSTEMS - Database, persistence, configuration
2. AI INTELLIGENCE - Local models, OpenAI, knowledge base
3. TRADING ENGINE - Signals, execution, risk management
4. BROKER CONNECTIVITY - Alpaca, Interactive Brokers
5. DATA SOURCES - Real-time feeds, historical data
6. LEARNING SYSTEMS - Pattern recognition, backtesting
7. KNOWLEDGE BASE - Research paper integration
8. PERFORMANCE - Speed, accuracy, memory usage
"""

import sys
import os
import json
import time
import sqlite3
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

class BenchmarkResult:
    """Container for benchmark results"""
    def __init__(self, name: str):
        self.name = name
        self.tests = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.score = 0.0
        self.start_time = None
        self.end_time = None
        
    def add_test(self, test_name: str, passed: bool, details: str = "", score: float = 0.0):
        status = "PASS" if passed else "FAIL"
        self.tests.append({
            "name": test_name,
            "status": status,
            "details": details,
            "score": score
        })
        if passed:
            self.passed += 1
        else:
            self.failed += 1
        self.score += score
        
    def add_warning(self, test_name: str, details: str):
        self.tests.append({
            "name": test_name,
            "status": "WARN",
            "details": details,
            "score": 0
        })
        self.warnings += 1


class PrometheusMasterBenchmark:
    """Master benchmark suite for all PROMETHEUS systems"""
    
    def __init__(self):
        self.results: Dict[str, BenchmarkResult] = {}
        self.overall_score = 0.0
        self.max_score = 0.0
        self.start_time = datetime.now()
        
    def print_header(self, title: str, char: str = "="):
        width = 100
        print()
        print(char * width)
        print(f"  {title}")
        print(char * width)
        
    def print_section(self, title: str):
        print()
        print("-" * 80)
        print(f"  📋 {title}")
        print("-" * 80)
        
    def print_result(self, test: str, passed: bool, details: str = "", score: float = 0):
        icon = "✅" if passed else "❌"
        score_str = f"[{score:.1f} pts]" if score > 0 else ""
        print(f"  {icon} {test}: {details} {score_str}")
        
    def print_warning(self, test: str, details: str):
        print(f"  ⚠️  {test}: {details}")

    # =========================================================================
    # LEVEL 1: CORE SYSTEMS BENCHMARK
    # =========================================================================
    def benchmark_core_systems(self) -> BenchmarkResult:
        """Test core system components"""
        result = BenchmarkResult("Core Systems")
        result.start_time = time.time()
        self.print_header("LEVEL 1: CORE SYSTEMS BENCHMARK", "█")
        
        # Test 1.1: Database connectivity
        self.print_section("Database Systems")
        db_files = [
            "trading_system.db",
            "prometheus_persistence.db",
            "paper_trading.db",
            "enhanced_paper_trading.db",
            "ai_learning.db",
            "gamification.db",
            "knowledge_base.db"
        ]
        
        for db_file in db_files:
            try:
                if os.path.exists(db_file):
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()
                    result.add_test(f"Database: {db_file}", True, f"{len(tables)} tables", 2.0)
                    self.print_result(f"Database: {db_file}", True, f"{len(tables)} tables", 2.0)
                else:
                    result.add_test(f"Database: {db_file}", False, "Not found")
                    self.print_result(f"Database: {db_file}", False, "Not found")
            except Exception as e:
                result.add_test(f"Database: {db_file}", False, str(e)[:50])
                self.print_result(f"Database: {db_file}", False, str(e)[:50])
        
        # Test 1.2: Configuration files
        self.print_section("Configuration Files")
        config_files = [
            ".env",
            "advanced_features_config.json",
            "ai_signal_weights_config.json",
            "trading_config.json",
            "risk_management_config.json"
        ]
        
        for config_file in config_files:
            try:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                    size = len(content)
                    result.add_test(f"Config: {config_file}", True, f"{size} bytes", 1.5)
                    self.print_result(f"Config: {config_file}", True, f"{size} bytes", 1.5)
                else:
                    result.add_warning(f"Config: {config_file}", "Optional config missing")
                    self.print_warning(f"Config: {config_file}", "Optional config missing")
            except Exception as e:
                result.add_test(f"Config: {config_file}", False, str(e)[:50])
                self.print_result(f"Config: {config_file}", False, str(e)[:50])
        
        # Test 1.3: Core module imports
        self.print_section("Core Module Imports")
        core_modules = [
            ("core.trading_engine", "TradingEngine"),
            ("core.persistence_layer", "PersistenceLayer"),
            ("core.risk_management", "RiskManager"),
            ("core.portfolio_manager", "PortfolioManager"),
        ]
        
        for module_path, class_name in core_modules:
            try:
                module = __import__(module_path, fromlist=[class_name])
                if hasattr(module, class_name):
                    result.add_test(f"Module: {module_path}", True, f"{class_name} available", 3.0)
                    self.print_result(f"Module: {module_path}", True, f"{class_name} available", 3.0)
                else:
                    result.add_test(f"Module: {module_path}", False, f"{class_name} not found")
                    self.print_result(f"Module: {module_path}", False, f"{class_name} not found")
            except Exception as e:
                result.add_warning(f"Module: {module_path}", str(e)[:60])
                self.print_warning(f"Module: {module_path}", str(e)[:60])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 2: AI INTELLIGENCE BENCHMARK
    # =========================================================================
    def benchmark_ai_intelligence(self) -> BenchmarkResult:
        """Test AI intelligence systems"""
        result = BenchmarkResult("AI Intelligence")
        result.start_time = time.time()
        self.print_header("LEVEL 2: AI INTELLIGENCE BENCHMARK", "█")
        
        # Test 2.1: Local Ollama models
        self.print_section("Local AI Models (Ollama)")
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m.get("name", "unknown") for m in models]
                result.add_test("Ollama Connection", True, f"{len(models)} models available", 5.0)
                self.print_result("Ollama Connection", True, f"{len(models)} models", 5.0)
                
                # Test key models (check for installed 7b/8b versions)
                key_models = ["deepseek-r1:8b", "qwen2.5:7b", "llava:7b"]
                for model in key_models:
                    found = any(model in m for m in model_names)
                    result.add_test(f"Model: {model}", found, "Available" if found else "Not found", 3.0 if found else 0)
                    self.print_result(f"Model: {model}", found, "Available" if found else "Not found", 3.0 if found else 0)
            else:
                result.add_test("Ollama Connection", False, f"HTTP {response.status_code}")
                self.print_result("Ollama Connection", False, f"HTTP {response.status_code}")
        except Exception as e:
            result.add_test("Ollama Connection", False, str(e)[:50])
            self.print_result("Ollama Connection", False, str(e)[:50])
        
        # Test 2.2: OpenAI integration
        self.print_section("OpenAI Integration")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            openai_key = os.getenv("OPENAI_API_KEY", "")
            if openai_key and len(openai_key) > 20:
                result.add_test("OpenAI API Key", True, f"Key configured ({len(openai_key)} chars)", 5.0)
                self.print_result("OpenAI API Key", True, f"Key configured ({len(openai_key)} chars)", 5.0)
                
                # Test actual OpenAI call
                try:
                    import openai
                    client = openai.OpenAI(api_key=openai_key)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": "Say 'PROMETHEUS BENCHMARK OK' in 5 words or less"}],
                        max_tokens=20
                    )
                    answer = response.choices[0].message.content
                    result.add_test("OpenAI API Call", True, f"Response: {answer[:30]}", 10.0)
                    self.print_result("OpenAI API Call", True, f"Response: {answer[:30]}", 10.0)
                except Exception as e:
                    result.add_test("OpenAI API Call", False, str(e)[:50])
                    self.print_result("OpenAI API Call", False, str(e)[:50])
            else:
                result.add_test("OpenAI API Key", False, "Not configured")
                self.print_result("OpenAI API Key", False, "Not configured")
        except Exception as e:
            result.add_test("OpenAI Integration", False, str(e)[:50])
            self.print_result("OpenAI Integration", False, str(e)[:50])
        
        # Test 2.3: Anthropic integration
        self.print_section("Anthropic Integration")
        try:
            anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
            if anthropic_key and len(anthropic_key) > 20:
                result.add_test("Anthropic API Key", True, f"Key configured ({len(anthropic_key)} chars)", 5.0)
                self.print_result("Anthropic API Key", True, f"Key configured ({len(anthropic_key)} chars)", 5.0)
            else:
                result.add_warning("Anthropic API Key", "Not configured (optional)")
                self.print_warning("Anthropic API Key", "Not configured (optional)")
        except Exception as e:
            result.add_warning("Anthropic Integration", str(e)[:50])
            self.print_warning("Anthropic Integration", str(e)[:50])
        
        # Test 2.4: AI model inference speed
        self.print_section("AI Inference Speed Test")
        try:
            import requests
            start = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": "What is 2+2? Answer with just the number.",
                    "stream": False,
                    "options": {"num_predict": 10}
                },
                timeout=60
            )
            inference_time = time.time() - start
            if response.status_code == 200:
                answer = response.json().get("response", "")
                tokens_per_sec = 10 / inference_time if inference_time > 0 else 0
                result.add_test("Local AI Inference", True, f"{inference_time:.2f}s, ~{tokens_per_sec:.1f} tok/s", 8.0)
                self.print_result("Local AI Inference", True, f"{inference_time:.2f}s, ~{tokens_per_sec:.1f} tok/s", 8.0)
            else:
                result.add_test("Local AI Inference", False, f"HTTP {response.status_code}")
                self.print_result("Local AI Inference", False, f"HTTP {response.status_code}")
        except Exception as e:
            result.add_warning("Local AI Inference", str(e)[:50])
            self.print_warning("Local AI Inference", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 3: KNOWLEDGE BASE BENCHMARK
    # =========================================================================
    def benchmark_knowledge_base(self) -> BenchmarkResult:
        """Test knowledge base and research paper integration"""
        result = BenchmarkResult("Knowledge Base")
        result.start_time = time.time()
        self.print_header("LEVEL 3: KNOWLEDGE BASE BENCHMARK", "█")
        
        # Test 3.1: ChromaDB connection
        self.print_section("ChromaDB Vector Database")
        try:
            import chromadb
            client = chromadb.PersistentClient(path="./knowledge_vectors")
            collections = client.list_collections()
            result.add_test("ChromaDB Connection", True, f"{len(collections)} collections", 5.0)
            self.print_result("ChromaDB Connection", True, f"{len(collections)} collections", 5.0)
            
            # Check main collection
            if collections:
                collection = client.get_collection("prometheus_knowledge")
                count = collection.count()
                result.add_test("Knowledge Vectors", True, f"{count} vectors stored", 8.0)
                self.print_result("Knowledge Vectors", True, f"{count} vectors stored", 8.0)
                
                # Test retrieval
                test_queries = [
                    "deep reinforcement learning portfolio optimization",
                    "momentum trading neural networks",
                    "sentiment analysis financial markets"
                ]
                
                for query in test_queries:
                    try:
                        results = collection.query(query_texts=[query], n_results=3)
                        if results and results.get("documents"):
                            docs = results["documents"][0]
                            distances = results.get("distances", [[]])[0]
                            avg_relevance = 1 - (sum(distances) / len(distances)) if distances else 0
                            result.add_test(f"Query: {query[:40]}...", True, f"{len(docs)} results, {avg_relevance:.1%} relevance", 3.0)
                            self.print_result(f"Query: {query[:40]}...", True, f"{len(docs)} results, {avg_relevance:.1%} relevance", 3.0)
                        else:
                            result.add_test(f"Query: {query[:40]}...", False, "No results")
                            self.print_result(f"Query: {query[:40]}...", False, "No results")
                    except Exception as e:
                        result.add_test(f"Query: {query[:40]}...", False, str(e)[:40])
                        self.print_result(f"Query: {query[:40]}...", False, str(e)[:40])
        except Exception as e:
            result.add_test("ChromaDB Connection", False, str(e)[:50])
            self.print_result("ChromaDB Connection", False, str(e)[:50])
        
        # Test 3.2: Research papers loaded
        self.print_section("Research Paper Integration")
        try:
            research_dir = Path("research_papers")
            if research_dir.exists():
                pdf_files = list(research_dir.glob("*.pdf"))
                txt_files = list(research_dir.glob("*.txt"))
                result.add_test("Research Papers", True, f"{len(pdf_files)} PDFs, {len(txt_files)} TXTs", 5.0)
                self.print_result("Research Papers", True, f"{len(pdf_files)} PDFs, {len(txt_files)} TXTs", 5.0)
            else:
                result.add_warning("Research Papers", "Directory not found")
                self.print_warning("Research Papers", "Directory not found")
        except Exception as e:
            result.add_warning("Research Papers", str(e)[:50])
            self.print_warning("Research Papers", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 4: TRADING ENGINE BENCHMARK
    # =========================================================================
    def benchmark_trading_engine(self) -> BenchmarkResult:
        """Test trading engine capabilities"""
        result = BenchmarkResult("Trading Engine")
        result.start_time = time.time()
        self.print_header("LEVEL 4: TRADING ENGINE BENCHMARK", "█")
        
        # Test 4.1: Signal generation
        self.print_section("Signal Generation")
        try:
            # Check if signal generation modules exist (using actual module names)
            signal_modules = [
                "core.ai_trading_intelligence",
                "core.real_ai_trading_intelligence",
                "revolutionary_master_engine"
            ]
            for module in signal_modules:
                try:
                    imported = __import__(module.replace(".", "/").replace("/", "."), fromlist=[""])
                    result.add_test(f"Module: {module}", True, "Importable", 3.0)
                    self.print_result(f"Module: {module}", True, "Importable", 3.0)
                except Exception as e:
                    result.add_warning(f"Module: {module}", str(e)[:40])
                    self.print_warning(f"Module: {module}", str(e)[:40])
        except Exception as e:
            result.add_test("Signal Generation", False, str(e)[:50])
            self.print_result("Signal Generation", False, str(e)[:50])
        
        # Test 4.2: Pattern recognition database
        self.print_section("Pattern Recognition")
        try:
            pattern_files = list(Path(".").glob("learned_patterns*.json"))
            for pf in pattern_files[:3]:
                with open(pf, 'r') as f:
                    data = json.load(f)
                pattern_count = len(data) if isinstance(data, list) else len(data.keys())
                result.add_test(f"Patterns: {pf.name}", True, f"{pattern_count} patterns", 4.0)
                self.print_result(f"Patterns: {pf.name}", True, f"{pattern_count} patterns", 4.0)
        except Exception as e:
            result.add_warning("Pattern Recognition", str(e)[:50])
            self.print_warning("Pattern Recognition", str(e)[:50])
        
        # Test 4.3: Risk management
        self.print_section("Risk Management")
        try:
            risk_config_path = Path("risk_management_config.json")
            if risk_config_path.exists():
                with open(risk_config_path, 'r') as f:
                    risk_config = json.load(f)
                result.add_test("Risk Config", True, f"{len(risk_config)} parameters", 5.0)
                self.print_result("Risk Config", True, f"{len(risk_config)} parameters", 5.0)
            else:
                # Check for inline risk params
                result.add_warning("Risk Config", "Using default parameters")
                self.print_warning("Risk Config", "Using default parameters")
        except Exception as e:
            result.add_warning("Risk Management", str(e)[:50])
            self.print_warning("Risk Management", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 5: BROKER CONNECTIVITY BENCHMARK
    # =========================================================================
    def benchmark_broker_connectivity(self) -> BenchmarkResult:
        """Test broker connections"""
        result = BenchmarkResult("Broker Connectivity")
        result.start_time = time.time()
        self.print_header("LEVEL 5: BROKER CONNECTIVITY BENCHMARK", "█")
        
        # Test 5.1: Alpaca connection
        self.print_section("Alpaca Trading")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            alpaca_key = os.getenv("ALPACA_API_KEY", "")
            alpaca_secret = os.getenv("ALPACA_SECRET_KEY", "")
            
            if alpaca_key and alpaca_secret:
                result.add_test("Alpaca Credentials", True, "Keys configured", 3.0)
                self.print_result("Alpaca Credentials", True, "Keys configured", 3.0)
                
                # Test actual connection
                try:
                    from alpaca.trading.client import TradingClient
                    # Use paper=False for LIVE trading (paper credentials not configured)
                    trading_client = TradingClient(alpaca_key, alpaca_secret, paper=False)
                    account = trading_client.get_account()
                    
                    equity = float(account.equity)
                    cash = float(account.cash)
                    buying_power = float(account.buying_power)
                    
                    result.add_test("Alpaca Account", True, f"Equity: ${equity:,.2f}", 10.0)
                    self.print_result("Alpaca Account", True, f"Equity: ${equity:,.2f}", 10.0)
                    
                    result.add_test("Alpaca Cash", True, f"Cash: ${cash:,.2f}", 5.0)
                    self.print_result("Alpaca Cash", True, f"Cash: ${cash:,.2f}", 5.0)
                    
                except Exception as e:
                    result.add_test("Alpaca Connection", False, str(e)[:50])
                    self.print_result("Alpaca Connection", False, str(e)[:50])
            else:
                result.add_test("Alpaca Credentials", False, "Not configured")
                self.print_result("Alpaca Credentials", False, "Not configured")
        except Exception as e:
            result.add_test("Alpaca Integration", False, str(e)[:50])
            self.print_result("Alpaca Integration", False, str(e)[:50])
        
        # Test 5.2: Interactive Brokers
        self.print_section("Interactive Brokers")
        try:
            ib_port = os.getenv("IB_PORT", "7497")
            ib_account = os.getenv("IB_ACCOUNT", "")
            
            if ib_account:
                result.add_test("IB Account Config", True, f"Account: {ib_account}", 3.0)
                self.print_result("IB Account Config", True, f"Account: {ib_account}", 3.0)
                
                # Check if IB Gateway/TWS is running
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    ib_result = sock.connect_ex(('127.0.0.1', int(ib_port)))
                    sock.close()
                    
                    if ib_result == 0:
                        result.add_test("IB Gateway", True, f"Running on port {ib_port}", 8.0)
                        self.print_result("IB Gateway", True, f"Running on port {ib_port}", 8.0)
                    else:
                        result.add_warning("IB Gateway", f"Not running on port {ib_port}")
                        self.print_warning("IB Gateway", f"Not running on port {ib_port}")
                except Exception as e:
                    result.add_warning("IB Gateway Check", str(e)[:50])
                    self.print_warning("IB Gateway Check", str(e)[:50])
            else:
                result.add_warning("IB Account", "Not configured")
                self.print_warning("IB Account", "Not configured")
        except Exception as e:
            result.add_warning("IB Integration", str(e)[:50])
            self.print_warning("IB Integration", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 6: DATA SOURCES BENCHMARK
    # =========================================================================
    def benchmark_data_sources(self) -> BenchmarkResult:
        """Test data source connectivity"""
        result = BenchmarkResult("Data Sources")
        result.start_time = time.time()
        self.print_header("LEVEL 6: DATA SOURCES BENCHMARK", "█")
        
        # Test 6.1: Polygon.io
        self.print_section("Market Data APIs")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            polygon_key = os.getenv("POLYGON_API_KEY", "")
            if polygon_key and len(polygon_key) > 10:
                result.add_test("Polygon.io API", True, "Key configured", 5.0)
                self.print_result("Polygon.io API", True, "Key configured", 5.0)
                
                # Test API call
                try:
                    import requests
                    response = requests.get(
                        f"https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={polygon_key}",
                        timeout=10
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("results"):
                            close_price = data["results"][0].get("c", 0)
                            result.add_test("Polygon.io Data", True, f"AAPL: ${close_price:.2f}", 8.0)
                            self.print_result("Polygon.io Data", True, f"AAPL: ${close_price:.2f}", 8.0)
                        else:
                            result.add_test("Polygon.io Data", True, "API responding", 5.0)
                            self.print_result("Polygon.io Data", True, "API responding", 5.0)
                    else:
                        result.add_warning("Polygon.io Data", f"HTTP {response.status_code}")
                        self.print_warning("Polygon.io Data", f"HTTP {response.status_code}")
                except Exception as e:
                    result.add_warning("Polygon.io Data", str(e)[:50])
                    self.print_warning("Polygon.io Data", str(e)[:50])
            else:
                result.add_warning("Polygon.io API", "Not configured")
                self.print_warning("Polygon.io API", "Not configured")
        except Exception as e:
            result.add_warning("Polygon.io", str(e)[:50])
            self.print_warning("Polygon.io", str(e)[:50])
        
        # Test 6.2: Alpaca market data
        self.print_section("Alpaca Market Data")
        try:
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockLatestQuoteRequest
            
            alpaca_key = os.getenv("ALPACA_API_KEY", "")
            alpaca_secret = os.getenv("ALPACA_SECRET_KEY", "")
            
            if alpaca_key and alpaca_secret:
                data_client = StockHistoricalDataClient(alpaca_key, alpaca_secret)
                request = StockLatestQuoteRequest(symbol_or_symbols=["SPY"])
                quotes = data_client.get_stock_latest_quote(request)
                
                if "SPY" in quotes:
                    spy_quote = quotes["SPY"]
                    bid = spy_quote.bid_price
                    ask = spy_quote.ask_price
                    result.add_test("Alpaca Market Data", True, f"SPY: ${bid:.2f} - ${ask:.2f}", 8.0)
                    self.print_result("Alpaca Market Data", True, f"SPY: ${bid:.2f} - ${ask:.2f}", 8.0)
                else:
                    result.add_test("Alpaca Market Data", True, "Connected", 5.0)
                    self.print_result("Alpaca Market Data", True, "Connected", 5.0)
        except Exception as e:
            result.add_warning("Alpaca Market Data", str(e)[:50])
            self.print_warning("Alpaca Market Data", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 7: LEARNING SYSTEMS BENCHMARK
    # =========================================================================
    def benchmark_learning_systems(self) -> BenchmarkResult:
        """Test learning and backtesting systems"""
        result = BenchmarkResult("Learning Systems")
        result.start_time = time.time()
        self.print_header("LEVEL 7: LEARNING SYSTEMS BENCHMARK", "█")
        
        # Test 7.1: AI Learning database
        self.print_section("AI Learning Database")
        try:
            if os.path.exists("ai_learning.db"):
                conn = sqlite3.connect("ai_learning.db")
                cursor = conn.cursor()
                
                # Check for learning data
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [t[0] for t in cursor.fetchall()]
                
                result.add_test("Learning Database", True, f"{len(tables)} tables", 5.0)
                self.print_result("Learning Database", True, f"{len(tables)} tables", 5.0)
                
                # Check for learned models
                for table in tables[:5]:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            result.add_test(f"Table: {table}", True, f"{count} records", 2.0)
                            self.print_result(f"Table: {table}", True, f"{count} records", 2.0)
                    except:
                        pass
                
                conn.close()
            else:
                result.add_warning("Learning Database", "Not found")
                self.print_warning("Learning Database", "Not found")
        except Exception as e:
            result.add_warning("Learning Database", str(e)[:50])
            self.print_warning("Learning Database", str(e)[:50])
        
        # Test 7.2: Backtest results
        self.print_section("Backtest History")
        try:
            backtest_files = list(Path(".").glob("*backtest*.json"))
            for bf in backtest_files[:5]:
                try:
                    size = bf.stat().st_size
                    result.add_test(f"Backtest: {bf.name[:40]}", True, f"{size:,} bytes", 2.0)
                    self.print_result(f"Backtest: {bf.name[:40]}", True, f"{size:,} bytes", 2.0)
                except:
                    pass
        except Exception as e:
            result.add_warning("Backtest History", str(e)[:50])
            self.print_warning("Backtest History", str(e)[:50])
        
        # Test 7.3: Pre-trained models
        self.print_section("Pre-trained Models")
        try:
            model_dirs = ["models", "ai_models", "trained_models", "pre_trained"]
            for model_dir in model_dirs:
                if os.path.exists(model_dir):
                    model_files = list(Path(model_dir).rglob("*"))
                    if model_files:
                        result.add_test(f"Models: {model_dir}", True, f"{len(model_files)} files", 5.0)
                        self.print_result(f"Models: {model_dir}", True, f"{len(model_files)} files", 5.0)
        except Exception as e:
            result.add_warning("Pre-trained Models", str(e)[:50])
            self.print_warning("Pre-trained Models", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # LEVEL 8: PERFORMANCE BENCHMARK
    # =========================================================================
    def benchmark_performance(self) -> BenchmarkResult:
        """Test system performance"""
        result = BenchmarkResult("Performance")
        result.start_time = time.time()
        self.print_header("LEVEL 8: PERFORMANCE BENCHMARK", "█")
        
        # Test 8.1: System resources
        self.print_section("System Resources")
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # CPU
            cpu_ok = cpu_percent < 90
            result.add_test("CPU Usage", cpu_ok, f"{cpu_percent:.1f}%", 5.0 if cpu_ok else 2.0)
            self.print_result("CPU Usage", cpu_ok, f"{cpu_percent:.1f}%", 5.0 if cpu_ok else 2.0)
            
            # Memory
            mem_ok = memory.percent < 90
            result.add_test("Memory Usage", mem_ok, f"{memory.percent:.1f}% ({memory.available/1024/1024/1024:.1f} GB free)", 5.0 if mem_ok else 2.0)
            self.print_result("Memory Usage", mem_ok, f"{memory.percent:.1f}%", 5.0 if mem_ok else 2.0)
            
            # Disk
            disk_ok = disk.percent < 95
            result.add_test("Disk Usage", disk_ok, f"{disk.percent:.1f}% ({disk.free/1024/1024/1024:.1f} GB free)", 5.0 if disk_ok else 2.0)
            self.print_result("Disk Usage", disk_ok, f"{disk.percent:.1f}%", 5.0 if disk_ok else 2.0)
            
        except Exception as e:
            result.add_warning("System Resources", str(e)[:50])
            self.print_warning("System Resources", str(e)[:50])
        
        # Test 8.2: Database query speed
        self.print_section("Database Performance")
        try:
            if os.path.exists("trading_system.db"):
                conn = sqlite3.connect("trading_system.db")
                cursor = conn.cursor()
                
                start = time.time()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                query_time = time.time() - start
                
                result.add_test("DB Query Speed", True, f"{query_time*1000:.2f}ms", 5.0)
                self.print_result("DB Query Speed", True, f"{query_time*1000:.2f}ms", 5.0)
                
                conn.close()
        except Exception as e:
            result.add_warning("Database Performance", str(e)[:50])
            self.print_warning("Database Performance", str(e)[:50])
        
        # Test 8.3: API response times
        self.print_section("API Response Times")
        try:
            import requests
            
            endpoints = [
                ("Ollama", "http://localhost:11434/api/tags"),
            ]
            
            for name, url in endpoints:
                try:
                    start = time.time()
                    response = requests.get(url, timeout=5)
                    response_time = time.time() - start
                    
                    if response.status_code == 200:
                        result.add_test(f"{name} Response", True, f"{response_time*1000:.0f}ms", 5.0)
                        self.print_result(f"{name} Response", True, f"{response_time*1000:.0f}ms", 5.0)
                    else:
                        result.add_warning(f"{name} Response", f"HTTP {response.status_code}")
                        self.print_warning(f"{name} Response", f"HTTP {response.status_code}")
                except Exception as e:
                    result.add_warning(f"{name} Response", str(e)[:40])
                    self.print_warning(f"{name} Response", str(e)[:40])
        except Exception as e:
            result.add_warning("API Response Times", str(e)[:50])
            self.print_warning("API Response Times", str(e)[:50])
        
        result.end_time = time.time()
        return result

    # =========================================================================
    # RUN ALL BENCHMARKS
    # =========================================================================
    def run_all_benchmarks(self):
        """Run all benchmark levels"""
        self.print_header("🔥 PROMETHEUS MASTER BENCHMARK SUITE 🔥", "█")
        print(f"  Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Testing ALL systems after ALL enhancements")
        print("█" * 100)
        
        # Run all benchmark levels
        benchmarks = [
            ("Level 1", self.benchmark_core_systems),
            ("Level 2", self.benchmark_ai_intelligence),
            ("Level 3", self.benchmark_knowledge_base),
            ("Level 4", self.benchmark_trading_engine),
            ("Level 5", self.benchmark_broker_connectivity),
            ("Level 6", self.benchmark_data_sources),
            ("Level 7", self.benchmark_learning_systems),
            ("Level 8", self.benchmark_performance),
        ]
        
        for level_name, benchmark_func in benchmarks:
            try:
                result = benchmark_func()
                self.results[level_name] = result
            except Exception as e:
                print(f"\n❌ ERROR in {level_name}: {str(e)[:100]}")
                traceback.print_exc()
        
        # Generate final report
        self.generate_final_report()
        
    def generate_final_report(self):
        """Generate comprehensive final report"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        self.print_header("📊 PROMETHEUS BENCHMARK FINAL REPORT", "█")
        
        print(f"\n  ⏱️  Total Duration: {duration:.1f} seconds")
        print(f"  📅 Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Summary table
        print("-" * 100)
        print(f"  {'LEVEL':<25} {'PASSED':<10} {'FAILED':<10} {'WARNINGS':<10} {'SCORE':<15} {'TIME':<10}")
        print("-" * 100)
        
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        total_score = 0.0
        
        for level_name, result in self.results.items():
            level_time = (result.end_time - result.start_time) if result.end_time and result.start_time else 0
            print(f"  {level_name:<25} {result.passed:<10} {result.failed:<10} {result.warnings:<10} {result.score:<15.1f} {level_time:<10.2f}s")
            total_passed += result.passed
            total_failed += result.failed
            total_warnings += result.warnings
            total_score += result.score
        
        print("-" * 100)
        print(f"  {'TOTAL':<25} {total_passed:<10} {total_failed:<10} {total_warnings:<10} {total_score:<15.1f}")
        print("-" * 100)
        
        # Calculate overall grade
        max_possible_score = 250.0  # Approximate max
        percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
        
        if percentage >= 90:
            grade = "A+"
            status = "🏆 EXCEPTIONAL"
        elif percentage >= 80:
            grade = "A"
            status = "✨ EXCELLENT"
        elif percentage >= 70:
            grade = "B+"
            status = "🌟 VERY GOOD"
        elif percentage >= 60:
            grade = "B"
            status = "👍 GOOD"
        elif percentage >= 50:
            grade = "C"
            status = "⚠️ NEEDS IMPROVEMENT"
        else:
            grade = "D"
            status = "❌ CRITICAL ISSUES"
        
        print()
        self.print_header(f"OVERALL SCORE: {total_score:.1f} / {max_possible_score:.0f} ({percentage:.1f}%)", "█")
        print(f"\n  📊 GRADE: {grade}")
        print(f"  🎯 STATUS: {status}")
        print()
        
        # Key highlights
        print("  📌 KEY HIGHLIGHTS:")
        print(f"     • Tests Passed: {total_passed}")
        print(f"     • Tests Failed: {total_failed}")
        print(f"     • Warnings: {total_warnings}")
        print(f"     • Success Rate: {(total_passed/(total_passed+total_failed)*100) if (total_passed+total_failed) > 0 else 0:.1f}%")
        print()
        
        # Save results to file
        report_file = f"PROMETHEUS_BENCHMARK_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_data = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_score": total_score,
            "max_score": max_possible_score,
            "percentage": percentage,
            "grade": grade,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_warnings": total_warnings,
            "levels": {}
        }
        
        for level_name, result in self.results.items():
            report_data["levels"][level_name] = {
                "passed": result.passed,
                "failed": result.failed,
                "warnings": result.warnings,
                "score": result.score,
                "tests": result.tests
            }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"  📄 Full report saved to: {report_file}")
        print()
        print("█" * 100)
        print("  🔥 PROMETHEUS MASTER BENCHMARK COMPLETE 🔥")
        print("█" * 100)


if __name__ == "__main__":
    benchmark = PrometheusMasterBenchmark()
    benchmark.run_all_benchmarks()
