# 教材分析工具 (Textbook Analyzer)

一个功能完整的教材内容分析工具，专注于提取和分析教材中的文化词条，支持从PDF处理到数据可视化的完整工作流程。

## 功能特点

- **多格式文件处理**：支持PDF、Markdown等多种格式的教材文件处理
- **智能预处理**：自动清理和标准化文档格式，包括图片链接和标题格式处理
- **高效结构提取**：使用多线程并发提取文档结构，支持断点续传
- **AI驱动的文化词条提取**：利用DeepSeek LLM智能分析教材内容，提取文化相关词条
- **智能文化分类**：将提取的词条按照传统文化、现代文化和革命文化进行自动分类
- **数据整合与可视化**：支持多文件Excel合并，生成统一规范的分析报告
- **灵活的命令行接口**：提供统一的主程序入口和丰富的参数选项

## 项目结构

```
textbook_analyzer/
├── analysis/                    # 数据分析和整合模块
│   ├── culture_summarizer.py  # 文化词条整理和分类
│   └── culture_merger.py      # Excel文件合并和数据整合
├── config/                     # 配置管理模块
│   └── env_config.py          # 环境变量和API配置
├── data/                       # 数据文件目录
│   ├── excel/                 # 生成的Excel表格
│   ├── json/                  # 提取的结构化数据
│   │   ├── culture/          # 文化词条JSON数据
│   │   └── structure/        # 文档结构JSON数据
│   ├── md/                   # Markdown文件
│   │   ├── cleaned/          # 清理后的MD文件
│   │   ├── manual/           # 手动处理的MD文件
│   │   └── manual_processed/ # 预处理后的MD文件
│   └── pdfs/                 # 原始PDF文件
├── llm/                        # LLM集成模块
│   └── async_culture_extractor.py  # 高性能异步文化词条提取器
├── preprocessors/              # 文档预处理模块
│   ├── structure_extractor_enhanced.py  # 增强版结构提取器
│   ├── md_preprocessor.py             # MD文件预处理
│   ├── image_processor.py             # 图像链接处理
│   └── title_processor.py             # 标题格式标准化
├── scripts/                    # 独立脚本模块
│   ├── preprocess_md.py       # MD文件预处理脚本
│   └── process_directory.py   # 批量文件处理
├── utils/                      # 工具函数库
│   └── file_utils.py          # 文件操作工具
├── main.py                     # 统一主程序入口
├── compress_pdf.py             # PDF文件压缩工具
├── md_processor.py             # MD文件处理器
└── __init__.py                 # 包初始化文件
```

## 环境要求

- **Python版本**：3.8 或更高版本
- **操作系统**：支持 Windows、macOS、Linux
- **API支持**：需要DeepSeek API密钥进行文化词条分析

## 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd textbook_analyzer
```

### 2. 创建虚拟环境

```bash
# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

```bash
# 创建环境变量文件
cp .env.example .env

# 编辑.env文件，填入您的DeepSeek API密钥
echo "DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here" > .env
```

## 使用方法

教材分析工具提供统一的命令行接口，支持完整的分析工作流程：

### 完整工作流程

```bash
# 1. 预处理MD文件（清理格式，标准化结构）
python -m textbook_analyzer.main preprocess \
    --input data/md/manual \
    --output data/md/manual_processed \
    --all --verbose

# 2. 提取文档结构（多线程并发处理）
python -m textbook_analyzer.main extract-structure \
    --input data/md/manual_processed \
    --output data/json/structure \
    --workers 8 --verbose

# 3. 提取文化词条（AI智能分析）
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --concurrent 5 --verbose

# 4. 生成Excel报告
python -m textbook_analyzer.main generate-excel \
    --input data/json/culture \
    --output data/excel \
    --model deepseek-reasoner --verbose

# 5. 合并多个Excel文件（可选）
python -m textbook_analyzer.main merge-excel \
    --input data/excel \
    --output data/final_report.xlsx \
    --model deepseek-reasoner --verbose
```

### 详细命令说明

#### 1. MD文件预处理

```bash
# 启用所有预处理功能
python -m textbook_analyzer.main preprocess \
    --input data/md/manual \
    --output data/md/manual_processed \
    --all --verbose

# 自定义预处理选项
python -m textbook_analyzer.main preprocess \
    --input data/md/manual \
    --output data/md/manual_processed \
    --images --titles --verbose
```

#### 2. 文档结构提取

```bash
# 处理整个目录
python -m textbook_analyzer.main extract-structure \
    --input data/md/manual_processed \
    --output data/json/structure \
    --workers 4 --verbose

# 处理指定文件
python -m textbook_analyzer.main extract-structure \
    --files file1.md file2.md file3.md \
    --output data/json/structure \
    --workers 4 --verbose

# 禁用断点续传（重新处理所有文件）
python -m textbook_analyzer.main extract-structure \
    --input data/md/manual_processed \
    --output data/json/structure \
    --no-resume --verbose
```

#### 3. 文化词条提取

```bash
# 高并发异步处理（推荐）
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --concurrent 5 --verbose

# 指定API密钥
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --api_key sk-your-key-here \
    --concurrent 3 --verbose

# 测试模式（处理单个样例）
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --test --verbose
```

#### 4. Excel报告生成

```bash
# 使用推理模型生成详细报告
python -m textbook_analyzer.main generate-excel \
    --input data/json/culture \
    --output data/excel \
    --model deepseek-reasoner --verbose

# 使用聊天模型（更快速）
python -m textbook_analyzer.main generate-excel \
    --input data/json/culture \
    --output data/excel \
    --model deepseek-chat --verbose

# 处理指定文件
python -m textbook_analyzer.main generate-excel \
    --files culture1.json culture2.json \
    --output data/excel \
    --model deepseek-reasoner --verbose
```

#### 5. Excel文件合并

```bash
# 合并目录中的所有Excel文件
python -m textbook_analyzer.main merge-excel \
    --input data/excel \
    --output data/merged_analysis.xlsx \
    --model deepseek-reasoner --verbose

# 合并指定的Excel文件
python -m textbook_analyzer.main merge-excel \
    --files report1.xlsx report2.xlsx report3.xlsx \
    --output data/final_report.xlsx \
    --model deepseek-reasoner --verbose
```

### 高级功能

#### 并发性能优化

```bash
# 结构提取：根据CPU核心数调整工作线程
python -m textbook_analyzer.main extract-structure \
    --input data/md/manual_processed \
    --output data/json/structure \
    --workers 8

# 文化词条提取：根据API限制调整并发数
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --concurrent 5
```

#### 断点续传

所有处理步骤默认支持断点续传，中断后重新运行会自动跳过已完成的文件：

```bash
# 启用断点续传（默认）
python -m textbook_analyzer.main extract-structure \
    --input data/md/manual_processed \
    --output data/json/structure

# 禁用断点续传
python -m textbook_analyzer.main extract-culture \
    --input data/json/structure \
    --output data/json/culture \
    --no-resume
```

## 主要依赖

- **数据处理**：pandas (>=1.3.0), openpyxl (>=3.0.9)
- **AI集成**：openai (>=1.0.0)
- **文件处理**：PyPDF2 (>=2.0.0), PyMuPDF (>=1.19.0)
- **异步处理**：aiohttp (>=3.8.0)
- **用户界面**：tqdm (>=4.62.0)
- **配置管理**：python-dotenv (>=0.19.0)

## 输出格式

### JSON结构数据

- **文档结构**：保存在`data/json/structure/`目录
- **文化词条**：保存在`data/json/culture/`目录

### Excel分析报告

- **单文件报告**：包含文化词条分类和统计信息
- **合并报告**：汇总多个文件的分析结果
- **数据可视化**：包含图表和统计分析

## 性能特点

- **多线程并发**：结构提取支持最大8个工作线程
- **异步请求**：文化词条提取支持高并发API调用
- **断点续传**：支持中断恢复，避免重复处理
- **内存优化**：大文件分块处理，降低内存占用

## 故障排除

### 常见问题

1. **API密钥错误**

   ```bash
   # 检查环境变量设置
   echo $DEEPSEEK_API_KEY
   ```
2. **并发数过高导致API限流**

   ```bash
   # 降低并发数
   --concurrent 2
   ```
3. **内存不足**

   ```bash
   # 减少工作线程数
   --workers 2
   ```
