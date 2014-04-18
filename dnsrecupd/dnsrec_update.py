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
        self.session_token = {}

    def api_hello(self):
        hello_url = self.config['apiurl'] + '/api/hello'
        res = requests.get(hello_url)
        return res.json()

    def login(self):
        login_url = self.config['apiurl'] + '/api/login'
        payload = {'username': self.config['apiuser'], 'api_token': self.config['apitoken']}
        res = requests.post(login_url, data=json.dumps(payload))
        json_res = res.json()
        NameComInterract.check_response(json_res)
        self.session_token['Api-Session-Token'] = json_res['session_token']
        print('Login message: ' + json_res['result']['message'])
        return json_res

    def logout(self):
        logout_url = self.config['apiurl'] + '/api/logout'
        res = requests.get(logout_url, headers=self.session_token)
        json_res = res.json()
        NameComInterract.check_response(json_res)
        print ('Logout message:' + json_res['result']['message'])
        return json_res

    @staticmethod
    def check_response(json_res):
        if json_res['result']['code'] != 100:
            raise NameComInterractionError('Login failed: ' + json_res['result']['message'])


class NameComInterractionError(Exception):
    pass

if __name__ == '__main__':
    main()