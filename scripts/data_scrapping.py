import pandas as pd
import datetime
import yfinance as yf

def get_historical_data(ticker_symbol, start_date, end_date):
    """
    Fetches historical data for a ticker symbol between two dates.
    """
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data


def simulate_investment_first_of_the_month(data, initial_investment):
    """
    Simulates the investment strategy: buying stocks on the first trading day of each month.
    """
    portfolio_value = []
    invested_cash = []
    cash = initial_investment
    last_month = None

    for index, row in data.iterrows():
        current_month = row['Date'].month
        if current_month != last_month and row['Date'].weekday() < 5:
            stocks_bought = cash / row['Close']
            portfolio_value.append(stocks_bought)
            invested_cash.append(cash)
        else:
            portfolio_value.append(0)
            invested_cash.append(0)

        last_month = current_month

    data['Current amount spent'] = invested_cash
    data['Amount of stock bought'] = portfolio_value
    data['Amount of stock'] = data['Amount of stock bought'].cumsum()
    data['Portfolio value'] = data['Close'] * data['Amount of stock']
    data['Money spent'] = data['Current amount spent'].cumsum()

    return data


def simulate_for_all_periods(ticker_symbol, initial_investment, years=10, total_years=100):
    """
    Simulates the investment strategy for all 10-year spans in the last 100 years,
    starting from each month, and returns a DataFrame with first and last investment dates and the return.
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365 * total_years)

    # Fetch historical data
    data = get_historical_data(ticker_symbol, start_date, end_date)

    results = []
    current_date = start_date

    while current_date + datetime.timedelta(days=365 * years) <= end_date:
        # Define the 10-year span
        span_start_date = current_date
        span_end_date = current_date + datetime.timedelta(days=365 * years)

        span_data = data[(data['Date'] >= span_start_date) & (data['Date'] < span_end_date)].copy()

        # Skip periods with incomplete data
        if len(span_data) == 0:
            current_date += datetime.timedelta(days=30)  # Move to the next month
            continue

        # Simulate the strategy
        simulated_data = simulate_investment_first_of_the_month(span_data, initial_investment)

        # Calculate final portfolio value and returns
        first_investment_date = simulated_data['Date'].iloc[0]
        last_investment_date = simulated_data['Date'].iloc[-1]
        final_portfolio_value = simulated_data['Portfolio value'].iloc[-1]
        total_money_spent = simulated_data['Money spent'].iloc[-1]
        return_percentage = (final_portfolio_value - total_money_spent) / total_money_spent * 100

        # Store results as a dictionary
        results.append({
            "First Investment Day": first_investment_date,
            "Last Investment Day": last_investment_date,
            "Return (%)": return_percentage
        })

        # Move to the next month
        current_date += datetime.timedelta(days=30)

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)
    return results_df


def simulate_3x_leveraged(data):
    """
    Simulates the behavior of a 3x leveraged ETF based on the daily returns of the S&P 500.
    """
    data['Daily Return'] = data['Close'].pct_change()  # Calculate daily returns
    data['Leveraged Return'] = data['Daily Return'] * 3  # Apply 3x leverage
    data['Leveraged Close'] = (1 + data['Leveraged Return']).cumprod() * data['Close'].iloc[0]  # Reconstruct prices
    return data


def simulate_investment_first_of_the_month_leveraged(data, initial_investment):
    """
    Simulates the investment strategy for a leveraged ETF.
    """
    portfolio_value = []
    invested_cash = []
    cash = initial_investment
    last_month = None

    for index, row in data.iterrows():
        current_month = row['Date'].month
        if current_month != last_month and row['Date'].weekday() < 5:
            stocks_bought = cash / row['Leveraged Close']
            portfolio_value.append(stocks_bought)
            invested_cash.append(cash)
        else:
            portfolio_value.append(0)
            invested_cash.append(0)

        last_month = current_month

    data['Current amount spent'] = invested_cash
    data['Amount of stock bought'] = portfolio_value
    data['Amount of stock'] = data['Amount of stock bought'].cumsum()
    data['Portfolio value'] = data['Leveraged Close'] * data['Amount of stock']
    data['Money spent'] = data['Current amount spent'].cumsum()

    return data


def simulate_for_all_periods_leveraged(ticker_symbol, initial_investment, years=10, total_years=100):
    """
    Simulates the investment strategy for all periods using a 3x leveraged ETF.
    """
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365 * total_years)

    # Fetch historical data
    data = get_historical_data(ticker_symbol, start_date, end_date)

    # Simulate 3x leveraged ETF
    data = simulate_3x_leveraged(data)

    results = []
    current_date = start_date

    while current_date + datetime.timedelta(days=365 * years) <= end_date:
        # Define the 10-year span
        span_start_date = current_date
        span_end_date = current_date + datetime.timedelta(days=365 * years)

        span_data = data[(data['Date'] >= span_start_date) & (data['Date'] < span_end_date)].copy()

        # Skip periods with incomplete data
        if len(span_data) == 0:
            current_date += datetime.timedelta(days=30)  # Move to the next month
            continue

        # Simulate the strategy
        simulated_data = simulate_investment_first_of_the_month_leveraged(span_data, initial_investment)

        # Calculate final portfolio value and returns
        first_investment_date = simulated_data['Date'].iloc[0]
        last_investment_date = simulated_data['Date'].iloc[-1]
        final_portfolio_value = simulated_data['Portfolio value'].iloc[-1]
        total_money_spent = simulated_data['Money spent'].iloc[-1]
        return_percentage = (final_portfolio_value - total_money_spent) / total_money_spent * 100

        # Store results as a dictionary
        results.append({
            "First Investment Day": first_investment_date,
            "Last Investment Day": last_investment_date,
            "Return (%)": return_percentage
        })

        # Move to the next month
        current_date += datetime.timedelta(days=30)

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)
    return results_df



if __name__ == "__main__":
    ticker_symbol = "^GSPC"  # S&P 500
    initial_investment = 200  # Invest $200 on the first trading day of each month
    years = 30  # Simulation for 20 years
    total_years = 95  # Total span of data to analyze

    # Run the simulation for the leveraged ETF
    results_df = simulate_for_all_periods_leveraged(ticker_symbol, initial_investment, years, total_years)
    results_df.to_csv(f"data/{years}_year_investment_simulation_3x.csv", index=False)





