import pandas as pd
import numpy as np
import talib
import json
from angelbroking import AngelBroking

config=json.loads("config.json")
# Connect to Angel API
api_key = config['api_key']
client_code = config['client_code']
password = config['password']
angel = AngelBroking(api_key=api_key, client_code=client_code, password=password)
login = angel.generate_session()

# Fetch historical data
symbol = 'SBIN' # Replace with the symbol you want to trade
interval = '1' # Replace with the interval you want to fetch (in minutes)
start_time = '2021-01-01 00:00:00' # Replace with the start time of the historical data
end_time = '2021-12-31 23:59:00' # Replace with the end time of the historical data
historical_data = angel.get_candle_data(symbol=symbol, interval=interval, start_time=start_time, end_time=end_time)['data'][symbol]

# Compute MACD and Signal Line
macd, signal, _ = talib.MACD(historical_data['close'], fastperiod=12, slowperiod=26, signalperiod=9)

# Generate Trading Signals
trading_signals = pd.DataFrame({'close': historical_data['close'], 'macd': macd, 'signal': signal})
trading_signals['positions'] = np.where(trading_signals['macd'] > trading_signals['signal'], 1, 0)
trading_signals['positions'] = np.where(trading_signals['macd'] < trading_signals['signal'], -1, trading_signals['positions'])
trading_signals['positions'] = trading_signals['positions'].fillna(0).diff()

# Place Orders
for i in range(len(trading_signals)):
    if trading_signals['positions'][i] == 1:
        angel.place_order(transaction_type='buy', variety='regular', symbol=symbol, quantity=1, order_type='market', product='MIS', duration='DAY')
    elif trading_signals['positions'][i] == -1:
        angel.place_order(transaction_type='sell', variety='regular', symbol=symbol, quantity=1, order_type='market', product='MIS', duration='DAY')
        
# Fetch Current Positions
current_positions = angel.get_positions()['data']

# Print Results
print(current_positions)
