import json
from datetime import datetime
from decimal import Decimal
from csv_writer import write_csv
from config import TO_DATE, FROM_DATE, FILENAME_IN, FILENAME_OUT, PRICE_FILE_NAME
from prices import get_price_for_time

# Load prices
print("Loading prices...")
try:
    with open(PRICE_FILE_NAME, 'r', encoding='utf8') as price_file:
        price_data = price_file.read()
        prices = json.loads(price_data)
except Exception as e:
    print("Error reading price data")
    print(e)
    exit(1)

if not prices:
    print("No price data")
    exit(1)

print("Prices loaded.")

# Load transactions
print("Loading transactions...")
try:
    with open(FILENAME_IN, 'r', encoding='utf8') as tx_file:
        tx_data = tx_file.read()
        transactions = json.loads(tx_data)
except Exception as e:
    print("Error reading tx data")
    print(e)
    exit(1)

if not transactions:
    print("No tx data")
    exit(1)

print("Transactions loaded.")
results = []
total_vrsc = 0
total_usd = Decimal(0)

print("\nSaving Coinbase Txs...")
for tx in transactions:
    try:
        usdval = (Decimal(get_price_for_time(prices, tx['blocktime'])) * Decimal(tx['amount'])).quantize(Decimal('0.00'))
    except TypeError:
        usdval = "NaN"
    if (tx['category'] == 'generate' or tx['category'] == 'mint')and \
            FROM_DATE < int(tx['blocktime']) < TO_DATE:
        tx_date = datetime.utcfromtimestamp(int(tx['blocktime']))
        if tx['category'] == 'stake':
            settype = "Staking"
        else:
            settype = "Staking"
        to_push = {
            'type': settype,
            'buy': tx['amount'],
            'buycur': 'VRSC',
            'sell': '',
            'sellcur': '',
            'fee': '',
            'feecur': '',
            'exchange': '',
            'group': '',
            'comment': 'Staking' if tx['category'] == 'mint' else 'Mining',
            'date': tx_date.strftime('%Y-%m-%d %H:%M:%S'),
            'TXID': tx['txid'],
            'usdvalue': usdval #(Decimal(get_price_for_time(prices, tx['blocktime'])) * Decimal(tx['amount'])).quantize(Decimal('0.00'))
        }
        total_usd = Decimal('0')
        total_usd += Decimal(to_push['usdvalue'])
        total_vrsc += Decimal(tx['amount'])
        results.append(to_push)

write_csv(FILENAME_OUT, results)

print(f"Recorded {len(results)} staking/mining transaction(s)!")
print(f"\nTotal VRSC: {total_vrsc}")
print(f"Total USD: {total_usd}")
print(f"Wrote detailed outputs to {FILENAME_OUT}\n")