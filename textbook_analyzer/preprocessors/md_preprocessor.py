import os
import re
from typing import List, Optional
from pathlib import Path
from .image_processor import ImageProcessor
from .title_processor import TitleProcessor

class MDPreprocessor:
    def __init__(self, md_dir: str, output_dir: str):
        """
        初始化MD预处理器
        
        Args:
            md_dir (str): MD文件所在目录
            output_dir (str): 输出目录
        """
        self.md_dir = md_dir
        self.output_dir = output_dir
        self.image_processor = ImageProcessor()
        self.title_processor = TitleProcessor()
        
    def process_single_file(self, md_path: str) -> Optional[str]:
        """
        处理单个MD文件
        
        Args:
            md_path (str): MD文件路径
            
        Returns:
            Optional[str]: 处理后的文件路径，如果处理失败则返回None
        """
        try:
            # 读取文件内容
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 处理图片链接
            content = self.image_processor.process_images(content)
            
            # 2. 处理标题
            content = self.title_processor.process_titles(content)
            
            # 生成输出文件路径
            output_path = self._get_output_path(md_path)
            
            # 保存处理后的内容
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return output_path
            
        except Exception as e:
            print(f"处理文件 {md_path} 时出错: {e}")
            return None
            
    def _get_output_path(self, md_path: str) -> str:
        """
        生成输出文件路径
        
        Args:
            md_path (str): 输入文件路径
            
        Returns:
            str: 输出文件路径
        """
        # 获取相对路径
        rel_path = os.path.relpath(md_path, self.md_dir)
        # 生成输出路径
        output_path = os.path.join(self.output_dir, rel_path)
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return output_path 