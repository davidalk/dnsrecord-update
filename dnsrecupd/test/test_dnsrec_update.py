import unittest
from unittest.mock import patch
from unittest.mock import Mock

from dnsrecupd import dnsrec_update
import os


class TestDnsRecUpdate(unittest.TestCase):

    def setUp(self):
        self.config = dnsrec_update.load_settings(os.path.dirname(__file__))

    def testLoadSettings(self):
        self.assertEqual(self.config['apiuser'], 'davidalk-ote', 'Username loaded from settings')

    @patch('dnsrecupd.dnsrec_update.SMTP')
    def testMail(self, MockSMTP):
        mockSmtpInstance = Mock()
        MockSMTP.return_value = mockSmtpInstance
        ex = dnsrec_update.InvalidLoginError('Test Exception')
        dnsrec_update.send_error(ex, self.config)
        MockSMTP.assert_called_with(self.config['smtp'])
        mockSmtpInstance.ehlo_or_helo_if_needed.assert_called_with()
        mockSmtpInstance.starttls.assert_called_with()
        mockSmtpInstance.login.assert_called_with(self.config['smtpuser'], self.config['smtppassword'])

if __name__ == '__main__':
    unittest.main()