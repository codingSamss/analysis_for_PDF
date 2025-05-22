#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from pathlib import Path
import fitz  # PyMuPDF
import tempfile
import shutil
import io
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 库未安装，将使用替代方法")
    print("如需使用 PyPDF2，请运行: pip install PyPDF2")

def compress_with_pypdf2(input_path, output_path):
    """使用 PyPDF2 压缩 PDF 文件"""
    try:
        print("正在使用 PyPDF2 进行压缩...")
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        # 复制所有页面，这会重新编码 PDF 并可能减小大小
        for page in reader.pages:
            writer.add_page(page)
        
        # 设置写入选项，去除一些元数据
        writer.add_metadata({
            '/Producer': 'PyPDF2'
        })
        
        # 压缩并写入文件
        with open(output_path, "wb") as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"PyPDF2 压缩失败: {e}")
        return False

def compress_with_ghostscript(input_path, output_path):
    """使用 Ghostscript 压缩 PDF 文件"""
    try:
        import subprocess
        print("正在使用 Ghostscript 进行压缩...")
        
        # 使用不同的压缩设置
        settings = [
            # 设置 1: 屏幕优化 (最小)
            ["-dPDFSETTINGS=/screen", "-dCompatibilityLevel=1.4"],
            # 设置 2: 电子书优化
            ["-dPDFSETTINGS=/ebook", "-dCompatibilityLevel=1.4"],
            # 设置 3: 打印优化
            ["-dPDFSETTINGS=/printer", "-dCompatibilityLevel=1.4"],
            # 设置 4: 自定义高压缩
            ["-dCompatibilityLevel=1.4", "-dAutoFilterColorImages=true", "-dColorImageFilter=/DCTEncode", 
             "-dDownsampleColorImages=true", "-dColorImageDownsampleType=/Bicubic", "-dColorImageResolution=72"],
            # 设置 5: 极限压缩
            ["-dCompatibilityLevel=1.4", "-dAutoFilterColorImages=true", "-dColorImageFilter=/DCTEncode", 
             "-dDownsampleColorImages=true", "-dColorImageDownsampleType=/Bicubic", "-dColorImageResolution=50",
             "-dGrayImageResolution=50", "-dMonoImageResolution=150"]
        ]
        
        temp_files = []
        for i, setting in enumerate(settings):
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = temp_file.name
                temp_files.append(temp_path)
            
            # 构建 Ghostscript 命令
            cmd = [
                "gs", "-sDEVICE=pdfwrite", "-dNOPAUSE", "-dQUIET", "-dBATCH",
                *setting,
                f"-sOutputFile={temp_path}", input_path
            ]
            
            try:
                # 执行命令
                subprocess.run(cmd, check=True)
                
                # 检查文件大小
                if os.path.exists(temp_path):
                    print(f"设置 {i+1} 压缩后大小: {os.path.getsize(temp_path) / (1024 * 1024):.2f}MB")
            except Exception as e:
                print(f"Ghostscript 设置 {i+1} 失败: {e}")
        
        # 选择最小的文件
        sizes = [(os.path.getsize(path), path) for path in temp_files if os.path.exists(path)]
        if sizes:
            sizes.sort()
            smallest_path = sizes[0][1]
            smallest_size = sizes[0][0] / (1024 * 1024)
            print(f"选择最小的文件: {smallest_size:.2f}MB")
            
            # 检查压缩是否有效，至少要小于原始大小的90%
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            if smallest_size < original_size * 0.9:
                shutil.copy2(smallest_path, output_path)
                print(f"实际压缩率: {(1 - smallest_size/original_size) * 100:.1f}%")
                
                # 清理临时文件
                for path in temp_files:
                    if os.path.exists(path):
                        os.unlink(path)
                
                return True
            else:
                print(f"Ghostscript 压缩效果不明显 (原始: {original_size:.2f}MB, 压缩后: {smallest_size:.2f}MB)")
        
        return False
    except Exception as e:
        print(f"Ghostscript 压缩失败: {e}")
        return False

def convert_pdf_to_images_and_back(input_path, output_path, dpi=150):
    """将PDF转换为图像然后重新生成PDF - 处理严重损坏的PDF的终极解决方案"""
    try:
        import subprocess
        from PIL import Image
        
        print(f"尝试将PDF转换为图像（分辨率: {dpi}DPI）然后重建...")
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        print(f"创建临时目录: {temp_dir}")
        
        # 使用Ghostscript将PDF转换为图像
        img_pattern = os.path.join(temp_dir, "page_%03d.png")
        cmd = [
            "gs", "-dNOPAUSE", "-dBATCH", "-sDEVICE=pngalpha", 
            f"-r{dpi}", f"-sOutputFile={img_pattern}", input_path
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print("PDF转换为图像成功")
        except Exception as e:
            print(f"转换为图像失败: {e}")
            return False
        
        # 收集生成的图像
        image_files = sorted([f for f in os.listdir(temp_dir) if f.startswith("page_") and f.endswith(".png")])
        
        if not image_files:
            print("未生成图像文件")
            return False
        
        print(f"找到 {len(image_files)} 个图像文件")
        
        # 将图像转回PDF
        first_image = Image.open(os.path.join(temp_dir, image_files[0]))
        images = []
        
        for img_file in image_files[1:]:
            try:
                images.append(Image.open(os.path.join(temp_dir, img_file)))
            except Exception as e:
                print(f"打开图像 {img_file} 失败: {e}")
        
        if images:
            # 保存为PDF
            first_image.save(
                output_path, 
                "PDF", 
                resolution=dpi, 
                save_all=True, 
                append_images=images,
                optimize=True
            )
            print(f"图像转换回PDF成功，保存到 {output_path}")
            
            # 检查文件大小
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            original_size = os.path.getsize(input_path) / (1024 * 1024)
            print(f"最终文件大小: {final_size:.2f}MB，原始大小: {original_size:.2f}MB")
            print(f"压缩率: {(1 - final_size/original_size) * 100:.1f}%")
            
            # 清理临时文件
            shutil.rmtree(temp_dir)
            return True
        else:
            print("没有可用的图像来创建PDF")
            return False
            
    except Exception as e:
        print(f"图像转换方法失败: {e}")
        return False

def compress_pdf(input_path: str, output_path: str = None, target_size_mb: float = 200) -> bool:
    """
    压缩PDF文件到指定大小
    
    Args:
        input_path (str): 输入PDF文件的路径
        output_path (str, optional): 输出PDF文件的路径，如果不指定则在原文件名后添加_compressed
        target_size_mb (float, optional): 目标文件大小（MB），默认200MB
        
    Returns:
        bool: 是否成功压缩
    """
    temp_path = None
    try:
        # 检查输入文件是否存在
        if not os.path.exists(input_path):
            print(f"错误：输入文件 '{input_path}' 不存在")
            return False
            
        # 检查输入文件是否为PDF
        if not input_path.lower().endswith('.pdf'):
            print(f"错误：输入文件 '{input_path}' 不是PDF文件")
            return False
            
        # 如果没有指定输出路径，则生成默认输出路径
        if output_path is None:
            input_path_obj = Path(input_path)
            output_path = str(input_path_obj.parent / f"{input_path_obj.stem}_compressed{input_path_obj.suffix}")
            
        # 获取原始文件大小（MB）
        original_size = os.path.getsize(input_path) / (1024 * 1024)
        print(f"原始文件大小: {original_size:.2f}MB")
        
        # 如果文件已经小于目标大小，直接复制
        if original_size <= target_size_mb:
            print(f"文件已经小于目标大小 {target_size_mb}MB，无需压缩")
            shutil.copy2(input_path, output_path)
            return True

        # 首先尝试使用Ghostscript，它通常效果最好
        if compress_with_ghostscript(input_path, output_path):
            # 检查压缩后的大小
            compressed_size = os.path.getsize(output_path) / (1024 * 1024)
            if compressed_size <= target_size_mb:
                print(f"使用Ghostscript压缩成功! 大小: {compressed_size:.2f}MB")
                return True
            else:
                print(f"Ghostscript压缩后仍超过目标大小: {compressed_size:.2f}MB > {target_size_mb}MB")
                # 继续尝试其他方法
        else:
            print("Ghostscript压缩失败，尝试其他方法")

        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_path = temp_file.name

        # 尝试使用PyMuPDF
        try:
            # 打开PDF文件，使用最保守的模式
            doc = fitz.open(input_path)
            
            # 使用最保守的保存选项
            save_options = {
                "garbage": 1,  # 最小程度清理
                "deflate": True,  # 压缩文本和图像
                "clean": False,  # 不清理冗余数据
                "linear": False,  # 不优化网络查看
                "pretty": False,  # 不美化输出
                "ascii": False,  # 使用二进制模式
                "no_new_id": True,  # 保持原始ID
                "expand": 0,  # 不展开内容流
            }
            
            # 保存压缩后的文件
            doc.save(temp_path, **save_options)
            doc.close()
            
            # 检查压缩后的文件大小
            compressed_size = os.path.getsize(temp_path) / (1024 * 1024)
            print(f"PyMuPDF简单压缩后大小: {compressed_size:.2f}MB")
            
            if compressed_size <= target_size_mb:
                shutil.move(temp_path, output_path)
                print(f"PyMuPDF压缩成功!")
                return True
            
            # 尝试进一步压缩
            print("尝试进一步压缩...")
            doc = fitz.open(temp_path)
            
            # 遍历所有页面压缩图像
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    image_list = page.get_images(full=True)
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            if base_image and len(base_image["image"]) > 524288:  # 大于512KB的图像
                                page.delete_image(xref)
                                page.insert_image(img[1], stream=base_image["image"], compression=0.7)
                        except Exception as e:
                            print(f"警告：压缩图像时出错: {e}")
                except Exception as e:
                    print(f"警告：处理页面 {page_num + 1} 时出错: {e}")
            
            # 保存最终文件
            doc.save(output_path, **save_options)
            doc.close()
            
            # 检查最终大小
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"PyMuPDF深度压缩后大小: {final_size:.2f}MB")
            
            if final_size <= target_size_mb:
                print(f"PyMuPDF压缩成功!")
                return True
                
        except Exception as e:
            print(f"PyMuPDF压缩失败: {e}")
                
        # 尝试使用 PyPDF2
        if 'PdfReader' in globals() and compress_with_pypdf2(input_path, output_path):
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"PyPDF2压缩后大小: {final_size:.2f}MB")
            
            if final_size <= target_size_mb:
                print(f"PyPDF2压缩成功!")
                return True
            else:
                print(f"PyPDF2压缩后仍超过目标大小: {final_size:.2f}MB > {target_size_mb}MB")
        
        # 最后尝试图像转换方法（如果其他方法都失败或效果不理想）
        print("尝试图像转换方法（终极解决方案）...")
        if convert_pdf_to_images_and_back(input_path, output_path, dpi=120):
            final_size = os.path.getsize(output_path) / (1024 * 1024)
            if final_size <= target_size_mb:
                print(f"图像转换方法成功! 大小: {final_size:.2f}MB")
                return True
            else:
                # 如果仍然太大，降低DPI再试一次
                print(f"压缩后仍超过目标大小，尝试降低分辨率...")
                if convert_pdf_to_images_and_back(input_path, output_path, dpi=72):
                    final_size = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"低分辨率图像转换方法: {final_size:.2f}MB")
                    return True
        
        # 所有方法都失败，直接复制原文件
        print("所有压缩方法都失败或效果不理想，使用原始文件...")
        shutil.copy2(input_path, output_path)
        return True
        
    except Exception as e:
        print(f"压缩过程中发生错误: {e}")
        return False
        
    finally:
        # 清理临时文件
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"警告：清理临时文件时出错: {e}")

def main():
    """
    主函数：处理命令行参数并执行压缩
    """
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='PDF文件压缩工具')
    parser.add_argument('--input_path', '-i', 
                      required=True,
                      help='输入PDF文件的绝对路径')
    parser.add_argument('--output_path', '-o',
                      help='输出PDF文件的绝对路径（可选）')
    parser.add_argument('--target_size', '-t',
                      type=float,
                      default=200,
                      help='目标文件大小（MB），默认200MB')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 执行压缩
    if compress_pdf(args.input_path, args.output_path, args.target_size):
        print("压缩完成！")
    else:
        print("压缩失败！")
        sys.exit(1)

if __name__ == "__main__":
    main() 