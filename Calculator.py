from csv_writer import write_csv
from pycoingecko import CoinGeckoAPI
import requests
from config import FILENAME_OUT, CURRENCY, ADDRESS, BLOCK
from forex_python.converter import CurrencyCodes
from time import sleep
import shutil

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
    {"currencyid": "iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU", "ticker": "TBTC.vETH"},
    {"currencyid": "iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY", "ticker": "PURE.vETH"},
    {"currencyid": "i61cV2uicKSi1rSMQCBNQeSYC3UAi9GVzd", "ticker": "USDC.vETH"},
    {"currencyid": "iEnQEjjozf1HZkqFT9U4NKnzz1iGZ7LbJ4", "ticker": "TRAC.vETH"},
    {"currencyid": "iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2", "ticker": "vARRR"},
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
    blockheight = requests.get("https://explorer.verus.io/api/getblockcount", timeout=10000)
    return blockheight.text

def gettxns():
    blkheight = getcurrentblockheight()
    req = requests.get(f"http://116.203.53.84:5000/getimports_blk/Bridge.vETH/{BLOCK}/{blkheight}", timeout=10000)
    return req.json()

def getdaiprice():
    req = requests.get(f"http://116.203.53.84:5000/getdaiveth_daireserveprice", timeout=10000)
    return req.json()

def getvrscprice():
    req = requests.get(f"http://116.203.53.84:5000/getvrsc_vrscreserveprice", timeout=10000)
    return req.json()

def getmkrprice():
    req = requests.get(f"http://116.203.53.84:5000/getmkrveth_mkrreserveprice", timeout=10000)
    return req.json()

def getethprice():
    req = requests.get(f"http://116.203.53.84:5000/getveth_vethreserveprice", timeout=10000)
    return req.json()

def getcurrencybalances(address):
    req = requests.get(f"http://116.203.53.84:5000/getaddressbalance/{address}", timeout=10000)
    return req.json()

def extract_currency_balances():
    json_data = getcurrencybalances(ADDRESS)
    currency_balance = json_data['result']['currencybalance']
    current_currency_balances = {iaddress: value for iaddress, value in currency_balance.items()}
    return current_currency_balances

def extract_total_received_balances():
    json_data = getcurrencybalances(ADDRESS)
    currency_received = json_data['result']['currencyreceived']
    total_received_balances = {iaddress: value for iaddress, value in currency_received.items()}
    return total_received_balances

def extract_currency_info(json_data):
    currencies_info = {}
    for currency_id, currency_data in json_data['result'][0]['importnotarization']['currencystate']['currencies'].items():
        iaddress = currency_id
        viaconversionprice = currency_data['viaconversionprice']
        lastconversionprice = currency_data['lastconversionprice']
        currencies_info[iaddress] = {'viaconversionprice': viaconversionprice, 'lastconversionprice': lastconversionprice}
    return currencies_info

def calculate_impermanent_loss(initial_price, current_price):
    if initial_price <= 0 or current_price <= 0:
        return "Prices must be positive"

    loss = 1 - (initial_price / current_price)
    return loss

def calculate_spent_percentage(current_funds, total_received):
    if total_received <= 0:
        return "Total received must be positive"

    spent_percentage = ((total_received - current_funds) / total_received) * 100
    return spent_percentage

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
    current_balances = extract_currency_balances()
    total_received_balances = extract_total_received_balances()
    currency_info = extract_currency_info(data)
    if "i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV" in currency_info:
        VRSC = currency_info["i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV"]
    if "i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X" in currency_info:
        ETH = currency_info["i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X"]
    if "iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4" in currency_info:
        MKR = currency_info["iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4"]
    if "iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM" in currency_info:
        DAI = currency_info["iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM"]
    daivalue = getdaiprice()[0]
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
        try:
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
                    "Reserve-to-Reserve": transaction['reservetoreserve'], 
                    "VRSC Conversion Price": VRSC['viaconversionprice'],
                    "VRSC Last Conversion Price": VRSC['lastconversionprice'],
                    "DAI Conversion Price": DAI['viaconversionprice'],
                    "DAI Last Conversion Price": DAI['lastconversionprice'],
                    "MKR Conversion Price": MKR['viaconversionprice'],
                    "MKR Last Conversion Price": MKR['lastconversionprice'],
                    "ETH Conversion Price": ETH['viaconversionprice'],
                    "ETH Last Conversion Price": ETH['lastconversionprice']
                })
                write_csv(FILENAME_OUT, results)
            print(f"Found {len(results)} number of total transactions associated with your address {ADDRESS}.")
            print("CSV File has been generated.")
            print("")
            print("---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            columns = shutil.get_terminal_size().columns
            print("Address Statistics from Cross-Chain Transactions".center(columns))
            print("")
            try:
                print(f"You own about {current_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV']} {get_ticker_by_currency_id('i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV')} out of {total_received_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV')} in DAI is about {current_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV'] * daivalue}, Total is worth about {total_received_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV'], total_received_balances['i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV')} yet.")
            print(f"{get_ticker_by_currency_id('i5w5MuNik5NtLcYmNzcvaoixooEebB6MGV')} at the time of investment was at {VRSC['viaconversionprice']} Conversion price and was at {VRSC['lastconversionprice']} Last Conversion price checked.")
            print(f"Impermanent Loss: {calculate_impermanent_loss(VRSC['viaconversionprice'], VRSC['lastconversionprice'])}")
            print("")
            try:
                print(f"You own about {current_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X']} {get_ticker_by_currency_id('i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X')} out of {total_received_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X')} in DAI is about {current_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X'] * daivalue}, Total is worth about {total_received_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X'], total_received_balances['i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X')} yet.")
            print(f"{get_ticker_by_currency_id('i9nwxtKuVYX4MSbeULLiK2ttVi6rUEhh4X')} at the time of investment was at {ETH['viaconversionprice']} Conversion price and was at {ETH['lastconversionprice']} Last Conversion price checked.")
            print(f"Impermanent Loss: {calculate_impermanent_loss(ETH['viaconversionprice'], ETH['lastconversionprice'])}")
            print("")
            try:
                print(f"You own about {current_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4']} {get_ticker_by_currency_id('iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4')} out of {total_received_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4')} in DAI is about {current_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4'] * daivalue}, Total is worth about {total_received_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4'], total_received_balances['iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4')} yet.")
            print(f"{get_ticker_by_currency_id('iCkKJuJScy4Z6NSDK7Mt42ZAB2NEnAE1o4')} at the time of investment was at {MKR['viaconversionprice']} Conversion price and was at {MKR['lastconversionprice']} Last Conversion price checked.")
            print(f"Impermanent Loss: {calculate_impermanent_loss(MKR['viaconversionprice'], MKR['lastconversionprice'])}")
            print("")
            try:
                print(f"You own about {current_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM']} {get_ticker_by_currency_id('iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM')} out of {total_received_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM')} in DAI is about {current_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM'] * daivalue}, Total is worth about {total_received_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM'], total_received_balances['iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM')} yet.")
            print(f"{get_ticker_by_currency_id('iGBs4DWztRNvNEJBt4mqHszLxfKTNHTkhM')} at the time of investment was at {DAI['viaconversionprice']} Conversion price and was at {DAI['lastconversionprice']} Last Conversion price checked.")
            print(f"Impermanent Loss: {calculate_impermanent_loss(DAI['viaconversionprice'], DAI['lastconversionprice'])}")
            print("")
            try:
                print(f"You own about {current_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU']} {get_ticker_by_currency_id('iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU')} out of {total_received_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU')} in DAI is about {current_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU'] * daivalue}, Total is worth about {total_received_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU'], total_received_balances['iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('iS8TfRPfVpKo5FVfSUzfHBQxo9KuzpnqLU')} yet.")
            print("")
            try:
                print(f"You own about {current_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY']} {get_ticker_by_currency_id('iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY')} out of {total_received_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY')} in DAI is about {current_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY'] * daivalue}, Total is worth about {total_received_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY'] * daivalue}.")
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY'], total_received_balances['iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('iHax5qYQGbcMGqJKKrPorpzUBX2oFFXGnY')} yet.")
            print("")
            try:
                print(f"You own about {current_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2']} {get_ticker_by_currency_id('iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2')} out of {total_received_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2']} that you had purchased/bought/invested in the past.")
                print(f"The price of your current {get_ticker_by_currency_id('iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2')} in DAI is about {current_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2'] * daivalue}, Total is worth about {total_received_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2'] * daivalue}.")            
                print(f"Spent Percentage: {calculate_spent_percentage(current_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2'], total_received_balances['iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2'])}%")
            except KeyError:
                print(f"You don't have any {get_ticker_by_currency_id('iExBJfZYK7KREDpuhj6PzZBzqMAKaFg7d2')} yet.")
            print("")
            print("The Conversion Price and the Last Checked Conversion Price are also saved in the csv file that is periodically logged along with the bridge transactions corresponding to this address.")
            print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
        except Exception as e:
            print(f"Error fetching the information from the bridge: {e}, Retrying in 30 seconds...")
            sleep(30)
            gettransactions()
    else:
        print("No bridge/cross-chain transactions found for address", ADDRESS)

gettransactions()
