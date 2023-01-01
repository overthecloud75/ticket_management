# title_list

FIREWALL_COLUMN_HEADER = [
    {
        'accessor': 'name',
        'header': 'Name',
    },
    {
        'accessor': 'ip',
        'header': 'ip',
    },
    {
        'accessor': 'ip_class',
        'header': 'Class',
    },
    {
        'accessor': 'protocol',
        'header': 'Protocol',
    },
    {
        'accessor': 'port',
        'header': 'Port',
    },
    {
        'accessor': 'block',
        'header': 'BLOCK',
    },
    {
        'accessor': 'message',
        'header': 'Message',
    },
]

# title_list

TICKET_COLUMN_HEADER = [
    {
        'accessor': 'timestamp',
        'header': 'Occurance',
    },
    {
        'accessor': 'ticket',
        'header': 'Ticket',
    },
    {
        'accessor': 'site',
        'header': 'Site',
    },
    {
        'accessor': 'ip',
        'header': 'Attacker IP',
    },
    {
        'accessor': 'geo_ip',
        'header': 'Country',
    },
    {
        'accessor': 'attack_no',
        'header': 'Attack NO',
    },
    {
        'accessor': 'attack_w',
        'header': 'Attack FRE',
    },
    {
        'accessor': 'origin',
        'header': 'Origin'
    },
    {
        'accessor': 'fix',
        'header': 'Action'
    },
    {
        'accessor': 'fix_timestamp',
        'header': 'Action Time'
    }
]

# access_log
'''
    ip: '207.46.13.54',
    timestamp: ISODate("2022-10-10T10:33:06.000Z"),
    body: '-',
    geo_ip: 'US',
    host: 'mcc.smsecure-service.com',
    http_version: 'HTTP/1.1',
    method: 'GET',
    referer: '-',
    size: 186,
    request_time: '0.000',
    status: 403,
    url: '/firewall',
    user_agent: 'Mozilla/5.0,
    
'''

ACCESS_COLUMN_HEADER = [
    {
        'accessor': 'timestamp',
        'header': 'Occurance',
    },
    {
        'accessor': 'ip',
        'header': 'Attacker IP',
    },
    {
        'accessor': 'geo_ip',
        'header': 'Country',
    },
    {
        'accessor': 'status',
        'header': 'Status',
    },
    {
        'accessor': 'host',
        'header': 'Host',
    },
    {
        'accessor': 'http_version',
        'header': 'HTTP Version',
    },
    {
        'accessor': 'scheme',
        'header': 'Scheme'
    },
    {
        'accessor': 'method',
        'header': 'Method'
    },
    {
        'accessor': 'url',
        'header': 'Url'
    },
    {
        'accessor': 'user_agent',
        'header': 'User Agent'
    },
    {
        'accessor': 'body',
        'header': 'Body'
    },
    {
        'accessor': 'request_time',
        'header': 'Time'
    },
]

# error_log
'''
    _id: ObjectId("639edb6cf7119ed53db52020"),
    ip: '45.134.144.65',
    timestamp: ISODate("2022-12-18T18:15:45.000Z"),
    http_version: 'HTTP/1.1',
    level: 'error',
    method: 'GET',
    reason: 'open() /var/www/ados/3c625c27b4da33d3d5c12e8d02104755/js/login.js failed (2: No such file or directory)',
    server: 'adoscompany.com,',
    url: '///3c625c27b4da33d3d5c12e8d02104755/js/login.js'
'''

ERROR_COLUMN_HEADER = [
    {
        'accessor': 'timestamp',
        'header': 'Occurance',
    },
    {
        'accessor': 'ip',
        'header': 'Attacker IP',
    },
    {
        'accessor': 'geo_ip',
        'header': 'Country',
    },
    {
        'accessor': 'server',
        'header': 'Server',
    },
    {
        'accessor': 'host',
        'header': 'Host',
    },
    {
        'accessor': 'http_version',
        'header': 'HTTP Version',
    },
    {
        'accessor': 'method',
        'header': 'Method'
    },
    {
        'accessor': 'url',
        'header': 'Url'
    },
    {
        'accessor': 'msg',
        'header': 'Message'
    }
]