#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
from .process_directory import process_directory

def parse_processor_options(images: bool, titles: bool, all_processors: bool, verbose: bool):
    """
    解析处理器选项，返回实际要使用的处理参数
    
    Args:
        images (bool): 是否启用图片处理
        titles (bool): 是否启用标题处理
        all_processors (bool): 是否启用所有处理器
        verbose (bool): 是否显示详细信息
        
    Returns:
        tuple: (process_images, process_titles)
    """
    if all_processors:
        process_images = True
        process_titles = True
        if verbose:
            print("启用所有处理逻辑：图片链接处理 + 标题格式处理")
    else:
        process_images = images
        process_titles = titles
        
        # 如果没有指定任何处理选项，默认启用所有
        if not process_images and not process_titles:
            if verbose:
                print("警告：未指定任何处理选项，默认启用所有处理逻辑")
                print("使用 --images 或 --titles 来选择性启用特定处理")
            process_images = True
            process_titles = True
        
        if verbose:
            enabled_processors = []
            if process_images:
                enabled_processors.append("图片链接处理")
            if process_titles:
                enabled_processors.append("标题格式处理")
            print(f"启用的处理逻辑：{' + '.join(enabled_processors)}")
    
    return process_images, process_titles

def main():
    """
    统一的MD文件预处理工具
    支持通过参数选择性启用不同的处理逻辑
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='MD文件预处理工具 - 统一入口')
    
    # 必需参数
    parser.add_argument('--input', '-i', 
                      required=True,
                      help='输入MD文件目录的路径')
    parser.add_argument('--output', '-o',
                      required=True,
                      help='输出MD文件目录的路径')
    
    # 处理选项
    parser.add_argument('--images', 
                      action='store_true',
                      help='启用图片链接处理')
    parser.add_argument('--titles', 
                      action='store_true',
                      help='启用标题格式处理')
    parser.add_argument('--all', 
                      action='store_true',
                      help='启用所有处理逻辑（等同于 --images --titles）')
    
    # 其他选项
    parser.add_argument('--verbose', '-v',
                      action='store_true',
                      help='显示详细信息')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 检查输入路径是否存在
    if not os.path.exists(args.input):
        print(f"错误：输入路径 '{args.input}' 不存在")
        sys.exit(1)
    
    # 解析处理器选项
    process_images, process_titles = parse_processor_options(
        args.images, args.titles, args.all, args.verbose
    )
    
    # 执行处理
    try:
        process_directory(
            input_dir=args.input,
            output_dir=args.output,
            verbose=args.verbose,
            process_images=process_images,
            process_titles=process_titles
        )
        print("MD文件预处理完成！")
        if args.verbose:
            print(f"输入目录: {args.input}")
            print(f"输出目录: {args.output}")
            
    except Exception as e:
        print(f"处理失败：{e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 