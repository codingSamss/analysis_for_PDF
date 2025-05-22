import os
import re
import json
from tqdm import tqdm

class MDProcessor:
    def __init__(self, md_dir):
        """
        初始化MD处理器
        
        Args:
            md_dir (str): MD文件所在目录
        """
        self.md_dir = md_dir
    
    def list_mds(self):
        """
        列出目录中的所有MD文件
        
        Returns:
            list: MD文件路径列表
        """
        md_files = []
        for file in os.listdir(self.md_dir):
            if file.lower().endswith('.md'):
                md_files.append(os.path.join(self.md_dir, file))
        return md_files
    
    def extract_text_from_md(self, md_path):
        """
        从MD文件中提取文本
        
        Args:
            md_path (str): MD文件路径
            
        Returns:
            list: 每页内容列表（对于MD文件，我们将其按章节分割）
        """
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按章节分割内容
            # 使用Markdown的标题标记（#）来分割章节
            sections = re.split(r'(?m)^#{1,6}\s+', content)
            
            # 移除空章节
            sections = [section.strip() for section in sections if section.strip()]
            
            return sections
        except Exception as e:
            print(f"处理 {md_path} 时出错: {e}")
            return []
    
    def process_text(self, sections):
        """
        处理提取出的文本，进行清洗和初步结构化
        
        Args:
            sections (list): 章节内容列表
            
        Returns:
            list: 处理后的章节内容列表
        """
        # 合并所有章节的文本
        full_text = "\n".join(sections)
        
        # 清理文本：移除多余空白字符
        cleaned_text = re.sub(r'\s+', ' ', full_text).strip()
        
        # 改进的章节识别模式
        # 1. 匹配Unit/Lesson/Module/Chapter后跟数字或单词
        # 2. 匹配可能的章节标题
        chapter_pattern = r'(Unit|Lesson|Module|Chapter)\s+(?:\d+|[A-Za-z]+)(?:\s+[A-Za-z\s]+)?'
        
        # 使用更智能的分割方法
        chapters = []
        current_pos = 0
        
        # 查找所有章节标题
        for match in re.finditer(chapter_pattern, cleaned_text):
            if current_pos < match.start():
                # 添加章节之间的内容
                chapters.append({
                    'chapter': 'Introduction' if current_pos == 0 else 'Unknown',
                    'text': cleaned_text[current_pos:match.start()].strip()
                })
            
            # 提取章节标题和内容
            chapter_title = match.group(0).strip()
            next_match = re.search(chapter_pattern, cleaned_text[match.end():])
            if next_match:
                chapter_content = cleaned_text[match.end():match.end()+next_match.start()].strip()
            else:
                chapter_content = cleaned_text[match.end():].strip()
            
            chapters.append({
                'chapter': chapter_title,
                'text': chapter_content
            })
            
            current_pos = match.end() + (next_match.start() if next_match else 0)
        
        # 如果没有识别出任何章节，返回整个文本
        if not chapters:
            return [{'text': cleaned_text, 'chapter': 'Unknown'}]
        
        return chapters
    
    def save_processed_text(self, md_path, structured_content, output_dir):
        """
        保存处理后的文本到JSON文件
        
        Args:
            md_path (str): 原MD文件路径
            structured_content (list): 结构化内容
            output_dir (str): 输出目录
            
        Returns:
            str: 保存的JSON文件路径
        """
        base_name = os.path.splitext(os.path.basename(md_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_processed.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(structured_content, f, ensure_ascii=False, indent=2)
            
        return output_path
    
    def process_md(self, md_path, output_dir):
        """
        处理单个MD文件
        
        Args:
            md_path (str): MD文件路径
            output_dir (str): 输出目录
            
        Returns:
            str: 处理后JSON文件的路径，如果处理失败返回None
        """
        try:
            print(f"开始处理: {os.path.basename(md_path)}")
            
            # 提取文本
            sections = self.extract_text_from_md(md_path)
            if not sections:
                print(f"无法从 {md_path} 提取文本")
                return None
            
            # 处理文本
            structured_content = self.process_text(sections)
            
            # 保存处理后的文本
            output_path = self.save_processed_text(md_path, structured_content, output_dir)
            
            print(f"处理完成: {os.path.basename(md_path)} -> {os.path.basename(output_path)}")
            return output_path
            
        except Exception as e:
            print(f"处理 {md_path} 时发生错误: {e}")
            return None
    
    def batch_process_mds(self, output_dir):
        """
        批量处理目录中的所有MD文件
        
        Args:
            output_dir (str): 输出目录
            
        Returns:
            list: 处理后的JSON文件路径列表
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        md_files = self.list_mds()
        processed_files = []
        
        print(f"找到 {len(md_files)} 个MD文件")
        
        for md_path in md_files:
            output_path = self.process_md(md_path, output_dir)
            if output_path:
                processed_files.append(output_path)
                
        print(f"完成处理 {len(processed_files)}/{len(md_files)} 个文件")
        return processed_files 