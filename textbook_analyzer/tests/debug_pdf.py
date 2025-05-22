import os
import json
from pdf_processor import PDFProcessor

def debug_pdf_extraction(pdf_path, output_dir):
    """
    调试PDF文本提取功能（仅使用OCR方式）
    
    Args:
        pdf_path (str): PDF文件路径
        output_dir (str): 输出目录
    """
    print(f"\n=== 开始调试PDF提取: {os.path.basename(pdf_path)} ===")
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建PDF处理器实例
    processor = PDFProcessor(os.path.dirname(pdf_path))
    
    # 使用OCR提取
    print("\n使用OCR提取:")
    pages_text_ocr = processor.extract_text_with_ocr(pdf_path)
    print(f"提取到 {len(pages_text_ocr)} 页文本")
    
    # 保存OCR结果
    ocr_output = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_ocr.json")
    with open(ocr_output, 'w', encoding='utf-8') as f:
        json.dump(pages_text_ocr, f, ensure_ascii=False, indent=2)
    print(f"OCR结果已保存到: {ocr_output}")
    
    # 处理文本并保存结构化结果
    print("\n处理文本并保存结构化结果:")
    structured_content = processor.process_text(pages_text_ocr)
    structured_output = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_structured.json")
    with open(structured_output, 'w', encoding='utf-8') as f:
        json.dump(structured_content, f, ensure_ascii=False, indent=2)
    print(f"结构化结果已保存到: {structured_output}")
    
    print("\n=== 调试完成 ===")
    print(f"所有结果文件已保存到目录: {output_dir}")

def main():
    # 设置PDF文件路径和输出目录
    pdf_path = "test.pdf"  # 替换为您的PDF文件路径
    output_dir = "debug_output"
    
    # 运行调试
    debug_pdf_extraction(pdf_path, output_dir)

if __name__ == "__main__":
    main() 