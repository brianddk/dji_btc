# [rights]  Copyright 2020 brianddk at github https://github.com/brianddk
# [license] Apache 2.0 License https://www.apache.org/licenses/LICENSE-2.0
# [repo]    https://github.com/brianddk/dji_btc
# [btc]     BTC-b32: bc1qwc2203uym96u0nmq04pcgqfs9ldqz9l3mz8fpj
# [tipjar]  https://gist.github.com/brianddk/3ec16fbf1d008ea290b0
# [ref]     https://finance.yahoo.com/quote/^DJI/history
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
    date = day[0].strip()
    dji_history[date] = day

url = 'https://api.pro.coinbase.com/'
auth = CoinbaseExchangePublic()
day=86400
params = dict(granularity = day)
dji_btc = []
while True:
    r = get(url + 'products/BTC-GBP/candles', auth=auth, params=params)
    candles = r.json()
    if not len(candles):
        break
    start = candles[-1][0]
    params['end']   = dt.utcfromtimestamp(start - day).isoformat()
    params['start'] = dt.utcfromtimestamp(start - day * len(candles)).isoformat()
    for candle in candles:
        btc_ts, btc_low, btc_high = [float(i) for i in candle[0:3]]
        ts = dt.utcfromtimestamp(btc_ts)
        date = f'{ts.year}-{ts.month:02}-{ts.day:02}'
        if date in dji_history.keys():
            dji_high, dji_low = [float(i) for i in dji_history[date][2:4]]
            high = dji_high / btc_low
            low  = dji_low / btc_high
            mid = (dji_high + dji_low)/(btc_high + btc_low)
            dji_btc.append([date, mid, high, low])
        
end = len(dji_btc) - 1
ma = 25 # moving average window (above and below) for std. deviation
max_dev = 2  # reject data more than this man SD's off mean
print(f'Date, Mid, High, Low')
for i in range(0, end+1):
    item = dji_btc[i]
    low, high = [i - ma, i + ma]
    if low < 0: low, high = [0, 2*ma]
    if high > end: low, high = [end-2*ma, end]
    set = [j[1] for j in dji_btc[low:high+1]]
    mean = sum(set) / len(set)
    s2 = sum([(j-mean)**2 for j in set]) * 1/(len(set) - 1)
    std_dev = s2**(1/2)
    cur_dev = abs(item[1] - mean)
    if cur_dev/std_dev < max_dev:
        print(f'{item[0]}, {item[1]}, {item[2]}, {item[3]}')
