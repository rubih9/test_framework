from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import jinja2
from loguru import logger

class HTMLReporter:
    def __init__(self, report_path: str, title: str = "Test Report"):
        self.report_path = Path(report_path)
        self.report_path.mkdir(parents=True, exist_ok=True)
        self.title = title
        
    def generate(self, results: List[Dict[str, Any]]) -> str:
        """生成HTML测试报告
        
        Args:
            results: 测试结果列表
            
        Returns:
            报告文件路径
        """
        template = self._get_template()
        passed_cases = sum(1 for r in results if r['is_passed'])
        total_cases = len(results)
        
        html = template.render(
            title=self.title,
            results=results,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=total_cases - passed_cases,
            pass_rate=round(passed_cases / total_cases * 100, 2) if total_cases > 0 else 0,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        report_file = self.report_path / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        report_file.write_text(html, encoding='utf-8')
        logger.info(f"测试报告已生成: {report_file}")
        
        return str(report_file)
        
    def _get_template(self) -> jinja2.Template:
        """获取报告模板"""
        template_str = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ title }}</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                }
                .summary {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .summary-item {
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }
                .passed { background-color: #e6ffe6; color: #006600; }
                .failed { background-color: #ffe6e6; color: #cc0000; }
                .total { background-color: #e6f3ff; color: #003366; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                th, td {
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }
                th {
                    background-color: #f8f9fa;
                    font-weight: bold;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .timestamp {
                    text-align: right;
                    color: #666;
                    margin-top: 20px;
                }
                .details {
                    max-height: 100px;
                    overflow-y: auto;
                    font-family: monospace;
                    white-space: pre-wrap;
                    background-color: #f8f9fa;
                    padding: 8px;
                    border-radius: 3px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ title }}</h1>
                </div>
                <div class="summary">
                    <div class="summary-item total">
                        <h3>总用例数</h3>
                        <p>{{ total_cases }}</p>
                    </div>
                    <div class="summary-item passed">
                        <h3>通过</h3>
                        <p>{{ passed_cases }}</p>
                    </div>
                    <div class="summary-item failed">
                        <h3>失败</h3>
                        <p>{{ failed_cases }}</p>
                    </div>
                    <div class="summary-item total">
                        <h3>通过率</h3>
                        <p>{{ pass_rate }}%</p>
                    </div>
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
                            <div class="details">
                            {% if result.error %}
                                {{ result.error }}
                            {% else %}
                                预期: {{ result.expected|tojson }}
                                实际: {{ result.actual|tojson }}
                            {% endif %}
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
                <div class="timestamp">
                    生成时间: {{ timestamp }}
                </div>
            </div>
        </body>
        </html>
        """
        return jinja2.Template(template_str) 