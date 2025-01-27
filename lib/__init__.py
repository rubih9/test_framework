"""
API自动化测试框架核心库
"""

from .handlers.test_case_handler import TestCaseHandler
from .core.api_client import APIClient
from .core.test_runner import TestRunner, run_tests
from .core.config import Config
from .utils.logger import LoggerManager
from .reporters.html_reporter import HTMLReporter
from .reporters.email_sender import EmailSender

__all__ = [
    'TestCaseHandler',
    'APIClient',
    'TestRunner',
    'run_tests',
    'Config',
    'LoggerManager',
    'HTMLReporter',
    'EmailSender'
] 