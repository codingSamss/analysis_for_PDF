#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from ..llm.culture_extractor import CultureExtractor

def test_single_node():
    """
    测试单个节点的文化词条提取
    """
    # 设置API密钥
    api_key = "sk-902aa20f11b64094a87cc3344ca10684"
    
    # 创建提取器实例
    extractor = CultureExtractor(api_key)
    
    # 读取JSON文件
    input_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/structure"
    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
    
    if not json_files:
        print("未找到JSON文件")
        return
    
    # 使用第一个JSON文件
    input_path = os.path.join(input_dir, json_files[0])
    print(f"使用文件: {input_path}")
    
    # 读取JSON文件
    with open(input_path, 'r', encoding='utf-8') as f:
        structure = json.load(f)
    
    # 找到第一个有内容的节点
    def find_first_content_node(node, path=None):
        if path is None:
            path = []
            
        # 检查当前节点
        if node.get("content", "").strip():
            return node, path
            
        # 检查子节点
        for child in node.get("children", []):
            new_path = path + [node.get("title", "")]
            result = find_first_content_node(child, new_path)
            if result:
                return result
                
        return None, None
    
    # 查找第一个有内容的节点
    node, path = find_first_content_node(structure)
    
    if not node:
        print("未找到有内容的节点")
        return
    
    print("\n节点信息:")
    print(f"标题: {node.get('title', '')}")
    print(f"层级: {node.get('level', 0)}")
    print(f"路径: {' > '.join(path) if path else '根节点'}")
    print(f"内容: {node.get('content', '')[:200]}...")  # 只显示前200个字符
    
    # 提取文化词条
    print("\n开始提取文化词条...")
    result = extractor.extract_from_node(node, path)
    
    # 打印结果
    if result:
        print("\n提取结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("提取失败")

if __name__ == "__main__":
    test_single_node() 