"""
报告生成模块
"""

from .html_reporter import HTMLReporter
from .email_sender import EmailSender

__all__ = ['HTMLReporter', 'EmailSender'] 