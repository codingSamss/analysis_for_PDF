import os
from pathlib import Path
from typing import List

def ensure_dir(directory: str) -> None:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str): 目录路径
    """
    os.makedirs(directory, exist_ok=True)

def get_md_files(directory: str) -> List[Path]:
    """
    获取目录下所有MD文件
    
    Args:
        directory (str): 目录路径
        
    Returns:
        List[Path]: MD文件路径列表
    """
    return list(Path(directory).glob('**/*.md'))

def get_relative_path(file_path: str, base_dir: str) -> str:
    """
    获取文件相对于基础目录的路径
    
    Args:
        file_path (str): 文件路径
        base_dir (str): 基础目录
        
    Returns:
        str: 相对路径
    """
    return os.path.relpath(file_path, base_dir)

def create_output_path(input_path: str, input_dir: str, output_dir: str) -> str:
    """
    创建输出文件路径
    
    Args:
        input_path (str): 输入文件路径
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        
    Returns:
        str: 输出文件路径
    """
    rel_path = get_relative_path(input_path, input_dir)
    output_path = os.path.join(output_dir, rel_path)
    ensure_dir(os.path.dirname(output_path))
    return output_path 