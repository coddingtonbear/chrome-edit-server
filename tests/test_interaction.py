try:
    from http.client import HTTPConnection, OK
except ImportError:
    from httplib import HTTPConnection, OK
import multiprocessing
import time
import unittest


TESTING_PORT = 49292


class TestInteraction(unittest.TestCase):
    def setUp(self):
        """
        Start the edit server process.
        """
        self.server = multiprocessing.Process(target=self.run_server)
        self.server.start()
        # Wait for a moment just to make sure the server is up before
        # we begin testing.
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
        from edit_server.cmdline import main
        main(
            [
                '--port=%s' % TESTING_PORT,
                'cp', 'tests/edited.txt',
            ]
        )

    def test_edit_file(self):
        connection = HTTPConnection('localhost', TESTING_PORT)
        connection.request('POST', '/', "Original text\n")
        response = connection.getresponse()

        self.assertEqual(response.status, OK)
        result = response.read().decode('utf-8')
        self.assertEqual(result, "Replaced text\n")
