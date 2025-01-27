import asyncio
from typing import Dict, List, Any, Type, Optional
from loguru import logger
from .config import Config
from .api_client import APIClient
from ..handlers.test_case_handler import BaseTestCaseHandler, ExcelTestCaseHandler, YAMLTestCaseHandler
from ..reporters.html_reporter import HTMLReporter
from ..reporters.email_sender import EmailSender
from ..utils.exceptions import TestFrameworkError, ValidationError, APIError
from ..utils.logger import LoggerManager

class TestRunner:
    def __init__(self, config_path: str, email_config_path: str = None):
        """初始化测试运行器
        
        Args:
            config_path: 配置文件路径
            email_config_path: 邮件配置文件路径
        """
        # 加载配置
        self.config = Config(config_path, email_config_path)
        
        # 初始化日志
        self.logger_manager = LoggerManager(self.config.log_path)
        self.logger = self.logger_manager.get_logger()
        
        # 初始化结果列表
        self.results = []
        
    def _get_test_case_handler(self) -> BaseTestCaseHandler:
        """根据测试用例文件类型获取对应的处理器
        
        Returns:
            测试用例处理器实例
        """
        test_case_path = self.config.test_case_path
        if test_case_path.endswith('.xlsx'):
            return ExcelTestCaseHandler(test_case_path)
        elif test_case_path.endswith('.yaml') or test_case_path.endswith('.yml'):
            return YAMLTestCaseHandler(test_case_path)
        else:
            raise TestFrameworkError(f"不支持的测试用例文件格式: {test_case_path}")
            
    async def run_test_case(
        self,
        case: Dict[str, Any],
        api_client: APIClient,
        test_handler: BaseTestCaseHandler
    ) -> Dict[str, Any]:
        """运行单个测试用例
        
        Args:
            case: 测试用例数据
            api_client: API客户端实例
            test_handler: 测试用例处理器实例
            
        Returns:
            测试结果
        """
        try:
            self.logger.info(f"执行测试用例: {case['case_id']} - {case['description']}")
            
            # 替换变量
            headers = test_handler.replace_variables(case.get('headers', {}))
            data = test_handler.replace_variables(case.get('data'))
            params = test_handler.replace_variables(case.get('params', {}))
            
            # 发送请求
            response = await api_client.request(
                method=case['method'],
                endpoint=case['api'],
                headers=headers,
                data=data,
                params=params
            )
            
            # 提取变量
            if case.get('extract'):
                test_handler.extract_variables(response['data'], case['extract'])
                
            # 验证结果
            expected = case.get('expected', {})
            actual = response['data']
            is_passed = test_handler.verify_response(actual, expected)
            
            result = {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': is_passed,
                'response': response,
                'expected': expected,
                'actual': actual
            }
            
            self.logger.info(f"测试用例 {case['case_id']} {'通过' if is_passed else '失败'}")
            return result
            
        except APIError as e:
            self.logger.error(f"API请求失败: {str(e)}")
            return {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': False,
                'error': f"API错误: {str(e)}"
            }
        except ValidationError as e:
            self.logger.error(f"数据验证失败: {str(e)}")
            return {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': False,
                'error': f"验证错误: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"测试用例执行失败: {str(e)}")
            return {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': False,
                'error': f"执行错误: {str(e)}"
            }
            
    async def run_all_tests(self):
        """运行所有测试用例"""
        self.logger.info("开始运行测试...")
        
        try:
            # 获取测试用例处理器
            test_handler = self._get_test_case_handler()
            test_cases = test_handler.load_test_cases()
            
            if not test_cases:
                self.logger.warning("未找到任何测试用例")
                return
                
            # 初始化API客户端
            async with APIClient(
                self.config.base_urls,
                self.config.timeout
            ) as api_client:
                # 按场景和步骤顺序执行测试
                for case in test_cases:
                    result = await self.run_test_case(case, api_client, test_handler)
                    self.results.append(result)
                    
            # 生成报告
            self._generate_and_send_report()
            
            self.logger.info("测试执行完成")
            
        except Exception as e:
            self.logger.error(f"测试执行过程中发生错误: {str(e)}")
            raise
            
    def _generate_and_send_report(self):
        """生成并发送测试报告"""
        try:
            # 生成HTML报告
            reporter = HTMLReporter(
                self.config.report_path,
                self.config.report_title
            )
            report_file = reporter.generate(self.results)
            
            # 发送邮件
            if self.config.email_settings.get('sender'):
                email_sender = EmailSender(self.config.email_settings)
                email_sender.send_report(report_file, self.results)
                
        except Exception as e:
            self.logger.error(f"生成或发送报告失败: {str(e)}")
            raise

def run_tests(config_path: str, email_config_path: str = None):
    """运行测试的便捷函数
    
    Args:
        config_path: 配置文件路径
        email_config_path: 邮件配置文件路径
    """
    runner = TestRunner(config_path, email_config_path)
    asyncio.run(runner.run_all_tests()) 