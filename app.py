from flask import Flask, render_template
import random
from flask_wtf import FlaskForm
import locale
import matplotlib
import numpy as np
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import seaborn as sns
from wtforms import Form, FloatField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, NumberRange

# === Flask Configuration ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cs50'

# === Classes ===
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

class ScenarioForm(FlaskForm):
    
    mu = FloatField('Scenario Mean', validators=[DataRequired(), NumberRange(min=0)])
    sigma = FloatField('Scenario Standard Deviation', validators=[DataRequired(), NumberRange(min=0)])
    number_sce = IntegerField('Number Of Scenarios', validators=[DataRequired(), NumberRange(min=1, max=999)])
    submit = SubmitField('Create')

# Functions #

def plot_histogram(data, filename, width=9, height=6):
    plt.figure(figsize=(width, height))
    sns.set_palette("husl")
    sns.histplot(data, kde=False, color='blue', alpha=0.7, edgecolor='lightgray')       
    plt.gca().set_facecolor('none')
    plt.xlabel('Scenario Value', color='lightgray')
    plt.ylabel('Frequency', color='lightgray')
    plt.title('Distribution of Randomly Generated Scenarios', color='lightgray')    
    plt.xticks(color='lightgray')
    plt.yticks(color='lightgray')
    plt.savefig(os.path.join(app.root_path, 'static', filename), transparent=True)
    plt.close()

def sell_order(coins, str_steps, price_normalize, scenario, file=None):
    profit = 0
    rating = 0
    file.write(f"Sell order - Coins: {coins}\n")
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
            rating += (scenario/val)/len(str_steps)
            file.write(f"at {val}, sold {sell_amount} for {sell}. Total Profit: {profit}\n")
            file.flush()
    return profit, coins, rating

def buy_order(money, str_steps, price_normalize, scenario, file=None):
    coins = 0
    rating = 0
    file.write(f"Buy order - Money: {money}\n")
    for i, val in enumerate(str_steps):
        try:
            val = int(val)
        except ValueError:
            continue
        if int(val) >= scenario:
            buy_amount = (price_normalize) / int(val)
            buy = buy_amount * int(val)
            money -= buy
            coins += buy_amount
            rating += (scenario/val)/len(str_steps)
            file.write(f"at : {val}, bought {buy_amount} for {buy}, Wallet: {coins}\n")
            file.flush()
    return money, coins, rating

sell_strategies = []
buy_strategies = []

def create_sell_strategies(sell_bottom, sell_top, steps, step_increment):
    sell_strategies.clear()
    for i in range(sell_bottom, sell_top, step_increment):
        for j in range(i+step_increment, sell_top+1, step_increment):
            sell_strategies.append({"name": f"Strategy {i}-{j}", "sell_top": j, "sell_bottom": i, "steps": steps})

def create_buy_strategies(buy_bottom, buy_top, steps, step_increment):
    buy_strategies.clear()
    for i in range(buy_bottom, buy_top, step_increment):
        for j in range(i+step_increment, buy_top+1, step_increment):
            buy_strategies.append({"name": f"Strategy {i}-{j}", "buy_top": j, "buy_bottom": i, "steps": steps})

def stats_sce(mu, sigma, scenarios):
    percentiles = np.percentile(scenarios, [5, 95])
    sce_stats =  {
            'mu': mu,
            'sigma': sigma,
            'min': min(scenarios),
            'max': max(scenarios),
            '5th_percentile': percentiles[0],
            '95th_percentile': percentiles[1]}     
    return sce_stats

# === Routes ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sell.html', methods=['GET', 'POST'])
def sell():
    form = SellForm()
    sorted_strategies = []
    strategy_profits = []
    # Validate forms
    if form.validate_on_submit():
        coins = float(form.coins.data)
        sell_bottom = int(form.sell_bottom.data)
        sell_top = int(form.sell_top.data)
        steps = int(form.steps.data)
        step_increment = int(form.step_increment.data)
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)
        # Create strategies
        create_sell_strategies(sell_bottom, sell_top, steps, step_increment)
        scenarios = [random.gauss(mu, sigma) for i in range(number_sce)]
        scenarios_str = ', '.join(map(str, scenarios))
        plot_histogram(scenarios, 'histogram.png')
        # Report
        with open('sell_report.txt', 'w') as file:
            file.write(f"User input: coins: {coins}, sell_bottom: {sell_bottom}, sell_top: {sell_top,}, steps: {steps}, step_increment: {step_increment}, mu: {mu}, sigma: {sigma}, number_sce: {number_sce}\n\n")
            file.write(f"Sell Strategies:\n{sell_strategies}\n\n")
            file.write(f"Scenarios\n{scenarios_str}\n\n")
            file.flush()
            # Create steps for strategies
            for strategy in sell_strategies:
                total_profit = 0
                total_rating = 0
                step_size = (strategy["sell_top"] - strategy["sell_bottom"]) / (strategy["steps"] - 1)
                str_steps = []
                file.write(f"\nStrategy: {strategy}\n")
                file.flush()
                # Writing all strategy steps to a list
                for i in range(strategy["steps"]):
                    price = strategy["sell_bottom"] + (i * step_size)
                    str_steps.append(price)
                # Calculating normalized price
                price_sum = sum(str_steps)
                price_denom = 0
                for i in range(strategy["steps"]):
                    price_denom += price_sum / str_steps[i]
                price_normalize = price_sum / price_denom
                # Calculating results
                for scenario in scenarios:
                    file.write(f"\nScenario: {scenario}\n")
                    coins = float(form.coins.data)
                    profit, coins, rating = sell_order(coins, str_steps, price_normalize, scenario, file=file)
                    total_profit += profit
                    total_rating += rating                            
                avg_profit = (total_profit / len(scenarios))
                avg_rating = (total_rating / len(scenarios))
                strategy_profits.append((strategy['sell_top'], strategy['sell_bottom'], strategy['steps'], avg_profit, avg_rating))
            sorted_strategies = sorted(strategy_profits, key=lambda x: x[2], reverse=True)       
            # Write report            
            file.write(f"Sorted Strategies: {sorted_strategies}")
            file.close()
        # Error handling
        if not strategy_profits:
            flash('No results found.', 'warning')
            return redirect(url_for('sell'))
        # Return values
        sorted_scenarios = sorted(scenarios, reverse=True)
        sce_stats = stats_sce(mu, sigma, scenarios)
        return render_template('sell_results.html', sorted_strategies=sorted_strategies, sorted_scenarios=sorted_scenarios, sce_stats=sce_stats)
    return render_template('sell.html', form=form)

@app.route('/buy.html', methods=['GET', 'POST'])
def buy():
    form = BuyForm()
    sorted_strategies = []
    strategy_amounts = []
    # Validate forms
    if form.validate_on_submit():
        money = float(form.money.data)
        buy_bottom = int(form.buy_bottom.data)
        buy_top = int(form.buy_top.data)
        steps = int(form.steps.data)
        step_increment = int(form.step_increment.data)
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)
        # Create Strategies
        create_buy_strategies(buy_bottom, buy_top, steps, step_increment)
        scenarios = [random.gauss(mu, sigma) for _ in range(number_sce)]
        scenarios_str = ', '.join(map(str, scenarios))
        plot_histogram(scenarios, 'histogram.png')        
        # Report
        with open('buy_report.txt', 'w') as file:
            file.write(f"User input: money: {money}, buy_bottom: {buy_bottom}, buy_top: {buy_top}, steps: {steps}, step_increment: {step_increment}, mu: {mu}, sigma: {sigma}, number_sce: {number_sce}\n\n")
            file.write(f"Buy Strategies:\n{buy_strategies}\n\n")
            file.write(f"Scenarios\n{scenarios_str}\n\n")
            file.flush()
            # Create steps for strategies
            for strategy in buy_strategies:
                total_coins = 0
                total_rating = 0
                step_size = (strategy["buy_top"] - strategy["buy_bottom"]) / (strategy["steps"] - 1)
                str_steps = []
                file.write(f"\nStrategy: {strategy}\n")
                file.flush()
                # Writing all strategy steps to a list
                for i in range(strategy["steps"]):
                    price = strategy["buy_top"] - (i * step_size)
                    str_steps.append(price)
                # Calculating normalized price
                price_sum = sum(str_steps)
                price_denom = 0
                for i in range(strategy["steps"]):
                    price_denom += price_sum / str_steps[i]
                price_normalize = price_sum / price_denom            
                # Calculating results
                for scenario in scenarios:
                    file.write(f"\nScenario: {scenario}\n")
                    money = float(form.money.data)
                    money, coins, rating = buy_order(money, str_steps, price_normalize, scenario, file=file)
                    total_coins += coins
                    total_rating += rating        
                avg_coins = (total_coins / len(scenarios))
                avg_rating = (total_rating / len(scenarios))
                file.write(f"avg_coins: {avg_coins} total_coins {total_coins}\n")
                strategy_amounts.append((strategy['buy_bottom'], strategy['buy_top'], strategy['steps'], avg_coins, avg_rating))                                    
            sorted_strategies = sorted(strategy_amounts, key=lambda x: x[4], reverse=True)       
            file.write(f"Sorted Strategies: {sorted_strategies}\n")
            file.close()
        # Error handling
        if not strategy_amounts:
            flash('No results found.', 'warning')
            return redirect(url_for('buy'))
        # Return values
        sorted_scenarios = sorted(scenarios, reverse=True)
        sce_stats = stats_sce(mu, sigma, scenarios)
        return render_template('buy_results.html', sorted_strategies=sorted_strategies, sorted_scenarios=sorted_scenarios, sce_stats=sce_stats)
    return render_template('buy.html', form=form)

@app.route('/scenarios.html', methods=['GET', 'POST'])
def scenario():
    form = ScenarioForm()
    # Validate forms
    if form.validate_on_submit():
        mu = float(form.mu.data)
        sigma = float(form.sigma.data)
        number_sce = int(form.number_sce.data)
        scenarios = [random.gauss(mu, sigma) for i in range(number_sce)]
        scenarios_str = ', '.join(map(str, scenarios))
        sce_stats = stats_sce(mu, sigma, scenarios)
        plot_histogram(scenarios, 'histogram.png') 
        # Report
        with open('scenario_report.txt', 'w') as file:
            file.write(f"Scenario parameters: mu: {mu}, sigma: {sigma}, number_sce: {number_sce}\n\n")
            file.write(f"Scenarios\n{scenarios_str}\n\n")
            file.close()
        # Return values
        sorted_scenarios = sorted(scenarios, reverse=True)   
        return render_template('scenario_results.html', sorted_scenarios = sorted_scenarios, sce_stats = sce_stats)
    
    return render_template('scenarios.html', form=form)

@app.template_filter()
def currency(val):
    cur = float(val)
    locale.setlocale(locale.LC_ALL, '')  # Set the locale based on the system settings
    return locale.format_string("%.2f €", cur, grouping=True)

@app.template_filter()
def number(val):
    num = float(val)
    return "{:,.2f}".format(num)

if __name__ == "__main__":
    app.run(debug=True)