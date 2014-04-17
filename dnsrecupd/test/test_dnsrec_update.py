import unittest
from dnsrecupd import dnsrec_update
import os

class TestDnsRecUpdate(unittest.TestCase):

    def testLoadSettings(self):
        config = dnsrec_update.load_settings(os.path.dirname(__file__))
        self.assertEqual(config['apiuser'], 'davidalk-ote', 'Username loaded from settings')

    def testMail(self):
        config = dnsrec_update.load_settings(os.path.dirname(__file__))
        ex = dnsrec_update.InvalidLoginError('Test Exception')
        dnsrec_update.send_error(ex, config)
