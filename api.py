import time
import requests
import re
import os
import json
import pynput
from pynput import keyboard
from pynput.keyboard import Key, Listener
from collections import defaultdict
from TeraPeaksAPI.browser.browser import BrowserInstance
from TeraPeaksAPI.data.parser import DataHandler
from TeraPeaksAPI.args.parser import Checker, ArgParser, CATEGORIES, SORTING_OPTIONS
from TeraPeaksAPI.dump.output import Dumper, DEFAULT_DIRECTORY

PARENT_DIR = os.path.dirname(os.path.abspath(__file__)) 

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.max_requests_per_second = max_requests_per_second
        self.request_counts = defaultdict(int)
        self.last_request_times = defaultdict(float)
        self.file_path = 'last_request_times.json'
        
    def load_last_request_times(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return defaultdict(float)

    def save_last_request_times(self):
        with open(self.file_path, 'w') as file:
            json.dump(dict(self.last_request_times), file)

    def wait_if_needed(self):
        current_time = time.time()
        if self.request_counts["request_last_sent"] >= self.max_requests_per_second:
            time_since_last_request = current_time - self.last_request_times["request_last_sent"]
            if time_since_last_request < 1:
                time.sleep(1 - time_since_last_request)
        self.request_counts["request_last_sent"] += 1
        self.last_request_times["request_last_sent"] = current_time
        self.save_last_request_times()

class API:
    HEADERS = json.load(open(os.path.join(PARENT_DIR, 'headers.json'), 'r'))
    
    def __init__(self):
        self.data_parser = DataHandler()
        self.arg_checker, self.arg_parser = None, None
        self.session = requests.Session()
        self.browser = BrowserInstance()
        self.rate_limiter = RateLimiter(1)
        self.post_mode = None
        self.last_url = None
        self.dumper = Dumper()
        
        self.session.headers = self.HEADERS
    
    def next_page(self, url: str, search: str, output_format: str, output_folder: str):
        if self.last_url:
            match = re.findall(r'offset=\d+', url)
            if match:
                unit = re.findall(r'\d+', match[0])[0]
                new_url = re.sub(r'offset=\d+', f'offset={unit + 50}', url)
                self.handle_data_retrieval(new_url, search, output_format, output_folder)
        else:
            raise ValueError("No search has yet been typed. You must do a search first before you can go to the next page of the results")
            
    def handle_data_retrieval(self, url: str, search: str, post_status, output_format: str, output_folder: str):
        self.rate_limiter.wait_if_needed()
        response = self.session.get(url)   
        self.last_url = url   
        data = self.data_parser.parse_response(post_status, response.text) 
        self.dumper.dump_data(data, search, output_format, output_folder) 
        
    def search(self, 
               search: str, 
               category: str, 
               post_status: str = "SOLD", 
               sorting_option: str = None, 
               sorting_order: str = "HL", 
               day_range: int | str = 90,
               start_date: str | None = None,
               end_date: str | None = None,
               output_folder: str = DEFAULT_DIRECTORY,
               output_format: str = "JSON"
               ):
        self.checker = Checker(search, category, post_status, sorting_option, sorting_order, day_range, start_date, end_date, output_folder, output_format)
        if self.checker.passed: 
            self.session = self.browser.get_fresh_cookies("https://www.ebay.com/sh/research?marketplace=EBAY-US&tabName=SOLD", self.session)
            arg_parser = ArgParser()
            search_keyword = re.sub("\s", "+", search)
            endDate, startDate = arg_parser.return_dates(day_range, start_date, end_date)
            sorting_option = arg_parser.choose_sorting(sorting_option) if sorting_option is not None else "" 
            url = f"https://www.ebay.com/sh/research/api/search?marketplace=EBAY-US&keywords={search_keyword}&dayRange={day_range}&endDate={endDate}&startDate={startDate}&categoryId={arg_parser.choose_category(category)}&offset=0&limit=50{sorting_option}&tabName={post_status}&tz=America%2FNew_York&modules=aggregates&modules=searchResults&modules=resultsHeader"
            self.handle_data_retrieval(url, search, post_status, output_format, output_folder)
 
api = API()    
pressed_keys = []
            
def search_wrapper():
    search = input("Type in the object you want to search: ")
    category = input(f"Type in the category you want to search for {search} in\nOptions are  {', '.join(list(CATEGORIES.keys()))}\n")
    post_status = input("Enter the type of posts you want to see\nOptions: \'SOLD\' or \'ACTIVE\'\n(Enter \'SKIP\' to skip the next filters, Default is \'SOLD\')\n")
    if post_status == "SKIP":
        post_status = "SOLD"
        api.search(search, category)
        return 
    sorting_options = ", ".join(list(SORTING_OPTIONS.get(post_status).keys()))
    sorting_option = input(f"Enter a sorting category if you want to sort the posts by a specific category.\nThe default is None, in ascending order.\nThe options are {sorting_options}\n(Enter \'SKIP\' to skip the next filters.)\n")
    if sorting_option == "SKIP":
        sorting_option = None
        api.search(search, category, post_status)
        return
    sorting_order = input("Enter the sorting order you want.\n\'HL\' for Descending Order\n\'LH\' for Ascending Order\nThe default option is \'HL\'\n(Enter \'SKIP\' to skip the next filters.)\n")
    if sorting_order == "SKIP":
        sorting_order == "HL"
        api.search(search, category, post_status, sorting_option)
        return
    day_range = input(f"Enter the range of days you want the data to span out from.\nThe options are {', '.join([7, 30, 90, 180, 365, 730, 1095, 'CUSTOM'])}\nIf you select \'CUSTOM\', then you have to enter the dates you want the data to span from. The default is 90\n(Enter \'SKIP\' to skip the next filters.)\n")
    if day_range == "SKIP":
        day_range = 90
        api.search(search, category, post_status, sorting_option, sorting_order)
        return
    if day_range == "CUSTOM":
        start_date = input("Enter the starting date you want to start the program from, in the format: YYYY-MM-DD\n")
        end_date = input("Enter the last date you want the search on, in the format: YYYY-MM-DD\n")
    output_folder = input("Enter the folder you want the data to be dumped to: The default folder is in the root directory of the project\n(Enter \'SKIP\' to skip the rest of the filters.)\n")
    if output_folder == "SKIP":
        output_folder = DEFAULT_DIRECTORY
        if day_range == "CUSTOM":
            api.search(search, category, post_status, sorting_option, day_range, start_date, end_date)
            return
        else:
            api.search(search, category, post_status, sorting_option, sorting_order, day_range)
            return
    output_format = input("Enter the output file format you want the data to be dumped in.\nThe options are \'JSON\' or \'CSV\'.\n The default is \'JSON\'. (Enter \'SKIP\' to skip this feature)\n")
    if output_format == "SKIP":
        output_format = "JSON"
        if day_range != "CUSTOM":
            api.search(search, category, post_status, sorting_option, sorting_order, day_range, output_folder)
            return
        else:
            api.search(search, category, post_status, sorting_option, sorting_order, day_range, start_date, end_date, output_folder)
            return
    if day_range != "CUSTOM":
        api.search(search, category, post_status, sorting_option, sorting_order, day_range, output_folder, output_format)
        return
    else:
        api.search(search, category, post_status, sorting_option, sorting_order, day_range, start_date, end_date, output_folder, output_format)
        return 
                        
def main():   
    print("Booting TeraPeaks Scraper...")                
    key_combinations = {
    (keyboard.Key.ctrl, keyboard.KeyCode(char='s')): search_wrapper,
    (keyboard.Key.ctrl, keyboard.KeyCode(char='n')): api.next_page,
    (keyboard.Key.ctrl, keyboard.KeyCode(char='l')): api.browser.launch_browser_for_login
    }
    def on_press(key):
        # Append the pressed key to the list
        pressed_keys.append(key)
        # Check if the sequence of keys pressed matches any of the key combinations
        for combo, func in key_combinations.items():
            if pressed_keys[-len(combo):] == list(combo):
                func() # Execute the corresponding function
                pressed_keys.clear() # Clear the sequence for the next key press
                return False # Stop the listener

    def on_release(key):
        # Check if the user has pressed Ctrl+Q to quit
        if key == keyboard.Key.ctrl and keyboard.Key.q == key:
            # Stop the listener 
            pressed_keys.clear()
            return False
    
    with Listener(on_press=on_press, on_release=on_release) as listener:    
        while True:
                print("TeraPeaks Scraper Booted!\nQuick Guide on how to use\nPress CTRL + S to search for an item\nPress CTRL + N to get the next page of data for your previous search\nPress CTRL + L to login in Ebay. You have to do this if this is your first search or else the search will not work.")
            # Keep the listener active in the main loop
                listener.join()

                # Check if the user has pressed Ctrl+Q to quit
                if keyboard.Key.ctrl == pynput.keyboard.controller.Controller().read_key() and keyboard.Key.q == pynput.keyboard.controller.Controller().read_key():
                    print('\nExiting...')
                    break

if __name__ == "__main__":
    main()
        