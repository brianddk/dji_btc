# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    https://github.com/brianddk/dji_btc
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  https://gist.github.com/brianddk/3ec16fbf1d008ea290b0
# [ref]     https://finance.yahoo.com/quote/%5EDJI/history?p=^DJI
# [post]    https://redd.it/ffyta8/
# [usage]   python3 dji_btc.py > dji_btc.csv

# The following URL needs to be downloaded by a browser
root  = 'https://query1.finance.yahoo.com/v7/finance/download/^DJI'
param = '?period1=475804800&period2=1583798400&interval=1d&events=history'
crumb = '' # session guid generated on yahoo finance site
url   = f'{root}{param}&crumb={crumb}'

from json import dumps
from datetime import datetime as dt
from requests import get
from requests.auth import AuthBase
from time import sleep
from sys import exit

class CoinbaseExchangePublic(AuthBase):
    def __call__(self, request):
        request.headers.update({
            'Content-Type': 'application/json'
        })
        sleep(1.1/3)
        return request

dji_history = {}
with open('daily_dji.csv') as f:
    history = f.readlines()

for d in history:
    if 'Date' in d or 'null' in d: continue
    day = d.strip().split(',')
    y, m, d = day[0].split('-')
    if not y in dji_history.keys(): dji_history[y] = {}
    if not m in dji_history[y].keys(): dji_history[y][m] = {}    
    dji_history[y][m][d] = day

url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangePublic()
day=86400
params = dict(granularity = day)
print(f'Date, Mid, High, Low')
while True:
    r = get(url + 'products/BTC-GBP/candles', auth=auth, params=params)
    candles = r.json()
    if not len(candles):
        break
    for candle in candles:
        btc_ts, btc_low, btc_high, _, _, _ = candle
        ts = dt.utcfromtimestamp(btc_ts)
        d = f'{ts.day:02}'
        m = f'{ts.month:02}'
        y = f'{ts.year}'
        if d in dji_history[y][m].keys():
            dji_date, _, dji_high, dji_low, _, _, _ = dji_history[y][m][d]
            high = float(dji_high) / float(btc_low)
            low  = float(dji_low) / float(btc_high)
            mid = (high + low)/2
            print(f'{dji_date}, {mid}, {high}, {low}')
        
    start = candles[-1][0]
    params['end']   = dt.utcfromtimestamp(start - day).isoformat()
    params['start'] = dt.utcfromtimestamp(start - day * len(candles)).isoformat()
