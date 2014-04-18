from smtplib import SMTP
from email.mime.text import MIMEText
import configparser
import os
import requests
import json

def main():
    pass

def load_settings(directory):
    config = configparser.ConfigParser()
    file = os.path.join(directory, 'settings.cfg')
    config.read_file(open(file))
    return config['CONFIG']

def send_error(ex, config):
    body = 'Error type: ' + type(ex).__name__ + '\nMessage: '
    for arg in ex.args:
        body += arg + '\n'
    msg = MIMEText(body)
    msg['Subject'] = 'name.com Update Error'
    msg['From'] = 'donotreply'
    msg['To'] = config['email']

    server = SMTP(config['smtp'])
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.login(config['smtpuser'], config['smtppassword'])
    server.send_message(msg)
    server.quit()


class NameComInterract:

    def __init__(self, config):
        self.config = config
        self.session_token = None

    def api_hello(self):
        hello_url = self.config['apiurl'] + '/api/hello'
        res = requests.get(hello_url)
        return res.json()

    def login(self):
        login_url = self.config['apiurl'] + '/api/login'
        payload = {'username': self.config['apiuser'], 'api_token': self.config['apitoken']}
        res = requests.post(login_url, data=json.dumps(payload))
        json_res = res.json()
        if json_res['result']['code'] != 100:
            raise NameComInterractionError('Login failed: ' + json_res['result']['message'])
        self.session_token = json_res['session_token']
        print('Login message: ' + json_res['result']['message'])
        return json_res


class NameComInterractionError(Exception):
    pass

if __name__ == '__main__':
    main()