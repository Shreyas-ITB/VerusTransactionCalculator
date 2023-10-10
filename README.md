# VerusRewardsCalculator

A simple program that calculates your staking rewards and exports it into a csv file.

## Requirements

* Python 3.9 or earlier \
* Verus Wallet that should be running in Native mode or CLI wallet

## Setup

- Install the package requirements of the program by running \
  ```pip install -r requirements.txt``` \
- Export the transactions from your wallet with the following commmand \
  ```listtransactions "*" 1000000 > txs.txt``` \
- Now copy that ``txs.txt`` file from the exported location and paste it in the project's folder. \
- Run the ``fetch-prices.py`` file to fetch the price. \
  ```python fetch-prices.py``` \
- Now finally run the ``Calculate.py`` file to export your rewards calculated into a csv file. \
  ```python Calculate.py``` \

## Recommendations

I highly recommend you to use a virtual environment to install the python packages, incase if anything goes wrong you can revert the changes back. \
Create a python venv by running ```python -m venv venv``` in the project's directory. And make sure to run the ``.sh`` or ``.ps1`` activate script in your console to switch the environment.
