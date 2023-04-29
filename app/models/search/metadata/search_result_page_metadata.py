"""Summary: Search Result Page Metadata Model

A search result page metadata model used to convert a search result page metadata document into a user metadata object
"""
from datetime import datetime


class SearchResultPageMetadata:
    """
    A class to represent the metadata for a search result page object

    Attributes
    ----------
    created_date : datetime
        The date and time the search result page object was created
    user_id : str
        The ID of the user who made the search
    query : str
        The search query entered by the user
    """
    def __init__(self, metadata_dict: dict) -> None:
        self.created_date = datetime.strptime(metadata_dict['created_date'], '%Y-%m-%d %H:%M:%S')
        self.user_id = metadata_dict['user_id']
        self.query = metadata_dict['query']
