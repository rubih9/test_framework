import sys
from pathlib import Path
from datetime import datetime
from loguru import logger
import jinja2
from typing import Any, Dict

class HTMLFormatter:
    def __init__(self):
        self.template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Test Log</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .log-container { max-width: 1200px; margin: 0 auto; }
        .log-entry { 
            padding: 8px; 
            margin: 4px 0; 
            border-radius: 4px;
            border-left: 4px solid #ddd;
        }
        .timestamp { color: #666; }
        .level { font-weight: bold; padding: 2px 6px; border-radius: 3px; }
        .location { color: #0066cc; }
        .DEBUG { background-color: #f8f9fa; border-left-color: #6c757d; }
        .INFO { background-color: #e9f5ff; border-left-color: #0d6efd; }
        .WARNING { background-color: #fff3cd; border-left-color: #ffc107; }
        .ERROR { background-color: #f8d7da; border-left-color: #dc3545; }
        .CRITICAL { background-color: #862e36; border-left-color: #58151c; color: white; }
    </style>
</head>
<body>
    <div class="log-container">
        <h1>Test Log</h1>
        {% for record in records %}
        <div class="log-entry {{ record.level }}">
            <span class="timestamp">{{ record.time }}</span> |
            <span class="level">{{ record.level }}</span> |
            <span class="location">{{ record.name }}:{{ record.function }}:{{ record.line }}</span> -
            <span class="message">{{ record.message }}</span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""
        self.template = jinja2.Template(self.template_str)
        self.records = []

    def write(self, message: str) -> None:
        record = self._parse_message(message)
        if record:
            self.records.append(record)
            with open(self.html_file, 'w', encoding='utf-8') as f:
                f.write(self.template.render(records=self.records))

    def _parse_message(self, message: str) -> Dict[str, Any]:
        try:
            parts = message.strip().split(' | ')
            time = parts[0]
            level = parts[1].strip()
            location, msg = parts[2].split(' - ', 1)
            name, function, line = location.split(':')
            return {
                'time': time,
                'level': level.strip(),
                'name': name,
                'function': function,
                'line': line,
                'message': msg
            }
        except Exception:
            return None

class LoggerManager:
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.log_path.mkdir(parents=True, exist_ok=True)
        self._configure_logger()
        
    def _configure_logger(self):
        """配置日志记录器"""
        # 移除默认的处理器
        logger.remove()
        
        # 添加控制台处理器
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="INFO"
        )
        
        # 添加文件处理器
        log_file = self.log_path / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="500 MB",
            retention="10 days"
        )
        
        # 添加HTML格式处理器
        html_formatter = HTMLFormatter()
        html_formatter.html_file = str(self.log_path / f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        logger.add(
            html_formatter.write,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="INFO"
        )
        
    @staticmethod
    def get_logger():
        """获取logger实例"""
        return logger 