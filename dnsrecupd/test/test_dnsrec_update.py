import unittest
from unittest.mock import patch

from dnsrecupd import dnsrec_update
import os


class TestDnsRecUpdate(unittest.TestCase):

    def setUp(self):
        self.config = dnsrec_update.load_settings(os.path.dirname(__file__))

    def testLoadSettings(self):
        self.assertEqual(self.config['apiuser'], 'davidalk-ote', 'Username loaded from settings')

    @patch(dnsrec_update.smtplib.SMTP)
    def testMail(self, MockSMTP):
        config = dnsrec_update.load_settings(os.path.dirname(__file__))
        ex = dnsrec_update.InvalidLoginError('Test Exception')
        dnsrec_update.send_error(ex, config)
        assert MockSMTP.calledehlo_or_helo_if_needed()

if __name__ == '__main__':
    unittest.main()