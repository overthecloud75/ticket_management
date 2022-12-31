from utils import Iptables, Page
from .db import BasicModel

iptables = Iptables()

class Firewall(BasicModel):
    def __init__(self, model='firewall_policies'):
        super().__init__(model=model)

    def get(self, page=1):
        data_list = iptables.get_rules()
        get_page = Page(page)
        paging, data_list = get_page.paginate(data_list)
        return paging, data_list

    def post(self, request_data={}):
        ip = request_data['ip']
        ip_class = request_data['ip_class']
        protocol = request_data['protocol']
        port = request_data['port']
        block = request_data['block'] 
        firewall_policy = self.collection.find_one(request_data)
        if not firewall_policy:
            iptables.post_rule(ip, ip_class=ip_class, protocol=protocol, port=port, block=block)
            self.collection.insert_one(request_data)
            self.db['tickets'].update_many({'ip': ip}, {'$set': {'fix': '차단', 'fix_timestamp': request_data['timestamp']}})

    def delete(self, request_data={}):
        ip = request_data['ip']
        ip_class = request_data['ip_class']
        protocol = request_data['protocol']
        port = request_data['port']
        block = request_data['block']
        firewall_policy = self.collection.find_one(request_data)
        iptables.delete_rule(ip, ip_class=ip_class, protocol=protocol, port=port, block=block)
        if firewall_policy:
            self.collection.delete_one(request_data)
            self.db['tickets'].update_many({'ip': ip}, {'$set': {'fix': '해제', 'fix_timestamp': ''}})
