import smtplib
from email.mime.text import MIMEText
import configparser
import os

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
    msg['Subject'] = 'DYNDNS Update Error'
    msg['From'] = 'donotreply'
    msg['To'] = config['Email']

    server = smtplib.SMTP(config['smtp'])
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.login(config['smtpuser'], config['smtppassword'])
    server.send_message(msg)
    server.quit()

class InvalidLoginError(Exception):
    pass

if __name__ == '__main__':
    main()