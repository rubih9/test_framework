import pandas as pd
import yaml
import json
from typing import Dict, List, Any
from loguru import logger
from abc import ABC, abstractmethod

class BaseTestCaseHandler(ABC):
    """测试用例处理器基类"""
    def __init__(self):
        self.test_cases = []
        self.variables = {}  # 存储提取的变量
        
    @abstractmethod
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        pass
        
    def get_scenario_cases(self, scenario: str) -> List[Dict[str, Any]]:
        """获取指定场景的测试用例
        
        Args:
            scenario: 场景名称
            
        Returns:
            场景相关的测试用例列表
        """
        return [case for case in self.test_cases if case['scenario'] == scenario]
        
    def extract_variables(self, response: Dict[str, Any], extract_rules: Dict[str, str]):
        """从响应中提取变量
        
        Args:
            response: API响应
            extract_rules: 提取规则
        """
        for var_name, path in extract_rules.items():
            try:
                value = self._extract_by_path(response, path)
                self.variables[var_name] = value
                logger.info(f"提取变量 {var_name}: {value}")
            except Exception as e:
                logger.error(f"提取变量 {var_name} 失败: {str(e)}")
                
    def _extract_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """根据路径提取值
        
        Args:
            data: 数据源
            path: 提取路径 (例如: "data.id")
            
        Returns:
            提取的值
        """
        current = data
        for key in path.split('.'):
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                current = current[int(key)]
            else:
                raise ValueError(f"无效的提取路径: {path}")
        return current
        
    def replace_variables(self, data: Any) -> Any:
        """替换数据中的变量引用
        
        Args:
            data: 需要替换变量的数据
            
        Returns:
            替换后的数据
        """
        if isinstance(data, str):
            # 替换 ${var_name} 格式的变量
            for var_name, value in self.variables.items():
                data = data.replace(f"${{{var_name}}}", str(value))
            return data
        elif isinstance(data, dict):
            return {k: self.replace_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_variables(item) for item in data]
        return data

class ExcelTestCaseHandler(BaseTestCaseHandler):
    """Excel 测试用例处理器"""
    def __init__(self, excel_path: str):
        super().__init__()
        self.excel_path = excel_path
        self.test_cases = self.load_test_cases()
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """从 Excel 文件加载测试用例
        
        Returns:
            测试用例列表
        """
        try:
            df = pd.read_excel(self.excel_path)
            test_cases = []
            
            for _, row in df.iterrows():
                case = {
                    'case_id': str(row['case_id']),
                    'scenario': str(row['scenario']),
                    'step': int(row['step']),
                    'description': str(row['description']),
                    'api': str(row['api']),
                    'method': str(row['method']),
                    'headers': json.loads(str(row['headers'])) if pd.notna(row.get('headers')) else {},
                    'data': json.loads(str(row['data'])) if pd.notna(row.get('data')) else {},
                    'expected': json.loads(str(row['expected'])) if pd.notna(row.get('expected')) else {},
                    'extract': json.loads(str(row['extract'])) if pd.notna(row.get('extract')) else {}
                }
                test_cases.append(case)
                
            logger.info(f"成功从 {self.excel_path} 加载 {len(test_cases)} 个测试用例")
            return test_cases
        except Exception as e:
            logger.error(f"加载测试用例失败: {str(e)}")
            return []

class YAMLTestCaseHandler(BaseTestCaseHandler):
    """YAML格式测试用例处理器"""
    def __init__(self, yaml_path: str):
        """初始化YAML测试用例处理器
        
        Args:
            yaml_path: YAML文件路径
        """
        super().__init__()
        self.yaml_path = yaml_path
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """加载YAML中的测试用例
        
        Returns:
            测试用例列表
        """
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                test_cases = yaml.safe_load(f)
                
            # 确保test_cases是列表格式
            if not isinstance(test_cases, list):
                raise ValueError("YAML文件必须包含测试用例列表")
                
            # 验证必要字段
            required_fields = {'case_id', 'scenario', 'step', 'method', 'api', 'description'}
            for case in test_cases:
                missing_fields = required_fields - set(case.keys())
                if missing_fields:
                    raise ValueError(f"测试用例缺少必要字段: {missing_fields}")
                    
            # 按场景和步骤排序
            test_cases.sort(key=lambda x: (x['scenario'], x['step']))
            
            self.test_cases = test_cases
            return test_cases
            
        except Exception as e:
            logger.error(f"加载YAML测试用例失败: {str(e)}")
            raise

# 向后兼容的别名
TestCaseHandler = ExcelTestCaseHandler 