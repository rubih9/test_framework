import argparse
import sys
from lib.core.test_runner import run_tests
from lib.utils.exceptions import TestFrameworkError
from loguru import logger

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='API测试框架')
    parser.add_argument(
        '-c', '--config',
        required=True,
        help='配置文件路径'
    )
    parser.add_argument(
        '-e', '--email-config',
        help='邮件配置文件路径'
    )
    return parser.parse_args()

def main():
    """主函数"""
    try:
        args = parse_args()
        run_tests(args.config, args.email_config)
    except TestFrameworkError as e:
        logger.error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("测试执行被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.exception("测试执行过程中发生未知错误")
        sys.exit(1)

if __name__ == '__main__':
    main() 