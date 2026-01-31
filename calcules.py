import pandas as pd
import numpy as np

def EMA_CALCULATOR(fechamentos: list[float], periodo:int) -> float:
    df = pd.DataFrame(fechamentos)
    return df[0].ewm(span=periodo, adjust=False).mean().to_list()


def SIGNALS(ema_curta, ema_longa):
    cruzou = False
    golden_cross = [False] * len(ema_curta)
    death_cross = [False] * len(ema_curta)

    for i in range(1, len(ema_curta)):    
            if (ema_curta[i-1] <= ema_longa[i-1]) and (ema_curta[i] > ema_longa[i]):
                golden_cross[i] = True
            if (ema_curta[i-1] >= ema_longa[i-1]) and (ema_curta[i] < ema_longa[i]):
                death_cross[i] = True

  
    return golden_cross, death_cross

def RSI_CALCULATOR(fechamentos: list[float], periodo: int = 14) -> list[float]:
    series_precos = pd.Series(fechamentos)
    delta = series_precos.diff()

    ganhos = delta.where(delta > 0, 0.0)
    perdas = -delta.where(delta < 0, 0.0)

    media_ganhos = ganhos.ewm(alpha=1/periodo, min_periods=periodo, adjust=False).mean()
    media_perdas = perdas.ewm(alpha=1/periodo, min_periods=periodo, adjust=False).mean()

    rs = media_ganhos / media_perdas
    
    rsi = 100 - (100 / (1 + rs))
    
    rsi = rsi.fillna(50) 

    return rsi.to_list()


def SHOW(candles, ema_curta, ema_longa, golden_cross, death_cross):
    import matplotlib.pyplot as plt

    periodo = range(len(candles)) 
    
    indices_golden = [i for i, x in enumerate(golden_cross) if x]
    indices_death = [i for i, x in enumerate(death_cross) if x]

    plt.figure(figsize=(10, 5))
    
    plt.plot(periodo, candles, label='Preço', color='gray', 
    alpha=0.5, markevery=golden_cross, marker="o", markerfacecolor='yellow', markeredgecolor='orange')

    plt.plot(periodo, candles, label='Preço', color='gray', 
    alpha=0.5, markevery=death_cross, marker="o", markerfacecolor='gray', markeredgecolor='black')
    
    plt.plot(periodo, ema_curta, label='EMA 9 (Rápida)', color='blue')
    plt.plot(periodo, ema_longa, label='EMA 21 (Lenta)', color='red')


    
    y_min, y_max = min(candles), max(candles)
    
    plt.vlines(x=indices_golden, ymin=y_min, ymax=y_max, 
               colors='orange', linestyle='-', alpha=0.5, label='golden cross')

    plt.vlines(x=indices_death, ymin=y_min, ymax=y_max, 
               colors='darkblue', linestyle='--', alpha=0.5, label='death cross')
    
    plt.title('Bitcoin 15m - Estratégia de Cruzamento')
    plt.legend()
    plt.grid(True, alpha=0.1)
    plt.show()