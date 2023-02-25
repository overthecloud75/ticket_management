from flask import Blueprint, render_template, request, redirect, url_for
from datetime import datetime, timedelta

from models import LogModel, UsageModel
from forms import RuleUpdateForm

# blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/loads', methods=['GET'])
def get_loads():
    management = UsageModel()
    begin_timestamp = datetime.now() - timedelta(days=1)
    data_dict = management.get(begin_timestamp)
    return data_dict, 200

@bp.route('/firewall/delete', methods=['POST'])
def delete_firewall_rule():
    form = RuleUpdateForm()
    if form.validate_on_submit():
        request_data = {'ip': form.ip.data, 'ip_class':form.ip_class.data, 'protocol': form.protocol.data, 'port': form.port.data, 'block': form.block.data}
        management = Firewall()
        management.delete(request_data=request_data)
        return 'validate', 200
    else:
        return 'not validate', 400

@bp.route('/remote/log', methods=['POST'])
def remote_log():
    log_list = request.json
    access_model = LogModel(model='access_logs')
    access_model.many_post(log_list)
    return 'ok', 200