import os
import json
import pandas as pd
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Set
from openai import OpenAI
from textbook_analyzer.config import env_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CultureMerger")

class CultureMerger:
    """将多个Excel文件中的文化词条汇总成统一规范"""
    
    def __init__(self, api_key: str = None, model: str = "deepseek-reasoner"):
        """
        初始化文化词条汇总器
        
        Args:
            api_key (str, optional): DeepSeek API密钥，用于调用LLM进行词条统一分类
            model (str, optional): 使用的模型名称，可选 "deepseek-reasoner" 或 "deepseek-chat"
        """
        self.api_key = api_key or env_config.get_api_key()
        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        
        # 文化分类映射
        self.culture_mapping = {
            "传统文化": "中华优秀传统文化",
            "现代文化": "社会主义先进文化", 
            "革命文化": "革命文化",
            "中华优秀传统文化": "中华优秀传统文化",
            "社会主义先进文化": "社会主义先进文化"
        }
        
        # 标准文化类型
        self.standard_culture_types = [
            "中华优秀传统文化",
            "革命文化", 
            "社会主义先进文化"
        ]
        
    def load_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        加载Excel文件
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            pd.DataFrame: Excel数据
        """
        try:
            df = pd.read_excel(file_path)
            logger.info(f"成功加载Excel文件: {os.path.basename(file_path)}，行数: {len(df)}")
            return df
        except Exception as e:
            logger.error(f"加载Excel文件 {file_path} 失败: {e}")
            return pd.DataFrame()
    
    def extract_terms_from_excel(self, df: pd.DataFrame, source_file: str) -> Dict[str, Set[str]]:
        """
        从Excel DataFrame中提取文化词条
        
        Args:
            df (pd.DataFrame): Excel数据
            source_file (str): 源文件名（用于日志）
            
        Returns:
            Dict[str, Set[str]]: 按文化分类整理的词条集合
        """
        culture_terms = {
            "中华优秀传统文化": set(),
            "革命文化": set(),
            "社会主义先进文化": set()
        }
        
        # 检查DataFrame是否为空或缺少必要列
        if df.empty:
            logger.warning(f"Excel文件 {source_file} 为空")
            return culture_terms
            
        required_columns = ["文化分类", "教材文本主题"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Excel文件 {source_file} 缺少必要列: {missing_columns}")
            return culture_terms
        
        # 遍历每一行，提取词条
        for _, row in df.iterrows():
            culture_type = str(row["文化分类"]).strip()
            themes_text = str(row["教材文本主题"]).strip()
            
            # 映射文化分类到标准名称
            standard_type = self.culture_mapping.get(culture_type)
            if not standard_type:
                logger.warning(f"未知的文化分类: {culture_type}")
                continue
            
            # 分割主题词（使用中文顿号、英文逗号、中文逗号）
            if themes_text and themes_text != 'nan':
                themes = []
                for separator in ['、', ',', '，']:
                    if separator in themes_text:
                        themes = themes_text.split(separator)
                        break
                else:
                    themes = [themes_text]
                
                # 清理和过滤词条
                for theme in themes:
                    theme = theme.strip()
                    if theme and theme != "无" and len(theme) > 0:
                        culture_terms[standard_type].add(theme)
        
        # 日志输出提取结果
        logger.info(f"从 {source_file} 提取的词条统计:")
        for culture_type, terms in culture_terms.items():
            logger.info(f"  {culture_type}: {len(terms)}个词条")
            
        return culture_terms
    
    def merge_culture_terms(self, all_terms: List[Dict[str, Set[str]]]) -> Dict[str, List[str]]:
        """
        合并所有文化词条，去重并转换为列表
        
        Args:
            all_terms (List[Dict[str, Set[str]]]): 所有文件的词条集合列表
            
        Returns:
            Dict[str, List[str]]: 合并后的词条字典
        """
        merged_terms = {
            "中华优秀传统文化": set(),
            "革命文化": set(),
            "社会主义先进文化": set()
        }
        
        # 合并所有词条
        for terms_dict in all_terms:
            for culture_type, terms in terms_dict.items():
                merged_terms[culture_type].update(terms)
        
        # 转换为列表并排序
        result = {}
        for culture_type, terms in merged_terms.items():
            sorted_terms = sorted(list(terms))
            result[culture_type] = sorted_terms
            logger.info(f"合并后的 {culture_type}: {len(sorted_terms)}个词条")
            if sorted_terms:
                logger.info(f"  示例: {sorted_terms[:10]}")
        
        return result
    
    def unify_classification(self, culture_type: str, terms: List[str]) -> Dict[str, List[str]]:
        """
        调用LLM对合并后的词条进行统一分类
        
        Args:
            culture_type (str): 文化类型
            terms (List[str]): 词条列表
            
        Returns:
            Dict[str, List[str]]: 统一分类后的词条
        """
        if not terms:
            return {}
            
        logger.info(f"开始对 {culture_type} 的 {len(terms)} 个词条进行统一分类...")
        
        # 构建系统提示词
        system_prompt = """你是一位精通中国文化分类和标准化的专家，擅长对文化词条进行统一规范。
你的主要任务是：
1. 对来自多个教材的文化词条进行统一分类和规范化
2. 创建清晰、有逻辑的子类别体系
3. 确保分类结果的一致性和专业性
4. 合并相似或重复的概念
5. 为每个子类别提供合适的名称
6. 确保所有词条都是中文表达"""

        # 根据文化类型构建特定的用户提示词
        if culture_type == "中华优秀传统文化":
            classification_hint = """
参考分类维度（仅供参考）：
- 传统节日与习俗
- 饮食文化
- 建筑与艺术
- 哲学思想与价值观
- 文学与语言
- 传统技艺与工艺
- 家庭伦理与社会关系
- 传统体育与娱乐"""
        elif culture_type == "革命文化":
            classification_hint = """
参考分类维度（仅供参考）：
- 革命精神与品格
- 革命历史与事件
- 革命人物与英雄
- 革命理论与思想
- 革命传统与传承
- 爱国主义教育
- 集体主义精神"""
        else:  # 社会主义先进文化
            classification_hint = """
参考分类维度（仅供参考）：
- 科学技术与创新
- 现代教育理念
- 社会主义价值观
- 国际交流与合作
- 环境保护与可持续发展
- 现代生活方式
- 社会文明进步"""

        user_prompt = f"""请对以下{culture_type}相关的词条进行统一分类整理，这些词条来自多个不同的教材。

{classification_hint}

要求：
1. 分析所有词条，识别其共同特征和主题
2. 创建合理的子类别，确保分类逻辑清晰
3. 将相似或重复的词条合并到同一子类别中
4. 子类别名称要简洁明确，体现该类别的核心特征
5. 每个子类别至少包含2个词条（除非确实只有1个独特词条）
6. 所有词条必须保持中文形式
7. 按词条的重要性和代表性进行排序

请按以下JSON格式返回结果（只返回JSON，不要有其他内容）：
{{
  "子类别1": ["词条1", "词条2", "词条3", ...],
  "子类别2": ["词条4", "词条5", "词条6", ...],
  ...
}}

需要统一分类的词条（共{len(terms)}个）：
{', '.join(terms)}"""
        
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用API进行统一分类... (尝试 {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=3000,
                    stream=False
                )
                
                # 解析API响应
                completion = response.choices[0].message.content
                
                # 尝试解析JSON响应
                try:
                    classified_terms = json.loads(completion)
                except json.JSONDecodeError:
                    # 如果无法解析JSON，尝试提取JSON部分
                    json_start = completion.find("{")
                    json_end = completion.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        try:
                            classified_terms = json.loads(completion[json_start:json_end])
                        except:
                            logger.error(f"无法解析API响应: {completion}")
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                                continue
                            else:
                                return {"统一分类": terms}
                    else:
                        logger.error(f"无法解析API响应: {completion}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            return {"统一分类": terms}
                
                # 验证和清理结果
                if not isinstance(classified_terms, dict):
                    logger.error("API返回的不是字典格式")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        return {"统一分类": terms}
                
                # 日志输出分类结果
                logger.info(f"{culture_type} 统一分类完成:")
                total_classified = 0
                for subtype, subterms in classified_terms.items():
                    if isinstance(subterms, list):
                        total_classified += len(subterms)
                        logger.info(f"  {subtype}: {len(subterms)}个词条")
                        if subterms:
                            logger.info(f"    示例: {subterms[:5]}")
                
                logger.info(f"总计分类词条: {total_classified}/{len(terms)}")
                return classified_terms
                        
            except Exception as e:
                logger.error(f"调用API失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {"统一分类": terms}
    
    def generate_unified_excel(self, merged_terms: Dict[str, List[str]], output_path: str) -> bool:
        """
        生成统一的Excel表格
        
        Args:
            merged_terms (Dict[str, List[str]]): 合并后的词条
            output_path (str): 输出Excel文件路径
            
        Returns:
            bool: 是否成功生成Excel
        """
        try:
            # 准备数据
            data = []
            
            # 遍历每种文化类型
            for culture_type, terms in merged_terms.items():
                if not terms:
                    continue
                    
                # 对词条进行统一分类
                logger.info(f"正在统一分类 {culture_type}...")
                classified_terms = self.unify_classification(culture_type, terms)
                
                # 将分类结果添加到数据中
                for subtype, subterms in classified_terms.items():
                    if not subterms:
                        continue
                        
                    # 添加一行数据
                    data.append({
                        "文化分类": culture_type,
                        "文化细类": f"{subtype}（{len(subterms)}）",
                        "教材文本主题": "、".join(subterms)
                    })
            
            logger.info(f"即将写入统一Excel的总行数: {len(data)}")
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存为Excel
            df.to_excel(output_path, index=False)
            
            logger.info(f"统一Excel表格已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成统一Excel表格失败: {e}")
            return False
    
    def merge_excel_files(self, input_files: List[str], output_path: str) -> bool:
        """
        合并多个Excel文件
        
        Args:
            input_files (List[str]): 输入Excel文件路径列表
            output_path (str): 输出Excel文件路径
            
        Returns:
            bool: 是否成功合并
        """
        try:
            logger.info(f"开始合并 {len(input_files)} 个Excel文件...")
            
            # 提取所有文件的词条
            all_terms = []
            for file_path in input_files:
                logger.info(f"正在处理文件: {os.path.basename(file_path)}")
                df = self.load_excel_file(file_path)
                if not df.empty:
                    terms = self.extract_terms_from_excel(df, os.path.basename(file_path))
                    all_terms.append(terms)
            
            if not all_terms:
                logger.error("没有成功读取任何Excel文件")
                return False
            
            # 合并词条
            merged_terms = self.merge_culture_terms(all_terms)
            
            # 生成统一Excel
            return self.generate_unified_excel(merged_terms, output_path)
            
        except Exception as e:
            logger.error(f"合并Excel文件失败: {e}")
            return False
    
    def merge_directory(self, input_dir: str, output_path: str) -> bool:
        """
        合并目录中的所有Excel文件
        
        Args:
            input_dir (str): 输入目录
            output_path (str): 输出Excel文件路径
            
        Returns:
            bool: 是否成功合并
        """
        # 获取所有Excel文件
        excel_files = []
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
                excel_files.append(os.path.join(input_dir, file_name))
        
        if not excel_files:
            logger.error(f"在目录 {input_dir} 中未找到Excel文件")
            return False
        
        logger.info(f"找到 {len(excel_files)} 个Excel文件")
        
        return self.merge_excel_files(excel_files, output_path)

def merge_culture_excel(input_dir: str = None, input_files: List[str] = None, 
                       output_path: str = None, api_key: str = None, 
                       model: str = "deepseek-reasoner") -> bool:
    """
    合并文化词条Excel文件并生成统一规范
    
    Args:
        input_dir (str, optional): 输入目录
        input_files (List[str], optional): 输入文件列表
        output_path (str): 输出Excel文件路径
        api_key (str, optional): DeepSeek API密钥
        model (str): 使用的模型名称
        
    Returns:
        bool: 是否成功合并
    """
    logger.info("=" * 50)
    logger.info("文化词条Excel合并开始")
    logger.info(f"使用模型: {model}")
    logger.info("=" * 50)
    
    merger = CultureMerger(api_key, model)
    
    if input_dir:
        success = merger.merge_directory(input_dir, output_path)
    elif input_files:
        success = merger.merge_excel_files(input_files, output_path)
    else:
        logger.error("必须指定输入目录或输入文件列表")
        return False
    
    logger.info("=" * 50)
    if success:
        logger.info("文化词条Excel合并完成")
        logger.info(f"统一Excel文件: {output_path}")
    else:
        logger.info("文化词条Excel合并失败")
    logger.info("=" * 50)
    
    return success

if __name__ == "__main__":
    # 测试代码
    input_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/excel"
    output_path = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/excel/统一文化词条规范.xlsx"
    
    # API密钥将从.env文件或环境变量中读取
    api_key = None  # 让配置管理器自动处理
    
    # 设置模型
    model = "deepseek-reasoner"
    
    # 合并文件
    merge_culture_excel(input_dir=input_dir, output_path=output_path, api_key=api_key, model=model) 