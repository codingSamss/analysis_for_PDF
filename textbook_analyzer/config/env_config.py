import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

class EnvConfig:
    """环境变量配置管理类"""
    
    _instance = None
    _loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._loaded:
            self._load_env()
            self._loaded = True
    
    def _load_env(self):
        """加载.env文件"""
        # 查找项目根目录的.env文件
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent  # 向上两级到项目根目录
        env_file = project_root / '.env'
        
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # 如果没有.env文件，尝试加载.env.example作为参考
            env_example = project_root / '.env.example'
            if env_example.exists():
                print(f"警告：未找到.env文件，请复制 {env_example} 为 .env 并配置您的API密钥")
    
    @property
    def deepseek_api_key(self) -> Optional[str]:
        """获取DeepSeek API密钥"""
        return os.getenv('DEEPSEEK_API_KEY')
    
    @property
    def deepseek_base_url(self) -> str:
        """获取DeepSeek API基础URL"""
        return os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    @property
    def default_model(self) -> str:
        """获取默认模型名称"""
        return os.getenv('DEFAULT_MODEL', 'deepseek-reasoner')
    
    def get_api_key(self, provided_key: Optional[str] = None) -> str:
        """
        获取API密钥，优先使用提供的密钥，否则使用环境变量
        
        Args:
            provided_key: 外部提供的API密钥
            
        Returns:
            str: API密钥
            
        Raises:
            ValueError: 如果没有找到有效的API密钥
        """
        api_key = provided_key or self.deepseek_api_key
        
        if not api_key:
            raise ValueError(
                "未找到DeepSeek API密钥！\n"
                "请通过以下方式之一提供API密钥：\n"
                "1. 在项目根目录创建.env文件并设置 DEEPSEEK_API_KEY=your-key\n"
                "2. 设置环境变量 DEEPSEEK_API_KEY\n"
                "3. 通过命令行参数 --api_key 提供\n"
                "4. 可以复制 .env.example 为 .env 作为模板"
            )
        
        return api_key


# 创建全局实例
env_config = EnvConfig() 