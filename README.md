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
│   ├── preprocess_md.py          # MD文件预处理（统一入口）
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

4. 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入您的DeepSeek API密钥
# DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
```

## 使用方法

### 主程序使用方式

教材分析工具提供了统一的主程序入口，支持多种子命令：

#### 1. MD文件预处理
```bash
# 使用所有处理逻辑（图片 + 标题）
python -m textbook_analyzer.main preprocess --input data/md/manual --output data/md/manual_processed --all --verbose

# 只处理图片链接
python -m textbook_analyzer.main preprocess --input data/md/manual --output data/md/manual_processed --images --verbose

# 只处理标题格式
python -m textbook_analyzer.main preprocess --input data/md/manual --output data/md/manual_processed --titles --verbose

# 同时启用图片和标题处理
python -m textbook_analyzer.main preprocess --input data/md/manual --output data/md/manual_processed --images --titles --verbose
```

#### 2. 提取文档结构
```bash
python -m textbook_analyzer.main extract-structure --input data/md/manual_processed --output data/json/structure
```

#### 3. 提取文化词条
```bash
# 同步模式
python -m textbook_analyzer.main extract-culture --input data/json/structure --output data/json/culture

# 异步模式（推荐，提高效率）
python -m textbook_analyzer.main extract-culture --input data/json/structure --output data/json/culture --async_mode
```

#### 4. 生成Excel表格
```bash
python -m textbook_analyzer.main generate-excel --input data/json/culture --output data/excel --model deepseek-reasoner
```

### 独立脚本使用方式

您也可以直接使用独立的脚本文件：

#### MD文件预处理（独立脚本）
```bash
# 灵活的预处理选项
python -m textbook_analyzer.scripts.preprocess_md --input data/md/manual --output data/md/manual_processed --images --titles --verbose
```

#### 其他脚本
```bash
# 提取文档结构
python -m textbook_analyzer.scripts.extract_structure --input data/md/manual_processed --output data/json/structure

# 异步提取文化词条
python -m textbook_analyzer.scripts.extract_culture_async --input data/json/structure --output data/json/culture

# 生成Excel表格
python -m textbook_analyzer.scripts.generate_excel --input data/json/culture --output data/excel
```

### 处理流程说明

1. **MD文件预处理**：将`manual`文件夹中的原始MD文件处理为标准化格式，输出到`manual_processed`文件夹
   - 图片链接处理：标准化图片链接格式
   - 标题处理：统一标题层级格式

2. **文档结构提取**：从预处理后的MD文件中提取结构化信息，保存为JSON格式

3. **文化词条提取**：利用LLM分析文档结构，提取文化相关词条

4. **Excel表格生成**：将提取的文化词条整理成Excel表格，便于分析和展示

## 依赖项

- Python 3.8+
- pandas
- openai
- tqdm
- openpyxl

## 许可证

[MIT](LICENSE) 