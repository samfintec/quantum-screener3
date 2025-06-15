
# Streamlit Trading Dashboard for Sateesh C Rathna

import streamlit as st
import pandas as pd
import yfinance as yf
import ccxt
import ta
from datetime import datetime

st.set_page_config(page_title="Live Screener Dashboard", layout="wide")

# ----- Functions -----
def fetch_yfinance_data(symbol, interval="5m", lookback="1d"):
    data = yf.download(tickers=symbol, period=lookback, interval=interval)
    return data.reset_index()

def fetch_crypto_data(symbol="BTC/USDT", timeframe="5m", limit=100):
    exchange = ccxt.binance()
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(bars, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
    return df

def analyze(df):
    required_columns = {'close', 'volume', 'high', 'low'}
    if df.empty or not required_columns.issubset(df.columns) or len(df) < 30:
        return None

    df['EMA7'] = ta.trend.ema_indicator(df['close'], window=7).ema_indicator()
    df['EMA13'] = ta.trend.ema_indicator(df['close'], window=13).ema_indicator()
    df['EMA21'] = ta.trend.ema_indicator(df['close'], window=21).ema_indicator()
    df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    df['RSI'] = ta.momentum.rsi(df['close'], window=14)
    df['VolumeMA20'] = df['volume'].rolling(window=20).mean()

    latest = df.iloc[-1]
    result = {
        'Price': round(latest['close'], 2),
        'RSI': round(latest['RSI'], 2),
        'Price > VWAP': latest['close'] > latest['VWAP'],
        'EMA Bullish': latest['EMA7'] > latest['EMA13'] > latest['EMA21'],
        'Volume Spike': latest['volume'] > 2 * latest['VolumeMA20']
    }
    return result

# ----- Dashboard -----
st.title("📊 Live Trading Screener - Sateesh C Rathna")

tab1, tab2 = st.tabs(["📈 NSE Stocks", "💰 Crypto"])

with tab1:
    st.subheader("NSE Stocks (via yFinance)")
    symbols = ["RELIANCE.NS", "TATASTEEL.NS", "INFY.NS"]
    interval = st.selectbox("Select Timeframe", ["5m", "15m"], key="nse_interval")
    nse_results = []

    for sym in symbols:
        df = fetch_yfinance_data(sym, interval)
        result = analyze(df)
        if result:
            nse_results.append({"Symbol": sym, **result})

    if nse_results:
        st.dataframe(pd.DataFrame(nse_results))
    else:
        st.info("No bullish setups found in NSE stocks.")

with tab2:
    st.subheader("Crypto Pairs (via Binance ccxt)")
    crypto_symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    crypto_interval = st.selectbox("Select Timeframe", ["5m", "15m"], key="crypto_interval")
    crypto_results = []

    for csym in crypto_symbols:
        df = fetch_crypto_data(csym, crypto_interval)
        result = analyze(df)
        if result:
            crypto_results.append({"Symbol": csym, **result})

    if crypto_results:
        st.dataframe(pd.DataFrame(crypto_results))
    else:
        st.info("No bullish setups found in crypto pairs.")
