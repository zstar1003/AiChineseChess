import openai
import requests
import json
import time
import re
from typing import Dict, Optional, List, Generator
from google import genai

class LLMPlayer:
    """大语言模型中国象棋玩家类"""
    
    def __init__(self, model_name: str, api_key: str, base_url: Optional[str] = None, display_name: str = "", socketio=None):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self.display_name = display_name or model_name
        self.move_count = 0
        self.total_thinking_time = 0
        self.socketio = socketio
    
    def get_move(self, board_state: str, move_history: List[dict]) -> Optional[Dict]:
        """获取模型的下一步棋（支持流式输出）
        
        Args:
            board_state: 当前棋盘状态
            move_history: 历史棋步列表
            
        Returns:
            Dict: 包含棋步和思考过程的字典
        """
        start_time = time.time()
        
        try:
            # 构建提示词
            prompt = self.build_chess_prompt(board_state, move_history)
            
            # 确定玩家颜色
            player_color = "red" if len(move_history) % 2 == 0 else "black"
            
            # 调用相应的流式API
            if "deepseek" in self.model_name.lower():
                response = self.call_deepseek_stream(prompt, player_color)
            elif "gemini" in self.model_name.lower():
                response = self.call_gemini_stream(prompt, player_color)
            else:
                # 回退到非流式API
                if "openai" in self.model_name.lower() or "gpt" in self.model_name.lower():
                    response = self.call_openai_api(prompt)
                elif "claude" in self.model_name.lower():
                    response = self.call_claude_api(prompt)
                else:
                    response = self.call_generic_api(prompt)
            
            # 解析响应
            move_info = self.parse_response(response)
            
            # 记录思考时间
            thinking_time = time.time() - start_time
            self.total_thinking_time += thinking_time
            self.move_count += 1
            
            if move_info:
                move_info['thinking_time'] = thinking_time
                move_info['player'] = self.display_name
                return move_info
            
        except Exception as e:
            print(f"获取{self.display_name}棋步时出错: {e}")
        
        return None
    
    def call_deepseek_stream(self, prompt: str, player_color: str) -> str:
        """调用DeepSeek流式API - 严格按照test_deepseek.py的逻辑"""
        try:
            # 严格按照test_deepseek.py的格式
            url = "https://api.siliconflow.cn/v1/chat/completions"
            
            payload = {
                "model": "deepseek-ai/DeepSeek-R1",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]
                            if line.strip() == '[DONE]':
                                break
                            try:
                                chunk = json.loads(line)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta and delta['content'] is not None:
                                        content = delta['content']
                                        full_response += content
                                        # 发送流式思考过程
                                        if self.socketio:
                                            self.socketio.emit('thinking_stream', {
                                                'player': player_color,
                                                'content': content,
                                                'is_complete': False
                                            })
                            except json.JSONDecodeError:
                                continue
                
                # 发送完成信号
                if self.socketio:
                    self.socketio.emit('thinking_stream', {
                        'player': player_color,
                        'content': '',
                        'is_complete': True
                    })
                
                return full_response
            else:
                print(f"DeepSeek流式API错误: {response.status_code} - {response.text}")
                return ""
                
        except Exception as e:
            print(f"DeepSeek流式API调用失败: {e}")
            return ""
    
    def call_gemini_stream(self, prompt: str, player_color: str) -> str:
        """调用Gemini流式API"""
        try:
            client = genai.Client(api_key=self.api_key)
            
            # 构建完整的提示
            full_prompt = f"你是一位专业的中国象棋大师，擅长分析局面和制定策略。\n\n{prompt}"
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt,
                config=genai.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            
            # Gemini API目前不支持真正的流式输出，我们模拟流式效果
            full_text = response.text
            
            # 按句子分割并逐步发送
            sentences = re.split(r'([。！？\n])', full_text)
            current_text = ""
            
            for i in range(0, len(sentences), 2):
                if i < len(sentences):
                    sentence = sentences[i]
                    if i + 1 < len(sentences):
                        sentence += sentences[i + 1]
                    
                    current_text += sentence
                    
                    if self.socketio:
                        self.socketio.emit('thinking_stream', {
                            'player': player_color,
                            'content': sentence,
                            'is_complete': False
                        })
                    
                    # 短暂延迟模拟流式效果
                    time.sleep(0.1)
            
            # 发送完成信号
            if self.socketio:
                self.socketio.emit('thinking_stream', {
                    'player': player_color,
                    'content': '',
                    'is_complete': True
                })
            
            return full_text
            
        except Exception as e:
            print(f"Gemini流式API调用失败: {e}")
            return ""
    
    def build_chess_prompt(self, board_state: str, move_history: List[dict]) -> str:
        """构建中国象棋提示词"""
        
        # 历史棋步字符串
        history_str = ""
        if move_history:
            for i, move in enumerate(move_history[-10:], 1):  # 只显示最近10步
                notation = move.get('notation', move.get('move', ''))
                player = "红方" if move.get('player') == 'red' else "黑方"
                history_str += f"{i}. {player}: {notation}\n"
        
        # 当前轮次
        current_turn = "红方" if len(move_history) % 2 == 0 else "黑方"
        
        # 棋盘说明
        board_explanation = """
棋盘格式说明：
- 大写字母代表红方棋子：K=帅, A=仕, B=相, N=马, R=车, C=炮, P=兵
- 小写字母代表黑方棋子：k=将, a=士, b=象, n=马, r=车, c=炮, p=卒
- '.' 代表空位
- 坐标系统：列用a-i表示(从左到右)，行用0-9表示(从上到下)
"""
        
        prompt = f"""你是一位中国象棋大师，正在进行一场中国象棋对局。

{board_explanation}

当前局面信息：
- 棋盘状态: {board_state}
- 当前轮次: {current_turn}
- 总步数: {len(move_history)}

最近棋步历史：
{history_str if history_str else "游戏刚开始"}

请分析当前局面并选择你的下一步棋。

要求：
1. 仔细分析当前局面的优劣势
2. 考虑可能的战术和战略（如：开局布阵、中局攻杀、残局技巧）
3. 选择最佳的下一步棋
4. 用坐标格式返回你的棋步（如：a0a1表示从a0移动到a1）

中国象棋规则提醒：
- 帅/将只能在九宫格内移动
- 士/仕只能在九宫格内斜走
- 相/象不能过河，走田字
- 马走日字，但可能被蹩腿
- 车走直线
- 炮走直线，吃子需要跳过一个棋子
- 兵/卒过河前只能向前，过河后可以左右移动

请按以下格式回复：
分析：[你对当前局面的分析]
策略：[你的下棋策略]
棋步：[坐标格式的棋步，如a0a1]

示例：
分析：当前开局阶段，需要快速出子控制中路
策略：先手出炮控制中路，为后续攻击做准备
棋步：b7b4
"""
        return prompt
    
    def call_openai_api(self, prompt: str) -> str:
        """调用OpenAI API"""
        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一位专业的中国象棋大师，擅长分析局面和制定策略。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            return ""
    
    def call_deepseek_api(self, prompt: str) -> str:
        """调用DeepSeek API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是一位专业的中国象棋大师，擅长分析局面和制定策略。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"DeepSeek API错误: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"DeepSeek API调用失败: {e}")
            return ""
    
    def call_claude_api(self, prompt: str) -> str:
        """调用Claude API"""
        try:
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            data = {
                "model": self.model_name,
                "max_tokens": 500,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
            else:
                print(f"Claude API错误: {response.status_code}")
                return ""
                
        except Exception as e:
            print(f"Claude API调用失败: {e}")
            return ""
    
    def call_generic_api(self, prompt: str) -> str:
        """调用通用API（兼容OpenAI格式）"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是一位专业的中国象棋大师。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return ""
                
        except Exception as e:
            print(f"通用API调用失败: {e}")
            return ""
    
    def parse_response(self, response: str) -> Optional[Dict]:
        """解析模型响应，提取棋步和思考过程"""
        if not response:
            return None
        
        try:
            # 提取分析内容
            analysis_match = re.search(r'分析[：:]\s*(.+?)(?=策略|棋步|$)', response, re.DOTALL)
            analysis = analysis_match.group(1).strip() if analysis_match else ""
            
            # 提取策略内容
            strategy_match = re.search(r'策略[：:]\s*(.+?)(?=棋步|$)', response, re.DOTALL)
            strategy = strategy_match.group(1).strip() if strategy_match else ""
            
            # 提取棋步（中国象棋坐标格式）
            move_match = re.search(r'棋步[：:]\s*([a-i][0-9][a-i][0-9])', response)
            if not move_match:
                # 尝试其他格式
                move_match = re.search(r'([a-i][0-9][a-i][0-9])', response)
            
            if move_match:
                move = move_match.group(1).lower()
                return {
                    'move': move,
                    'analysis': analysis,
                    'strategy': strategy,
                    'thinking': f"分析: {analysis}\n策略: {strategy}",
                    'raw_response': response
                }
            else:
                print(f"无法从响应中提取有效棋步: {response}")
                return None
                
        except Exception as e:
            print(f"解析响应时出错: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """获取玩家统计信息"""
        avg_thinking_time = self.total_thinking_time / self.move_count if self.move_count > 0 else 0
        return {
            'display_name': self.display_name,
            'model_name': self.model_name,
            'move_count': self.move_count,
            'total_thinking_time': self.total_thinking_time,
            'avg_thinking_time': avg_thinking_time
        }