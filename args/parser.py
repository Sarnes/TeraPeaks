from datetime import datetime
import os

CATEGORIES = {
        "cellphones": 9355, 
        "computers": 177, 
        "tablets": 171485, 
        "apple laptops": 111422, 
        "vinyl records": 176985,
        "video game consoles": 139971,
        "video games": 139973
        }

SORTING_OPTIONS = {
    "SOLD" : {
        "Average Sale Price": "avgsalesprice",
        "Items Sold": "itemssold",
        "Total Sales": "totalsales",
        "Bids": "bids",
        "Date Last Sold": "datelastsold"
    },
    "ACTIVE" : {
        "Listing Price": "listingPrice",
        "Bids": "bids",
        "Watchers": "watchers",
        "Promoted": "promoted",
        "Start Date": "startDate"
    }
}

class Checker:
        def __init__(self, 
                    search: str,
                    category: str, 
                    post_status: str, 
                    sorting_option: str, 
                    sorting_order: str,
                    day_range: str | int, 
                    start_date: str | None, 
                    end_date: str | None, 
                    output_folder: str, 
                    output_format: str) -> None:
            self.passed = self.check_args(search, category, post_status, sorting_option, sorting_order, day_range, start_date, end_date, output_folder, output_format)
        
        def check_args(self, 
                    search: str,
                    category: str, 
                    post_status: str | None = None, 
                    sorting_option: str | None = None, 
                    sorting_order: str | None = None,
                    day_range: str | int | None = None, 
                    start_date: str | None = None, 
                    end_date: str | None = None,
                    output_folder: str | None = None,
                    output_format: str | None = None,
                    ):
            if not type(search) == str:
                raise TypeError(f"Search paramter: {search} is not a string")
            if not post_status in ["SOLD", "ACTIVE"]:
                raise ValueError(f"Post Status must be either be \'SOLD\' or \'ACTIVE\'\n{post_status} is not a valid value") 
            if not output_format in ["JSON", "CSV"]:
                raise ValueError("This tool only outputs JSON, or CSV formats. You can either not pass in the output format variable, or you can pass in \'CSV\'")
            checks = [ self.check_category(category), self.check_sorting_option(post_status, sorting_option, sorting_order), self.check_day_range(day_range, start_date, end_date), self.check_path(output_folder)]
            if False in checks:
                return False
            return True
        
        @staticmethod
        def check_path(path):
            if not os.path.exists(path):
                raise ValueError("The path does not exist.")
            
            # Check if the path is a directory
            if not os.path.isdir(path):
                raise ValueError("The path is not a directory.")
            
            # Check if the program has write access to the directory
            if not os.access(path, os.W_OK):
                raise ValueError("The program does not have write access to the directory.")
            
            return True, "The directory is valid and accessible."
        
        def check_category(self, category: str) -> bool:
            possible_categories = list(CATEGORIES.keys())
            if type(category) != str:
                raise TypeError(f"Category type must be a string,\n and must be one of these options\n{', '.join(possible_categories)}")
            if not category in possible_categories:
                raise ValueError(f"Category must be one of these strings\n{', '.join(possible_categories)}")
            return True
        
        def check_sorting_option(self,  post_status: str, sorting_option: str, order: str) -> bool:
            if sorting_option is not None:
                options = list(SORTING_OPTIONS.get(post_status).keys())
                if not sorting_option in options:
                    raise ValueError(f"The sorting option when in the {post_status} mode, must be one of these options:\n{', '.join(options)}")
                if not order in ["HL", "LH"]:
                    raise ValueError("Order Options must be either\n \'HL' for Highest to Lowest\n\'LH\' for Lowest To Highest")
            return True
        
        def check_day_range(self, day_range, startDate, endDate):
            possible_ranges = [7, 30, 90, 180, 365, 730, 1095, "CUSTOM"]
            if not day_range in possible_ranges:
                raise ValueError(f"The day range argument, when used, must be one of the following options: \n {', '.join(possible_ranges)}")
            if day_range == "CUSTOM":
                if startDate is None or endDate is None:
                    raise ValueError("If you want to use a custom range of dates, then you must pass in the start date and the end date. In this format: YYYY-MM-DD")
            return True

class ArgParser:
    
    def convert_to_epoch_milliseconds(date_string):
        try:
            # Parse the user's input into a datetime object
            date_time = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
            # Convert the datetime object to epoch time in milliseconds
            epoch_milliseconds = int(date_time.timestamp() * 1000)
            return epoch_milliseconds
        except ValueError as VE:
            raise VE("Incorrect date format. Please enter the date in the format YYYY-MM-DD")
        
    def choose_category(self, category: str):
        category = CATEGORIES.get(category)
        if category is None:
            categories = list(CATEGORIES.keys())
            category_options = ', '.join(categories)
            raise ValueError(f"You did not pass in a valid category\n You have to pass in one of the categories below:\n{category_options}")
        return category
    
    def choose_sorting(self, 
                       post_mode: str, 
                       sorting_option: str | None = None, 
                       sorting_order: str | None = None) -> str:
        sort = ""
        sort = SORTING_OPTIONS.get(post_mode).get(sorting_option)
        if sorting_order == "HL":
            sort = "-" + sort
        sort = f"&sorting={sort}"
        return sort
      
    def return_dates(self, day_range, start_date, end_date):
        if day_range != "CUSTOM":
            now = datetime.now()
            now = int(now.timestamp() * 1000)
            past = now - (day_range * 86400000)
            return now, past
        else:
            return self.convert_to_epoch_milliseconds(start_date), self.convert_to_epoch_milliseconds(end_date)