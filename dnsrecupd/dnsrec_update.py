from smtplib import SMTP
from email.mime.text import MIMEText
import configparser
import os
import requests
import json

def main():
    config = load_settings(os.path.dirname(__file__))
    try:
        update_dns_with_ip(config)
    except Exception as ex:
        send_error(ex, config)

def update_dns_with_ip(config):
    nameint = NameComInterract(config)
    response = nameint.api_hello()
    ip_add = response['client_ip']
    new_home_record = {'hostname': 'home',
                               'type': 'A',
                               'content': ip_add,
                               'ttl': 300}
    nameint.login()
    dns_records = nameint.list_dns_records()
    dns_name = 'home.' + config['domain']
    current_home_record = next((record for record in dns_records if record['name'] == dns_name and record['type'] ==  'A'), None)
    return_value = current_home_record
    if current_home_record != None:
        if current_home_record['content'] != ip_add:
            print('Updating ip address to: ' + str(ip_add))
            nameint.delete_dns_record(current_home_record['record_id'])
            return_value = nameint.create_dns_record(new_home_record)
        else:
            print('No action, ip up to date')
    else:
        print('Adding new dns record:')
        print(new_home_record)
        return_value = nameint.create_dns_record(new_home_record)
    return return_value


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

    def create_domain(self, domain):
        create_domain_url = self.config['apiurl'] + '/api/domain/create'
        response = requests.post(create_domain_url, data=json.dumps(domain), headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res

    def list_domains(self):
        list_domain_url = self.config['apiurl'] + '/api/domain/list'
        response = requests.get(list_domain_url, headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res['domains']

    def list_dns_records(self):
        list_dns_url = self.config['apiurl'] + '/api/dns/list/' + self.config['domain']
        response = requests.get(list_dns_url, headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res['records']

    def create_dns_record(self, dns):
        print('Creating dns record: ')
        print(dns)
        create_dns_url = self.config['apiurl'] + '/api/dns/create/' + self.config['domain']
        response = requests.post(create_dns_url, data=json.dumps(dns), headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res

    def delete_dns_record(self, record_id):
        print('Deleting dns record_id: ' + str(record_id))
        payload = {'record_id':  record_id}
        delete_dns_url = self.config['apiurl'] + '/api/dns/delete/' + self.config['domain']
        response = requests.post(delete_dns_url, data=json.dumps(payload), headers=self.session_token)
        json_res = NameComInterract.process_response(response)
        return json_res

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
