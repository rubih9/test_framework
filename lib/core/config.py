import yaml
from typing import Dict, Any
from pathlib import Path

class Config:
    def __init__(self, config_path: str, email_config_path: str = None):
        self.config = self._load_yaml(config_path)
        self.email_config = self._load_yaml(email_config_path) if email_config_path else {}
        
    @staticmethod
    def _load_yaml(file_path: str) -> Dict[str, Any]:
        """加载YAML配置文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            配置字典
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    @property
    def base_urls(self) -> Dict[str, str]:
        return self.config.get('base_urls', {})
        
    @property
    def timeout(self) -> int:
        return self.config.get('timeout', 30)
        
    @property
    def test_case_path(self) -> str:
        return self.config.get('test_case_path', '')
        
    @property
    def log_path(self) -> str:
        return self.config.get('log_path', 'logs')
        
    @property
    def report_path(self) -> str:
        return self.config.get('report_path', 'reports')
        
    @property
    def report_title(self) -> str:
        return self.config.get('report_title', 'Test Report')
        
    @property
    def email_settings(self) -> Dict[str, Any]:
        return {
            'sender': self.email_config.get('sender'),
            'password': self.email_config.get('password'),
            'smtp_server': self.email_config.get('smtp_server'),
            'smtp_port': self.email_config.get('smtp_port'),
            'recipients': self.email_config.get('recipients', []),
            'send_on_fail_only': self.email_config.get('send_on_fail_only', False)
        } 