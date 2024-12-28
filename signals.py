from keys import api, secret
from pybit.unified_trading import HTTP
import pandas as pd
import asyncio
import ta
from time import sleep
from main import send_signal_to_telegram

session = HTTP(
    api_key=api,
    api_secret=secret,
    # testnet=True
    )

timeframe = 1  # minutes

def get_balance():
    try:
        resp = session.get_wallet_balance(accountType="UNIFIED", coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
        resp = float(resp)
        return resp
    except Exception as err:
        print(err)

def klines(symbol):
    try:
        resp = session.get_kline(
            category='linear',
            symbol=symbol,
            interval=timeframe,
            limit=200
        )['result']['list']
        resp = pd.DataFrame(resp)
        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
        resp = resp.set_index('Time')
        resp = resp.astype(float)
        resp = resp[::-1]
        return resp
    except Exception as err:
        print(err)


def signals(symbol):
    try:
        # Получаем данные о свечах
        kl = klines(symbol)
        
        # Рассчитываем RSI (14 периодов)
        kl['RSI'] = ta.momentum.rsi(kl['Close'], window=14)

        # Рассчитываем Bollinger Bands (20 периодов, отклонение 2)
        bollinger = ta.volatility.BollingerBands(kl['Close'], window=20, window_dev=2)
        kl['bollinger_upper'] = bollinger.bollinger_hband()
        kl['bollinger_lower'] = bollinger.bollinger_lband()

        # Последние 2 значения RSI
        rsi_values = kl['RSI'].iloc[-2:]
        rsi_up = all(rsi > 70 for rsi in rsi_values)
        rsi_down = all(rsi < 30 for rsi in rsi_values)          
        # Проверка выхода за полосу Боллинджера
        current_price = kl['Close'].iloc[-1]
        upper_band = kl['bollinger_upper'].iloc[-1]
        lower_band = kl['bollinger_lower'].iloc[-1]

        signal = 'none'

        # Если оба RSI выше 50 и цена выходит за верхнюю полосу Боллинджера
        if rsi_down and current_price < lower_band:
            signal = 'BUY'
        
        # Если оба RSI ниже 30 и цена выходит за нижнюю полосу Боллинджера
        elif rsi_up and current_price > upper_band:
            signal = 'SELL'

        return signal

    except Exception as e:
        print(f"Ошибка расчёта индикаторов: {e}")
        return 'none'




# def signals(symbol):
#     try:
#         # Получаем данные о свечах
#         kl = klines(symbol)
        
#         # Индикаторы
#         macd = ta.trend.MACD(kl['Close']).macd()  # MACD
#         signal_line = ta.trend.MACD(kl['Close']).macd_signal()  # Сигнальная линия MACD
        
#         if macd.iloc[-3] < signal_line.iloc[-3] and macd.iloc[-2] > signal_line.iloc[-2] and macd.iloc[-1] > signal_line.iloc[-1]:
#             return 'UP'
        
#         elif macd.iloc[-3] > signal_line.iloc[-3] and macd.iloc[-2] < signal_line.iloc[-2] and macd.iloc[-1] < signal_line.iloc[-1]:
#             return 'DOWN'
        
#         return 'none'  # Нет сигнала
        
#     except Exception as e:
#         print(f"Ошибка расчёта MACD или SuperTrend: {e}")
#         return 'none'





symbols = [
    'BTCUSDT', 'ETHUSDT', 'XRPUSDT', '1000PEPEUSDT', 'WIFUSDT', 'PNUTUSDT',
    'BCHUSDT', 'ADAUSDT', 'DOGEUSDT', 'DOTUSDT',

    'SUIUSDT', 'GMTUSDT', 'PHAUSDT', 'UXLINKUSDT', 'ATAUSDT', 'LINKUSDT', 'VIRTUALUSDT', 'STEEMUSDT', 'HYPEUSDT'
]

# Infinite loop
while True: 
    balance = get_balance()
    if balance == None:
        print('Cant connect to API')
    if balance != None:
        balance = float(balance)
        print(f'\033[32mБаланс: {balance}\033[0m')

        for elem in symbols:
            signal = signals(elem)
            if signal == 'BUY':
                print(f'Найден BUY сигнал для {elem}')
                asyncio.run(send_signal_to_telegram(signal, elem))
            if signal == 'SELL':
                print(f'Найден SELL сигнал для {elem}')
                asyncio.run(send_signal_to_telegram(signal, elem))
    print('Ждем...')
    sleep(timeframe*20)
         