
import time
import requests
import pprint

import calcules

symbol = "BTC-BRL"
countback = 4000
resolution = "15m"
current_timestamp=int(time.time())

ganho_min = 0.02
stop_loss = 0.10

candles_url = f"https://api.mercadobitcoin.net/api/v4/candles?symbol={symbol}&resolution={resolution}&to={current_timestamp}&countback={countback}"
dados = requests.get(candles_url)
candles = dados.json()

fechamentos = [float(i) for i in candles['c']]

altos = [float(i) for i in candles['h']]

baixos = [float(i) for i in candles['l']]



ema_curta = calcules.EMA_CALCULATOR(fechamentos, 9)
ema_longa = calcules.EMA_CALCULATOR(fechamentos, 21)
ema_200 = calcules.EMA_CALCULATOR(fechamentos, 200)
rsi = calcules.RSI_CALCULATOR(fechamentos, 14)
adx_indicator = calcules.ADX_CALCULATOR(baixos, altos, fechamentos, 14)

golden_crusades, death_crusades = calcules.SIGNALS(ema_curta, ema_longa)


compras = [False] * countback
vendas = [False] * countback

id_compra, id_venda = [],[]
actual_state = None


for i in range(len(fechamentos)):
    sinal_compra = golden_crusades[i]
    sinal_venda = death_crusades[i]
    rsi_atual = rsi[i]
    actual_price = fechamentos[i]
    adx_atual = adx_indicator[i]
    distancia_media = (actual_price / ema_curta[-i]) - 1

    if actual_state == "HOLD":
        print("Percentual de ganho: ", (fechamentos[i] / fechamentos[id_compra[-1]] - 1))
        if (fechamentos[i] / fechamentos[id_compra[-1]]) - 1 <= -stop_loss:
            actual_state = "SOLD"
            vendas[i] = True
            id_venda.append(i)
            print(f"STOP LOSS ATINGIDO: Saída a {fechamentos[i]} (Perda de {(fechamentos[i] / fechamentos[id_compra[-1]] - 1)*100:.2f}%)")

        elif (fechamentos[i] / fechamentos[id_compra[-1]] - 1) >= ganho_min:
                actual_state = "SOLD"
                vendas[i] = True
                id_venda.append(i)
                print(f"VENDA EXECUTADA: {'Morte' if sinal_venda else 'Quebra de Tendência (EMA 200)'}")


    elif sinal_compra:
        
        if adx_atual < 25:
            print(f"STATUS: Lateralizado (ADX: {adx_atual:.2f}). Operação bloqueada.")
        elif actual_price < ema_200[i]:
            print("Não Compra, tendencia baixa EMA 200")
        elif rsi_atual > 80:
            print(f"IGNORADO: RSI muito alto ({rsi_atual:.0f}). Risco de topo.")
        elif distancia_media > 0.015:
            print(f"IGNORADO: Preço muito esticado ({distancia_media*100:.2f}% acima da EMA9).")
        else:
            if actual_state != "HOLD":
                actual_state = "HOLD"
                compras[i] = True 
                id_compra.append(i)
                print(rsi_atual)

soma = 0 
for i in range(len(id_venda)):
    print("-------------------------------")
    soma += fechamentos[id_venda[i]] - fechamentos[id_compra[i]]
    print(f"{fechamentos[id_venda[i]]} - {fechamentos[id_compra[i]]} : {fechamentos[id_venda[i]] - fechamentos[id_compra[i]]}")

print(soma)
calcules.SHOW(fechamentos, ema_curta, ema_longa, golden_crusades, death_crusades, compras, vendas)

