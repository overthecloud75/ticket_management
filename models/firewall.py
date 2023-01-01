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
            if ip_class == '/32':
                self.db['tickets'].update_many({'ip': ip}, {'$set': {'fix': '차단', 'fix_timestamp': request_data['timestamp']}})
            elif ip_class == '/24':
                ip_list = self.range_ip_24(ip)
                for set_ip in ip_list:
                    self.db['tickets'].update_many({'ip': set_ip}, {'$set': {'fix': '차단', 'fix_timestamp': request_data['timestamp']}})
        else:
            for policy in firewall_policy:
                print(policy)
                
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
            if ip_class == '/32':
                self.db['tickets'].update_many({'ip': ip}, {'$set': {'fix': '해제', 'fix_timestamp': ''}})
            elif ip_class == '/24':
                ip_list = self.range_ip_24(ip)
                for set_ip in ip_list:
                    self.db['tickets'].update_many({'ip': set_ip}, {'$set': {'fix': '해제', 'fix_timestamp': ''}})

    def range_ip_24(self, ip):
        str_ip = self.make_str_ip(ip)
        ip_split = str_ip.split('.')
        ip_range_low = ip_split[0] + '.' + ip_split[1] + '.' + ip_split[2] + '.' + '001'
        ip_range_high = ip_split[0] + '.' + ip_split[1] + '.' + ip_split[2] + '.' + '255'
        ticket_list = self.db['tickets'].find({'str_ip': {'$gte': ip_range_low, '$lte': ip_range_high}})

        ip_list = []
        for ticket in ticket_list:
            if ticket['ip'] not in ip_list:
                ip_list.append(ticket['ip'])
        return ip_list

    def make_str_ip(self, ip):
        ip_split = ip.split('.')
        for i in range(4):
            if len(ip_split[i]) == 3:
                pass
            elif len(ip_split[i]) == 2:
                ip_split[i] = '0' + ip_split[i]
            elif len(ip_split[i]) == 1:
                ip_split[i] = '00' + ip_split[i]
        str_ip = ip_split[0] + '.' + ip_split[1] + '.' + ip_split[2] + '.' + ip_split[3]
        return str_ip
        
