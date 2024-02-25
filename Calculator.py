from csv_writer import write_csv
from pycoingecko import CoinGeckoAPI
import requests
from config import FILENAME_OUT, CURRENCY, ADDRESS

results = []
total_vout = []
total_vin = []
total_currency = []

# Helps to send the request to the RPC.
def send_request(method, headers, data):
    response = requests.request(method, "https://rpc.vrsc.komodefi.com", headers=headers, json=data)
    return response.json()

def fetchprice():
    cg = CoinGeckoAPI()
    data = cg.get_price(ids="verus-coin", vs_currencies=CURRENCY)
    return data['verus-coin'][CURRENCY]

def gettransactions():
    print("\nSaving Coinbase Txs...")
    print("Fetching prices...")
    print("This might take a while... depends on how many transactions you have made over time.")
    print("It scans all the transactons that you have made..")
    gettx = requests.get(f"https://explorer.verus.io/ext/getaddress/{ADDRESS}")
    for tx in gettx.json()['last_txs']:
        address = tx['addresses']
        payload = {
        "jsonrpc": "1.0",
        "id": "curltest",
        "method": "getrawtransaction",
        "params": [address, 1]
        }
        gettxexpanded = send_request("POST", {'content-type': 'text/plain;'}, payload)
        result = gettxexpanded['result']
        confirmations = result['confirmations']
        blocktime = result['blocktime']
        height = result['height']
        try:
            expiryheight = result['expiryheight']
        except:
            expiryheight = "NULL"
        txid = result['txid']

        # Extracting information from vin element
        vin_info = result['vin']
        try:
            vin_value = vin_info[0]['value']  # Extracting only the first vin value
        except:
            vin_value = 0

        # Extracting information from vout element
        vout_info = result['vout']
        try:
            vout_value = vout_info[0]['value']
        except:
            vout_value = 0
        # vout_type = [vout['scriptPubKey']['type'] for vout in vout_info]
        to_push = {
                'type': "txn",
                'vinamt': vin_value,
                'vincur': 'VRSC',
                'voutamt': vout_value,
                'voutcur': 'VRSC',
                'fee': '0.00000001',
                'feecur': 'VRSC',
                'exchange': 'false',
                'group': '',
                'comment': 'Transaction',
                'date': blocktime,
                'TXID': txid,
                'height': height,
                'expiry': expiryheight,
                'confirmations': confirmations,
                f'{CURRENCY}value per coin': fetchprice() * 1,
                f'{CURRENCY}value': fetchprice() * vout_value
            }
        results.append(to_push)
        total_vin.append(vin_value)
        total_vout.append(vout_value)
        write_csv(FILENAME_OUT, results)

gettransactions()
print(f"Recorded {len(results)} transaction(s)!")
print(f"Total VIN(s) Recorded: {len(total_vin)}")
print(f"Total VOUT(s) Recorded: {len(total_vout)}")
print(f"Wrote detailed outputs to {FILENAME_OUT}\n")
