# import iptc
import os
import ipaddress
import logging

from configs import FW_CHAINS, DPORT_TO_PORT

'''
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT
-N RH-Firewall-1-INPUT
-N f2b-modesecurity
-N f2b-sshd
-A INPUT -p tcp -m multiport --dports 80,443 -j f2b-modesecurity
-A INPUT -p tcp -m multiport --dports 22 -j f2b-sshd
-A f2b-modesecurity -j RETURN
-A f2b-sshd -s 184.82.198.131/32 -j REJECT --reject-with icmp-port-unreachable
-A f2b-sshd -s 68.183.83.242/32 -j REJECT --reject-with icmp-port-unreachable
-A f2b-sshd -j RETURN
'''

class Iptables:
    def __init__(self):
        '''
            when start, if chain in config not exist in chains, enroll the chain.  
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.info('Iptables Start')

        self.enroll_chains()

    # https://codefather.tech/blog/validate-ip-address-python/
    def _validate_ip_address(self, address):
        result = True
        try:
            ip = ipaddress.ip_address(address)
            self.logger.info('IP address {} is valid. The object returned is {}'.format(address, ip))
        except ValueError:
            self.logger.info('IP address {} is not valid'.format(address)) 
            result = False
        return result

    # https://gist.github.com/zhangchunlin/1513742/89a38864b41e002e4a6600a946c076ad0fe6f7bb
    def _do_cmd(self, cmd):
        stream = os.popen(cmd)
        output = stream.read()
        return output

    def _enroll_chain(self, chain):
        cmd = 'iptables -N {chain}'.format(chain=chain)
        self._do_cmd(cmd)

    def _target_role(self, port, chain, protocol='tcp'):
        if port == 'all':
            cmd = 'iptables -A INPUT -p {protocol} -j {chain}'.format(protocol=protocol, chain=chain)
            dports = 'all'
        else:
            if port == 'ssh': 
                dports = '22'
            else:
                dports = '80,443'
            cmd = 'iptables -A INPUT -p {protocol} -m multiport --dports {dports} -j {chain}'.format(protocol=protocol, dports=dports, chain=chain)
        self._do_cmd(cmd)

    def enroll_chains(self):
        # chains = iptc.easy.get_chains('filter')
        chains, rules, tables = self._get_chains()
        for port, chain in FW_CHAINS.items():
            if not chain in chains:
                self._enroll_chain(chain)
                self._target_role(port, chain)

    def post_rule(self, ip, ip_class='/32', protocol='tcp', port='all', block='DROP'):
        chain = FW_CHAINS[port]
        if self._validate_ip_address(ip):
            if block=='ACCEPT':
                cmd = 'iptables -A {chain} -s {ip_type} -j {block}'.format(ip_type=ip + ip_class, block=block, chain=chain)
            elif block=='REJECT':
                cmd = 'iptables -A {chain} -s {ip_type} -j {block} --reject-with icmp-port-unreachable'.format(ip_type=ip + ip_class, block=block, chain=chain)
            else:
                cmd = 'iptables -A {chain} -s {ip_type} -j {block}'.format(ip_type=ip + ip_class, block='DROP', chain=chain)
            self._do_cmd(cmd)

    def delete_rule(self, ip, ip_class='/32', protocol='tcp', port='all', block='DROP'):
        chain = FW_CHAINS[port]
        if self._validate_ip_address(ip):
            if block=='ACCEPT':
                cmd = 'iptables -D {chain} -s {ip_type} -j {block}'.format(ip_type=ip + ip_class, block=block, chain=chain)
            elif block=='REJECT':
                cmd = 'iptables -D {chain} -s {ip_type} -j {block} --reject-with icmp-port-unreachable'.format(ip_type=ip + ip_class, block=block, chain=chain)
            else:
                cmd = 'iptables -D {chain} -s {ip_type} -j {block}'.format(ip_type=ip + ip_class, block='DROP', chain=chain)
            self._do_cmd(cmd)

    def get_rules(self):
        target_def = {}
        iptables = {}
        filter_list = []

        _, rules, tables = self._get_chains()
        for rule in rules:
            target_def[rule[-1]] = {}
            target_def[rule[-1]]['direction'] = rule[1]
            target_def[rule[-1]]['protocol'] = rule[3]
            if 'multiport' in rule:
                target_def[rule[-1]]['port'] = rule[7]
            else:
                target_def[rule[-1]]['port'] = 'all'
            
        for table in tables:
            filter = {}
            filter['name'] = table[1]
            filter['message'] =''
            filter['ip'] = table[3].split('/')[0]
            filter['ip_class'] = '/' + table[3].split('/')[1]
            filter['protocol'] = target_def[table[1]]['protocol']
            filter['port'] = target_def[table[1]]['port']
            filter['block'] = table[-1]

            filter_list.append(filter)

        '''chains = iptc.easy.get_chains('filter')
        
        for chain in chains:
            filters = iptc.easy.dump_chain('filter', chain)
            if chain == 'INPUT':
                for filter in filters:
                    target_def[filter['target']] = filter
            elif chain in target_def:
                for filter in filters:
                    if 'src' in filter: 
                        filter['name'] = chain
                        filter['message'] = ''
                        filter['ip'] = filter['src'].split('/')[0]
                        filter['ip_class'] = '/' + filter['src'].split('/')[1]
                        filter['protocol'] = target_def[chain]['protocol']
                        if 'multiport' in target_def[chain]:
                            filter['port'] = DPORT_TO_PORT[target_def[chain]['multiport']['dports']]
                        else:
                            filter['port'] = 'all'
                        del filter['counters']
                        if 'REJECT' in filter['target']:
                            filter['block'] = 'REJECT'
                            filter['message'] = filter['target']['REJECT']['reject-with']
                        elif 'ACCEPT' in filter['target']:
                            filter['block'] = 'ACCEPT'
                        elif 'DROP' in filter['target']:
                            filter['block'] = 'DROP'
                        filter_list.append(filter)'''
        return filter_list

    def _get_rules(self):
        target_def = {}
        iptables = {}
        filter_list = []
        
        chains = self._get_chains()

    def _get_chains(self):
        rule_list = self._do_cmd('iptables -S').split('\n')
        
        chain_list = []
        for port, chain in FW_CHAINS.items():
            chain_list.append(chain)

        chains = []
        rules = []
        tables = []
        for rule in rule_list:
            if rule.startswith('-N'):
                result_list = rule.split(' ')
                if len(result_list) > 1 and result_list[1] in chain_list:
                    chains.append(result_list[1])
            elif rule.startswith('-A'):
                result_list = rule.split(' ')
                if len(result_list) > 1:
                    if result_list[1] in chain_list:
                        tables.append(result_list)
                    elif result_list[-1] in chain_list:
                        rules.append(result_list)
        return chains, rules, tables 


