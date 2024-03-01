from csv_writer import write_csv
from pycoingecko import CoinGeckoAPI
import requests
from config import FILENAME_OUT, CURRENCY, ADDRESS, BLOCK
from forex_python.converter import CurrencyCodes

# Initialize CurrencyCodes object
currency_codes = CurrencyCodes()
results = []
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
    req = requests.get(f"http://116.203.53.84:5000/getimports/Bridge.vETH/{BLOCK}/{blkheight}")
    return req.json()

def getdaiprice():
    req = requests.get(f"http://116.203.53.84:5000/getdaiveth_daireserveprice")
    return req.json()

def getvrscprice():
    req = requests.get(f"http://116.203.53.84:5000/getvrsc_vrscreserveprice")
    return req.json()

def getmkrprice():
    req = requests.get(f"http://116.203.53.84:5000/getmkrveth_mkrreserveprice")
    return req.json()

def getethprice():
    req = requests.get(f"http://116.203.53.84:5000/getveth_vethreserveprice")
    return req.json()

def gettransactions():
    print("Fetching prices...")
    price = fetchprice()
    currenciessym = currency_codes.get_symbol(CURRENCY.upper())
    print(f"Value of 1 VRSC in {CURRENCY.upper()} is {price}{currenciessym}")
    print("Fetching the transactions from the bridge using VerusStatisticsAPI.")
    # Iterate through result
    data = gettxns()
    # List to store matched data
    matched_data = []

    # Iterate through result
    for res in data["result"]:
        # Check if destination address matches
        for transfer in res["transfers"]:
            if transfer["destination"]["address"] == ADDRESS:
                # Get required information
                exporttxid = res["import"]["exporttxid"]
                importheight = res["importheight"]
                blockhash = res["importnotarization"]["proofroots"][0]["blockhash"]
                gasprice = res["importnotarization"]["proofroots"][0]["gasprice"]
                height = res["importnotarization"]["proofroots"][0]["height"]
                importtxid = res["importtxid"]
                # Get currency value and type
                currency, value = transfer["currencyvalues"].popitem()
                currencytype = transfer["destination"]["type"]
                destinationcurrencyid = transfer["destinationcurrencyid"]
                feecurrencyid = transfer["feecurrencyid"]
                fees = transfer["fees"]
                # reservetoreserve = transfer["reservetoreserve"]
                
                # Append matched data to the list
                matched_data.append({
                    "exporttxid": exporttxid,
                    "importheight": importheight,
                    "blockhash": blockhash,
                    "gasprice": gasprice,
                    "height": height,
                    "importtxid": importtxid,
                    "currencyid": currency,
                    "amount": value,
                    "destination_type": currencytype,
                    "destinationcurrencyid": destinationcurrencyid,
                    "feecurrencyid": feecurrencyid,
                    "fees": fees,
                    "convert": True,
                    "reservetoreserve": True
                })
    # Check if any matches were found
    if matched_data:
        print(f"Cross-Chain transactions found for address {ADDRESS}, Calculating the values might take some time..")
        for transaction in matched_data:
            if get_ticker_by_currency_id(transaction['currencyid']) == "DAI.vETH":
                currencyval = transaction['amount'] * getdaiprice()[0]
            elif get_ticker_by_currency_id(transaction['currencyid']) == "MKR.vETH":
                currencyval = transaction['amount'] * getmkrprice()[0]
            elif get_ticker_by_currency_id(transaction['currencyid']) == "vETH":
                currencyval = transaction['amount'] * getethprice()[0]
            elif get_ticker_by_currency_id(transaction['currencyid']) == "VRSC":
                currencyval = transaction['amount'] * getvrscprice()[0]
            results.append({
                "Conversion Status": transaction['convert'],
                "Currency": get_ticker_by_currency_id(transaction['currencyid']),
                "Amount": transaction['amount'],
                "USD Value": f"{currencyval}$",
                "Fees": transaction['fees'],
                "Fees Currency": get_ticker_by_currency_id(transaction['feecurrencyid']),
                "Destination Currency": get_ticker_by_currency_id(transaction['destinationcurrencyid']),
                "Address": ADDRESS,
                "Import TXID": transaction['importtxid'],
                "Export TXID": transaction['exporttxid'],
                "Block Hash": transaction['blockhash'],
                "Import Height": transaction['importheight'],
                "Block Height": transaction['height'],
                "Gas Price": transaction['gasprice'],
                "Type": transaction['destination_type'],
                "Reserve-to-Reserve": transaction['reservetoreserve']
            })
            write_csv(FILENAME_OUT, results)
        print(f"Found {len(results)} number of total transactions associated with your address {ADDRESS}.")
        print("CSV File has been generated.")
    else:
        print("No bridge/cross-chain transactions found for address", ADDRESS)

gettransactions()
