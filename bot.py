import requests
import time
import numpy as np
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

maximum_loss = -10  # Alterado para -10% (mais realista)
take_profit = 2

# NOVO: Variáveis para simulação financeira
initial_capital = 1000.00  # Capital inicial em reais
btc_quantity = 0.0  # Quantidade de BTC comprada
current_capital = initial_capital  # Capital atual

# Database connection variables
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

# buy_price = 650000
# sell_price = 658000
symbol = "BTC-BRL"
countback = 100 
resolution = "15m"

position = {
    'is_open':False,
    'entry_price':None
}

def create_logs_table():
    """Cria a tabela de logs se ela não existir"""
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        cursor = connection.cursor()
        
        # Criar tabela se não existir
        create_table_query = """
        CREATE TABLE IF NOT EXISTS trading_logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            price DECIMAL(12,2),
            rsi DECIMAL(5,2),
            trend VARCHAR(10),
            action VARCHAR(10),
            profit_percent DECIMAL(8,2),
            current_capital DECIMAL(12,2),
            btc_quantity DECIMAL(16,8),
            log_message TEXT
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        
        cursor.close()
        connection.close()
        print("Tabela 'trading_logs' criada/verificada com sucesso!")
        
    except Exception as e:
        print(f"Erro ao criar/verificar tabela: {e}")

def insert_log(price, rsi_val, trend, action, profit_percent, current_capital, btc_quantity, log_message=""):
    """Insere um log no banco de dados"""
    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        cursor = connection.cursor()
        
        insert_query = """
        INSERT INTO trading_logs (price, rsi, trend, action, profit_percent, current_capital, btc_quantity, log_message)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        
        cursor.execute(insert_query, (price, rsi_val, trend, action, profit_percent, current_capital, btc_quantity, log_message))
        connection.commit()
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Erro ao inserir log: {e}")

def rsi(prices, period=14):
    prices = np.array(prices, dtype=float)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        gain = max(delta, 0)
        loss = -min(delta, 0)
        up = (up * (period - 1) + gain) / period
        down = (down * (period - 1) + loss) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi[-1]

def ema(values, period) -> float:
    values = np.array(values, dtype=float)
    ema_values = [values[0]]
    k = 2 / (period + 1)
    for price in values[1:]:
        ema_values.append(price * k + ema_values[-1] * (1 - k))
    return np.array(ema_values)

def init_bot():
    global current_capital, btc_quantity  # NOVO: variáveis globais
    
    current_timestamp = int(time.time())
    candles_url = f"https://api.mercadobitcoin.net/api/v4/candles?symbol={symbol}&resolution={resolution}&to={current_timestamp}&countback={countback}"
    dados = requests.get(candles_url)
    candles = dados.json()

    open_vals = []
    close_vals = []
    low_vals = []
    high_vals = []

    for i, k in candles.items():
        if i == 'o':
            open_vals = k
        elif i == 'c':
            close_vals = k
        elif i == 'l':
            low_vals = k
        elif i == 'h':
            high_vals = k

    rsi_val = rsi(close_vals)
    ema_short = ema(close_vals, 9)[-1]
    ema_long = ema(close_vals,21)[-1]
    last_close_val = float(close_vals[-1])
   
    if ema_short > ema_long:
        trend = 'high'
    elif ema_short < ema_long:
        trend = 'low'
    else:
        trend = 'stable'

    print(f'Preço Atual: R$ {last_close_val:.2f}')
    print(f'RSI: {rsi_val:.2f} | Tendencia: {trend}')
    print(f'Capital Atual: R$ {current_capital:.2f} | BTC: {btc_quantity:.8f}')

    
    action = "HOLD"
    log_message = ""

    if rsi_val < 50 and trend == "high" and not position['is_open']:
        btc_quantity = current_capital / last_close_val
        action = "BUY"
        position['is_open'] = True
        position["entry_price"] = last_close_val
        log_message = f"COMPRANDO {btc_quantity:.8f} BTC por R$ {current_capital:.2f}"
        print(log_message)

    elif rsi_val > 70 and trend == "low" and position['is_open']:
        sell_value = btc_quantity * last_close_val
        profit_real = sell_value - initial_capital
        profit_percent = (profit_real / initial_capital) * 100
        action = "SELL"
        position['is_open'] = False
        current_capital = sell_value
        log_message = f"VENDENDO {btc_quantity:.8f} BTC por R$ {sell_value:.2f} | Lucro: R$ {profit_real:.2f} ({profit_percent:.2f}%)"
        print(log_message)
        btc_quantity = 0.0

    if position["is_open"]:
        current_value = btc_quantity * last_close_val
        profit_real = current_value - initial_capital
        profit_percent = (profit_real / initial_capital) * 100
        print(f"Valor atual da posição: R$ {current_value:.2f} | Lucro: R$ {profit_real:.2f} ({profit_percent:.2f}%)")

        if profit_percent <= maximum_loss:
            sell_value = btc_quantity * last_close_val
            current_capital = sell_value
            log_message = f"Stop-loss atingido ({profit_percent:.2f}%) — VENDENDO por R$ {sell_value:.2f}!"
            print(log_message)
            position["is_open"] = False
            btc_quantity = 0.0

        elif profit_percent >= take_profit:
            sell_value = btc_quantity * last_close_val
            current_capital = sell_value
            log_message = f"Take-profit atingido ({profit_percent:.2f}%) — VENDENDO por R$ {sell_value:.2f}!"
            print(log_message)
            position["is_open"] = False
            btc_quantity = 0.0
    else:
        profit_real = 0
        profit_percent = 0

    insert_log(last_close_val, rsi_val, trend, action, profit_percent, current_capital, btc_quantity, log_message)


# NOVO: Criar tabela na inicialização
create_logs_table()

while True:
    init_bot()
    time.sleep(60 * 15)