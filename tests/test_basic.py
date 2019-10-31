import os

from django.test import RequestFactory

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_json(rf: RequestFactory):
    # with open(f"{BASE_DIR}/tests/data/basic.json") as f:
    #     request = rf.post('/foo/bar', data=f, content_type='application/json')
    #     print(request)
    pass


def test_msgpack(rf: RequestFactory):
    pass
