#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from ..analysis.culture_summarizer import summarize_culture_terms
from ..config import env_config

def main():
    """
    主函数：处理命令行参数并执行文化词条整理
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='生成文化词条Excel表格')
    parser.add_argument('--input', type=str, default='textbook_analyzer/data/json/culture',
                      help='输入目录路径')
    parser.add_argument('--output', type=str, default='textbook_analyzer/data/excel',
                      help='输出目录路径')
    parser.add_argument('--api_key', type=str,
                      help='DeepSeek API密钥')
    parser.add_argument('--model', type=str, default='deepseek-reasoner',
                      choices=['deepseek-reasoner', 'deepseek-chat'],
                      help='使用的模型名称，可选 deepseek-reasoner 或 deepseek-chat')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理API密钥
    try:
        api_key = env_config.get_api_key(args.api_key)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)
    
    # 确保输入输出目录存在
    os.makedirs(args.input, exist_ok=True)
    os.makedirs(args.output, exist_ok=True)
    
    # 处理目录
    print(f"开始处理目录: {args.input}")
    print(f"输出目录: {args.output}")
    
    # 调用整理函数
    summarize_culture_terms(args.input, args.output, api_key, args.model)
    
    print("文化词条整理完成！Excel表格已生成。")

if __name__ == "__main__":
    main() 