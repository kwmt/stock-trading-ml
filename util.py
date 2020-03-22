import pandas as pd
from sklearn import preprocessing
import numpy as np

history_points = 50


def csv_to_dataset(csv_path):
    data = pd.read_csv(csv_path)
    data = data.drop('date', axis=1)
    # 最新のデータを消してる？
    # data = data.drop(0, axis=0)

    data = data.values

    # 正規化
    # ネットワークの収束の速さを向上させるために、データを正規化する。（0-1間）
    data_normaliser = preprocessing.MinMaxScaler()
    data_normalised = data_normaliser.fit_transform(data)

    # 最新の過去{history_points}日間のストック履歴に基づいて学習し、次の日の予測を行う
    # ohlcv_histories_normalisedの各値は、50個のopen, high, low, close, volume値を含むnumpy配列
    max_range = len(data_normalised) - history_points
    ohlcv_histories_normalised = np.array([data_normalised[i:i + history_points].copy() 
                                    for i in range(max_range)])
    # next_day_open_values_normalisedの各行は、ohlcv_histories_normalisedの各行の次の日にオープンの正規化された値
    next_day_open_values_normalised = np.array([data_normalised[:, 0][i + history_points].copy() 
                                        for i in range(max_range)])
    next_day_open_values_normalised = np.expand_dims(next_day_open_values_normalised, -1)

    # next_day_open_valuesの各行は、next_day_open_values_normalisedの各行の次の日のオープン価格
    next_day_open_values = np.array([data[:, 0][i + history_points].copy() for i in range(len(data) - history_points)])
    next_day_open_values = np.expand_dims(next_day_open_values, -1)

    # next_day_open_values     
    y_normaliser = preprocessing.MinMaxScaler()
    y_normaliser.fit(next_day_open_values)

    # 単純移動平均
    def calc_ema(values, time_period):
        # https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp
        sma = np.mean(values[:, 3])
        ema_values = [sma]
        k = 2 / (1 + time_period)
        for i in range(len(his) - time_period, len(his)):
            close = his[i][3]
            ema_values.append(close * k + ema_values[-1] * (1 - k))
        return ema_values[-1]

    technical_indicators = []
    for his in ohlcv_histories_normalised:
        # note since we are using his[3] we are taking the SMA of the closing price
        sma = np.mean(his[:, 3])
        macd = calc_ema(his, 12) - calc_ema(his, 26)
        technical_indicators.append(np.array([sma]))
        # technical_indicators.append(np.array([sma,macd,]))

    technical_indicators = np.array(technical_indicators)

    tech_ind_scaler = preprocessing.MinMaxScaler()
    technical_indicators_normalised = tech_ind_scaler.fit_transform(technical_indicators)

    # 形状チェック 
    assert ohlcv_histories_normalised.shape[0] == next_day_open_values_normalised.shape[0] == technical_indicators_normalised.shape[0]
    return ohlcv_histories_normalised, technical_indicators_normalised, next_day_open_values_normalised, next_day_open_values, y_normaliser


# def multiple_csv_to_dataset(test_set_name):
#     import os
#     ohlcv_histories = 0
#     technical_indicators = 0
#     next_day_open_values = 0
#     for csv_file_path in list(filter(lambda x: x.endswith('daily.csv'), os.listdir('./'))):
#         if not csv_file_path == test_set_name:
#             print(csv_file_path)
#             if type(ohlcv_histories) == int:
#                 ohlcv_histories, technical_indicators, next_day_open_values, _, _ = csv_to_dataset(csv_file_path)
#             else:
#                 a, b, c, _, _ = csv_to_dataset(csv_file_path)
#                 ohlcv_histories = np.concatenate((ohlcv_histories, a), 0)
#                 technical_indicators = np.concatenate((technical_indicators, b), 0)
#                 next_day_open_values = np.concatenate((next_day_open_values, c), 0)

#     ohlcv_train = ohlcv_histories
#     tech_ind_train = technical_indicators
#     y_train = next_day_open_values

#     ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser = csv_to_dataset(test_set_name)

#     return ohlcv_train, tech_ind_train, y_train, ohlcv_test, tech_ind_test, y_test, unscaled_y_test, y_normaliser
