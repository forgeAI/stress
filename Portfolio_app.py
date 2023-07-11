import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import datetime
from zipline.api import order_target_percent, set_commission, commission

def initialize(context):
    pass

def handle_data(context, data):
    pass

def run_strategy(stocks, start_date, end_date):
    # Set the commission for the strategy
    set_commission(commission.PerDollar(cost=0.001))

    # Define the start and end dates for the backtest
    start = pd.to_datetime(start_date).tz_localize('UTC')
    end = pd.to_datetime(end_date).tz_localize('UTC')

    # Fetch historical data for the benchmark (S&P 500)
    benchmark = '^GSPC'
    benchmark_data = yf.download(benchmark, start=start_date, end=end_date)['Adj Close']

    # Fetch historical data for the stocks
    stock_data = yf.download(stocks, start=start_date, end=end_date)['Adj Close']

    # Create the trading environment
    from zipline.reloaded.data.bundles import register
    register('custom_bundle', pd.DataFrame(stock_data))
    from zipline.reloaded.data import bundles
    bundle = bundles.load('custom_bundle')
    from zipline.reloaded import TradingAlgorithm

    # Create and run the backtest
    algo = TradingAlgorithm(initialize=initialize, handle_data=handle_data)
    results = algo.run(bundle, start=start, end=end)

    # Get the portfolio and benchmark returns
    portfolio_returns = results.portfolio_value.pct_change().fillna(0)
    benchmark_returns = benchmark_data.pct_change().fillna(0)

    # Calculate cumulative returns
    portfolio_cumulative_returns = (1 + portfolio_returns).cumprod() - 1
    benchmark_cumulative_returns = (1 + benchmark_returns).cumprod() - 1

    return portfolio_cumulative_returns, benchmark_cumulative_returns

def main():
    st.title('GMV Portfolio Backtesting')
    stocks = st.multiselect('Select stocks', ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'FB'], default=['AAPL', 'MSFT'])
    start_date = st.date_input('Select start date', value=datetime(2017, 1, 1))
    end_date = st.date_input('Select end date', value=datetime(2023, 1, 1))

    if st.button('Backtest'):
        portfolio_returns, benchmark_returns = run_strategy(stocks, start_date, end_date)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(portfolio_returns, label='Portfolio Returns')
        ax.plot(benchmark_returns, label='Benchmark Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Returns')
        ax.legend()
        st.pyplot(fig)

        st.write('---')
        st.write('**Backtest Information**')
        st.write(f'Number of stocks: {len(stocks)}')
        st.write(f'Start date: {start_date}')
        st.write(f'End date: {end_date}')


main()
