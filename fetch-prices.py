import json
import asyncio
from decimal import Decimal
from pycoingecko import CoinGeckoAPI
from config import FROM_DATE, TO_DATE, PRICE_FILE_NAME

def main():
    print("Fetching prices...")
    cg = CoinGeckoAPI()
    
    data = cg.get_coin_market_chart_range_by_id(id='verus-coin', vs_currency='usd', from_timestamp=FROM_DATE, to_timestamp=TO_DATE, localization=False)
    
    prices = data['prices']
    price_map = {}
    
    for ohcv in prices:
        timestamp = int(ohcv[0] / 1000)  # Convert milliseconds to seconds
        price = ohcv[1]
        price_map[str(timestamp)] = str(price)
    
    with open(PRICE_FILE_NAME, 'w', encoding='utf-8') as price_file:
        json.dump(price_map, price_file, ensure_ascii=False, indent=2)
    
    print("Done writing price file.")

if __name__ == "__main__":
    main()