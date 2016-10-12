import json
import os.path
import requests
import signal
import subprocess
import sys
import time
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def waitServerStart():
    max_time = 5  # wait 5 seconds max
    start = time.time()
    while time.time() - start < max_time:
        try:
            r = requests.get('http://localhost:5000')
            r.raise_for_status()
            return
        except (requests.ConnectionError, requests.exceptions.RequestException):
            pass
        time.sleep(0.1)
    raise RuntimeError('Server did not start within %d seconds' % max_time)


class TestClientServer(unittest.TestCase):

    def test_add(self):
        server_p = subprocess.Popen(
            [
                sys.executable,
                os.path.join(PROJECT_ROOT, 'manage.py'),
                'runserver',
            ],
            cwd=PROJECT_ROOT,
        )
        try:
            waitServerStart()
            r = requests.get('http://localhost:5000/index.json')
            r.raise_for_status()
            length_before = len(json.loads(r.content.decode('utf-8'))['updates'])
            client_p = subprocess.Popen(
                [
                    sys.executable,
                    os.path.join(PROJECT_ROOT, 'manage.py'),
                    'add',
                ],
                cwd=PROJECT_ROOT,
            )
            try:
                client_p.communicate()
                self.assertEqual(client_p.returncode, 0)
            except:
                if client_p.poll() is None:
                    client_p.send_signal(signal.SIGKILL)
                raise
            r = requests.get('http://localhost:5000/index.json')
            r.raise_for_status()
            length_after = len(json.loads(r.content.decode('utf-8'))['updates'])
            self.assertEqual(length_before, length_after - 1)
            server_p.send_signal(signal.SIGINT)
            server_p.communicate()
            self.assertEqual(server_p.returncode, 0)
        except:
            if server_p.poll() is None:
                server_p.send_signal(signal.SIGKILL)
            raise
