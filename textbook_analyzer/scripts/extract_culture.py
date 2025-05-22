#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from ..llm.culture_extractor import extract_culture_terms, test_extract_single_node

def main():
    """
    主函数：处理命令行参数并执行文化词条提取
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='文化词条提取工具')
    parser.add_argument('--input', '-i', 
                      default="/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/structure",
                      help='输入JSON文件目录的路径')
    parser.add_argument('--output', '-o',
                      default="/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/culture",
                      help='输出JSON文件目录的路径')
    parser.add_argument('--api_key', '-k',
                      help='DeepSeek API密钥')
    parser.add_argument('--test', '-t',
                      action='store_true',
                      help='运行单个测试样例')
    parser.add_argument('--verbose', '-v',
                      action='store_true',
                      help='显示详细信息')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 处理API密钥
    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误：未提供DeepSeek API密钥。请使用--api_key参数或设置DEEPSEEK_API_KEY环境变量。")
        sys.exit(1)
    
    if args.test:
        # 运行测试样例
        test_content = """
        在中国传统文化中，孝道是一种重要的价值观念。尊老爱幼体现了中华民族的传统美德。
        红色革命精神激励着一代又一代人前进。井冈山精神和长征精神是中国革命文化的重要组成部分。
        中国共产党领导人民创造了社会主义先进文化，科学发展观和中国特色社会主义理论体系指导着国家建设。
        """
        print("运行测试样例...")
        test_extract_single_node(api_key, test_content)
    else:
        # 检查输入路径是否存在
        if not os.path.exists(args.input):
            print(f"错误：输入路径 '{args.input}' 不存在")
            sys.exit(1)
        
        # 处理目录
        print(f"开始处理目录: {args.input}")
        print(f"输出目录: {args.output}")
        extract_culture_terms(args.input, args.output, api_key, args.verbose)
        print("文化词条提取完成！")

if __name__ == "__main__":
    main() 