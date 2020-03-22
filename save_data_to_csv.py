from alpha_vantage.timeseries import TimeSeries
from pprint import pprint
import json
import argparse
import pandas as pd

def save_dataset(symbol, time_window):
    credentials = json.load(open('creds.json', 'r'))
    api_key = credentials['av_api_key']
    print(symbol, time_window)
    ts = TimeSeries(key=api_key, output_format='pandas')
    if time_window == 'intraday':
        data, meta_data = ts.get_intraday(
            symbol='MSFT', interval='1min', outputsize='full')
    elif time_window == 'daily':
        data, meta_data = ts.get_daily(symbol, outputsize='full')
    elif time_window == 'daily_adj':
        data, meta_data = ts.get_daily_adjusted(symbol, outputsize='full')

    pprint(data.head(10))

    csv_path = f'./{symbol}_{time_window}.csv'
    data.to_csv(csv_path)
    csv_to_dataset(csv_path)

def csv_to_dataset(csv_path):
    data = pd.read_csv(csv_path)
    data = data.drop('date', axis=1)
    # data = data.drop(0, axis=0)
    print(data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('symbol', type=str, help="the stock symbol you want to download")
    parser.add_argument('time_window', type=str, choices=[
                        'intraday', 'daily', 'daily_adj'], help="the time period you want to download the stock history for")

    namespace = parser.parse_args()
    save_dataset(**vars(namespace))
