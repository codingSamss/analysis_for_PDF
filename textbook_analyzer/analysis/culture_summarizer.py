import os
import json
import pandas as pd
import logging
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from openai import OpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CultureSummarizer")

class CultureSummarizer:
    """将提取的文化词条整理成Excel表格"""
    
    def __init__(self, api_key: str = None, model: str = "deepseek-reasoner"):
        """
        初始化文化词条整理器
        
        Args:
            api_key (str, optional): DeepSeek API密钥，用于调用LLM进行词条分类
            model (str, optional): 使用的模型名称，可选 "deepseek-reasoner" 或 "deepseek-chat"
        """
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        # 文化分类映射
        self.culture_mapping = {
            "中华优秀传统文化": "传统文化",
            "社会主义先进文化": "现代文化", 
            "革命文化": "革命文化"
        }
        
    def load_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        加载JSON文件
        
        Args:
            file_path (str): JSON文件路径
            
        Returns:
            Dict[str, Any]: JSON数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载JSON文件 {file_path} 失败: {e}")
            return {}
    
    def extract_culture_terms(self, json_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        从JSON数据中提取文化词条
        
        Args:
            json_data (Dict[str, Any]): JSON数据
            
        Returns:
            Dict[str, List[str]]: 按文化分类整理的词条
        """
        culture_terms = {
            "中华优秀传统文化": set(),
            "社会主义先进文化": set(),
            "革命文化": set()
        }
        
        # 遍历所有结果
        for result in json_data.get("results", []):
            # 提取每种文化类型的词条
            for culture_type, terms in result.items():
                if culture_type in culture_terms and isinstance(terms, list):
                    # 过滤掉"无"和空字符串
                    valid_terms = [term for term in terms if term and term != "无"]
                    culture_terms[culture_type].update(valid_terms)
        
        # 日志输出每类词条数量和部分内容
        for k, v in culture_terms.items():
            logger.info(f"{self.culture_mapping[k]}词条数量: {len(v)}，示例: {list(v)[:10]}")
        
        # 将集合转换为列表
        return {k: list(v) for k, v in culture_terms.items()}
    
    def classify_terms(self, culture_type: str, terms: List[str]) -> Dict[str, List[str]]:
        """
        调用LLM对词条进行分类
        
        Args:
            culture_type (str): 文化类型
            terms (List[str]): 词条列表
            
        Returns:
            Dict[str, List[str]]: 分类后的词条
        """
        if not terms:
            return {}
            
        # 如果没有API密钥，使用简单的分类方法
        if not self.api_key:
            # 确保没有英文词条
            translated_terms = []
            for term in terms:
                # 如果包含英文字符，则将其置空，后续会过滤掉
                if any(ord(c) < 128 for c in term) and not all(ord(c) < 128 for c in term):
                    # 中英混合的情况，只保留中文部分
                    chinese_only = ''.join([c for c in term if ord(c) >= 128])
                    if chinese_only.strip():
                        translated_terms.append(chinese_only.strip())
                elif all(ord(c) < 128 for c in term):
                    # 纯英文的情况，由于无法翻译，暂时过滤掉
                    continue
                else:
                    # 纯中文的情况，直接保留
                    translated_terms.append(term)
            
            return {"未分类": translated_terms} if translated_terms else {}
        
        # 日志输出将要发送的词条内容
        logger.info(f"发送给LLM的{self.culture_mapping[culture_type]}词条（前50个）: {terms[:50]}")
        
        # 构建系统提示词
        system_prompt = """你是一位精通中国文化和翻译的专家，擅长对文化词条进行分类和整理。
你的主要任务是：
1. 准确理解每个词条的文化内涵
2. 将英文词条准确翻译成对应的中文概念
3. 根据词条的文化属性进行合理分类
4. 确保分类结果符合中国文化的特点
5. 保持分类的专业性和准确性
以下是三种文化的定义：
传统文化是中华民族和中国人民在修齐治平、尊时守位、知常达变、开物成务、建功立业过程中逐渐形成的有别于其他民族的独特标识，其中蕴含的天下为公、民为邦本、为政以德、革故鼎新、任人唯贤、天人合一、自强不息、厚德载物、讲信修睦、亲仁善邻等，是中国人民在长期生产生活中积累的宇宙观、天下观、社会观、道德观的重要体现。
革命文化是近代以来特别是五四新文化运动以来，在党和人民的伟大斗争中培育和创造的思想理论、价值追求、精神品格，如红船精神、井冈山精神、长征精神、延安精神、沂蒙精神、西柏坡精神等，集中体现了马克思主义指导下的中国近现代文化的发展及其成果，展现了中国人民顽强不屈、坚韧不拔的民族气节和英雄气概。
现代文化是在党领导人民推进中国特色社会主义伟大实践中，在马克思主义指导下形成的面向现代化、面向世界、面向未来的，民族的科学的大众的社会主义文化，代表着时代进步潮流和发展要求。

"""



        # 构建用户提示词
        user_prompt = f"""请将以下{self.culture_mapping[culture_type]}相关的词条按照合理的子类别进行分类整理。

要求：
1. 分析这些词条，根据其含义和特点进行分类
2. 创建合适的子类别名称（如"饮食文化"、"手工艺与艺术"等）
3. 将每个词条归入最合适的子类别
4. 非常重要：所有词条必须是中文，如果遇到英文词条，必须将其翻译成中文对应的概念
5. 合并相似或重复的词条
6. 每个子类别至少包含1个词条
7. 严禁在结果中包含任何英文词条，必须全部转换为中文
8. 禁止捏造词条内容，所有内容必须来源于教材文本

请按以下JSON格式返回结果（只返回JSON，不要有其他内容）：
{{
  "子类别1": ["中文词条1", "中文词条2", ...],
  "子类别2": ["中文词条3", "中文词条4", ...],
  ...
}}

需要分类的词条：
{', '.join(terms)}"""
        
        max_retries = 3
        retry_delay = 1  # 秒
        
        for attempt in range(max_retries):
            try:
                logger.info(f"调用API对{self.culture_mapping[culture_type]}词条进行分类... (尝试 {attempt + 1}/{max_retries})")
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000,
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
                                return {"未分类": self.filter_non_chinese_terms(terms)}
                    else:
                        logger.error(f"无法解析API响应: {completion}")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            return {"未分类": self.filter_non_chinese_terms(terms)}
                
                # 确保所有词条都是中文
                for subtype, subterms in classified_terms.items():
                    classified_terms[subtype] = self.filter_non_chinese_terms(subterms)
                    
                # 日志输出LLM返回的子类别和每个子类别的主题词数量、示例
                logger.info(f"LLM返回{self.culture_mapping[culture_type]}子类别数量: {len(classified_terms)}")
                for subtype, subterms in classified_terms.items():
                    logger.info(f"  子类别: {subtype}，数量: {len(subterms)}，示例: {subterms[:5]}")
                return classified_terms
                        
            except Exception as e:
                logger.error(f"调用API失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    return {"未分类": self.filter_non_chinese_terms(terms)}
    
    def filter_non_chinese_terms(self, terms: List[str]) -> List[str]:
        """
        过滤非中文词条或将混合词条转换为纯中文
        
        Args:
            terms (List[str]): 词条列表
            
        Returns:
            List[str]: 过滤后的词条列表
        """
        filtered_terms = []
        for term in terms:
            if not term:
                continue
                
            # 如果是中英混合，只保留中文部分
            if any(ord(c) < 128 for c in term) and not all(ord(c) < 128 for c in term):
                chinese_only = ''.join([c for c in term if ord(c) >= 128])
                if chinese_only.strip():
                    filtered_terms.append(chinese_only.strip())
            # 如果是纯英文，跳过（因为我们无法在这里翻译它）
            elif all(ord(c) < 128 for c in term):
                continue
            # 如果是纯中文，直接保留
            else:
                filtered_terms.append(term)
                
        return filtered_terms
    
    def generate_excel(self, culture_terms: Dict[str, List[str]], output_path: str) -> bool:
        """
        生成Excel表格
        
        Args:
            culture_terms (Dict[str, List[str]]): 按文化分类整理的词条
            output_path (str): 输出Excel文件路径
            
        Returns:
            bool: 是否成功生成Excel
        """
        try:
            # 准备数据
            data = []
            
            # 遍历每种文化类型
            for culture_type, terms in culture_terms.items():
                if not terms:
                    continue
                    
                # 对词条进行分类
                classified_terms = self.classify_terms(culture_type, terms)
                
                # 将分类结果添加到数据中
                for subtype, subterms in classified_terms.items():
                    if not subterms:
                        continue
                        
                    # 添加一行数据
                    data.append({
                        "文化分类": self.culture_mapping[culture_type],
                        "文化细类": f"{subtype}（{len(subterms)}）",
                        "教材文本主题": "、".join(subterms)
                    })
            
            logger.info(f"即将写入Excel的总行数: {len(data)}")
            
            # 创建DataFrame
            df = pd.DataFrame(data)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 保存为Excel
            df.to_excel(output_path, index=False)
            
            logger.info(f"Excel表格已保存到: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成Excel表格失败: {e}")
            return False
    
    def process_file(self, input_path: str, output_path: str) -> bool:
        """
        处理单个JSON文件
        
        Args:
            input_path (str): 输入JSON文件路径
            output_path (str): 输出Excel文件路径
            
        Returns:
            bool: 是否成功处理
        """
        try:
            logger.info(f"处理文件: {input_path}")
            
            # 加载JSON文件
            json_data = self.load_json_file(input_path)
            
            # 提取文化词条
            culture_terms = self.extract_culture_terms(json_data)
            
            # 生成Excel表格
            return self.generate_excel(culture_terms, output_path)
            
        except Exception as e:
            logger.error(f"处理文件失败: {e}")
            return False
    
    def process_directory(self, input_dir: str, output_dir: str) -> List[str]:
        """
        处理目录中的所有JSON文件
        
        Args:
            input_dir (str): 输入目录
            output_dir (str): 输出目录
            
        Returns:
            List[str]: 处理成功的文件列表
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取所有JSON文件
        json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]
        
        logger.info(f"找到 {len(json_files)} 个JSON文件")
        processed_files = []
        
        # 处理每个文件
        for i, json_file in enumerate(json_files, 1):
            logger.info(f"处理文件 {i}/{len(json_files)}: {json_file}")
            input_path = os.path.join(input_dir, json_file)
            output_file = json_file.replace('.json', '.xlsx')
            output_path = os.path.join(output_dir, output_file)
            
            if self.process_file(input_path, output_path):
                processed_files.append(output_path)
        
        return processed_files

def summarize_culture_terms(input_dir: str, output_dir: str, api_key: str = None, model: str = "deepseek-reasoner") -> None:
    """
    整理文化词条并生成Excel表格
    
    Args:
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        api_key (str, optional): DeepSeek API密钥
        model (str, optional): 使用的模型名称，可选 "deepseek-reasoner" 或 "deepseek-chat"
    """
    logger.info("=" * 50)
    logger.info("文化词条整理开始")
    logger.info(f"使用模型: {model}")
    logger.info("=" * 50)
    
    summarizer = CultureSummarizer(api_key, model)
    processed_files = summarizer.process_directory(input_dir, output_dir)
    
    logger.info("=" * 50)
    logger.info("文化词条整理完成")
    logger.info(f"共处理了 {len(processed_files)} 个文件")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 50)

if __name__ == "__main__":
    # 设置输入输出目录
    input_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/culture"
    output_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/excel"
    
    # API密钥将从.env文件或环境变量中读取
    api_key = None  # 让配置管理器自动处理
    
    # 设置模型（可选 "deepseek-reasoner" 或 "deepseek-chat"）
    model = "deepseek-reasoner"
    
    # 处理文件
    summarize_culture_terms(input_dir, output_dir, api_key, model) 