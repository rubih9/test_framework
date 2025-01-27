# API测试框架

一个简单但功能强大的API测试框架，支持Excel和YAML格式的测试用例，提供美观的HTML测试报告和邮件通知功能。

## 特性

- 支持Excel和YAML格式的测试用例
- 支持多平台API测试
- 支持变量提取和引用
- 支持深度响应验证
- 美观的HTML测试报告
- 邮件通知功能
- 完善的日志记录
- 异步HTTP请求
- 自动重试机制

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/rubih9/test_framework.git
cd test_framework
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 配置

### 主配置文件 (config/config.yaml)

```yaml
# API基础URL配置
base_urls:
  default: "http://api.example.com"
  platform1: "http://api1.example.com"
  platform2: "http://api2.example.com"

# 超时设置（秒）
timeout: 30

# 测试用例文件路径
test_case_path: "testcases/test_cases.xlsx"  # 或 "testcases/test_cases.yaml"

# 日志路径
log_path: "logs"

# 报告路径
report_path: "reports"

# 报告标题
report_title: "API测试报告"
```

### 邮件配置文件 (config/email_config.yaml)

```yaml
# 发件人配置
sender: "your-email@example.com"
password: "your-password"
smtp_server: "smtp.example.com"
smtp_port: 587

# 收件人列表
recipients:
  - "recipient1@example.com"
  - "recipient2@example.com"

# 仅在测试失败时发送邮件
send_on_fail_only: true
```

## 测试用例格式

### Excel格式

创建一个Excel文件，包含以下列（testcase中有可参考内容）：

- case_id: 用例ID
- scenario: 场景名称
- step: 步骤序号
- description: 用例描述
- api: API路径
- method: HTTP方法
- headers: 请求头（JSON格式）
- data: 请求数据（JSON格式）
- expected: 预期结果（JSON格式）
- extract: 变量提取规则（JSON格式）

### YAML格式

```yaml
- case_id: "test_001"
  scenario: "用户管理"
  step: 1
  description: "创建用户"
  api: "users"
  method: "POST"
  headers:
    Content-Type: "application/json"
  data:
    name: "测试用户"
    email: "test@example.com"
  expected:
    code: 200
    message: "success"
  extract:
    user_id: "data.id"
```

## 使用方法

1. 准备配置文件和测试用例

2. 运行测试：

```bash
python run.py -c config/config.yaml -e config/email_config.yaml
```

## 目录结构

```text
test_framework/
├── config/
│   ├── config.yaml
│   └── email_config.yaml
├── lib/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── config.py
│   │   └── test_runner.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── test_case_handler.py
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── html_reporter.py
│   │   └── email_sender.py
│   └── utils/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── helpers.py
│       └── logger.py
├── logs/
├── reports/
├── testcases/
│   ├── test_cases.xlsx
│   └── test_cases.yaml
├── requirements.txt
├── README.md
└── run.py
```

## 常见问题

1. SSL证书验证失败
   - 在API请求时设置 `verify_ssl=False`

2. 邮件发送失败
   - 检查SMTP服务器配置
   - 确保密码正确
   - 检查防火墙设置

3. 测试用例格式错误
   - 检查JSON格式是否正确
   - 确保所有必要字段都已填写

## 许可证

MIT License
