from flask import Blueprint, render_template, request, redirect, url_for
import uuid
from datetime import datetime 

from models import Firewall, TicketModel, AccessModel, ErrorModel
from forms import RuleUpdateForm, TicketUpdateForm
from configs import FIREWALL_COLUMN_HEADER, TICKET_COLUMN_HEADER, ACCESS_COLUMN_HEADER, ERROR_COLUMN_HEADER, ANALYZE_SITE

# blueprint
bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for('main.ticket'))

@bp.route('/firewall', methods=['GET', 'POST'])
def firewall():
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = Firewall()
    form = RuleUpdateForm()
    nonce = uuid.uuid4().hex
    if request.method == 'POST' and form.validate_on_submit():
        request_data = {'ip': form.ip.data, 'ip_class':form.ip_class.data, 'protocol': form.protocol.data, 'port': form.port.data, 'block': form.block.data, 'timestamp': datetime.now()}
        management.post(request_data=request_data)

    column_header = FIREWALL_COLUMN_HEADER
    update_title = 'Firewall'

    paging, data_list = management.get(page=page)
    return render_template('pages/firewall.html', **locals())

@bp.route('/ticket', methods=['GET', 'POST'])
def ticket():
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = TicketModel()
    form = TicketUpdateForm()
    nonce = uuid.uuid4().hex
    if request.method == 'POST':
        request_data = {'_id': form.id.data, 'fix':form.fix.data, 'fix_timestamp': datetime.now()}
        management.post(request_data=request_data)

    column_header = TICKET_COLUMN_HEADER
    update_title = 'Ticket'

    paging, data_list = management.get(page=page)
    return render_template('pages/ticket.html', **locals())

@bp.route('/ticket/<ticket>', methods=['GET'])
def history(ticket):
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = AccessModel()
    column_header = ACCESS_COLUMN_HEADER
    update_title = 'Access'

    paging, data_list = management.get_by_ticket(ticket, page=page)
    return render_template('pages/access.html', **locals())

@bp.route('/api/firewall/delete', methods=['POST'])
def delete_firewall_rule():
    form = RuleUpdateForm()
    if form.validate_on_submit():
        request_data = {'ip': form.ip.data, 'ip_class':form.ip_class.data, 'protocol': form.protocol.data, 'port': form.port.data, 'block': form.block.data}
        management = Firewall()
        management.delete(request_data=request_data)
        return 'validate', 200
    else:
        return 'not validate', 400

@bp.route('/access_log', methods=['GET'])
def access():
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = AccessModel()
    column_header = ACCESS_COLUMN_HEADER
    paging, data_list = management.get(page=page)
    return render_template('pages/access.html', **locals())

@bp.route('/access_log/site/<site>', methods=['GET'])
def access_by_site(site):
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = AccessModel()
    column_header = ACCESS_COLUMN_HEADER
    paging, data_list = management.get_by_site(site, page=page)
    return render_template('pages/access.html', **locals())

@bp.route('/access_log/status/<status>', methods=['GET'])
def access_by_status(status):
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = AccessModel()
    column_header = ACCESS_COLUMN_HEADER
    paging, data_list = management.get_by_status(status, page=page)
    return render_template('pages/access.html', **locals())

@bp.route('/error_log', methods=['GET'])
def error():
    page = request.args.get('page', default=1)

    analyze_site = ANALYZE_SITE
    management = ErrorModel()
    column_header = ERROR_COLUMN_HEADER
    paging, data_list = management.get(page=page)
    return render_template('pages/access.html', **locals())


