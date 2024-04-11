import time
import requests
import re
import os
import json
from collections import defaultdict
from TeraPeaksAPI.browser.browser import BrowserInstance
from data.parser import DataHandler
from args.parser import Checker, ArgParser

PARENT_DIR = os.path.dirname(os.path.abspath(__file__)) 

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.max_requests_per_second = max_requests_per_second
        self.request_counts = defaultdict(int)
        self.last_request_times = defaultdict(float)

    def wait_if_needed(self, provider_name):
        current_time = time.time()
        if self.request_counts[provider_name] >= self.max_requests_per_second:
            time_since_last_request = current_time - self.last_request_times[provider_name]
            if time_since_last_request < 1:
                time.sleep(1 - time_since_last_request)
        self.request_counts[provider_name] += 1
        self.last_request_times[provider_name] = current_time

class TP_API:
    HEADERS = json.load(os.path.join(PARENT_DIR, 'headers.json'))
    
    def __init__(self):
        self.data_parser = DataHandler()
        self.arg_checker, self.arg_parser = None, None
        self.session = requests.Session()
        self.session = BrowserInstance().get_fresh_cookies("https://www.ebay.com/sh/research?marketplace=EBAY-US&tabName=SOLD", self.session)
        self.post_mode = None
        
        self.session.headers = self.HEADERS
        
    def search(self, 
               search: str, 
               category: str, 
               post_status: str = "SOLD", 
               sorting_option: str = "-itemssold", 
               sorting_order: str = "HL", 
               day_range: int | str = 90,
               start_date: str | None = None,
               end_date: str | None = None
               ):
        self.checker = Checker(search, category, post_status, sorting_option, sorting_order, day_range, start_date, end_date)
        if self.checker.passed:
            arg_parser = ArgParser()
            search_keyword = re.sub("\s", "+", search)
            endDate, startDate = arg_parser.return_dates(day_range, start_date, end_date)
            sorting_option = arg_parser.choose_sorting(sorting_option)
            url = f"https://www.ebay.com/sh/research/api/search?marketplace=EBAY-US&keywords={search_keyword}&dayRange={day_range}&endDate={endDate}&startDate={startDate}&categoryId={arg_parser.choose_category(category)}&sorting={sorting_option}&tabName={post_status}&tz=America%2FNew_York&modules=aggregates&modules=searchResults&modules=resultsHeader"
            response = self.session.get(url)      
            print(self.data_parser.parse_response(response.text))  
        
        
api = TP_API()
api.search("MacBook Pro", "apple laptops", post_status="SOLD")