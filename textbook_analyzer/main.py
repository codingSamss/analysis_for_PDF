#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
教材分析工具主入口
用于统一调用各个模块的功能
"""

import argparse
import os
import sys
from typing import List
from textbook_analyzer.config import env_config

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
    preprocess_parser.add_argument('--images', action='store_true', help='启用图片链接处理')
    preprocess_parser.add_argument('--titles', action='store_true', help='启用标题格式处理')
    preprocess_parser.add_argument('--all', action='store_true', help='启用所有处理逻辑')
    preprocess_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')

    # 结构提取命令 - 新增支持指定文件和并发
    structure_parser = subparsers.add_parser('extract-structure', help='提取文档结构')
    
    # 输入选项（互斥）
    structure_input_group = structure_parser.add_mutually_exclusive_group(required=True)
    structure_input_group.add_argument('--input', '-i', help='输入MD文件目录路径')
    structure_input_group.add_argument('--files', '-f', nargs='+', help='指定要处理的MD文件路径列表')
    
    structure_parser.add_argument('--output', '-o', required=True, help='输出JSON文件目录路径')
    structure_parser.add_argument('--workers', '-w', type=int, default=4, help='最大并发工作线程数 (默认: 4)')
    structure_parser.add_argument('--no-resume', action='store_true', help='禁用断点续传，重新处理所有文件')
    structure_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')

    # 文化词条提取命令 - 新增支持指定文件和高级参数
    culture_parser = subparsers.add_parser('extract-culture', help='提取文化词条')
    
    # 输入选项（互斥）
    culture_input_group = culture_parser.add_mutually_exclusive_group(required=True)
    culture_input_group.add_argument('--input', '-i', help='输入JSON文件目录路径')
    culture_input_group.add_argument('--files', '-f', nargs='+', help='指定要处理的JSON文件路径列表')
    
    culture_parser.add_argument('--output', '-o', required=True, help='输出JSON文件目录路径')
    culture_parser.add_argument('--api_key', '-k', help='DeepSeek API密钥')
    culture_parser.add_argument('--concurrent', '-c', type=int, default=3, help='最大并发请求数 (默认: 3)')
    culture_parser.add_argument('--no-resume', action='store_true', help='禁用断点续传，从头开始处理')
    culture_parser.add_argument('--test', '-t', action='store_true', help='运行单个测试样例')
    culture_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    
    # 保留原有的async_mode参数以兼容
    culture_parser.add_argument('--async_mode', '-a', action='store_true', help='使用异步处理（默认启用）')
    culture_parser.add_argument('--retry', '-r', type=int, default=3, help='失败重试次数（兼容参数）')

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
        from textbook_analyzer.scripts.preprocess_md import parse_processor_options
        from textbook_analyzer.scripts.process_directory import process_directory
        
        # 检查输入路径
        if not os.path.exists(args.input):
            print(f"错误：输入路径 '{args.input}' 不存在")
            sys.exit(1)
        
        # 解析处理器选项
        process_images, process_titles = parse_processor_options(
            args.images, args.titles, args.all, getattr(args, 'verbose', True)
        )
        
        # 执行预处理
        try:
            process_directory(
                input_dir=args.input,
                output_dir=args.output,
                verbose=getattr(args, 'verbose', True),
                process_images=process_images,
                process_titles=process_titles
            )
            print("MD文件预处理完成！")
        except Exception as e:
            print(f"预处理失败：{e}")
            sys.exit(1)
    
    elif args.command == 'extract-structure':
        # 新的结构提取逻辑
        _handle_structure_extraction(args)
    
    elif args.command == 'extract-culture':
        # 新的文化词条提取逻辑
        _handle_culture_extraction(args)
    
    elif args.command == 'generate-excel':
        try:
            api_key = env_config.get_api_key(args.api_key)
        except ValueError as e:
            print(f"错误：{e}")
            sys.exit(1)
            
        from textbook_analyzer.analysis.culture_summarizer import summarize_culture_terms
        summarize_culture_terms(args.input, args.output, api_key, args.model)
    
    else:
        parser.print_help()
        sys.exit(1)


def _handle_structure_extraction(args):
    """处理结构提取命令"""
    from textbook_analyzer.preprocessors.structure_extractor_enhanced import extract_structure_batch, extract_structure_directory
    
    if args.input:
        # 目录模式
        if not os.path.exists(args.input):
            print(f"错误：输入目录 '{args.input}' 不存在")
            sys.exit(1)
        
        print(f"模式：目录处理")
        print(f"输入目录: {args.input}")
        print(f"输出目录: {args.output}")
        print(f"最大并发数: {args.workers}")
        print(f"断点续传: {'禁用' if args.no_resume else '启用'}")
        print("-" * 50)
        
        # 处理整个目录
        processed_files = extract_structure_directory(
            input_dir=args.input,
            output_dir=args.output,
            max_workers=args.workers,
            resume=not args.no_resume,
            verbose=args.verbose
        )
        
    elif args.files:
        # 指定文件模式
        input_files = args.files
        
        # 检查文件是否存在
        missing_files = []
        existing_files = []
        for file_path in input_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            elif not file_path.endswith('.md'):
                print(f"警告：跳过非MD文件 '{file_path}'")
            else:
                existing_files.append(file_path)
        
        if missing_files:
            print("错误：以下文件不存在:")
            for file_path in missing_files:
                print(f"  - {file_path}")
            sys.exit(1)
        
        if not existing_files:
            print("错误：没有找到有效的MD文件")
            sys.exit(1)
        
        print(f"模式：指定文件处理")
        print(f"待处理文件数: {len(existing_files)}")
        print(f"输出目录: {args.output}")
        print(f"最大并发数: {args.workers}")
        print(f"断点续传: {'禁用' if args.no_resume else '启用'}")
        print("文件列表:")
        for i, file_path in enumerate(existing_files, 1):
            print(f"  {i}. {os.path.basename(file_path)}")
        print("-" * 50)
        
        # 处理指定文件
        processed_files = extract_structure_batch(
            input_files=existing_files,
            output_dir=args.output,
            max_workers=args.workers,
            resume=not args.no_resume,
            verbose=args.verbose
        )
    
    # 显示处理结果
    print("\n" + "=" * 50)
    if processed_files:
        print(f"✅ 结构提取完成！成功处理了 {len(processed_files)} 个文件")
        print("生成的JSON文件:")
        for file_path in processed_files:
            print(f"  - {os.path.basename(file_path)}")
    else:
        print("ℹ️ 没有新文件需要处理（可能都已存在，使用 --no-resume 强制重新处理）")
    print("=" * 50)


def _handle_culture_extraction(args):
    """处理文化词条提取命令"""
    try:
        api_key = env_config.get_api_key(args.api_key)
    except ValueError as e:
        print(f"错误：{e}")
        sys.exit(1)
    
    if args.test:
        # 运行测试样例
        from textbook_analyzer.llm.async_culture_extractor import test_extract_single_node
        test_content = """
        在中国传统文化中，孝道是一种重要的价值观念。尊老爱幼体现了中华民族的传统美德。
        红色革命精神激励着一代又一代人前进。井冈山精神和长征精神是中国革命文化的重要组成部分。
        中国共产党领导人民创造了社会主义先进文化，科学发展观和中国特色社会主义理论体系指导着国家建设。
        """
        print("运行测试样例...")
        test_extract_single_node(api_key, test_content)
        return
    
    if args.input:
        # 目录模式
        if not os.path.exists(args.input):
            print(f"错误：输入目录 '{args.input}' 不存在")
            sys.exit(1)
        
        print(f"模式：目录处理")
        print(f"输入目录: {args.input}")
        print(f"输出目录: {args.output}")
        print(f"最大并发数: {args.concurrent}")
        print(f"断点续传: {'禁用' if args.no_resume else '启用'}")
        print("-" * 50)
        
        # 处理整个目录
        from textbook_analyzer.llm.async_culture_extractor import extract_culture_terms
        extract_culture_terms(
            args.input, 
            args.output, 
            api_key, 
            max_concurrent=args.concurrent, 
            resume=not args.no_resume, 
            verbose=args.verbose
        )
        
    elif args.files:
        # 指定文件模式
        input_files = args.files
        
        # 检查文件是否存在
        missing_files = []
        existing_files = []
        for file_path in input_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
            elif not file_path.endswith('.json'):
                print(f"警告：跳过非JSON文件 '{file_path}'")
            else:
                existing_files.append(file_path)
        
        if missing_files:
            print("错误：以下文件不存在:")
            for file_path in missing_files:
                print(f"  - {file_path}")
            sys.exit(1)
        
        if not existing_files:
            print("错误：没有找到有效的JSON文件")
            sys.exit(1)
        
        print(f"模式：指定文件处理")
        print(f"待处理文件数: {len(existing_files)}")
        print(f"输出目录: {args.output}")
        print(f"最大并发数: {args.concurrent}")
        print(f"断点续传: {'禁用' if args.no_resume else '启用'}")
        print("文件列表:")
        for i, file_path in enumerate(existing_files, 1):
            print(f"  {i}. {os.path.basename(file_path)}")
        print("-" * 50)
        
        # 处理指定文件
        _extract_culture_terms_batch(
            input_files=existing_files,
            output_dir=args.output,
            api_key=api_key,
            max_concurrent=args.concurrent,
            resume=not args.no_resume,
            verbose=args.verbose
        )
    
    print("\n" + "=" * 50)
    print("✅ 文化词条提取完成！")
    print("=" * 50)


def _extract_culture_terms_batch(input_files: List[str], output_dir: str, api_key: str = None, 
                                max_concurrent: int = 3, resume: bool = True, verbose: bool = False) -> List[str]:
    """
    批量提取文化词条
    
    Args:
        input_files (List[str]): 输入JSON文件路径列表
        output_dir (str): 输出目录
        api_key (str, optional): DeepSeek API密钥
        max_concurrent (int): 最大并发请求数
        resume (bool): 是否从上次中断处继续
        verbose (bool): 是否显示详细信息
        
    Returns:
        List[str]: 处理成功的文件列表
    """
    import asyncio
    from textbook_analyzer.llm.async_culture_extractor import AsyncCultureExtractor
    
    async def process_batch():
        # 创建提取器
        extractor = AsyncCultureExtractor(api_key, max_concurrent)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 处理每个文件
        processed_files = []
        for i, input_file in enumerate(input_files, 1):
            print(f"处理文件 {i}/{len(input_files)}: {os.path.basename(input_file)}")
            
            # 生成输出文件名
            output_file = os.path.basename(input_file).replace('.json', '_culture.json')
            output_path = os.path.join(output_dir, output_file)
            
            # 如果不是续传模式，或者输出文件不存在，则处理文件
            if not resume or not os.path.exists(output_path):
                if await extractor.process_file(input_file, output_path, resume):
                    processed_files.append(output_path)
            else:
                print(f"文件已处理，跳过: {os.path.basename(output_path)}")
                processed_files.append(output_path)
        
        return processed_files
    
    return asyncio.run(process_batch())

if __name__ == "__main__":
    main() 