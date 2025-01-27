import os
from lib.test_runner import run_tests

if __name__ == '__main__':
    config_path = os.path.join('config', 'config.yaml')
    email_config_path = os.path.join('config', 'email_config.yaml')
    run_tests(config_path, email_config_path) 