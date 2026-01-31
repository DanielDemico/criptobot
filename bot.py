
import time
import requests
import pprint

import calcules

symbol = "BTC-BRL"
countback = 400 
resolution = "15m"
current_timestamp=int(time.time())


candles_url = f"https://api.mercadobitcoin.net/api/v4/candles?symbol={symbol}&resolution={resolution}&to={current_timestamp}&countback={countback}"
dados = requests.get(candles_url)
candles = dados.json()

fechamentos = [float(i) for i in candles['c']]

actual_price = fechamentos[-1]


ema_curta = calcules.EMA_CALCULATOR(fechamentos, 9)
ema_longa = calcules.EMA_CALCULATOR(fechamentos, 21)
ema_200 = calcules.EMA_CALCULATOR(fechamentos, 200)[-1]

golden_crusades, death_crusades = calcules.SIGNALS(ema_curta, ema_longa)

sinal_compra = golden_crusades[-1]

sinal_venda = death_crusades[-1]

actual_state = None
if sinal_compra:
    if actual_price > ema_200:
        print("Compra efetuada")
        actual_price = "HOLDING"
    else:
        print(">>> SINAL DE COMPRA IGNORADO (Contra a Tendência/Abaixo da EMA200)")
elif sinal_venda and actual_state != "SOLD":
    print("Venda")
    actual_state="SOLD"


calcules.SHOW(fechamentos, ema_curta, ema_longa, golden_crusades, death_crusades)



