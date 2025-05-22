from pathlib import Path
from ..preprocessors.md_preprocessor import MDPreprocessor
from ..utils.file_utils import get_md_files, ensure_dir

def process_directory(input_dir: str, output_dir: str, verbose: bool = False) -> None:
    """
    处理指定目录下的所有MD文件
    
    Args:
        input_dir (str): 输入目录路径
        output_dir (str): 输出目录路径
        verbose (bool): 是否显示详细信息
    """
    # 确保输出目录存在
    ensure_dir(output_dir)
    
    # 获取所有MD文件
    md_files = get_md_files(input_dir)
    
    if verbose:
        print(f"找到 {len(md_files)} 个MD文件")
    
    # 创建预处理器实例
    processor = MDPreprocessor(input_dir, output_dir)
    
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