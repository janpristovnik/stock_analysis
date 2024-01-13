import pandas as pd
import datetime
import yfinance as yf



def get_data_by_ticker_and_years(ticker_symbol="^GSPC", years= 10):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=365 * years)  # 10 years ago

    # Fetch historical data from Yahoo Finance
    data = yf.download(ticker_symbol, start=start_date, end=end_date)
    # Reset the index to move the time to a column
    data.reset_index(inplace=True)
    return data

def simulate_investment(data, initial_investment):
    portfolio_value = []
    invested_cash = []
    cash = initial_investment

    last_month = None  # Keep track of the last processed month

    for index, row in data.iterrows():
        current_month = row['Date'].month

        # Check if it's the first day of a new month and it's a weekday (Monday to Friday)
        if current_month != last_month and row['Date'].weekday() < 5:
            # Calculate the amount of stocks that can be bought with available cash
            stocks_bought = cash / row['Close']
            # Update cash after buying stocks
            # Calculate portfolio value at this point in time
            amount_of_stock_bought = stocks_bought
            portfolio_value.append(amount_of_stock_bought)
            invested_cash.append(cash)
        else:
            # If it's not the first day of a new month or it's a weekend, just append 0 to both lists
            portfolio_value.append(0)
            invested_cash.append(0)

        last_month = current_month  # Update last processed month

    return portfolio_value, invested_cash


if __name__ == "__main__":
    ticker_symbol = "^GSPC"
    years = 20
    initial_investment = 50  # Adjust this to your initial investment amount
    investment_days = [1]  # Invest on the 1st day of each month

    data = get_data_by_ticker_and_years(ticker_symbol, years)
    portfolio_value, invested_cash = simulate_investment(data, initial_investment)

    # Add the portfolio value to the DataFrame
    data['Current amount spent'] = invested_cash
    data['Amount of stock bought'] = portfolio_value
    data['Amount of stock'] = data['Amount of stock bought'].cumsum()
    data['Portfolio value'] = data['Close']*data['Amount of stock']
    data['Money spent'] = data['Current amount spent'].cumsum()
    print(data[['Date', 'Close', 'Amount of stock bought', 'Amount of stock', 'Portfolio value', 'Money spent', 'Current amount spent']])
    print()


