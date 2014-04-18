import unittest
from unittest.mock import patch
from unittest.mock import Mock

from dnsrecupd import dnsrec_update
import os
from dnsrecupd.dnsrec_update import NameComInterractionError


class TestDnsRecUpdate(unittest.TestCase):

    def setUp(self):
        self.config = dnsrec_update.load_settings(os.path.dirname(__file__))

    def test_settings_load(self):
        self.assertEqual(self.config['apiuser'], 'davidalk-ote', 'apiuser matches')
        self.assertEqual(self.config['apiurl'], 'https://api.dev.name.com', 'apiurl matches')

    @patch('dnsrecupd.dnsrec_update.SMTP')
    def test_send_error_calls_smtp(self, MockSMTP):
        mock_smtp_instance = Mock()
        MockSMTP.return_value = mock_smtp_instance
        ex = NameComInterractionError('Test Exception')
        dnsrec_update.send_error(ex, self.config)
        MockSMTP.assert_called_with(self.config['smtp'])
        mock_smtp_instance.ehlo_or_helo_if_needed.assert_called_with()
        mock_smtp_instance.starttls.assert_called_with()
        mock_smtp_instance.login.assert_called_with(self.config['smtpuser'], self.config['smtppassword'])

    def test_api_hello_returns(self):
        namecom_interact = dnsrec_update.NameComInterract(self.config)
        hello = namecom_interact.api_hello()
        self.assertEqual(100, hello['result']['code'], 'api hello returns correctly')
        self.assertEqual('Name.com API Test Server', hello['service'])

    def test_login_successful(self):
        namecom_interact = dnsrec_update.NameComInterract(self.config)
        login = namecom_interact.login()
        self.assertEqual(100, login['result']['code'], 'login success status returned')

    def test_login_throws_exception(self):
        bad_config = {'apiurl': 'https://api.dev.name.com', 'apiuser': 'davidalk-ote', 'apitoken': 'bad_token'}
        namecom_interact = dnsrec_update.NameComInterract(bad_config)
        with self.assertRaises(NameComInterractionError):
            namecom_interact.login()

    def test_logout_successful(self):
        namecom_interact = dnsrec_update.NameComInterract(self.config)
        namecom_interact.login()
        res = namecom_interact.logout()
        self.assertEqual(100, res['result']['code'], 'logout success status returned')

    def test_list_domains_returns_results(self):
        namecom_interact = dnsrec_update.NameComInterract(self.config)
        namecom_interact.login()
        domains_list = namecom_interact.list_domains()
        self.assertIsNotNone(domains_list['al-kanani.com'], 'domain is populated')
        print('Domain list:')
        print(domains_list)
        namecom_interact.logout()

    def test_update_dns_with_ip(self):
        return_value = dnsrec_update.update_dns_with_ip(self.config)
        self.assertIsNotNone(return_value, 'update_dns_with_ip returns value')
        #Remove entry
        namecom_interact = dnsrec_update.NameComInterract(self.config)
        namecom_interact.login()
        record_id = namecom_interact.list_dns_records().pop(0)
        namecom_interact.delete_dns_record(record_id['record_id'])
        namecom_interact.logout()

    @staticmethod
    def get_domain():
        domain = {'domain_name': 'al-kanani.com', 'period': 1}
        return domain

if __name__ == '__main__':
    unittest.main()