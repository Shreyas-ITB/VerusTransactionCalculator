# Configure them as per your needs!

TO_DATE = 200000000000  # Top date bound in epoch time
FROM_DATE = 1546300800  # Bottom date bound in epoch time
FILENAME_OUT = "coinbase_records.csv"  # Name of file to be imported to cointracking
FILENAME_IN = "txs.txt"  # Output from listtransactions api call pointed towards txt file
PRICE_FILE_NAME = 'prices.txt'  # Name of the JSON file that prices are fetched and saved to