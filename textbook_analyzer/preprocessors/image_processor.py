import os
import re
from typing import List, Tuple

class ImageProcessor:
    def __init__(self):
        """初始化图片处理器"""
        self.image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
        
    def process_images(self, content: str) -> str:
        """
        处理MD文件中的图片链接（删除所有图片）
        
        Args:
            content (str): MD文件内容
            
        Returns:
            str: 处理后的内容
        """
        # 删除所有图片链接（包括完整的 ![alt](path) 标记）
        # 匹配整个图片标记，包括可能的换行
        content = self.image_pattern.sub('', content)
        
        # 清理多余的空行（图片删除后可能留下的空行）
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content 