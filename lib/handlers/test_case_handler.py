from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import pandas as pd
import yaml
import json
from loguru import logger
from ..utils.exceptions import TestCaseError, ValidationError
from ..utils.helpers import deep_get, deep_compare, validate_variable_name

class BaseTestCaseHandler(ABC):
    """测试用例处理器基类"""
    def __init__(self):
        self.test_cases = []
        self.variables = {}
        self.required_fields = {'case_id', 'scenario', 'step', 'method', 'api', 'description'}
        
    @abstractmethod
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """加载测试用例"""
        pass
        
    def validate_test_case(self, case: Dict[str, Any]) -> None:
        """验证测试用例格式
        
        Args:
            case: 测试用例数据
            
        Raises:
            ValidationError: 验证失败
        """
        # 检查必要字段
        missing_fields = self.required_fields - set(case.keys())
        if missing_fields:
            raise ValidationError(f"测试用例缺少必要字段: {missing_fields}")
            
        # 验证字段类型和格式
        if not isinstance(case['case_id'], (str, int)):
            raise ValidationError("case_id必须是字符串或整数")
            
        if not isinstance(case['scenario'], str):
            raise ValidationError("scenario必须是字符串")
            
        if not isinstance(case['step'], int):
            raise ValidationError("step必须是整数")
            
        if case['method'] not in {'GET', 'POST', 'PUT', 'DELETE', 'PATCH'}:
            raise ValidationError(f"不支持的HTTP方法: {case['method']}")
            
        # 验证数据格式
        if 'headers' in case and not isinstance(case['headers'], dict):
            raise ValidationError("headers必须是字典格式")
            
        if 'data' in case and not isinstance(case['data'], (dict, list)):
            raise ValidationError("data必须是字典或列表格式")
            
        if 'expected' in case and not isinstance(case['expected'], dict):
            raise ValidationError("expected必须是字典格式")
            
        if 'extract' in case:
            if not isinstance(case['extract'], dict):
                raise ValidationError("extract必须是字典格式")
            # 验证变量名格式
            for var_name in case['extract'].keys():
                if not validate_variable_name(var_name):
                    raise ValidationError(f"非法的变量名: {var_name}")
                    
    def get_scenario_cases(self, scenario: str) -> List[Dict[str, Any]]:
        """获取指定场景的测试用例
        
        Args:
            scenario: 场景名称
            
        Returns:
            场景相关的测试用例列表
        """
        cases = [case for case in self.test_cases if case['scenario'] == scenario]
        cases.sort(key=lambda x: x['step'])
        return cases
        
    def extract_variables(self, response: Dict[str, Any], extract_rules: Dict[str, str]) -> None:
        """从响应中提取变量
        
        Args:
            response: API响应
            extract_rules: 提取规则
            
        Raises:
            ValidationError: 变量提取失败
        """
        for var_name, path in extract_rules.items():
            try:
                value = deep_get(response, path)
                if value is None:
                    raise ValidationError(f"无法从路径 {path} 提取值")
                self.variables[var_name] = value
                logger.info(f"提取变量 {var_name}: {value}")
            except Exception as e:
                raise ValidationError(f"提取变量 {var_name} 失败: {str(e)}")
                
    def replace_variables(self, data: Any) -> Any:
        """替换数据中的变量引用
        
        Args:
            data: 需要替换变量的数据
            
        Returns:
            替换后的数据
            
        Raises:
            ValidationError: 变量替换失败
        """
        if isinstance(data, str):
            try:
                # 替换 ${var_name} 格式的变量
                result = data
                for var_name, value in self.variables.items():
                    placeholder = f"${{{var_name}}}"
                    if placeholder in result:
                        result = result.replace(placeholder, str(value))
                return result
            except Exception as e:
                raise ValidationError(f"替换变量失败: {str(e)}")
        elif isinstance(data, dict):
            return {k: self.replace_variables(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.replace_variables(item) for item in data]
        return data
        
    def verify_response(self, actual: Any, expected: Dict[str, Any]) -> bool:
        """验证响应结果
        
        Args:
            actual: 实际响应
            expected: 预期结果
            
        Returns:
            是否匹配
        """
        try:
            return deep_compare(actual, expected)
        except Exception as e:
            logger.error(f"响应验证失败: {str(e)}")
            return False

class ExcelTestCaseHandler(BaseTestCaseHandler):
    """Excel测试用例处理器"""
    def __init__(self, excel_path: str):
        super().__init__()
        self.excel_path = excel_path
        self.test_cases = self.load_test_cases()
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """从Excel文件加载测试用例
        
        Returns:
            测试用例列表
            
        Raises:
            TestCaseError: 加载失败
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
                    'method': str(row['method']).upper(),
                    'headers': json.loads(str(row['headers'])) if pd.notna(row.get('headers')) else {},
                    'data': json.loads(str(row['data'])) if pd.notna(row.get('data')) else {},
                    'expected': json.loads(str(row['expected'])) if pd.notna(row.get('expected')) else {},
                    'extract': json.loads(str(row['extract'])) if pd.notna(row.get('extract')) else {}
                }
                
                # 验证测试用例格式
                self.validate_test_case(case)
                test_cases.append(case)
                
            logger.info(f"成功从 {self.excel_path} 加载 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            raise TestCaseError(f"加载Excel测试用例失败: {str(e)}")

class YAMLTestCaseHandler(BaseTestCaseHandler):
    """YAML测试用例处理器"""
    def __init__(self, yaml_path: str):
        super().__init__()
        self.yaml_path = yaml_path
        self.test_cases = self.load_test_cases()
        
    def load_test_cases(self) -> List[Dict[str, Any]]:
        """加载YAML测试用例
        
        Returns:
            测试用例列表
            
        Raises:
            TestCaseError: 加载失败
        """
        try:
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                test_cases = yaml.safe_load(f)
                
            if not isinstance(test_cases, list):
                raise ValidationError("YAML文件必须包含测试用例列表")
                
            # 验证每个测试用例
            for case in test_cases:
                self.validate_test_case(case)
                
            # 按场景和步骤排序
            test_cases.sort(key=lambda x: (x['scenario'], x['step']))
            
            logger.info(f"成功从 {self.yaml_path} 加载 {len(test_cases)} 个测试用例")
            return test_cases
            
        except Exception as e:
            raise TestCaseError(f"加载YAML测试用例失败: {str(e)}")

# 向后兼容的别名
TestCaseHandler = ExcelTestCaseHandler 