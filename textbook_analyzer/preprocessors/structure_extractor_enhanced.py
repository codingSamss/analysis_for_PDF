#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("StructureExtractor")

class StructureExtractor:
    """MD文件结构提取器，支持并发和断点续传"""
    
    def __init__(self, max_workers: int = 4):
        """
        初始化结构提取器
        
        Args:
            max_workers (int): 最大并发工作线程数
        """
        self.max_workers = max_workers
    
    def extract_structure_from_md(self, file_path: str) -> Dict[str, Any]:
        """
        从MD文件提取结构化信息
        
        Args:
            file_path (str): MD文件路径
            
        Returns:
            Dict[str, Any]: 结构化数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 构建文档结构
            structure = {
                "title": os.path.basename(file_path).replace('.md', ''),
                "level": 0,
                "content": "",
                "children": []
            }
            
            # 按标题层级分割内容
            sections = self._split_by_headers(content)
            
            # 构建层级结构
            stack = [structure]  # 用于跟踪当前的层级结构
            
            for section in sections:
                level = section["level"]
                title = section["title"]
                content = section["content"]
                
                # 创建新节点
                new_node = {
                    "title": title,
                    "level": level,
                    "content": content.strip(),
                    "children": []
                }
                
                # 根据层级决定插入位置
                if level == 1:
                    # 一级标题，直接添加到根结构
                    structure["children"].append(new_node)
                    stack = [structure, new_node]
                elif level > 1:
                    # 多级标题，找到合适的父节点
                    while len(stack) > level and len(stack) > 1:
                        stack.pop()
                    
                    if len(stack) == 0:
                        stack = [structure]
                    
                    # 添加到当前层级的父节点
                    parent = stack[-1]
                    parent["children"].append(new_node)
                    
                    # 更新堆栈
                    if level >= len(stack):
                        stack.append(new_node)
                    else:
                        stack = stack[:level] + [new_node]
                else:
                    # level 0，添加到根内容
                    if structure["content"]:
                        structure["content"] += "\n\n" + content.strip()
                    else:
                        structure["content"] = content.strip()
            
            return structure
            
        except Exception as e:
            logger.error(f"提取文件 {file_path} 结构时出错: {e}")
            return None
    
    def _split_by_headers(self, content: str) -> List[Dict[str, Any]]:
        """
        按标题分割内容
        
        Args:
            content (str): MD文件内容
            
        Returns:
            List[Dict[str, Any]]: 分割后的段落列表
        """
        sections = []
        lines = content.split('\n')
        
        current_section = {
            "level": 0,
            "title": "文档开始",
            "content": ""
        }
        
        for line in lines:
            # 检测标题行
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            
            if header_match:
                # 保存当前段落
                if current_section["content"].strip() or current_section["title"] != "文档开始":
                    sections.append(current_section)
                
                # 开始新段落
                level = len(header_match.group(1))  # # 的数量
                title = header_match.group(2).strip()
                
                current_section = {
                    "level": level,
                    "title": title,
                    "content": ""
                }
            else:
                # 添加到当前段落内容
                current_section["content"] += line + '\n'
        
        # 添加最后一个段落
        if current_section["content"].strip() or current_section["title"] != "文档开始":
            sections.append(current_section)
        
        return sections
    
    def process_file(self, input_path: str, output_path: str) -> bool:
        """
        处理单个MD文件
        
        Args:
            input_path (str): 输入MD文件路径
            output_path (str): 输出JSON文件路径
            
        Returns:
            bool: 是否成功处理
        """
        try:
            logger.info(f"开始处理文件: {os.path.basename(input_path)}")
            start_time = time.time()
            
            # 提取结构
            structure = self.extract_structure_from_md(input_path)
            
            if structure is None:
                return False
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存JSON文件
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(structure, f, ensure_ascii=False, indent=2)
            
            end_time = time.time()
            logger.info(f"文件处理完成: {os.path.basename(output_path)} (耗时: {end_time - start_time:.2f}秒)")
            
            return True
            
        except Exception as e:
            logger.error(f"处理文件 {input_path} 时出错: {e}")
            return False
    
    def process_files(self, input_files: List[str], output_dir: str, resume: bool = True) -> List[str]:
        """
        并发处理多个MD文件，支持断点续传
        
        Args:
            input_files (List[str]): 输入MD文件路径列表
            output_dir (str): 输出目录
            resume (bool): 是否启用断点续传
            
        Returns:
            List[str]: 成功处理的文件列表
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 准备任务列表
        tasks = []
        for input_path in input_files:
            file_name = os.path.basename(input_path).replace('.md', '.json')
            output_path = os.path.join(output_dir, file_name)
            
            # 断点续传：跳过已存在的文件
            if resume and os.path.exists(output_path):
                logger.info(f"文件已存在，跳过: {os.path.basename(output_path)}")
                continue
            
            tasks.append((input_path, output_path))
        
        if not tasks:
            logger.info("所有文件都已处理完成")
            return []
        
        logger.info(f"开始并发处理 {len(tasks)} 个文件，最大并发数: {self.max_workers}")
        
        processed_files = []
        
        # 使用线程池并发处理
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.process_file, input_path, output_path): (input_path, output_path)
                for input_path, output_path in tasks
            }
            
            # 处理完成的任务
            for future in as_completed(future_to_task):
                input_path, output_path = future_to_task[future]
                try:
                    success = future.result()
                    if success:
                        processed_files.append(output_path)
                        logger.info(f"处理进度: {len(processed_files)}/{len(tasks)}")
                except Exception as e:
                    logger.error(f"处理文件 {input_path} 时发生异常: {e}")
        
        return processed_files
    
    def process_directory(self, input_dir: str, output_dir: str, resume: bool = True) -> List[str]:
        """
        处理目录中的所有MD文件
        
        Args:
            input_dir (str): 输入目录
            output_dir (str): 输出目录
            resume (bool): 是否启用断点续传
            
        Returns:
            List[str]: 成功处理的文件列表
        """
        # 获取所有MD文件
        md_files = []
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.md'):
                md_files.append(os.path.join(input_dir, file_name))
        
        logger.info(f"找到 {len(md_files)} 个MD文件")
        
        return self.process_files(md_files, output_dir, resume)


def extract_structure_batch(input_files: List[str], output_dir: str, max_workers: int = 4, resume: bool = True, verbose: bool = False) -> List[str]:
    """
    批量提取MD文件结构
    
    Args:
        input_files (List[str]): 输入MD文件路径列表
        output_dir (str): 输出目录
        max_workers (int): 最大并发工作线程数
        resume (bool): 是否启用断点续传
        verbose (bool): 是否显示详细信息
        
    Returns:
        List[str]: 成功处理的文件列表
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("=" * 50)
    logger.info("批量结构提取开始")
    logger.info("=" * 50)
    logger.info(f"最大并发数: {max_workers}")
    logger.info(f"断点续传: {'启用' if resume else '禁用'}")
    logger.info(f"待处理文件数: {len(input_files)}")
    
    extractor = StructureExtractor(max_workers)
    processed_files = extractor.process_files(input_files, output_dir, resume)
    
    logger.info("=" * 50)
    logger.info("批量结构提取完成")
    logger.info(f"成功处理: {len(processed_files)} 个文件")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 50)
    
    return processed_files


def extract_structure_directory(input_dir: str, output_dir: str, max_workers: int = 4, resume: bool = True, verbose: bool = False) -> List[str]:
    """
    提取目录中所有MD文件的结构
    
    Args:
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        max_workers (int): 最大并发工作线程数
        resume (bool): 是否启用断点续传
        verbose (bool): 是否显示详细信息
        
    Returns:
        List[str]: 成功处理的文件列表
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("=" * 50)
    logger.info("目录结构提取开始")
    logger.info("=" * 50)
    logger.info(f"输入目录: {input_dir}")
    logger.info(f"输出目录: {output_dir}")
    logger.info(f"最大并发数: {max_workers}")
    logger.info(f"断点续传: {'启用' if resume else '禁用'}")
    
    extractor = StructureExtractor(max_workers)
    processed_files = extractor.process_directory(input_dir, output_dir, resume)
    
    logger.info("=" * 50)
    logger.info("目录结构提取完成")
    logger.info(f"成功处理: {len(processed_files)} 个文件")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 50)
    
    return processed_files


# 兼容性函数
def process_manual_processed_files(input_dir: str, output_dir: str, verbose: bool = False) -> None:
    """兼容性函数，保持与原版的接口一致"""
    extract_structure_directory(input_dir, output_dir, verbose=verbose) 