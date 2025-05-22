import os
import json
from md_processor import MDProcessor

def debug_md_extraction(md_path, output_dir):
    """
    调试MD文本提取功能
    
    Args:
        md_path (str): MD文件路径
        output_dir (str): 输出目录
    """
    print(f"\n=== 开始调试MD提取: {os.path.basename(md_path)} ===")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建MD处理器实例
    processor = MDProcessor(os.path.dirname(md_path))
    
    # 提取文本
    print("\n提取文本:")
    sections = processor.extract_text_from_md(md_path)
    print(f"提取到 {len(sections)} 个章节")
    
    # 保存原始提取结果
    raw_output = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(md_path))[0]}_raw.json")
    with open(raw_output, 'w', encoding='utf-8') as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
    print(f"原始提取结果已保存到: {raw_output}")
    
    # 处理文本并保存结构化结果
    print("\n处理文本并保存结构化结果:")
    structured_content = processor.process_text(sections)
    structured_output = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(md_path))[0]}_structured.json")
    with open(structured_output, 'w', encoding='utf-8') as f:
        json.dump(structured_content, f, ensure_ascii=False, indent=2)
    print(f"结构化结果已保存到: {structured_output}")
    
    print("\n=== 调试完成 ===")
    print(f"所有结果文件已保存到目录: {output_dir}")

def main():
    # 设置MD文件路径和输出目录
    md_path = "textbook_analyzer/data/md/markdown.md"  # 修改为正确的路径
    output_dir = "debug_output"
    
    # 运行调试
    debug_md_extraction(md_path, output_dir)

if __name__ == "__main__":
    main() 