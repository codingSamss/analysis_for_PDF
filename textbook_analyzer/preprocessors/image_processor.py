import re
from typing import List, Tuple

class ImageProcessor:
    def __init__(self):
        """初始化图片处理器"""
        self.image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
        
    def process_images(self, content: str) -> str:
        """
        处理MD文件中的图片链接
        
        Args:
            content (str): MD文件内容
            
        Returns:
            str: 处理后的内容
        """
        # 查找所有图片链接
        images = self.image_pattern.findall(content)
        
        # 处理每个图片链接
        for img_path in images:
            # 获取图片文件名
            img_name = os.path.basename(img_path)
            # 替换图片链接
            content = content.replace(img_path, img_name)
            
        return content 