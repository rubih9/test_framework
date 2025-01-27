import asyncio
import os
import yaml
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger
import jinja2
import yagmail
from .test_case_handler import TestCaseHandler, ExcelTestCaseHandler, YAMLTestCaseHandler, BaseTestCaseHandler
from .api_client import APIClient

class TestRunner:
    def __init__(self, config_path: str, email_config_path: str):
        """初始化测试运行器
        
        Args:
            config_path: 配置文件路径
            email_config_path: 邮件配置文件路径
        """
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
            
        with open(email_config_path) as f:
            self.email_config = yaml.safe_load(f)
            
        self.results = []
        self.setup_logger()
        
    def setup_logger(self):
        """配置日志记录器"""
        log_path = self.config['log_path']
        os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(log_path, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        logger.add(log_file, rotation="500 MB")
        
    async def run_test_case(self, case: Dict[str, Any], api_client: APIClient, test_handler: TestCaseHandler) -> Dict[str, Any]:
        """运行单个测试用例
        
        Args:
            case: 测试用例数据
            api_client: API客户端实例
            test_handler: 测试用例处理器实例
            
        Returns:
            测试结果
        """
        try:
            # 替换变量
            headers = test_handler.replace_variables(case.get('headers', {}))
            data = test_handler.replace_variables(case.get('data'))
            
            # 发送请求
            response = await api_client.request(
                method=case['method'],
                endpoint=case['api'],
                headers=headers,
                data=data
            )
            
            # 提取变量
            if case.get('extract'):
                test_handler.extract_variables(response['data'], case['extract'])
                
            # 验证结果
            expected = case.get('expected', {})
            actual = response['data']
            is_passed = self._verify_response(actual, expected)
            
            result = {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': is_passed,
                'response': response,
                'expected': expected,
                'actual': actual
            }
            
            logger.info(f"测试用例 {case['case_id']} {'通过' if is_passed else '失败'}")
            return result
            
        except Exception as e:
            logger.error(f"测试用例 {case['case_id']} 执行出错: {str(e)}")
            return {
                'case_id': case['case_id'],
                'scenario': case['scenario'],
                'description': case['description'],
                'is_passed': False,
                'error': str(e)
            }
            
    def _verify_response(self, actual: Any, expected: Dict[str, Any]) -> bool:
        """验证响应结果
        
        Args:
            actual: 实际响应
            expected: 预期结果
            
        Returns:
            验证是否通过
        """
        try:
            for key, value in expected.items():
                if isinstance(value, dict):
                    if not self._verify_response(actual.get(key, {}), value):
                        return False
                elif actual.get(key) != value:
                    return False
            return True
        except:
            return False
            
    async def run_all_tests(self):
        """运行所有测试用例"""
        logger.info("开始运行测试...")
        
        # 初始化API客户端
        async with APIClient(self.config['base_urls'], self.config['timeout']) as api_client:
            # 根据文件类型选择测试用例处理器
            if self.config['test_case_path'].endswith('.xlsx'):
                test_handler = ExcelTestCaseHandler(self.config['test_case_path'])
            elif self.config['test_case_path'].endswith('.yaml'):
                test_handler = YAMLTestCaseHandler(self.config['test_case_path'])
            else:
                raise ValueError("Unsupported test case file format")
            
            test_cases = test_handler.load_test_cases()
            
            if not test_cases:
                logger.warning("未找到任何测试用例")
                return
            
            # 按场景和步骤排序所有用例
            test_cases.sort(key=lambda x: (x['scenario'], x['step']))
            
            # 创建Excel测试用例处理器
            handler = ExcelTestCaseHandler(self.config['test_case_path'])
            
            for case in test_cases:
                result = await self.run_test_case(case, api_client, handler)
                self.results.append(result)
                
        self.generate_report()
        self.send_report_email()
        
    def generate_report(self):
        """生成HTML测试报告"""
        report_path = self.config['report_path']
        os.makedirs(report_path, exist_ok=True)
        
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .summary { margin-bottom: 20px; }
                .passed { color: green; }
                .failed { color: red; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
            </style>
        </head>
        <body>
            <h1>{{ title }}</h1>
            <div class="summary">
                <p>总用例数: {{ total_cases }}</p>
                <p class="passed">通过: {{ passed_cases }}</p>
                <p class="failed">失败: {{ failed_cases }}</p>
                <p>通过率: {{ pass_rate }}%</p>
            </div>
            <table>
                <tr>
                    <th>用例ID</th>
                    <th>场景</th>
                    <th>描述</th>
                    <th>结果</th>
                    <th>详情</th>
                </tr>
                {% for result in results %}
                <tr>
                    <td>{{ result.case_id }}</td>
                    <td>{{ result.scenario }}</td>
                    <td>{{ result.description }}</td>
                    <td class="{{ 'passed' if result.is_passed else 'failed' }}">
                        {{ '通过' if result.is_passed else '失败' }}
                    </td>
                    <td>
                        {% if result.error %}
                            {{ result.error }}
                        {% else %}
                            预期: {{ result.expected|tojson }}
                            实际: {{ result.actual|tojson }}
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
        """
        
        template = jinja2.Template(template_str)
        passed_cases = sum(1 for r in self.results if r['is_passed'])
        total_cases = len(self.results)
        
        html = template.render(
            title=self.config['report_title'],
            results=self.results,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=total_cases - passed_cases,
            pass_rate=round(passed_cases / total_cases * 100, 2) if total_cases > 0 else 0
        )
        
        report_file = os.path.join(report_path, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        logger.info(f"测试报告已生成: {report_file}")
        return report_file
        
    def send_report_email(self):
        """发送测试报告邮件"""
        try:
            if self.email_config['send_on_fail_only']:
                if all(r['is_passed'] for r in self.results):
                    logger.info("所有测试用例通过，不发送邮件")
                    return
                    
            report_file = self.generate_report()
            yag = yagmail.SMTP(
                user=self.email_config['sender'],
                password=self.email_config['password'],
                host=self.email_config['smtp_server'],
                port=self.email_config['smtp_port']
            )
            
            yag.send(
                to=self.email_config['receivers'],
                subject=self.email_config['email_title'],
                contents=[
                    "请查看附件中的测试报告。",
                    report_file
                ]
            )
            
            logger.info("测试报告邮件已发送")
            
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            
def run_tests(config_path: str, email_config_path: str):
    """运行测试的入口函数"""
    runner = TestRunner(config_path, email_config_path)
    asyncio.run(runner.run_all_tests()) 