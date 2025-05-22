#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from ..preprocessors.structure_extractor import process_manual_processed_files

def main():
    """
    主函数：处理命令行参数并执行结构提取
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='MD文件结构提取工具')
    parser.add_argument('--input', '-i', 
                      default="/Users/suqi3/Desktop/paper/textbook_analyzer/data/md/manual_processed",
                      help='输入MD文件目录的路径')
    parser.add_argument('--output', '-o',
                      default="/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/structure",
                      help='输出JSON文件目录的路径')
    parser.add_argument('--verbose', '-v',
                      action='store_true',
                      help='显示详细信息')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查输入路径是否存在
    if not os.path.exists(args.input):
        print(f"错误：输入路径 '{args.input}' 不存在")
        sys.exit(1)
    
    # 处理目录
    process_manual_processed_files(args.input, args.output, args.verbose)
    print("结构提取完成！")

if __name__ == "__main__":
    main() 