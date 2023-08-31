import csv

def read_csv_to_dict(sheet):
    records = []
    with open(sheet, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            records.append(row)
    return records

def check_nested_key_value(data, target_key, target_value):
    if isinstance(data, dict):
        if data.get(target_key) == target_value:
            return True
        for value in data.values():
            if check_nested_key_value(value, target_key, target_value):
                return True
    elif isinstance(data, list):
        for item in data:
            if check_nested_key_value(item, target_key, target_value):
                return True
    return False