from csv_writer import write_csv
from pycoingecko import CoinGeckoAPI
import requests
from config import FILENAME_OUT, CURRENCY, ADDRESS, BLOCK
from forex_python.converter import CurrencyCodes

# Initialize CurrencyCodes object
currency_codes = CurrencyCodes()
results = []
matching_transactions = []
arr_currencies = [
    {"currencyid": "i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV", "ticker": "VRSC"},
    {"currencyid": "iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM", "ticker": "DAI.vETH"},
    {"currencyid": "iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4", "ticker": "MKR.vETH"},
    {"currencyid": "i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X", "ticker": "vETH"},
    {"currencyid": "iJczmut8fHgRvVxaNfEPm7SkgJLDFtPcrK", "ticker": "LINK.vETH"},
    {"currencyid": "iC5TQFrFXSYLQGkiZ8FYmZHFJzaRF5CYgE", "ticker": "EURC.vETH"},
    {"currencyid": "iS3NjE3XRYWoHRoovpLhFnbDraCq7NFStf", "ticker": "WBTC.vETH"},
    {"currencyid": "i9oCSqKALwJtcv49xUKS2U2i79h1kX6NEY", "ticker": "USDT.vETH"},
    {"currencyid": "i61cV2uicKSi1rSMQCBNQeSYC3UAi9GVzd", "ticker": "USDC.vETH"},
    {"currencyid": "iEnQEjjozf1HZkqFT9U4NKnzz1iGZ7LbJ4", "ticker": "TRAC.vETH"},
    {"currencyid": "iNtUUdjsqV34snGZJerAvPLaojo6tV9sfd", "ticker": "MARS4.vETH"}
]

def fetchprice():
    cg = CoinGeckoAPI()
    data = cg.get_price(ids="verus-coin", vs_currencies=CURRENCY)
    return data['verus-coin'][CURRENCY]

def format_number(number):
    suffixes = ['', 'thousand', 'million', 'billion', 'trillion']
    suffix_index = 0
    
    while abs(number) >= 1000 and suffix_index < len(suffixes)-1:
        number /= 1000.0
        suffix_index += 1
        
    return '{:.2f} {}'.format(number, suffixes[suffix_index])

def get_ticker_by_currency_id(currency_id):
    currency = next((item for item in arr_currencies if item["currencyid"] == currency_id), None)
    if currency:
        return currency["ticker"]
    return "Currency not found"

def getcurrentblockheight():
    blockheight = requests.get("https://explorer.verus.io/api/getblockcount")
    return blockheight.text

def gettxns():
    blkheight = getcurrentblockheight()
    req = requests.get(f"http://116.203.53.84:5000/gettransactions/Bridge.vETH/{BLOCK}/{blkheight}")
    return req.json()

def gettransactions():
    print("Fetching prices...")
    price = fetchprice()
    currenciessym = currency_codes.get_symbol(CURRENCY.upper())
    print(f"Value of 1 VRSC in {CURRENCY.upper()} is {price}{currenciessym}")
    print("Fetching the transactions from the bridge using VerusStatisticsAPI.")
    txns = gettxns()
    # Iterate through each item in the JSON data
    for item in txns:
        destination = item.get("destination", {})
        if destination.get("address") == ADDRESS:
            convert = item.get("convert")
            currencyvalues = item.get("currencyvalues", {})
            currencyid, amount = list(currencyvalues.items())[0]  # Assuming there's only one item in currencyvalues
            destination_type = destination.get("type")
            fees = item.get("fees")
            feecurrencyid = item.get("feecurrencyid")
            destinationcurrencyid = item.get("destinationcurrencyid")
            reservetoreserve = item.get("reservetoreserve")
            # Append matching transaction to the list
            matching_transactions.append({
                "convert": convert,
                "currencyid": currencyid,
                "amount": amount,
                "destination_type": destination_type,
                "fees": fees,
                "feecurrencyid": feecurrencyid,
                "destinationcurrencyid": destinationcurrencyid,
                "reservetoreserve": reservetoreserve
            })
    # Check if any matches were found
    if matching_transactions:
        print(f"Cross-Chain transactions found for address {ADDRESS}, Calculating the values might take some time..")
        for transaction in matching_transactions:
            total_amount = 0
            total_amount += transaction['amount']
            results.append({
                "Conversion Status": transaction['convert'],
                "Currency": get_ticker_by_currency_id(transaction['currencyid']),
                "Amount": transaction['amount'],
                f"{CURRENCY.upper()} Value": f"{transaction['amount'] * price}{currenciessym}",
                "Fees": transaction['fees'],
                "Fees Currency": get_ticker_by_currency_id(transaction['feecurrencyid']),
                "Destination Currency": get_ticker_by_currency_id(transaction['destinationcurrencyid']),
                "Address": ADDRESS,
                "Type": transaction['destination_type'],
                "Reserve-to-Reserve": transaction['reservetoreserve']
            })
            write_csv(FILENAME_OUT, results)
        print(f"Found {len(results)} number of total transactions associated with your address {ADDRESS}.")
        print("CSV File has been generated.")
    else:
        print("No bridge/cross-chain transactions found for address", ADDRESS)

gettransactions()
