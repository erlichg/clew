import os


def pytest_generate_tests(metafunc):
    os.environ['RABBIT_HOST'] = 'localhost'
    os.environ['RABBIT_USER'] = 'avi'
    os.environ['RABBIT_PASS'] = 'avipass'
