from datetime import datetime, timedelta
import csv
import os 
import asyncio

from .db import BasicModel
from .mail import send_email 
from .bot import bot_send_message
from configs import BASE_DIR, EVIDENCE_DIR, CSV_FILE_NAME, USE_NOTICE_EMAIL, ACCESS_LOG_KEYS, AUTH_LOG_KEYS, USE_BOT
from configs import MONITORING_SITE, WEB_SITE_IP, FIREWALL_SITE, MANUAL_SITE, ANALYZE_SITE

class LogModel(BasicModel):
    def __init__(self, model='fail2ban_logs', need_notice=False):
        super().__init__(model=model)

        self.need_notice = need_notice

    def _get_ticket(self, log):
        timestamp = log['timestamp']
        str_timestamp = timestamp.strftime('%y%m%d')
        s_timestamp = datetime(timestamp.year, timestamp.month, timestamp.day)
        f_timestamp = s_timestamp + timedelta(days=1)
        ticket_no = 0
        results = self.db['fail2ban_logs'].find({'timestamp' : {'$gte': s_timestamp, '$lt': f_timestamp}})
        for result in results:
            ticket_no = ticket_no + 1
        ticket_no = str(ticket_no)
        if len(ticket_no) == 1:
            ticket_no = 'TCK' + str_timestamp + '-000' + ticket_no
        elif len(ticket_no) == 2:
            ticket_no = 'TCK' + str_timestamp + '-00' + ticket_no
        elif len(ticket_no) == 3:
            ticket_no = 'TCK' + str_timestamp + '-0' + ticket_no
        else:
            ticket_no = 'TCK' + str_timestamp + '-' + ticket_no
        return ticket_no

    def _write_csv_and_get_attack_no(self, results, wr, site, keys):
        '''
            1. write result to csv
            2. get site, attack_no 
        '''
        attack_no = 0 
        wr.writerow(keys)
        for i, result in enumerate(results):
            if i == 0 and 'host' in result:
                site = result['host']
            result_list = []
            for key in keys:
                if key == 'timestamp':
                    result_list.append(result[key].strftime('%y-%m-%d %H:%M:%S'))
                else:
                    if key in result:
                        result_list.append(result[key])
                    else:
                        result_list.append('-')
            wr.writerow(result_list)
            attack_no = attack_no + 1
        return site, attack_no

    def _post_ticket(self, log, ticket_no, site, attack_no):

        ip = log['ip']
        ticket_info = log
        ticket_info['model'] = self.model
        ticket_info['ticket'] = ticket_no
        ticket_info['site'] = site
        ticket_info['attack_no'] = attack_no
        ticket_info['str_ip'] = self.make_str_ip(ip)
        try:
            ticket_info['attack_w'] = self.db['tickets'].count_documents({'ip': ip}) + 1
        except Exception as e:
            self.logger.error('attack_w is failed: {}'.format(e))
        self.db['tickets'].insert_one(ticket_info)

    def _get_subject(self, log):
        '''
            1. get ticket_no 
            2. make evidence file
            3. get site, attack_no 
            4. save ticket info 
        '''
        ticket_no = self._get_ticket(log)
           
        subject_main = '[?????? ??????]'
        site = WEB_SITE_IP

        csv_file_name = os.path.join(BASE_DIR, EVIDENCE_DIR, ticket_no + '_' + CSV_FILE_NAME)

        with open(csv_file_name, 'w', encoding='utf-8', newline='') as csv_file:
            wr = csv.writer(csv_file)
            if 'origin' in log:
                if log['origin'] == '[modsecurity]':
                    subject_main = '[{} : {} ?????? ??????] '.format(ticket_no, 'WEB')
                    results = self.db['access_logs'].find({'ip': log['ip']}).sort('timestamp', -1)
                    site, attack_no = self._write_csv_and_get_attack_no(results, wr, site, ACCESS_LOG_KEYS)
                else:
                    subject_main = '[{} : {} ?????? ??????] '.format(ticket_no, 'AUTH')  
                    results = self.db['auth_logs'].find({'ip': log['ip']}).sort('timestamp', -1)
                    site, attack_no = self._write_csv_and_get_attack_no(results, wr, site, AUTH_LOG_KEYS)

        subject = subject_main + 'site: ' + site + ', ????????? ip: ' + log['ip']

        self._post_ticket(log, ticket_no, site, attack_no)
        return subject, site, attack_no, csv_file_name

    def _notice_email(self, log, signature=''):
        # check recipents  
        security_users = self.db['security_users'].find()
        email_list = []
        for user in security_users:
            email_list.append(user['email'])
        if not email_list:
            email_list.append(DEFAULT_USER)
        
        if USE_NOTICE_EMAIL:
            # https://techexpert.tips/ko/python-ko/?????????-office-365???-????????????-?????????-?????????
            # https://nowonbun.tistory.com/684 (?????????)

            subject, site, attack_no, csv_file_name = self._get_subject(log)
            str_time = log['timestamp'].strftime('%y-%m-%d %H:%M:%S')

            body = '\n' \
                ' ???????????????. ?????? ?????? ???????????????. {} ?????? ????????? ????????? ?????????????????????.\n' \
                '\n' \
                '- site         : {} \n' \
                '- time         : {} \n' \
                '- attacker ip  : {} \n' \
                '- attack num   : {} \n' \
                '- country      : {} \n' \
                '\n' \
                '????????? site ?????? ????????? ??? ?????? ????????? ???????????????. \n' \
                '{} ????????? ?????? ?????? ??? ??????????????? ????????? ???????????????. \n' \
                ' -> {} \n' \
                '\n' \
                '????????? ????????? ????????? ?????? ????????? site ??? ??????????????? ????????? ?????????. \n' \
                ' -> {} \n' \
                '\n' \
                'Manual: {} \n' \
                '\n' \
                'Analyze the attacker ip \n' \
                ' -> {} \n' \
                .format(site, site, str_time, log['ip'], attack_no, log['geo_ip'], CSV_FILE_NAME, MONITORING_SITE, FIREWALL_SITE, MANUAL_SITE, ANALYZE_SITE + log['ip'])

            self.logger.info('email: {}'.format(subject))
            sent = send_email(email_list=email_list, subject=subject, body=body, attached_file=csv_file_name)
            if USE_BOT:
                try:
                    asyncio.run(bot_send_message(msg=body))
                except Exception as e:
                    self.logger.error('bot error: {}'.format(e))
            return sent 
        else:
            self.logger.error('email failed')
            return False
    
    def _post(self, log):
        if 'ip' in log:
            if type(log['timestamp']) == str:
                log['timestamp'] = datetime.strptime(log['timestamp'], '%Y-%m-%d:%H:%M:%S')
            if self.need_notice:
                if 'url' in log:
                    result = self.collection.find_one({'timestamp': log['timestamp'], 'ip': log['ip'], 'url': log['url']})
                    if not result:
                        self.collection.update_one({'timestamp': log['timestamp'], 'ip': log['ip'], 'url': log['url']}, {'$set': log}, upsert=True)
                        self._notice_email(log)
                else:
                    result = self.collection.find_one({'timestamp': log['timestamp'], 'ip': log['ip']})
                    if not result:
                        self.collection.update_one({'timestamp': log['timestamp'], 'ip': log['ip']}, {'$set': log}, upsert=True)
                        self._notice_email(log)
            else:
                if 'url' in log:
                    self.collection.update_one({'timestamp': log['timestamp'], 'ip': log['ip'], 'url': log['url']}, {'$set': log}, upsert=True)
                else:
                    self.collection.update_one({'timestamp': log['timestamp'], 'ip': log['ip']}, {'$set': log}, upsert=True)

    def many_post(self, log_list):
        log_list = reversed(log_list)
        for log in log_list:
            self.logger.info('{}: {}'.format(self.model, log))
            self._post(log)

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

