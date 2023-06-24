from flask import Flask, render_template
import random
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from wtforms import Form, FloatField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql://username:password@localhost/db_name'
app.config['SECRET_KEY'] = 'cs50'
db = SQLAlchemy(app)

# Classes
class SellForm(FlaskForm):
    coins = FloatField('Coins', validators=[DataRequired(), NumberRange(min=0)])
    sell_bottom = IntegerField('Sell Bottom', validators=[DataRequired(), NumberRange(min=0)])
    sell_top = IntegerField('Sell Top', validators=[DataRequired(), NumberRange(min=0)])
    steps = IntegerField('Steps', validators=[DataRequired(), NumberRange(min=1)])
    step_increment = IntegerField('Step Increment', validators=[DataRequired(), NumberRange(min=1)])
    mu = FloatField('Scenario Mean', validators=[DataRequired(), NumberRange(min=0)])
    sigma = FloatField('Scenario Standard Deviation', validators=[DataRequired(), NumberRange(min=0)])
    number_sce = IntegerField('Number Of Scenarios', validators=[DataRequired(), NumberRange(min = 1, max=999)])
    submit = SubmitField('Sell')

class BuyForm(FlaskForm):
    money = FloatField('Money', validators=[DataRequired(), NumberRange(min=0)])
    buy_bottom = IntegerField('Buy Bottom', validators=[DataRequired(), NumberRange(min=0)])
    buy_top = IntegerField('Buy Top', validators=[DataRequired(), NumberRange(min=0)])
    steps = IntegerField('Steps', validators=[DataRequired(), NumberRange(min=1)])
    step_increment = IntegerField('Step Increment', validators=[DataRequired(), NumberRange(min=1)])
    mu = FloatField('Scenario Mean', validators=[DataRequired(), NumberRange(min=0)])
    sigma = FloatField('Scenario Standard Deviation', validators=[DataRequired(), NumberRange(min=0)])
    number_sce = IntegerField('Number Of Scenarios', validators=[DataRequired(), NumberRange(min=1, max=999)])
    submit = SubmitField('Buy')

# Functions
# Truncate floats
def trunc(a, x):
    int1 = int(a * (10**x))/(10**x)
    return float(int1)

def sell_order(coins, str_steps, price_normalize, scenario, file=None):
    profit = 0    
    for i, val in enumerate(str_steps):
        try:
            val = int(val)
        except ValueError:
            continue
        if int(val) <= scenario:
            sell_amount = (price_normalize) / int(val)
            sell = sell_amount * int(val)
            coins -= sell_amount
            profit += sell
            file.write(f"Sell order - Coins: {coins}, Step: {val}, Profit: {profit}\n")
    return profit, coins

def buy_order(money, str_steps, price_normalize, scenario, file=None):
    coins = 0    
    for i, val in enumerate(str_steps):
        try:
            val = int(val)
        except ValueError:
            continue
        if int(val) <= scenario:
            buy_amount = (price_normalize) / int(val)
            buy = buy_amount * int(val)
            money -= buy_amount
            coins += buy
            file.write(f"Buy order - Coins: {coins}, Step: {val}, Money: {money}\n")
    return money, coins


# Sell Strategies

sell_bottom = 0
sell_top = 1
step_size = 1
steps = 1
step_increment = 1
sell_strategies = []
buy_strategies = []


def create_sell_strategies(sell_bottom, sell_top, steps, step_increment):
    for i in range(sell_bottom, sell_top, step_increment):
        for j in range(i+step_increment, sell_top+1, step_increment):
            sell_strategies.append({"name": f"Strategy {i}-{j}", "sell_top": j, "sell_bottom": i, "steps": steps})

def create_buy_strategies(buy_bottom, buy_top, steps, step_increment):
    for i in range(buy_bottom, buy_top, step_increment):
        for j in range(i+step_increment, buy_top+1, step_increment):
            buy_strategies.append({"name": f"Strategy {i}-{j}", "buy_top": j, "buy_bottom": i, "steps": steps})
 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sell.html', methods=['GET', 'POST'])
def sell():
    form = SellForm()
    strategy_profits = []
    if form.validate_on_submit():
        coins = float(form.coins.data)
        sell_bottom = int(form.sell_bottom.data)
        sell_top = int(form.sell_top.data)
        steps = int(form.steps.data)
        step_increment = int(form.step_increment.data)
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)

        # Print form field values
        # print("coins:", coins)
        # print("sell_bottom:", sell_bottom)
        # print("sell_top:", sell_top)
        # print("steps:", steps)
        # print("mu:", mu)
        # print("sigma:", sigma)
        # print("number_sce:", number_sce)
       
        create_sell_strategies(sell_bottom, sell_top, steps, step_increment)
        scenarios = [random.gauss(mu, sigma) for i in range(number_sce)]
        with open('sell_report.txt', 'w') as file:
            for strategy in sell_strategies:
                total_profit = 0
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
                    coins = float(form.coins.data)
                    profit, coins = sell_order(coins, str_steps, price_normalize, scenario, file=file)
                    total_profit += profit
                    # print("scenario " + str(trunc(scenario,0)) + " profit: " + str(profit) + " total profit: " + str(total_profit))
                avg_profit = (total_profit / len(scenarios))
                avg_profit = int(avg_profit)
                strategy_profits.append((strategy['name'], avg_profit))
                        
        sorted_strategies = sorted(strategy_profits, key=lambda x: x[1], reverse=True)       
        plt.hist(scenarios, bins='auto', color='skyblue', alpha=0.7)
        plt.xlabel('Scenario Value')
        plt.ylabel('Frequency')
        plt.title('Distribution of Randomly Generated Scenarios')
        plt.savefig(os.path.join(app.root_path, 'static', 'histogram.png'))
        plt.close()


        if not strategy_profits:
            flash('No results found.', 'warning')
            return redirect(url_for('sell'))
        return render_template('sell_results.html', sorted_strategies=sorted_strategies)

    return render_template('sell.html', form=form)

@app.route('/buy.html', methods=['GET', 'POST'])
def buy():
    form = BuyForm()
    strategy_amounts = []
    if form.validate_on_submit():
        money = float(form.money.data)
        buy_bottom = int(form.buy_bottom.data)
        buy_top = int(form.buy_top.data)
        steps = int(form.steps.data)
        step_increment = int(form.step_increment.data)
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)

        # Generate scenarios
        scenarios = [random.gauss(mu, sigma) for _ in range(number_sce)]

        # Create buy strategies
        create_buy_strategies(buy_bottom, buy_top, steps, step_increment)
        
        # Calculate total number of coins bought for each strategy
        strategy_results = []
        with open('buy_report.txt', 'w') as file:
            for strategy in buy_strategies:
                total_coins = 0
                step_size = (strategy["buy_top"] - strategy["buy_bottom"]) / (strategy["steps"] - 1)
                str_steps = []
                
                for i in range(strategy["steps"]):
                    price = strategy["buy_top"] - (i * step_size)
                    str_steps.append(price)
                price_sum = sum(str_steps)
                price_denom = 0
                for i in range(strategy["steps"]):
                    price_denom += price_sum / str_steps[i]
                price_normalize = price_sum / price_denom            

                for scenario in scenarios:
                    money = float(form.money.data)
                    coins, money = sell_order(money, str_steps, price_normalize, scenario, file=file)
                    total_coins += coins
        
                avg_coins = (total_coins / len(scenarios))
                avg_coins = int(avg_coins)
                strategy_amounts.append((strategy['name'], avg_coins))
                     
        sorted_strategies = sorted(strategy_amounts, key=lambda x: x[1], reverse=True)       
        plt.hist(scenarios, bins='auto', color='skyblue', alpha=0.7)
        plt.xlabel('Scenario Value')
        plt.ylabel('Frequency')
        plt.title('Distribution of Randomly Generated Scenarios')
        plt.savefig(os.path.join(app.root_path, 'static', 'histogram.png'))
        plt.close()


        if not strategy_amounts:
            flash('No results found.', 'warning')
            return redirect(url_for('buy'))
        return render_template('buy_results.html', sorted_strategies=sorted_strategies)

    return render_template('buy.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)