* 23/02/25
    - 0.6.2 (views/api_views.py) <br>
        apply to get remote log <br>

    - 0.6.1 (templates/navbar.html) <br>
        apply nav-pill and nav-link active <br>

    - 0.6.0 (templates/chart.html) <br>
        chart with chart.js for cpu and mem usage <br>

* 23/01/29
    - 0.5.9 (models/bot.py) <br>
        apply telegram bot <br>

* 23/01/01
    - 0.5.8 (models/firewall.py) <br>
        consider when ip range /24 case <br>
    - 0.5.7 (views/main_views.py) <br>
        access_by_status() <br>
    - 0.5.6 (utils/analyzse.py) <br>
        use messsge in nginx_error_logs <br>

* 22/12/31
    - 0.5.5 (models/firewall.py) <br>
        model='firewall_policies' <br>

* 22/12/30
    - 0.5.4 (views/main_views.py) <br>
        error() <br>

* 22/12/25
    - 0.5.3 (utils/iptables.py) <br>
        -A INPUT -> -I INPUT 1 in _target_role <br>
    - 0.5.2 (views/main_views.py) <br>
        access_log_by_site <br>
    - 0.5.1 (viewss/main_views.py) <br>
        access_log <br>

* 22/12/24
    - 0.5.0 (models/log_db.py) <br>
        site info is different according to host <br>

* 22/12/23
    - 0.4.9 (models/mail.py) <br>
        DEFAULT_USER <br>

* 22/12/21
    - 0.4.8 (utils/iptables.py) <br>
        not use iptc anymore <br>

* 22/12/11
    - 0.4.7 (analyze.py) <br>
        add access_log keys : host, body, request_time <br>
        to do that, should change log_format in nginx.conf <br>