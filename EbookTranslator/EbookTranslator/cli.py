#!/usr/bin/env python3
"""
EbookTranslator的命令行界面
"""

import argparse
import sys
import os
from pathlib import Path
from .main_function import main_function


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description='翻译PDF文档')
    parser.add_argument('pdf_path', type=str, help='PDF文件路径')
    parser.add_argument('-o', '--original', default='auto', help='原始语言 (默认: auto)')
    parser.add_argument('-t', '--target', default='zh', help='目标语言 (默认: zh)')
    parser.add_argument('-b', '--begin', type=int, default=1, help='开始页码 (默认: 1)')
    parser.add_argument('-e', '--end', type=int, default=None, help='结束页码 (默认: 最后一页)')
    parser.add_argument('-c', '--config', type=str, default=None, help='配置文件路径')
    parser.add_argument('-d', '--dpi', type=int, default=72, help='OCR模式的DPI (默认: 72)')

    args = parser.parse_args()

    # 检查PDF文件是否存在
    print('路径',args.pdf_path)

    if not os.path.exists(args.pdf_path):
        print(f"错误: 找不到文件 '{args.pdf_path}'")
        sys.exit(1)

    try:
        # 运行主函数
        translator = main_function(
            pdf_path=args.pdf_path,
            original_language=args.original,
            target_language=args.target,
            bn=args.begin,
            en=args.end,
            config_path=args.config,
            DPI=args.dpi
        )
        translator.main()
        print(f"翻译完成! 输出文件保存在 target 目录")
    except Exception as e:
        print(f"翻译过程中发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
