# API Automation Test Framework

一个强大的接口自动化测试框架，支持以下特性：

- 📝 从Excel文件读取测试用例
- 🔄 支持场景化测试（如：创建-查询-删除等连贯操作）
- 📊 自动生成HTML测试报告
- 📧 邮件通知功能
- 📝 完整的日志记录
- ⚙️ 灵活的配置管理

## 安装

```bash
pip install -r requirements.txt
```

## 目录结构

``` text
test_framework/
├── config/                 # 配置文件目录
│   ├── config.yaml        # 主配置文件
│   └── email_config.yaml  # 邮件配置
├── testcases/             # 测试用例目录
│   └── test_cases.xlsx    # Excel测试用例
├── logs/                  # 日志目录
├── reports/               # 测试报告目录
├── lib/                   # 框架核心库
└── run.py                 # 启动文件
```

## Excel用例格式

测试用例Excel文件包含以下列：

- `case_id`: 用例ID
- `scenario`: 场景名称
- `step`: 步骤序号
- `description`: 用例描述
- `api`: 接口路径
- `method`: 请求方法(GET/POST/PUT/DELETE)
- `headers`: 请求头
- `data`: 请求数据
- `expected`: 预期结果
- `extract`: 需要提取的变量
- `depends`: 依赖的步骤

## 运行测试

```bash
python run.py
```

## 配置文件说明

config.yaml示例：

``` yaml
base_url: http://api.example.com
test_case_path: testcases/
report_path: reports/
log_path: logs/
```

email_config.yaml示例：

```yaml
smtp_server: smtp.example.com
smtp_port: 587
sender: sender@example.com
password: your_password
receivers:
  - receiver1@example.com
  - receiver2@example.com
```
