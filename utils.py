from binance.client import Client
import numpy as np
import finlab_crypto
from finlab_crypto import Strategy
import pandas as pd
from binance import Client
import requests

def place_order(pair, side, quantity, stop_loss_percent, take_profit_percent):
    api_key = 'IMe4eYde4ivFkH98FeDgAppDEqufxAVsqiciR3AQyucvpl01Obcm7uIlFhDDd19p'
    api_secret = '770u8vCFNlNzkn4TqIQDACed8J9uzyxBnuam1RHj8u9tB34lGU7roVI4Hi7gCjaG'
    client = Client(api_key, api_secret, testnet=True)  # 設定 testnet=False 以使用實際的帳戶
    
    symbol = pair.upper()
    price = client.futures_symbol_ticker(symbol=symbol)['price']
    price = float(price)

    if side == 'BUY':
        stop_loss_price = price * (1 - stop_loss_percent / 100)
        take_profit_price = price * (1 + take_profit_percent / 100)
    elif side == 'SELL':
        stop_loss_price = price * (1 + stop_loss_percent / 100)
        take_profit_price = price * (1 - take_profit_percent / 100)
    else:
        raise ValueError('Invalid side, must be BUY or SELL')

    quantity = np.round(float(quantity/price),2)  # 計算下單量，小數點後 2 位
    order = client.futures_create_order(symbol=symbol, side=side, type='LIMIT', timeInForce='GTC', quantity=quantity, price=price, stopPrice=stop_loss_price, closePosition=False, reduceOnly=False)
    client.futures_create_order(symbol=symbol, side='SELL' if side == 'BUY' else 'BUY', type='TAKE_PROFIT_MARKET', timeInForce='GTC', stopPrice=take_profit_price, closePosition=True, reduceOnly=True)

    return order

def send_to_telegram(message):
    apiToken = '5850662274:AAGeKZqM1JfQfh3CrSKG6BZ9pEvDajdBUqs'
    chatID = '1567262377'
    apiURL = f'https://api.telegram.org/bot{apiToken}/sendMessage'
    try:
        response = requests.post(apiURL, json={'chat_id': chatID, 'text': message})
        print(response.text)
    except Exception as e:
        print(e)

def get_signal(
      pair='BTCUSDT',
      freq='15m',
      n_bar = 10000,
      client = Client(api_key='IMe4eYde4ivFkH98FeDgAppDEqufxAVsqiciR3AQyucvpl01Obcm7uIlFhDDd19p',
                      api_secret='770u8vCFNlNzkn4TqIQDACed8J9uzyxBnuam1RHj8u9tB34lGU7roVI4Hi7gCjaG')
                      ):
  # get the pair ohlcv data
  ohlcv = finlab_crypto.crawler.get_nbars_binance(pair,freq,n_bar,client)
  
  # def base sma_Strategy
  @Strategy(sma1=20, sma2=60)
  def sma_strategy(ohlcv):
    close = ohlcv.close
    # crete sma1 and sma2
    sma1 = close.rolling(sma_strategy.sma1).mean()
    sma2 = close.rolling(sma_strategy.sma2).mean()
    # def entries and exits
    entries = (sma1 > sma2) & (sma1.shift() < sma2.shift())
    exits = (sma1 < sma2) & (sma1.shift() > sma2.shift())
    return entries, exits
  
  # search range
  variables = {
      'sma1': np.arange(5, 100, 5), 
      'sma2': np.arange(10, 200, 5),
      }
  
  # sma_strategy.backtest
  portfolio = sma_strategy.backtest(ohlcv, variables=variables, freq=freq ,plot=False)
  # find portfolio.total_profit().max()
  temp = portfolio.total_profit()[portfolio.total_profit()==portfolio.total_profit().max()].to_frame().reset_index()
  # find portfolio.total_profit().max() use n1 and n2
  n1,n2 = temp['sma1'].values[0],temp['sma2'].values[0]
  
  # create signal table
  table = pd.DataFrame()
  table['close'] = ohlcv.close
  table['n1'] = ohlcv.close.rolling(n1).mean()
  table['n2'] = ohlcv.close.rolling(n2).mean()
  table['buy'] = ((table['n1'] > table['n2']) & (table['n1'].shift() < table['n2'].shift())).astype(int)
  table['sell'] = ((table['n1'] < table['n2']) & (table['n1'].shift() > table['n2'].shift())).astype(int)
  # get last row of the table
  table = table.replace(0,np.nan).tail(1)
  # if buy and sell eqal np.nan pass
  if table[['buy','sell']].sum().sum() == 0:
     signal = 'pass'
  # if buy == 1
  if table[['buy']].values[0][0] == 1:
     signal = 'buy'
  # if sell == 1
  if table[['sell']].values[0][0] == 1:
     signal = 'sell'
  return signal