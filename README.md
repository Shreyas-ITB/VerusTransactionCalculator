# VerusRewardsCalculator

A simple program that calculates your transactions and exports it into a csv file in a nice informative readable form.

## Requirements

* Python 3.9 or earlier

## Setup

- Install the package requirements of the program by running \
  ```pip install -r requirements.txt``` 
- Edit the ``config.py`` file according to your preference, make sure to add your address in the ``ADDRESS`` variable and the currency you want the prices to be in the ``CURRENCY`` variable.
- Now finally run the ``Calculate.py`` file to export your rewards calculated into a csv file. \
  ```python Calculate.py``` 

## Recommendations

I highly recommend you to use a virtual environment to install the python packages, incase if anything goes wrong you can revert the changes back. \
Create a python venv by running ```python -m venv venv``` in the project's directory. And make sure to run the ``.sh`` or ``.ps1`` activate script in your console to switch the environment.

### What's Changed?
- It can automatically fetch the transactions from the address you provide to give you a complete overview of transactions in a clean looking CSV file.
- Includes the price changes in your desired currency.
- Goes through each and every transaction that you have made.
- Includes the provided amount and the settled amount.

## Note
- The time it takes depends on the number of transactions you have made from the address.
- It also depends on your network speed.
