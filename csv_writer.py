import csv

def write_csv(file_name, data):
    try:
        with open(file_name, mode='w', newline='') as csv_file:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    except Exception as e:
        print(f"Error writing to CSV file: {e}")