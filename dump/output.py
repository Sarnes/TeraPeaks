import json
from pathlib import Path
import csv
import os

OPTIONS = ["JSON", "CSV"]
_ = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DIRECTORY = Path(_).parent
CURRENT_DIRECTORY = os.getcwd()

class Dumper:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def write_product_csv(data, search, output_folder):
        file_path = os.path.join(output_folder, f"{search}-product.csv")
        with open(file_path, 'w', newline=''):
            fieldnames = list(data.keys())
            writer = csv.DictWriter(file_path, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow(data)
         
    @staticmethod        
    def write_listing_csv(data, search, output_folder):
        file_path = os.path.join(output_folder, f"{search}-product.csv")
        with open(file_path, 'w', newline=''):
            fieldnames = list(data[0].keys())
            writer = csv.DictWriter(file_path, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)
    
    def write_csv(self, data: dict, search: str, output_folder: str):
        self.write_product_csv(data.get("product"), search, output_folder)
        self.write_listing_csv(data.get("listing"), search, output_folder)
        return True
        

    def dump_data(self,  data: dict, search: str, option: str = "JSON", output_dir: str = DEFAULT_DIRECTORY):
        output_folder = os.path.join(output_dir, search)
        os.makedirs(output_folder, exist_ok=True)
        if option == "JSON":
            file_path = os.path.join(output_folder, f"{search}.json")
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
            return True
        elif option == "CSV":
            self.write_csv(data, search, output_folder)
        return True