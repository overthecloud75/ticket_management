import os
import threading
import time
from logging.config import dictConfig
from flask import Flask
from datetime import datetime

from models import LogModel, UsageModel
from utils import Analyze, get_usage
from configs import BASE_DIR, LOG_DIR, WEB_SERVER_TYPE

def read_log():

    access_model = LogModel(model='access_logs')
    error_model = LogModel(model='error_logs')
    auth_model = LogModel(model='auth_logs')
    fail2ban_model = LogModel(model='fail2ban_logs', need_notice=True)
    analyze = Analyze(interval=10)  
    while True:
        # timestamp를 refresh
        analyze.timestamp = datetime.now()
        print(analyze.timestamp)
        ban_list = analyze.read_fail2ban_log()

        if WEB_SERVER_TYPE == 'nginx':
            access_log_list = analyze.read_nginx_access_log()
            error_log_list = analyze.read_nginx_error_log()
            auth_log_list = analyze.read_auth_log()

        access_model.many_post(access_log_list)
        error_model.many_post(error_log_list)
        auth_model.many_post(auth_log_list)
        fail2ban_model.many_post(ban_list)

        analyze.previous_timestamp = analyze.timestamp

        time.sleep(300)

def read_cpu_mem():
    ps_model = UsageModel()
    while True:
        time.sleep(30)
        usage = get_usage()
        usage['timestamp'] = datetime.now()
        ps_model.post(usage)

def create_app():
    # https://flask.palletsprojects.com/en/2.0.x/logging/
    # https://wikidocs.net/81081
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(BASE_DIR, LOG_DIR, 'project.log'),
                'maxBytes': 1024 * 1024 * 5,  # 5 MB
                'backupCount': 5,
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'INFO',
            'handlers': ['file']
        }
    })

    app = Flask(__name__)
    # https://wikidocs.net/81066
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SESSION_COOKIE_SECURE'] = True
    ### jinja update 
    app.jinja_env.globals.update(
        enumerate=enumerate, 
    )

    from views import main_views, api_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(api_views.bp)

    return app

if __name__ == '__main__':
    app = create_app()
    
    th = threading.Thread(target=read_log)
    th.daemon = True
    th.start()

    th2 = threading.Thread(target=read_cpu_mem)
    th2.daemon = True
    th2.start()

    app.run(host='127.0.0.1', debug=False, threaded=True)