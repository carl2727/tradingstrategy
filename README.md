# Trading Strategy

***Final project for Harvard CS50 2023***

### Video Demo: https://youtu.be/efZWo1MrmVM


This is a web-based Trading Simulator that allows users to simulate buying and selling cryptocurrencies using different strategies and scenarios. The application is built using Python with the Flask web framework and provides a user-friendly interface to interact with.

It also serves as final project for Harvard's CS50: Introduction to Computer Science Class of 2023.  


## Getting Started
To run Trading Strategy locally, follow the steps below:

1. Clone the repository to your local machine.
2. Create a virtual environment and activate it.
3. Install the required dependencies by running the following command:  
```pip install -r requirements.txt```
4. Run the Flask application using the following command:  
```python app.py```  
5. Open a web browser and navigate to http://localhost:5000 to access the application.

## Features
Trading Strategy includes the following features:

### Selling Strategies 
Users can define selling strategies based on parameters like coins, sell bottom, sell top, steps, step increment, scenario mean, scenario standard deviation, and number of scenarios. The application evaluates the defined selling strategies and presents the results, including the average profit for each strategy.

### Buying Strategies 
Users can define buying strategies based on parameters like money, buy bottom, buy top, steps, step increment, scenario mean, scenario standard deviation, and number of scenarios. The application evaluates the defined buying strategies and displays the average number of coins acquired and the overall rating for each strategy.

### Scenario Analysis 
Users can analyze random scenarios without defining strategies. They can input the scenario mean, scenario standard deviation, and number of scenarios. The application generates a histogram of the random scenarios along with statistical metrics, such as minimum, maximum, 5th percentile, and 95th percentile values.

## Project Structure
The project consists of the following files:

***app.py***: The main Python script that sets up the Flask application and defines the routes and functionality.  
  
***base.html***: The base HTML template that provides the structure for other pages and includes the navigation menu.  
  
***buy.html***: The template for the buy form page, where users can input parameters for buying strategies.  
  
***buy_results.html***: The template for displaying the results of the buying strategies.  
  
***index.html***: The homepage template.  
  
***scenario_results.html***: The template for displaying the results of the scenario analysis.  
  
***scenarios.html***: The template for the scenario form page, where users can input parameters for scenario analysis.  
  
***sell.html***: The template for the sell form page, where users can input parameters for selling strategies.  
  
***sell_results.html***: The template for displaying the results of the selling strategies.  
  
***styles.css***: The CSS file for customizing the appearance of the web pages.  
  
***histogram.png***: The generated histogram image for scenario analysis.  


## Logic of the App
Trading Strategy operates based on a set of well-defined logic and algorithms that enable users to simulate buying and selling cryptocurrencies using various strategies and scenarios. Here's an overview of the key logic behind the application:

### Selling Strategies  
***Strategy Creation***: Users can define selling strategies by specifying the following parameters: coins, sell bottom, sell top, steps, step increment, scenario mean, scenario standard deviation, and number of scenarios. Based on these inputs, the application creates a set of selling strategies to be evaluated.

***Step-wise Approach***: The application divides the range between sell bottom and sell top into multiple steps based on the number of steps and step increment provided by the user. For each step, it calculates the corresponding selling price.

***Transaction Normalization***: To ensure a fair evaluation, the amount of coins sold in each transaction is normalized across all steps. This normalization balances the weight of each transaction against others, as each transaction has the same total value.

***Scenario Generation***: The application generates a specified number of random scenarios using a Gaussian distribution with the given scenario mean and standard deviation. These scenarios represent potential cryptocurrency prices in the market. 

***Strategy Evaluation***: For each selling strategy, the application calculates the normalized price based on the steps and step increment provided. It then evaluates the strategy for each scenario by determining whether the selling price at a given step is less than or equal to the scenario price. If it is, the application calculates the sell amount and profit, updating the remaining coins and total profit accordingly.

***Results Presentation***: The results of each selling strategy are recorded, including the sell steps, profit for each scenario, and average profit across all scenarios. The strategies are then sorted based on their average profit, and the final results are presented to the user.

### Buying Strategies
***Strategy Creation***: Users can define buying strategies by specifying parameters such as money, buy bottom, buy top, steps, step increment, scenario mean, scenario standard deviation, and number of scenarios. The application creates a set of buying strategies to be evaluated based on these inputs.

***Step-wise Approach***: The application divides the range between buy bottom and buy top into multiple steps, determined by the number of steps and step increment provided by the user. For each step, the corresponding buying price is calculated.

***Transaction Normalization***: To ensure a fair evaluation, the amount of coins bought in each transaction is normalized across all steps. This balances the weight of each transaction against others, as each transaction has the same total value.

***Scenario Generation***: Random scenarios are generated using a Gaussian distribution with the specified scenario mean and standard deviation. These scenarios represent potential cryptocurrency prices in the market.

***Strategy Evaluation***: Each buying strategy is evaluated for every scenario. The application checks if the buying price at a given step is greater than or equal to the scenario price. If it is, the application calculates the buy amount, updates the remaining money, and calculates the acquired coins and overall rating for that scenario.

***Results Presentation***: The results of each buying strategy are recorded, including the buy steps, number of coins acquired for each scenario, and the overall rating across all scenarios. The strategies are then sorted based on their overall rating, and the final results are presented to the user.
