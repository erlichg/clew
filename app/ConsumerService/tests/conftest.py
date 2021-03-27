import os


def pytest_generate_tests(metafunc):
    os.environ['RABBIT_HOST'] = 'localhost'
    os.environ['RABBIT_USER'] = 'avi'
    os.environ['RABBIT_PASS'] = 'avipass'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_NAME'] = 'TEST_clew_medical'
    os.environ['DB_USER'] = 'avidb'
    os.environ['DB_PASSWORD'] = 'password'
