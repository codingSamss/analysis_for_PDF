import os
import json
import time
import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from textbook_analyzer.config import env_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AsyncCultureExtractor")

class AsyncCultureExtractor:
    """异步版本的文化词条提取器，支持并发请求、重试和断点续传"""
    
    def __init__(self, api_key: str = None, max_concurrent: int = 3, max_retries: int = 3):
        """
        初始化异步文化词条提取器
        
        Args:
            api_key (str, optional): DeepSeek API密钥
            max_concurrent (int): 最大并发请求数
            max_retries (int): 最大重试次数
        """
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # 定义三种文化类型
        self.culture_types = [
            "中华优秀传统文化",
            "革命文化",
            "社会主义先进文化"
        ]
        
        # 基础提示词模板
        self.prompt_template = """
你是一位精通中英文的翻译专家和文化研究学者，现在需要你分析英语教材内容中可能包含的文化元素。

请按照以下步骤操作：
1. 首先，理解并翻译提供的英文教材内容（如果内容是英文）
2. 分析这些内容中是否包含或暗示了与三种文化相关的元素：中华优秀传统文化、革命文化、社会主义先进文化
3. 提取出明确相关的词条，或者从内容中推断出隐含的文化元素
4. 注意：教材内容中可能通过人名、地名、活动、价值观等间接体现文化元素，严谨捏造出不存在于教材的内容


以下是三种文化的定义：

中华优秀传统文化是中华民族和中国人民在修齐治平、尊时守位、知常达变、开物成务、建功立业过程中逐渐形成的有别于其他民族的独特标识，其中蕴含的天下为公、民为邦本、为政以德、革故鼎新、任人唯贤、天人合一、自强不息、厚德载物、讲信修睦、亲仁善邻等，是中国人民在长期生产生活中积累的宇宙观、天下观、社会观、道德观的重要体现。

革命文化是近代以来特别是五四新文化运动以来，在党和人民的伟大斗争中培育和创造的思想理论、价值追求、精神品格，如红船精神、井冈山精神、长征精神、延安精神、沂蒙精神、西柏坡精神等，集中体现了马克思主义指导下的中国近现代文化的发展及其成果，展现了中国人民顽强不屈、坚韧不拔的民族气节和英雄气概。

社会主义先进文化是在党领导人民推进中国特色社会主义伟大实践中，在马克思主义指导下形成的面向现代化、面向世界、面向未来的，民族的科学的大众的社会主义文化，代表着时代进步潮流和发展要求。

分析提示：
- 中国地名、人名可能反映中华文化（如北京、上海、长城、康康、小雅等）
- 团队合作、友谊、尊重长辈等价值观可能体现传统文化
- 集体主义、爱国情怀可能体现革命文化或社会主义先进文化
- 科学、创新、环保等现代理念可能体现社会主义先进文化

请按以下JSON格式返回结果（只返回JSON，不要有其他内容）：
{{
  "中华优秀传统文化": ["词条1", "词条2", ...],
  "革命文化": ["词条1", "词条2", ...],
  "社会主义先进文化": ["词条1", "词条2", ...]
}}

分析的文本如下（{context_info}）：
{content}
"""

    async def call_deepseek_api(self, prompt: str, retry_count: int = 0) -> Optional[Dict[str, Any]]:
        """
        异步调用DeepSeek API，带重试机制
        
        Args:
            prompt (str): 提示词
            retry_count (int): 当前重试次数
            
        Returns:
            Optional[Dict[str, Any]]: API响应或None（如果请求失败）
        """
        if not self.api_key:
            raise ValueError("DeepSeek API密钥未设置")
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,  # 使用低温度提高输出一致性
            "max_tokens": 2000
        }
        
        logger.info("=" * 50)
        logger.info("API调用详情:")
        logger.info(f"模型: {payload['model']}")
        logger.info(f"温度: {payload['temperature']}")
        logger.info(f"最大token数: {payload['max_tokens']}")
        logger.info("提示词摘要: %s...", prompt[:100])
        
        # 使用信号量限制并发
        async with self.semaphore:
            try:
                logger.info("发送API请求...")
                start_time = time.time()
                
                # 创建一个超时为30秒的客户端会话
                timeout = aiohttp.ClientTimeout(total=30)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(self.api_url, headers=headers, json=payload) as response:
                        end_time = time.time()
                        logger.info(f"请求耗时: {end_time - start_time:.2f}秒")
                        logger.info(f"状态码: {response.status}")
                        
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"API错误响应: {error_text}")
                            
                            # 如果是可重试的错误（如429、500等）且未超过最大重试次数，则重试
                            if response.status in [429, 500, 502, 503, 504] and retry_count < self.max_retries:
                                retry_count += 1
                                wait_time = 2 ** retry_count  # 指数退避
                                logger.info(f"等待 {wait_time} 秒后进行第 {retry_count} 次重试...")
                                await asyncio.sleep(wait_time)
                                return await self.call_deepseek_api(prompt, retry_count)
                            return None
                            
                        result = await response.json()
                        
                        # 打印API响应摘要
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0].get("message", {}).get("content", "")
                            logger.info("API响应摘要:")
                            logger.info(content[:200] + "..." if len(content) > 200 else content)
                        
                        return result
                
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"API请求失败: {e}")
                
                # 如果未超过最大重试次数，则重试
                if retry_count < self.max_retries:
                    retry_count += 1
                    wait_time = 2 ** retry_count  # 指数退避
                    logger.info(f"等待 {wait_time} 秒后进行第 {retry_count} 次重试...")
                    await asyncio.sleep(wait_time)
                    return await self.call_deepseek_api(prompt, retry_count)
                    
                return None
    
    async def extract_from_node(self, node: Dict[str, Any], context_path: List[str] = None) -> Dict[str, Any]:
        """
        从单个节点异步提取文化词条
        
        Args:
            node (Dict[str, Any]): 节点数据
            context_path (List[str], optional): 上下文路径
            
        Returns:
            Dict[str, Any]: 提取结果
        """
        if not context_path:
            context_path = []
            
        # 只处理有内容的节点
        content = node.get("content", "").strip()
        if not content:
            return None
            
        # 构建提示词的上下文信息
        title = node.get("title", "")
        level = node.get("level", 0)
        level_name = ["文档", "章节", "主题", "文章"][min(level, 3)]
        
        context_info = f"{level_name}标题: {title}"
        if context_path:
            context_info += f", 路径: {' > '.join(context_path)}"
            
        logger.info(f"处理节点: {title}")
        logger.info(f"层级: {level} ({level_name})")
        logger.info(f"路径: {' > '.join(context_path) if context_path else '根节点'}")
        logger.info(f"内容长度: {len(content)} 字符")
        
        # 构建完整提示词
        prompt = self.prompt_template.format(
            context_info=context_info,
            content=content
        )
        
        # 调用API
        response = await self.call_deepseek_api(prompt)
        
        if not response:
            logger.error(f"提取失败: {title}")
            return None
            
        try:
            # 解析API响应
            completion = response.get("choices", [{}])[0].get("message", {}).get("content", "{}")
            
            # 尝试解析JSON响应
            try:
                result = json.loads(completion)
            except json.JSONDecodeError:
                # 如果无法解析JSON，尝试提取JSON部分
                json_start = completion.find("{")
                json_end = completion.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    try:
                        result = json.loads(completion[json_start:json_end])
                    except:
                        logger.error(f"无法解析API响应: {completion}")
                        result = {culture: [] for culture in self.culture_types}
                else:
                    logger.error(f"无法解析API响应: {completion}")
                    result = {culture: [] for culture in self.culture_types}
            
            # 确保结果包含所有文化类型
            for culture in self.culture_types:
                if culture not in result:
                    result[culture] = []
            
            # 添加节点元数据
            result["metadata"] = {
                "title": title,
                "level": level,
                "path": context_path + [title]
            }
            
            # 打印提取结果摘要
            logger.info("提取结果摘要:")
            for culture in self.culture_types:
                terms = result.get(culture, [])
                logger.info(f"{culture}: {len(terms)}个词条")
                if terms and terms[0] != "无":
                    logger.info(f"示例: {', '.join(terms[:3])}{'...' if len(terms) > 3 else ''}")
            
            return result
            
        except Exception as e:
            logger.error(f"处理API响应时出错: {e}")
            return None
    
    async def process_structure(self, structure: Dict[str, Any], processed_nodes: Set[str] = None) -> List[Dict[str, Any]]:
        """
        异步处理整个结构，提取文化词条，支持断点续传
        
        Args:
            structure (Dict[str, Any]): 结构数据
            processed_nodes (Set[str], optional): 已处理过的节点ID集合，用于断点续传
            
        Returns:
            List[Dict[str, Any]]: 提取结果列表
        """
        if processed_nodes is None:
            processed_nodes = set()
            
        results = []
        # 计算总节点数和需要处理的节点
        total_nodes = 0
        nodes_to_process = []
        
        def collect_nodes(node, path=[]):
            nonlocal total_nodes
            node_id = f"{node.get('title', '')}_{node.get('level', 0)}"
            
            if node.get("level", 0) > 0:
                total_nodes += 1
                if node_id not in processed_nodes and node.get("content", "").strip():
                    nodes_to_process.append((node, path))
            
            for child in node.get("children", []):
                new_path = path + [node.get("title", "")] if node.get("level", 0) > 0 else path
                collect_nodes(child, new_path)
        
        # 收集需要处理的节点
        collect_nodes(structure)
        
        logger.info(f"总节点数: {total_nodes}")
        logger.info(f"待处理节点数: {len(nodes_to_process)}")
        
        # 创建异步任务列表
        tasks = []
        for node, path in nodes_to_process:
            tasks.append(self.extract_from_node(node, path))
        
        # 使用as_completed异步处理所有节点，获取结果的顺序可能与提交顺序不同
        for i, future in enumerate(asyncio.as_completed(tasks), 1):
            try:
                result = await future
                if result:
                    results.append(result)
                    # 更新进度
                    logger.info(f"处理进度: {i}/{len(nodes_to_process)} ({i/len(nodes_to_process)*100:.1f}%)")
                    
                    # 保存当前处理过的节点ID
                    node_id = f"{result['metadata']['title']}_{result['metadata']['level']}"
                    processed_nodes.add(node_id)
                    
                    # 定期保存进度
                    if i % 10 == 0:
                        logger.info("保存处理进度...")
                        self.save_progress(processed_nodes)
            except Exception as e:
                logger.error(f"处理节点时出错: {e}")
        
        return results
    
    def save_progress(self, processed_nodes: Set[str], file_path: str = None):
        """
        保存处理进度
        
        Args:
            processed_nodes (Set[str]): 已处理节点ID集合
            file_path (str, optional): 进度文件路径
        """
        if file_path is None:
            file_path = "extraction_progress.json"
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(list(processed_nodes), f)
            logger.info(f"进度已保存到 {file_path}")
        except Exception as e:
            logger.error(f"保存进度失败: {e}")
    
    def load_progress(self, file_path: str = None) -> Set[str]:
        """
        加载处理进度
        
        Args:
            file_path (str, optional): 进度文件路径
            
        Returns:
            Set[str]: 已处理节点ID集合
        """
        if file_path is None:
            file_path = "extraction_progress.json"
            
        if not os.path.exists(file_path):
            return set()
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"加载进度失败: {e}")
            return set()
    
    async def process_file(self, input_path: str, output_path: str, resume: bool = True) -> bool:
        """
        异步处理单个JSON文件，支持断点续传
        
        Args:
            input_path (str): 输入JSON文件路径
            output_path (str): 输出JSON文件路径
            resume (bool): 是否从上次中断处继续
            
        Returns:
            bool: 是否成功处理
        """
        try:
            logger.info(f"开始处理文件: {input_path}")
            start_time = time.time()
            
            # 读取JSON文件
            with open(input_path, 'r', encoding='utf-8') as f:
                structure = json.load(f)
            
            # 加载处理进度
            progress_file = f"{output_path}.progress"
            processed_nodes = self.load_progress(progress_file) if resume else set()
            
            # 处理结构
            results = await self.process_structure(structure, processed_nodes)
            
            # 构建结果数据
            output_data = {
                "document": os.path.basename(input_path).replace('.json', ''),
                "results": results
            }
            
            # 保存结果
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            end_time = time.time()
            logger.info(f"文件处理完成: {output_path}")
            logger.info(f"总耗时: {end_time - start_time:.2f}秒")
            logger.info(f"处理节点数: {len(results)}")
            
            # 清理进度文件
            if os.path.exists(progress_file):
                os.remove(progress_file)
                
            return True
            
        except Exception as e:
            logger.error(f"处理文件 {input_path} 时出错: {e}")
            return False
    
    async def process_directory(self, input_dir: str, output_dir: str, resume: bool = True) -> List[str]:
        """
        异步处理目录中的所有JSON文件，支持断点续传
        
        Args:
            input_dir (str): 输入目录
            output_dir (str): 输出目录
            resume (bool): 是否从上次中断处继续
            
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
            output_file = json_file.replace('.json', '_culture.json')
            output_path = os.path.join(output_dir, output_file)
            
            # 如果不是续传模式，或者输出文件不存在，则处理文件
            if not resume or not os.path.exists(output_path):
                if await self.process_file(input_path, output_path, resume):
                    processed_files.append(output_path)
            else:
                logger.info(f"文件已处理，跳过: {output_path}")
                processed_files.append(output_path)
        
        return processed_files

async def extract_culture_terms_async(input_dir: str, output_dir: str, api_key: str = None, 
                                      max_concurrent: int = 3, resume: bool = True, verbose: bool = False) -> None:
    """
    异步提取文化词条
    
    Args:
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        api_key (str, optional): DeepSeek API密钥
        max_concurrent (int): 最大并发请求数
        resume (bool): 是否从上次中断处继续
        verbose (bool): 是否显示详细信息
    """
    # 使用配置管理器获取API key
    api_key = env_config.get_api_key(api_key)
    
    # 设置日志级别
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("=" * 50)
    logger.info("文化词条提取开始")
    logger.info("=" * 50)
    logger.info(f"最大并发请求数: {max_concurrent}")
    logger.info(f"断点续传模式: {'启用' if resume else '禁用'}")
    
    # 创建提取器
    extractor = AsyncCultureExtractor(api_key, max_concurrent)
    
    # 处理目录
    processed_files = await extractor.process_directory(input_dir, output_dir, resume)
    
    logger.info("=" * 50)
    logger.info("文化词条提取完成")
    logger.info(f"共处理了 {len(processed_files)} 个文件")
    logger.info(f"输出目录: {output_dir}")
    logger.info("=" * 50)

def extract_culture_terms(input_dir: str, output_dir: str, api_key: str = None, 
                          max_concurrent: int = 3, resume: bool = True, verbose: bool = False) -> None:
    """
    提取文化词条（同步入口函数）
    
    Args:
        input_dir (str): 输入目录
        output_dir (str): 输出目录
        api_key (str, optional): DeepSeek API密钥
        max_concurrent (int): 最大并发请求数
        resume (bool): 是否从上次中断处继续
        verbose (bool): 是否显示详细信息
    """
    asyncio.run(extract_culture_terms_async(input_dir, output_dir, api_key, max_concurrent, resume, verbose))

async def test_extract_single_node_async(api_key: str, content: str, context_info: str = "测试内容") -> None:
    """
    测试单个节点的词条提取（异步版本）
    
    Args:
        api_key (str): DeepSeek API密钥
        content (str): 要分析的内容
        context_info (str): 上下文信息
    """
    if not api_key:
        raise ValueError("未提供DeepSeek API密钥")
        
    logger.info("=" * 50)
    logger.info("开始测试单个节点提取")
    logger.info("=" * 50)
    
    extractor = AsyncCultureExtractor(api_key)
    
    # 构建测试节点
    test_node = {
        "title": "测试节点",
        "level": 1,
        "content": content
    }
    
    # 提取词条
    result = await extractor.extract_from_node(test_node, [context_info])
    
    # 打印结果
    if result:
        logger.info("提取结果:")
        logger.info(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        logger.info("提取失败")
    
    logger.info("=" * 50)
    logger.info("测试完成")
    logger.info("=" * 50)

def test_extract_single_node(api_key: str, content: str, context_info: str = "测试内容") -> None:
    """
    测试单个节点的词条提取（同步入口函数）
    
    Args:
        api_key (str): DeepSeek API密钥
        content (str): 要分析的内容
        context_info (str): 上下文信息
    """
    asyncio.run(test_extract_single_node_async(api_key, content, context_info))

if __name__ == "__main__":
    # 测试代码 - API key 将从.env文件或环境变量中读取
    api_key = None  # 让配置管理器自动处理
    
    # 取消下面的注释来测试单个节点提取
    # test_content = """
    # 在中国传统文化中，孝道是一种重要的价值观念。尊老爱幼体现了中华民族的传统美德。
    # 红色革命精神激励着一代又一代人前进。井冈山精神和长征精神是中国革命文化的重要组成部分。
    # 中国共产党领导人民创造了社会主义先进文化，科学发展观和中国特色社会主义理论体系指导着国家建设。
    # """
    # test_extract_single_node(api_key, test_content)
    
    # 实际处理目录
    input_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/structure"
    output_dir = "/Users/suqi3/Desktop/paper/textbook_analyzer/data/json/culture"
    
    # 取消下面的注释来处理整个目录
    # extract_culture_terms(input_dir, output_dir, api_key, max_concurrent=3, resume=True, verbose=True) 