#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
教材分析工具主入口
用于统一调用各个模块的功能
"""

import argparse
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def main():
    """
    主函数：解析命令行参数，分发到对应的功能模块
    """
    parser = argparse.ArgumentParser(description='教材分析工具 - 提取和分析教材中的文化词条')
    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 预处理命令
    preprocess_parser = subparsers.add_parser('preprocess', help='预处理MD文件')
    preprocess_parser.add_argument('--input', '-i', required=True, help='输入文件或目录路径')
    preprocess_parser.add_argument('--output', '-o', required=True, help='输出目录路径')

    # 结构提取命令
    structure_parser = subparsers.add_parser('extract-structure', help='提取文档结构')
    structure_parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    structure_parser.add_argument('--output', '-o', required=True, help='输出JSON文件路径')

    # 文化词条提取命令
    culture_parser = subparsers.add_parser('extract-culture', help='提取文化词条')
    culture_parser.add_argument('--input', '-i', required=True, help='输入文件或目录路径')
    culture_parser.add_argument('--output', '-o', required=True, help='输出目录路径')
    culture_parser.add_argument('--api_key', '-k', help='DeepSeek API密钥')
    culture_parser.add_argument('--async_mode', '-a', action='store_true', help='使用异步处理提高效率')
    culture_parser.add_argument('--retry', '-r', type=int, default=3, help='失败重试次数')

    # Excel生成命令
    excel_parser = subparsers.add_parser('generate-excel', help='生成Excel表格')
    excel_parser.add_argument('--input', '-i', required=True, help='输入JSON目录路径')
    excel_parser.add_argument('--output', '-o', required=True, help='输出Excel目录路径')
    excel_parser.add_argument('--api_key', '-k', help='DeepSeek API密钥')
    excel_parser.add_argument('--model', '-m', default='deepseek-reasoner', 
                             choices=['deepseek-reasoner', 'deepseek-chat'],
                             help='使用的模型名称')

    # 解析命令行参数
    args = parser.parse_args()

    # 处理命令
    if args.command == 'preprocess':
        from textbook_analyzer.scripts.process_directory import process_directory
        process_directory(args.input, args.output)
    
    elif args.command == 'extract-structure':
        from textbook_analyzer.scripts.extract_structure import extract_structure
        extract_structure(args.input, args.output)
    
    elif args.command == 'extract-culture':
        api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("错误：未提供DeepSeek API密钥，请通过--api_key参数或环境变量DEEPSEEK_API_KEY提供")
            sys.exit(1)
            
        if args.async_mode:
            from textbook_analyzer.scripts.extract_culture_async import extract_culture_async
            extract_culture_async(args.input, args.output, api_key, args.retry)
        else:
            from textbook_analyzer.scripts.extract_culture import extract_culture
            extract_culture(args.input, args.output, api_key)
    
    elif args.command == 'generate-excel':
        api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            print("错误：未提供DeepSeek API密钥，请通过--api_key参数或环境变量DEEPSEEK_API_KEY提供")
            sys.exit(1)
            
        from textbook_analyzer.analysis.culture_summarizer import summarize_culture_terms
        summarize_culture_terms(args.input, args.output, api_key, args.model)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main() 