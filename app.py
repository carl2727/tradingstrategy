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
    sell_bottom = FloatField('Sell Bottom', validators=[DataRequired(), NumberRange(min=0)])
    sell_top = FloatField('Sell Top', validators=[DataRequired(), NumberRange(min=0)])
    step_size = IntegerField('Step Size', validators=[DataRequired(), NumberRange(min=1)])
    steps = IntegerField('Steps', validators=[DataRequired(), NumberRange(min=1)])
    mu = FloatField('Scenario Mean', validators=[DataRequired(), NumberRange(min=0)])
    sigma = FloatField('Scenario Standard Deviation', validators=[DataRequired(), NumberRange(min=0)])
    number_sce = IntegerField('Number Of Scenarios', validators=[DataRequired(), NumberRange(min = 1, max=999)])
    submit = SubmitField('Sell')

# Functions
# Truncate floats
def trunc(a, x):
    int1 = int(a * (10**x))/(10**x)
    return float(int1)

def sell_order(coins, str_steps, price_normalize, scenario):
    print("sell_order arguments:")
    print("coins:", coins)
    print("str_steps:", str_steps)
    print("price_normalize:", price_normalize)
    print("scenario:", scenario)
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
            # Debugging
            # print(int(val))
            # print("Sold " + str(trunc(sell_amount,4)) + " coins at " + str(int(price)) + " for " + str(trunc(sell,2)) + " New total = " + str(profit))
    # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nTotal profit: " + str(trunc(profit,2)))
    # print("Coins left: " + str(trunc(coins,4)))
    return profit, coins

# Sell Strategies
sell_strategies = []
sell_bottom = 0
sell_top = 1
step_size = 1
steps = 1

def create_strategies(sell_bottom, sell_top, step_size, steps):
    for i in range(sell_bottom, sell_top, step_size):
        for j in range(i+step_size, sell_top+1, step_size):
            sell_strategies.append({"name": f"Strategy {i}-{j}", "sell_top": j, "sell_bottom": i, "steps": 5})

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
        step_size = int(form.step_size.data)
        steps = int(form.steps.data)
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)

        # Print form field values
        print("coins:", coins)
        print("sell_bottom:", sell_bottom)
        print("sell_top:", sell_top)
        print("steps:", steps)
        print("mu:", mu)
        print("sigma:", sigma)
        print("number_sce:", number_sce)
       
        create_strategies(sell_bottom, sell_top, step_size, steps)
        scenarios = [random.gauss(mu, sigma) for i in range(number_sce)]
        for strategy in sell_strategies:
            # print(f"Simulating sell orders using {strategy['name']}...")
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
                profit, coins = sell_order(coins, str_steps, price_normalize, scenario)
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
        plt.savefig(os.path.join(app.root_path, 'static', 'histogram.png'))  # Save the plot as a PNG image
        plt.close()


        if not strategy_profits:
            flash('No results found.', 'warning')
            return redirect(url_for('sell'))
        return render_template('sell_results.html', sorted_strategies=sorted_strategies)

    return render_template('sell.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)