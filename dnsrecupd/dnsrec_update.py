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
        response = requests.get(hello_url)
        return response.json()

    def login(self):
        login_url = self.config['apiurl'] + '/api/login'
        payload = {'username': self.config['apiuser'], 'api_token': self.config['apitoken']}
        response = requests.post(login_url, data=json.dumps(payload))
        json_res = NameComInterract.process_response(response)
        self.session_token['Api-Session-Token'] = json_res['session_token']
        print('Login message: ' + json_res['result']['message'])
        return json_res

    def logout(self):
        logout_url = self.config['apiurl'] + '/api/logout'
        response = requests.get(logout_url, headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        print ('Logout message:' + json_res['result']['message'])
        return json_res

    def list_domains(self):
        list_domain_url = self.config['apiurl'] + '/api/domain/list'
        response = requests.get(list_domain_url, headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res['domains']

    def list_dns(self):
        list_dns_url = self.config['apiurl'] + '/api/dns/list/' + self.config['domain']
        response = requests.get(list_dns_url, headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res['records']

    @staticmethod
    def process_response(response):
        json_res = response.json()
        if json_res['result']['code'] != 100:
            raise NameComInterractionError('\nError Code: ' + str(json_res['result']['code']) + '\nError Message: ' + json_res['result']['message'])
        return json_res


class NameComInterractionError(Exception):
    pass

if __name__ == '__main__':
    main()
