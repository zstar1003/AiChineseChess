import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chess-llm-battle-secret-key'
    
    # API配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL = os.environ.get('DEEPSEEK_BASE_URL') or 'https://api.deepseek.com/v1'
    
    # 对战配置
    MAX_THINKING_TIME = 30  # 最大思考时间（秒）
    MAX_MOVES = 200  # 最大步数
    
    # 模型配置
    SUPPORTED_MODELS = {
        'openai': {
            'gpt-4': 'GPT-4',
            'gpt-4-turbo': 'GPT-4 Turbo',
            'o3-mini': 'OpenAI o3-mini',
            'o3': 'OpenAI o3'
        },
        'deepseek': {
            'deepseek-chat': 'DeepSeek Chat',
            'deepseek-coder': 'DeepSeek Coder'
        },
        'claude': {
            'claude-3-sonnet': 'Claude 3 Sonnet',
            'claude-3-opus': 'Claude 3 Opus'
        }
    }