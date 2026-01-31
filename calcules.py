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
    
    rsi = rsi.fillna(100) 

    return rsi.to_list()

def ADX_CALCULATOR(baixas, altas, fechamentos, periodo=14):
    df = pd.DataFrame({
        'high': altas,
        'low': baixas,
        'close': fechamentos
    })

    df['prev_close'] = df['close'].shift(1)
    df['tr'] = np.maximum(df['high'] - df['low'], 
               np.maximum(abs(df['high'] - df['prev_close']), 
               abs(df['low'] - df['prev_close'])))

    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']

    df['+dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['-dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)

    def wilder_smoothing(data, n):
        return data.ewm(alpha=1/n, adjust=False).mean()

    df['tr_smooth'] = wilder_smoothing(df['tr'], periodo)
    df['+dm_smooth'] = wilder_smoothing(df['+dm'], periodo)
    df['-dm_smooth'] = wilder_smoothing(df['-dm'], periodo)

    # 4. DI (Directional Indicators)
    df['+di'] = 100 * (df['+dm_smooth'] / df['tr_smooth'])
    df['-di'] = 100 * (df['-dm_smooth'] / df['tr_smooth'])

    # 5. DX e ADX
    df['dx'] = 100 * (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di']))
    df['adx'] = wilder_smoothing(df['dx'], periodo)

    return df['adx'].tolist()


def SHOW(candles, ema_curta, ema_longa, golden_cross, death_cross, compras, vendas):
    import matplotlib.pyplot as plt

    periodo = range(len(candles)) 
    
    indices_golden = [i for i, x in enumerate(golden_cross) if x]
    indices_death = [i for i, x in enumerate(death_cross) if x]

    indices_compra = [i for i, x in enumerate(compras) if x]
    indices_vendas = [i for i, x in enumerate(vendas) if x]


    plt.figure(figsize=(10, 5))
    
    plt.plot(periodo, candles, label='Preço', color='gray', 
    alpha=0.5, markevery=golden_cross, marker="o", markerfacecolor='yellow', markeredgecolor='orange')

    plt.plot(periodo, candles, label='Preço', color='gray', 
    alpha=0.5, markevery=death_cross, marker="o", markerfacecolor='gray', markeredgecolor='black')

    plt.plot(periodo, candles, label='COMPRA', color='gray', 
    alpha=0.9, markevery=compras, marker="o", markerfacecolor='green', markeredgecolor='green')

    plt.plot(periodo, candles, label='VENDA', color='gray', 
    alpha=0.9, markevery=vendas, marker="o", markerfacecolor='red', markeredgecolor='red')
    
    plt.plot(periodo, ema_curta, label='EMA 9 (Rápida)', color='blue')
    plt.plot(periodo, ema_longa, label='EMA 21 (Lenta)', color='red')


    
    y_min, y_max = min(candles), max(candles)
    
    plt.vlines(x=indices_golden, ymin=y_min, ymax=y_max, 
               colors='orange', linestyle='-', alpha=0.1, label='golden cross')

    plt.vlines(x=indices_death, ymin=y_min, ymax=y_max, 
               colors='darkblue', linestyle='--', alpha=0.1, label='death cross')
               
    plt.vlines(x=indices_compra, ymin=y_min, ymax=y_max, 
                colors='green', linestyle='--', alpha=0.7, label='COMPRA', )

    plt.vlines(x=indices_vendas, ymin=y_min, ymax=y_max, 
               colors='red', linestyle='--', alpha=0.7, label='VENDA')
               
               
    
    plt.title('Bitcoin 15m - Estratégia de Cruzamento')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='best')
    plt.grid(True, alpha=0.1)
    plt.show()