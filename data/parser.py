import re
import emoji
import json

class DataHandler:
    
    @staticmethod
    def remove_emojis(text: str) -> str:
        text_demojized = emoji.demojize(text)
        text_clean = re.sub(r':\w+:', '', text_demojized)
        return text_clean
    
    @staticmethod
    def is_promoted(post: dict) -> bool:
        promoted: bool = None
        try:
            post.get('promoted').get('text').get('textSpans')[0].get('text')
            promoted = False
        except AttributeError:
            if post.get('promoted').get('icon').get('name') == 'tick':
                promoted = True
        return promoted
    
    @staticmethod
    def is_top_rated_seller(post: dict) -> bool:
        is_top_rated_seller: bool | None = None
        try:
            post.get("listingPrice").get("topRatedSeller").get("textSpans")[0].get("text")
            is_top_rated_seller = True
        except AttributeError:
            is_top_rated_seller = False
        return is_top_rated_seller
            
    @staticmethod    
    def RGM_data(data: dict) -> dict:
        parsed_data = {}
        for section in data.get("sections"):
            for dataitem in section.get("dataItems"):
                label = dataitem.get("header").get("accessibilityText")
                if parsed_data.get(label) is None:
                    parsed_data[label] = dataitem.get("value").get("accessibilityText")
        return parsed_data
    
    
    def SRM_data(self, data: dict) -> list:
        parsed_data = []
        for post in data.get("results"):
            post_data = {
                "title": self.remove_emojis(post.get("listing").get("title").get("textSpans")[0].get("text")),
                "avgsalesprice": post.get("avgsalesprice").get('avgsalesprice').get('textSpans')[0].get('text'),
                "avgshipping": post.get('avgshipping').get("avgshipping").get('textSpans')[0].get('text'),
                "freeshipping": post.get('avgshipping').get('freeshipping').get('textSpans')[0].get('text'),
                "itemssold": post.get('itemssold').get('textSpans')[0].get('text'),
                "totalsales": post.get('totalsales').get('textSpans')[0].get('text'),
                "bids": post.get('bids').get('textSpans')[0].get('text'),
                "datelastsold": post.get('datelastsold').get('textSpans')[0].get('text')
            }
            parsed_data.append(post_data)
        return parsed_data
    
    def ASRM_data(self, data: dict) -> list:
        parsed_data = []
        for post in data.get("results"):
            post_data = {
                "title": self.remove_emojis(post.get("listing").get("title").get("textSpans")[0].get("text")),
                "listingPrice": post.get("listingPrice").get("listingPrice").get("textSpans")[0].get("text"),
                "listingShipping": post.get("listingPrice").get("listingShipping").get("textSpans")[0].get("text"),
                "topRatedSeller": self.is_top_rated_seller(post),
                "bids": post.get('bids').get('textSpans')[0].get('text'),
                "watchers": post.get('watchers').get('textSpans')[0].get('text'),
                "promoted": self.is_promoted(post),
                "startDate": post.get('startDate').get('textSpans')[0].get('text')
            }
            parsed_data.append(post_data)
        return parsed_data
    
        
    def parse_data(self, post_mode, data: list):
        parsed_data = {}
        for json_data in data:
            data_type = json_data.get('__type')
            if data_type == 'ResearchAggregateModule':
                    parsed_data['product'] = self.RGM_data(json_data)
            else:
                if post_mode == "SOLD":
                    if data_type == 'SearchResultsModule':
                        parsed_data['listings'] = self.SRM_data(json_data)
                elif post_mode == "ACTIVE":
                    if data_type == 'ActiveSearchResultsModule':
                        parsed_data['listings'] = self.ASRM_data(json_data)
        return parsed_data         
        
    def parse_response(self, response: str):
        json_objects =response.split('\n\n')
        parsed_objects = [json.loads(obj) for obj in json_objects if obj]
        return self.parse_data(parsed_objects)