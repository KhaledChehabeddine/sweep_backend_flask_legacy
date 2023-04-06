"""Summary: Home Sub Feature Model

A home sub feature model used to convert a home sub feature document into a home sub feature object
"""

from typing import List
from app.models.home.home_sub_feature_item import HomeSubFeatureItem


class HomeSubFeature:
    """
    A class to represent a home sub feature model


    Attributes
    ----------
    home_sub_feature_items : List[HomeSubFeatureItem]
        Home sub feature's items
    _id : str
        Home sub feature's id
    subtitle : str
        Home sub feature's subtitle
    title : str
        Home sub feature's title

    Methods
    -------
    get_home_sub_feature_items() : List[HomeSubFeatureItem]
        Returns the home sub feature's items
    set_home_sub_feature_items(home_sub_feature_items) : None
        Sets the home sub feature's items
    get_id() : str
        Returns the home sub feature's id
    set_id(_id) : None
        Sets the home sub feature's id
    get_subtitle() : str
        Returns the home sub feature's sub_title
    set_subtitle(subtitle) : None
        Sets the home sub feature's sub_title
    get_title() : str
        Returns the home sub feature's title
    set_title(title) : None
        Sets the home sub feature's title
    """

    def __init__(self, home_sub_feature_document: dict) -> None:
        self.home_sub_feature_items = home_sub_feature_document['home_sub_feature_items']
        self._id = home_sub_feature_document['_id']
        self.subtitle = home_sub_feature_document['subtitle']
        self.title = home_sub_feature_document['title']

    def get_home_sub_feature_items(self) -> List[HomeSubFeatureItem]:
        """
        :return: Home sub feature's items
        """
        return self.home_sub_feature_items

    def set_home_sub_feature_items(self, home_sub_feature_items: List[HomeSubFeatureItem]) -> None:
        """
        :param home_sub_feature_items: Home sub feature's items
        """
        self.home_sub_feature_items = home_sub_feature_items

    def get_id(self) -> str:
        """
        :return: Home sub feature's id
        """
        return self._id

    def set_id(self, _id: str) -> None:
        """
        :param _id: Home sub feature's id
        """
        self._id = _id

    def get_subtitle(self) -> str:
        """
        :return: Home sub feature's subtitle
        """
        return self.subtitle

    def set_subtitle(self, subtitle: str) -> None:
        """
        :param subtitle: Home sub feature's subtitle
        """
        self.subtitle = subtitle

    def get_title(self) -> str:
        """
        :return: Home sub feature's title
        """
        return self.title

    def set_title(self, title: str) -> None:
        """
        :param title: Home sub feature's title
        """
        self.title = title