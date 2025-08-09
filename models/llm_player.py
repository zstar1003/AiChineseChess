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
        """调用DeepSeek流式API - 使用requests直接调用避免OpenAI客户端问题"""
        try:
            print(f"开始调用DeepSeek流式API，玩家颜色: {player_color}")
            
            # 使用 requests 直接调用流式API，避免 OpenAI 客户端的兼容性问题
            import requests
            import json
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "deepseek-ai/DeepSeek-R1-0528-Qwen3-8B",
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": True
            }
            
            print(f"发送请求到: https://api.siliconflow.cn/v1/chat/completions")
            
            response = requests.post(
                "https://api.siliconflow.cn/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"API请求失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                return ""
            
            print("开始接收流式响应...")
            
            full_content = ""
            chunk_count = 0
            buffer = ""  # 缓冲区，用于积累内容
            buffer_size = 20  # 每20个字符发送一次，减少零碎输出
            
            # 处理流式响应
            for line in response.iter_lines():
                if line:
                    chunk_count += 1
                    line_str = line.decode('utf-8')
                    
                    # 跳过非数据行
                    if not line_str.startswith('data: '):
                        continue
                    
                    # 移除 "data: " 前缀
                    json_str = line_str[6:]
                    
                    # 跳过结束标记
                    if json_str.strip() == '[DONE]':
                        break
                    
                    try:
                        # 解析JSON数据
                        chunk_data = json.loads(json_str)
                        
                        if 'choices' in chunk_data and chunk_data['choices']:
                            delta = chunk_data['choices'][0].get('delta', {})
                            
                            # 处理普通内容
                            if 'content' in delta and delta['content']:
                                content = delta['content']
                                full_content += content
                                buffer += content
                            
                            # 处理推理内容（DeepSeek-R1特有）
                            if 'reasoning_content' in delta and delta['reasoning_content']:
                                reasoning_content = delta['reasoning_content']
                                full_content += reasoning_content
                                buffer += reasoning_content
                            
                            # 当缓冲区达到一定大小时发送
                            if len(buffer) >= buffer_size:
                                print(f"发送缓冲内容 (长度{len(buffer)}): {repr(buffer[:50])}...")
                                if self.socketio:
                                    try:
                                        # 使用Flask-SocketIO的正确方式发送事件
                                        event_data = {
                                            'player': player_color,
                                            'content': buffer,
                                            'is_complete': False
                                        }
                                        print(f"准备发送事件数据: {event_data}")
                                        
                                        # 发送事件
                                        self.socketio.emit('thinking_stream', event_data)
                                        print(f"成功发送thinking_stream事件到{player_color}")
                                        
                                        # 强制刷新Socket.IO
                                        self.socketio.sleep(0.01)
                                        
                                    except Exception as e:
                                        print(f"发送thinking_stream事件失败: {e}")
                                        import traceback
                                        traceback.print_exc()
                                else:
                                    print("警告: socketio实例为None")
                                buffer = ""  # 清空缓冲区
                    
                    except json.JSONDecodeError as e:
                        print(f"解析JSON失败: {e}, 原始数据: {json_str}")
                        continue
            
            # 发送剩余的缓冲内容
            if buffer:
                print(f"发送最后的缓冲内容 (长度{len(buffer)}): {repr(buffer[:50])}...")
                if self.socketio:
                    try:
                        self.socketio.emit('thinking_stream', {
                            'player': player_color,
                            'content': buffer,
                            'is_complete': False
                        })
                        print(f"成功发送最后的thinking_stream事件到{player_color}")
                    except Exception as e:
                        print(f"发送最后的thinking_stream事件失败: {e}")
                else:
                    print("警告: socketio实例为None")
            
            print(f"流式响应完成，总块数: {chunk_count}, 总内容长度: {len(full_content)}")
            
            # 发送完成信号
            if self.socketio:
                try:
                    print("发送流式完成信号")
                    self.socketio.emit('thinking_stream', {
                        'player': player_color,
                        'content': '',
                        'is_complete': True
                    })
                    print(f"成功发送完成信号到{player_color}")
                except Exception as e:
                    print(f"发送完成信号失败: {e}")
            else:
                print("警告: socketio实例为None，无法发送完成信号")
            
            return full_content
                
        except Exception as e:
            print(f"DeepSeek流式API调用失败: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def call_gemini_stream(self, prompt: str, player_color: str) -> str:
        """调用Gemini流式API"""
        try:
            from google import genai
            
            # 创建客户端（API密钥从环境变量获取）
            client = genai.Client(api_key=self.api_key)
            
            # 构建完整的提示
            full_prompt = f"你是一位专业的中国象棋大师，擅长分析局面和制定策略。\n\n{prompt}"
            
            # 生成内容
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
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
            import traceback
            traceback.print_exc()
            return ""
    
    def format_board_display(self, board_state: str) -> str:
        """将棋盘状态转换为更直观的显示格式"""
        try:
            # 将棋盘状态按行分割
            lines = board_state.strip().split('\n')
            if len(lines) != 10:
                return board_state  # 如果格式不正确，返回原始状态
            
            # 添加列标识
            display = "  a b c d e f g h i\n"
            
            for i, line in enumerate(lines):
                # 添加行号和棋子，用空格分隔
                row_display = f"{i} "
                for j, char in enumerate(line):
                    if j < len(line):
                        row_display += char + " "
                display += row_display.rstrip() + "\n"
            
            return display
            
        except Exception as e:
            print(f"格式化棋盘显示时出错: {e}")
            return board_state

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
        
        # 将棋盘状态转换为更直观的显示
        board_display = self.format_board_display(board_state)
        
        # 棋盘说明
        board_explanation = f"""
棋盘格式说明：
- 大写字母代表红方棋子：K=帅, A=仕, B=相, N=马, R=车, C=炮, P=兵
- 小写字母代表黑方棋子：k=将, a=士, b=象, n=马, r=车, c=炮, p=卒
- '.' 代表空位
- 坐标系统：列用a-i表示(从左到右)，行用0-9表示(从上到下)

当前棋盘状态（带坐标）：
{board_display}

【重要规则 - 必须严格遵守】：
1. 绝对不能移动到己方棋子占据的位置！
   - 红方棋子（大写字母）不能移动到有其他红方棋子的位置
   - 黑方棋子（小写字母）不能移动到有其他黑方棋子的位置
2. 只能移动到空位（'.'）或吃掉对方棋子的位置
3. 必须遵守各棋子的移动规则
4. 兵/卒过河前只能向前，过河后可以左右移动
5. 炮吃子需要跳过一个棋子，不吃子时路径必须畅通

【棋步验证步骤】：
在选择棋步前，请务必检查：
1. 起始位置是否有你的棋子？
2. 目标位置是否为空位或对方棋子？
3. 移动路径是否符合该棋子的规则？
4. 是否违反了任何象棋规则？
"""
        
        prompt = f"""你是一位中国象棋大师，正在进行一场中国象棋对局。

{board_explanation}

当前局面信息：
- 当前轮次: {current_turn}
- 总步数: {len(move_history)}

最近棋步历史：
{history_str if history_str else "游戏刚开始"}

请分析当前局面并选择你的下一步棋。

要求：
1. 仔细观察棋盘，确认每个位置的棋子
2. 分析当前局面的优劣势
3. 考虑可能的战术和战略
4. 选择一个合法有效的棋步
5. 用坐标格式返回你的棋步（如：a0a1表示从a0移动到a1）

中国象棋规则提醒：
- 帅/将只能在九宫格内移动，一次一格
- 士/仕只能在九宫格内斜走
- 相/象不能过河，走田字，不能被塞象眼
- 马走日字，但可能被蹩腿
- 车走直线，路径必须畅通
- 炮走直线，吃子需要跳过一个棋子，不吃子时路径必须畅通
- 兵/卒过河前只能向前，过河后可以左右移动

请按以下格式回复：
分析：[你对当前局面的分析，包括棋子位置观察]
策略：[你的下棋策略]
棋步：[坐标格式的棋步，如a0a1]

注意：请确保你的棋步是合法的，不要移动到己方棋子占据的位置！
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
            print(f"开始解析响应，响应长度: {len(response)}")
            print(f"响应内容预览: {response[-500:]}")  # 显示最后500个字符
            
            # 提取分析内容
            analysis_match = re.search(r'分析[：:]\s*(.+?)(?=策略|棋步|$)', response, re.DOTALL)
            analysis = analysis_match.group(1).strip() if analysis_match else ""
            
            # 提取策略内容
            strategy_match = re.search(r'策略[：:]\s*(.+?)(?=棋步|$)', response, re.DOTALL)
            strategy = strategy_match.group(1).strip() if strategy_match else ""
            
            # 提取棋步（中国象棋坐标格式）- 更宽松的匹配
            move_patterns = [
                r'棋步[：:]\s*([a-i][0-9][a-i][0-9])',  # 标准格式：棋步：e6e7
                r'([a-i][0-9][a-i][0-9])\s*$',          # 行末的坐标格式
                r'([a-i][0-9][a-i][0-9])',              # 任何位置的坐标格式
            ]
            
            move = None
            for pattern in move_patterns:
                move_match = re.search(pattern, response)
                if move_match:
                    move = move_match.group(1).lower()
                    print(f"使用模式 '{pattern}' 找到棋步: {move}")
                    break
            
            if move:
                result = {
                    'move': move,
                    'analysis': analysis,
                    'strategy': strategy,
                    'thinking': f"分析: {analysis}\n策略: {strategy}",
                    'raw_response': response
                }
                print(f"成功解析棋步: {result}")
                return result
            else:
                print(f"无法从响应中提取有效棋步")
                print(f"完整响应内容: {response}")
                return None
                
        except Exception as e:
            print(f"解析响应时出错: {e}")
            import traceback
            traceback.print_exc()
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