# 📚 教材分析工具使用指南

本工具用于提取和分析教材中的文化词条，支持从MD文件到最终Excel报告的完整流程。

## 🚀 快速开始

### 环境配置
确保已配置API密钥（在.env文件中设置`DEEPSEEK_API_KEY`）

### 完整处理流程

#### 1️⃣ 结构提取（MD → JSON）

**处理指定的两个教材文件：**
```bash
python -m textbook_analyzer.main extract-structure \
    --files \
    "textbook_analyzer/data/md/manual_processed/人教版义务教育教科书 英语 七年级 下册.md" \
    "textbook_analyzer/data/md/manual_processed/人教版义务教育教科书 英语 七年级 上册.md" \
    --output textbook_analyzer/data/json/structure \
    --workers 4 \
    --verbose
```

**处理整个目录：**
```bash
python -m textbook_analyzer.main extract-structure \
    --input textbook_analyzer/data/md/manual_processed \
    --output textbook_analyzer/data/json/structure \
    --workers 4 \
    --verbose
```

#### 2️⃣ 文化词条提取（JSON → 文化词条JSON）

**处理指定的JSON文件：**
```bash
python -m textbook_analyzer.main extract-culture \
    --files \
    "textbook_analyzer/data/json/structure/人教版义务教育教科书 英语 七年级 下册.json" \
    "textbook_analyzer/data/json/structure/人教版义务教育教科书 英语 七年级 上册.json" \
    --output textbook_analyzer/data/json/culture \
    --concurrent 3 \
    --verbose
```

**处理整个目录：**
```bash
python -m textbook_analyzer.main extract-culture \
    --input textbook_analyzer/data/json/structure \
    --output textbook_analyzer/data/json/culture \
    --concurrent 3 \
    --verbose
```

#### 3️⃣ 生成Excel报告
```bash
python -m textbook_analyzer.main generate-excel \
    --input textbook_analyzer/data/json/culture \
    --output textbook_analyzer/data/excel
```

## 📋 详细参数说明

### 结构提取 (extract-structure)

| 参数 | 简写 | 必选 | 说明 |
|------|------|------|------|
| `--input` | `-i` | 互斥* | 输入MD文件目录路径 |
| `--files` | `-f` | 互斥* | 指定要处理的MD文件路径列表 |
| `--output` | `-o` | ✅ | 输出JSON文件目录路径 |
| `--workers` | `-w` | ❌ | 最大并发工作线程数 (默认: 4) |
| `--no-resume` | | ❌ | 禁用断点续传，重新处理所有文件 |
| `--verbose` | `-v` | ❌ | 显示详细信息 |

*`--input` 和 `--files` 必须选择其一

### 文化词条提取 (extract-culture)

| 参数 | 简写 | 必选 | 说明 |
|------|------|------|------|
| `--input` | `-i` | 互斥* | 输入JSON文件目录路径 |
| `--files` | `-f` | 互斥* | 指定要处理的JSON文件路径列表 |
| `--output` | `-o` | ✅ | 输出JSON文件目录路径 |
| `--api_key` | `-k` | ❌ | DeepSeek API密钥（可从.env读取） |
| `--concurrent` | `-c` | ❌ | 最大并发请求数 (默认: 3) |
| `--no-resume` | | ❌ | 禁用断点续传，从头开始处理 |
| `--test` | `-t` | ❌ | 运行单个测试样例 |
| `--verbose` | `-v` | ❌ | 显示详细信息 |

*`--input` 和 `--files` 必须选择其一

### Excel生成 (generate-excel)

| 参数 | 简写 | 必选 | 说明 |
|------|------|------|------|
| `--input` | `-i` | ✅ | 输入JSON目录路径 |
| `--output` | `-o` | ✅ | 输出Excel目录路径 |
| `--api_key` | `-k` | ❌ | DeepSeek API密钥 |
| `--model` | `-m` | ❌ | 模型名称 (deepseek-reasoner/deepseek-chat) |

## 💡 功能特色

### ✅ 并发处理
- **结构提取**: 多线程并发处理MD文件
- **文化词条提取**: 异步并发API请求，提高效率

### ✅ 断点续传
- 自动跳过已处理的文件
- 支持中断后继续处理
- 使用 `--no-resume` 强制重新处理

### ✅ 灵活输入
- **目录模式**: 处理整个目录下的所有文件
- **指定文件模式**: 只处理指定的文件列表

### ✅ 详细进度
- 实时显示处理进度
- 错误重试机制
- 详细的日志信息

## 🎯 具体示例

### 示例1: 处理您的两个教材文件

```bash
# 步骤1: 结构提取
python -m textbook_analyzer.main extract-structure \
    --files \
    "textbook_analyzer/data/md/manual_processed/人教版义务教育教科书 英语 七年级 下册.md" \
    "textbook_analyzer/data/md/manual_processed/人教版义务教育教科书 英语 七年级 上册.md" \
    --output textbook_analyzer/data/json/structure \
    --workers 2 \
    --verbose

# 步骤2: 文化词条提取
python -m textbook_analyzer.main extract-culture \
    --files \
    "textbook_analyzer/data/json/structure/人教版义务教育教科书 英语 七年级 下册.json" \
    "textbook_analyzer/data/json/structure/人教版义务教育教科书 英语 七年级 上册.json" \
    --output textbook_analyzer/data/json/culture \
    --concurrent 2 \
    --verbose

# 步骤3: 生成Excel报告
python -m textbook_analyzer.main generate-excel \
    --input textbook_analyzer/data/json/culture \
    --output textbook_analyzer/data/excel
```

### 示例2: 测试API配置

```bash
python -m textbook_analyzer.main extract-culture \
    --test \
    --output /tmp
```

### 示例3: 处理单个文件

```bash
python -m textbook_analyzer.main extract-structure \
    --files "path/to/single_file.md" \
    --output output_dir \
    --workers 1
```

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   - 检查.env文件中的DEEPSEEK_API_KEY设置
   - 或使用 `--api_key` 参数手动指定

2. **文件未找到**
   - 确认文件路径正确
   - 检查文件权限

3. **断点续传问题**
   - 使用 `--no-resume` 强制重新处理
   - 删除输出目录重新开始

4. **并发设置**
   - 降低 `--workers` 或 `--concurrent` 数值
   - 根据网络状况调整并发数

## 📂 文件结构

```
textbook_analyzer/
├── data/
│   ├── md/manual_processed/     # 手动处理的MD文件
│   ├── json/structure/          # 结构提取的JSON文件
│   ├── json/culture/           # 文化词条提取结果
│   └── excel/                  # 最终Excel报告
├── llm/                        # 核心处理模块
├── preprocessors/              # 预处理模块
└── main.py                     # 主入口
```

所有功能现在都通过 `python -m textbook_analyzer.main` 统一调用！ 