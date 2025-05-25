# 教材分析工具 (Textbook Analyzer)

一个用于分析教材内容的工具，特别专注于提取和分析教材中的文化词条。

## 功能特点

- **Markdown文件处理**：处理从PDF转换而来的Markdown文件，进行标准化和结构化
- **文化词条提取**：利用LLM分析教材内容，提取文化相关词条
- **文化分类**：将提取的词条按照传统文化、现代文化和革命文化进行分类
- **数据可视化**：将分析结果生成为Excel表格，便于后续研究和展示

## 项目结构

```
textbook_analyzer/
├── analysis/            # 数据分析模块
│   └── culture_summarizer.py  # 文化词条整理和分类
├── data/                # 数据文件
│   ├── excel/           # 生成的Excel表格
│   ├── json/            # 提取的结构化数据
│   │   ├── culture/     # 文化词条JSON数据
│   │   └── structure/   # 文档结构JSON数据
│   ├── md/              # Markdown文件
│   │   ├── cleaned/     # 清理后的MD文件
│   │   ├── manual/      # 手动处理的MD文件
│   │   └── manual_processed/ # 手动处理后的MD文件
│   └── pdfs/            # 原始PDF文件
├── llm/                 # LLM相关模块
│   ├── async_culture_extractor.py  # 异步文化词条提取器
│   └── culture_extractor.py        # 文化词条提取器
├── preprocessors/       # 预处理模块
│   ├── image_processor.py      # 图像处理
│   ├── md_preprocessor.py      # MD文件预处理
│   ├── structure_extractor.py  # 结构提取
│   └── title_processor.py      # 标题处理
├── scripts/             # 命令行脚本
│   ├── extract_culture_async.py  # 异步提取文化词条
│   ├── extract_culture.py        # 提取文化词条
│   ├── extract_structure.py      # 提取文档结构
│   ├── generate_excel.py         # 生成Excel表格
│   └── process_directory.py      # 批量处理目录
├── utils/               # 工具函数
│   └── file_utils.py    # 文件处理工具
├── __init__.py          # 包初始化文件
└── requirements.txt     # 项目依赖
```

## 安装

1. 克隆仓库

```bash
git clone <repository-url>
cd textbook_analyzer
```

2. 创建并激活虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 处理MD文件

```bash
python -m textbook_analyzer.scripts.process_directory <input_dir> <output_dir>
```

### 按一定规则将手动标注后的md文件

```python
python -m textbook_analyzer.main preprocess --input data/md/manual --output data/md/manual_processed
```

2. 提取文档结构

```bash
python -m textbook_analyzer.scripts.extract_structure --input <input_file> --output <output_file>
```

### 3. 提取文化词条

```bash
python -m textbook_analyzer.scripts.extract_culture_async --input <input_dir> --output <output_dir>
```

### 4. 生成Excel表格

```bash
python -m textbook_analyzer.scripts.generate_excel --input <input_dir> --output <output_dir> --model <model_name>
```

## 依赖项

- Python 3.8+
- pandas
- openai
- tqdm
- openpyxl

## 许可证

[MIT](LICENSE)
