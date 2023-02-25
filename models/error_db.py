from utils import Page
from .db import BasicModel

class ErrorModel(BasicModel):

    def __init__(self, model='error_logs', need_notice=False):
        super().__init__(model=model)

    def get(self, page=1):
        data_list = self.collection.find().sort('timestamp', -1)
        get_page = Page(page)
        paging, data_list = get_page.paginate(data_list, collection=self.collection)
        return paging, data_list

    def get_by_ticket(self, ticket, page=1):
        result = self.db['tickets'].find_one({'ticket': ticket})
        if result:
            data_list = self._get_by_ip(result['ip'])
        else:
            data_list = []
        get_page = Page(page)
        paging, data_list = get_page.paginate(data_list, collection=self.collection)
        return paging, data_list
