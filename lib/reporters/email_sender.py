from typing import List, Dict, Any
import yagmail
from loguru import logger

class EmailSender:
    def __init__(self, email_settings: Dict[str, Any]):
        """初始化邮件发送器
        
        Args:
            email_settings: 邮件配置
        """
        self.settings = email_settings
        self._validate_settings()
        
    def _validate_settings(self):
        """验证邮件配置"""
        required_fields = ['sender', 'password', 'smtp_server', 'smtp_port']
        missing_fields = [field for field in required_fields if not self.settings.get(field)]
        if missing_fields:
            raise ValueError(f"邮件配置缺少必要字段: {missing_fields}")
            
    def send_report(self, report_file: str, results: List[Dict[str, Any]]) -> bool:
        """发送测试报告邮件
        
        Args:
            report_file: 报告文件路径
            results: 测试结果列表
            
        Returns:
            是否发送成功
        """
        try:
            # 检查是否需要发送邮件
            if self.settings.get('send_on_fail_only'):
                if all(r['is_passed'] for r in results):
                    logger.info("所有测试用例通过，不发送邮件")
                    return True
                    
            # 准备邮件内容
            passed_cases = sum(1 for r in results if r['is_passed'])
            total_cases = len(results)
            pass_rate = round(passed_cases / total_cases * 100, 2) if total_cases > 0 else 0
            
            subject = f"测试报告 - 通过率: {pass_rate}% ({passed_cases}/{total_cases})"
            
            # 发送邮件
            with yagmail.SMTP(
                user=self.settings['sender'],
                password=self.settings['password'],
                host=self.settings['smtp_server'],
                port=self.settings['smtp_port']
            ) as yag:
                yag.send(
                    to=self.settings.get('recipients', []),
                    subject=subject,
                    contents=[
                        f"测试执行完成，共执行 {total_cases} 个用例",
                        f"通过: {passed_cases}",
                        f"失败: {total_cases - passed_cases}",
                        f"通过率: {pass_rate}%",
                        f"\n详细结果请查看附件。",
                        report_file  # 自动作为附件发送
                    ]
                )
                
            logger.info("测试报告邮件发送成功")
            return True
            
        except Exception as e:
            logger.error(f"发送测试报告邮件失败: {str(e)}")
            return False 