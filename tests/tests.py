import http.client
import os
import multiprocessing
import unittest


class TestInteraction(unittest.TestCase):
    def setUp(self):
        """
        Start the edit server process.
        """
        self.server = multiprocessing.Process(target=self.run_server)
        self.server.start()
        import time
        time.sleep(1)

    def tearDown(self):
        """
        Terminate the edit server process.
        """
        self.server.terminate()

    def run_server(self):
        """
        Run edit server
        """
        os.environ['EDIT_SERVER_EDITOR'] = 'cp tests/edited.txt'
        from subprocess import call
        call(['./edit-server'])

    def test_edit_file(self):
        connection = http.client.HTTPConnection('localhost', 9292)
        connection.request('POST', '/', "Original text\n")
        response = connection.getresponse()

        self.assertEqual(response.status, http.client.OK)
        result = response.read().decode('utf-8')
        self.assertEqual(result, "Replaced text\n")
