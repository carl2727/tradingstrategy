from flask import Flask
import random

app = Flask(__name__)

def trunc(a, x):
    int1 = int(a * (10**x))/(10**x)
    return float(int1)

def sell_order(coins, str_steps, price_normalize, sce):
    profit = 0    
    for i, val in enumerate(str_steps):
        if val <= sce:
            # print(int(val))
            sell_amount = (price_normalize) / val
            sell = sell_amount * val
            coins -= sell_amount
            profit += sell
            # print("Sold " + str(trunc(sell_amount,4)) + " coins at " + str(int(price)) + " for " + str(trunc(sell,2)) + " New total = " + str(profit))

    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nTotal profit: " + str(trunc(profit,2)))
    # print("Coins left: " + str(trunc(coins,4)))
    return profit, coins

# Portfolio
amount = 1
market_price = 25673

# Sell Strategies
sell_strategies = []
sell_bottom = 50000
sell_top = 180000
step_size = 2000

for i in range(sell_bottom, sell_top, step_size):
    for j in range(i+step_size, sell_top+1, step_size):
        sell_strategies.append({"name": f"Strategy {i}-{j}", "sell_top": j, "sell_bottom": i, "steps": 5})


# Scenarios
mu = 120000
sigma = 20000
scenarios = [random.gauss(mu, sigma) for i in range(100)]
# print(scenarios)


strategy_profits = []
for strategy in sell_strategies:
    # print(f"Simulating sell orders using {strategy['name']}...")
    total_profit = 0
    coins = amount
    step_size = (strategy["sell_top"] - strategy["sell_bottom"]) / (strategy["steps"] - 1)
    str_steps = []
    for i in range(strategy["steps"]):
        price = strategy["sell_bottom"] + (i * step_size)
        str_steps.append(price)
    price_sum = sum(str_steps)
    price_denom = 0
    for i in range(strategy["steps"]):
        price_denom += price_sum / str_steps[i]
    price_normalize = price_sum / price_denom
    # print(price_normalize)
    for scenario in scenarios:
         profit, coins = sell_order(coins, str_steps, price_normalize, scenario)
         total_profit += profit
         # print("scenario " + str(trunc(scenario,0)) + " profit: " + str(profit) + " total profit: " + str(total_profit))
    avg_profit = (total_profit / len(scenarios))
    avg_profit = int(avg_profit)
    strategy_profits.append((strategy['name'], avg_profit))
    
sorted_strategies = sorted(strategy_profits, key=lambda x: x[1], reverse=True)

for strategy in sorted_strategies:
    print(f"Average profit using {strategy[0]}: {strategy[1]}\n")