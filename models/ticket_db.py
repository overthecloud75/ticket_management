import logging

from utils import Page
from .db import BasicModel

class TicketModel(BasicModel):

    def __init__(self, model='tickets', need_notice=False):
        super().__init__(model=model)

    def get(self, page=1):
        data_list = self.collection.find().sort('timestamp', -1)
        get_page = Page(page)
        paging, data_list = get_page.paginate(data_list, collection=self.collection)
        return paging, data_list

    def post(self, request_data={}):
        self.post_by_id(request_data)



   