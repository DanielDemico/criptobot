
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
rsi = calcules.RSI_CALCULATOR(fechamentos, 14 )

golden_crusades, death_crusades = calcules.SIGNALS(ema_curta, ema_longa)

sinal_compra = golden_crusades[-1]
sinal_venda = death_crusades[-1]
rsi_atual = rsi[-1]

actual_state = None

if sinal_venda and actual_state != "SOLD":
    print("Venda")

elif sinal_compra:
    if actual_price < ema_200:
        print("Não Compra, tendencia baixa EMA 200")
    elif rsi_atual > 70:
        print(f"IGNORADO: RSI muito alto ({rsi_atual:.0f}). Risco de topo.")
    else:
        print("COMPRA")



calcules.SHOW(fechamentos, ema_curta, ema_longa, golden_crusades, death_crusades)



