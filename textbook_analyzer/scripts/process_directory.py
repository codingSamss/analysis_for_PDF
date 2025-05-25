from pathlib import Path
from ..preprocessors.md_preprocessor import MDPreprocessor
from ..utils.file_utils import get_md_files, ensure_dir
import os

def process_directory(input_dir: str, output_dir: str, verbose: bool = False, 
                     process_images: bool = True, process_titles: bool = True) -> None:
    """
    处理指定目录下的所有MD文件
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        verbose (bool): 是否显示详细信息
        process_images (bool): 是否处理图片链接，默认True
        process_titles (bool): 是否处理标题，默认True
    """
    # 确保输出目录存在
    ensure_dir(output_dir)
    
    # 获取所有MD文件
    md_files = get_md_files(input_dir)
    
    if verbose:
        print(f"找到 {len(md_files)} 个MD文件")
    
    # 创建预处理器实例
    processor = MDPreprocessor(input_dir, output_dir, process_images, process_titles)
    
    # 处理每个文件
    for md_file in md_files:
        try:
            if verbose:
                print(f"处理文件: {md_file}")
            
            # 处理文件
            result = processor.process_single_file(str(md_file))
            
            if result and verbose:
                print(f"处理完成: {result}")
                
        except Exception as e:
            print(f"处理文件 {md_file} 时出错: {e}")
            continue

def process_specific_files(file_paths: list, output_dir: str, verbose: bool = False,
                          process_images: bool = True, process_titles: bool = True) -> None:
    """
    处理指定的MD文件列表
    
    Args:
        file_paths (list): MD文件路径列表
        output_dir (str): 输出目录路径
        verbose (bool): 是否显示详细信息
        process_images (bool): 是否处理图片链接，默认True
        process_titles (bool): 是否处理标题，默认True
    """
    # 确保输出目录存在
    ensure_dir(output_dir)
    
    if verbose:
        print(f"准备处理 {len(file_paths)} 个指定文件")
    
    # 验证文件存在性
    valid_files = []
    for file_path in file_paths:
        if os.path.exists(file_path) and file_path.endswith('.md'):
            valid_files.append(file_path)
        else:
            print(f"警告：文件不存在或不是MD文件: {file_path}")
    
    if not valid_files:
        print("错误：没有找到有效的MD文件")
        return
    
    if verbose:
        print(f"有效文件数量: {len(valid_files)}")
    
    # 处理每个文件
    for file_path in valid_files:
        try:
            if verbose:
                print(f"处理文件: {file_path}")
            
            # 为每个文件创建独立的处理器，使用文件所在目录作为输入目录
            input_dir = os.path.dirname(file_path)
            processor = MDPreprocessor(input_dir, output_dir, process_images, process_titles)
            
            # 处理文件
            result = processor.process_single_file(file_path)
            
            if result and verbose:
                print(f"处理完成: {result}")
                
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")
            continue 