from hamcrest import *
from flaskal.flaskal import yaml_to_code
import unittest
import subprocess
import time
import requests
import sqlite3
import os

DB_LOCATION = '/tmp/flaskal.db'

test_sql = """
CREATE TABLE test 
(id INTEGER PRIMARY KEY ASC, name VARCHAR(250));
"""

test_yaml = """
Test:
    table: test 
    rest: /api/test/
    columns:
    - name=id type=integer primary_key=True
    - name=name type=String(250)
"""

class FlaskalTest(unittest.TestCase):

    def start_server(self):
        self.proc = None

        code = yaml_to_code(test_yaml)
        assert_that(code, contains_string("class Test(Base)"))

        with open('/tmp/test_flaskal_app.py', 'w') as f:
            f.write(code)

        self.proc = subprocess.Popen(['python', '/tmp/test_flaskal_app.py'])
        time.sleep(1)

    def setUp(self):
        if os.path.exists(DB_LOCATION):
            os.unlink(DB_LOCATION)
        conn = sqlite3.connect(DB_LOCATION)
        c = conn.cursor()
        c.execute(test_sql)
        conn.commit()
        conn.close()
        try:
            requests.get("http://localhost:5000/?start_test")
        except:
            self.start_server()

    def test_flaskal_happy_path(self):

        resp = requests.get('http://localhost:5000/api/test/')
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), equal_to([]))

        resp = requests.post('http://localhost:5000/api/test/', 
                             json={"name": "bart"})
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), has_key("name"))
        assert_that(resp.json(), has_key("id"))
        id = resp.json()['id']

        resp = requests.get('http://localhost:5000/api/test/%d/' % id)
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json()['name'], equal_to('bart'))

        resp = requests.get('http://localhost:5000/api/test/')
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json()[0], has_key("name"))

        resp = requests.delete('http://localhost:5000/api/test/%d/' % id)
        assert_that(resp.status_code, equal_to(200))

        resp = requests.get('http://localhost:5000/api/test/%d/' % id)
        assert_that(resp.status_code, equal_to(404))

        resp = requests.get('http://localhost:5000/api/test/')
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), equal_to([]))

    def test_flaskal_filter(self):

        resp = requests.post('http://localhost:5000/api/test/', 
                             json={"name": "bart"})
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), has_key("name"))
        assert_that(resp.json(), has_key("id"))
        id = resp.json()['id']

        resp = requests.post('http://localhost:5000/api/test/', 
                             json={"name": "someone else"})
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), has_key("name"))
        assert_that(resp.json(), has_key("id"))

        resp = requests.get('http://localhost:5000/api/test/', params={'name': 'bart'})
        assert_that(resp.status_code, equal_to(200))
        assert_that(resp.json(), equal_to([{'name': 'bart', 'id': id}]))


