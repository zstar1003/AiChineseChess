import time
from typing import List, Dict, Optional
from .chess_game import ChessGame
from .llm_player import LLMPlayer

class ChessBattle:
    """象棋对战管理类"""
    
    def __init__(self, red_player: LLMPlayer, black_player: LLMPlayer):
        self.game = ChessGame()
        self.red_player = red_player
        self.black_player = black_player
        self.battle_log = []
        self.start_time = time.time()
        self.status = "waiting"  # waiting, playing, finished, error
        
    def start_battle(self) -> Dict:
        """开始对战（同步版本，用于测试）"""
        self.status = "playing"
        self.start_time = time.time()
        
        move_count = 0
        max_moves = 200  # 最大步数限制
        
        while not self.game.is_game_over() and move_count < max_moves:
            try:
                # 获取当前玩家
                current_player = (self.red_player 
                                if self.game.current_player == "red" 
                                else self.black_player)
                
                print(f"轮到 {current_player.display_name} 下棋...")
                
                # 获取模型的下一步棋
                move_result = current_player.get_move(
                    self.game.get_board_state(),
                    self.game.move_history
                )
                
                if move_result and self.game.make_move(move_result['move']):
                    # 记录棋步
                    self.log_move(current_player.display_name, move_result)
                    move_count += 1
                    
                    print(f"{current_player.display_name} 走了: {move_result['move']}")
                    if move_result.get('thinking'):
                        print(f"思考过程: {move_result['thinking'][:100]}...")
                    
                else:
                    # 无效棋步，结束游戏
                    self.status = "error"
                    error_msg = f"{current_player.display_name} 产生了无效棋步"
                    print(error_msg)
                    self.battle_log.append({
                        'type': 'error',
                        'message': error_msg,
                        'timestamp': time.time()
                    })
                    break
                    
            except Exception as e:
                self.status = "error"
                error_msg = f"对战出错: {str(e)}"
                print(error_msg)
                self.battle_log.append({
                    'type': 'error',
                    'message': error_msg,
                    'timestamp': time.time()
                })
                break
        
        # 游戏结束
        self.status = "finished"
        result = self.get_battle_result()
        
        return {
            'result': result,
            'total_moves': len(self.game.move_history),
            'duration': time.time() - self.start_time,
            'battle_log': self.battle_log,
            'final_board': self.game.get_board_unicode(),
            'pgn': self.game.get_pgn()
        }
    
    def log_move(self, player_name: str, move_result: Dict):
        """记录棋步到对战日志"""
        log_entry = {
            'type': 'move',
            'player': player_name,
            'move': move_result['move'],
            'thinking': move_result.get('thinking', ''),
            'analysis': move_result.get('analysis', ''),
            'strategy': move_result.get('strategy', ''),
            'thinking_time': move_result.get('thinking_time', 0),
            'board_state': self.game.get_board_state(),
            'move_count': len(self.game.move_history),
            'timestamp': time.time(),
            'evaluation': self.game.get_position_evaluation()
        }
        
        self.battle_log.append(log_entry)
    
    def get_battle_result(self) -> Dict:
        """获取对战结果"""
        if not self.game.is_game_over() and self.status != "error":
            return {
                'status': 'ongoing',
                'message': '对局进行中',
                'winner': None
            }
        
        if self.status == "error":
            return {
                'status': 'error',
                'message': '对局因错误结束',
                'winner': None
            }
        
        game_result = self.game.get_game_result()
        
        if "白方获胜" in game_result:
            winner = self.red_player.display_name
            message = f"{winner} 获胜（白方）"
        elif "黑方获胜" in game_result:
            winner = self.black_player.display_name
            message = f"{winner} 获胜（黑方）"
        else:
            winner = None
            message = "平局"
        
        return {
            'status': 'finished',
            'message': message,
            'winner': winner,
            'game_result': game_result,
            'total_moves': len(self.game.move_history),
            'duration': time.time() - self.start_time
        }
    
    def get_current_status(self) -> Dict:
        """获取当前对战状态"""
        return {
            'status': self.status,
            'board_state': self.game.get_board_state(),
            'board_unicode': self.game.get_board_unicode(),
            'current_player': self.game.current_player,
            'move_count': len(self.game.move_history),
            'is_game_over': self.game.is_game_over(),
            'last_move': self.game.get_last_move(),
            'legal_moves': self.game.get_legal_moves(),
            'evaluation': self.game.get_position_evaluation(),
            'red_player': self.red_player.display_name,
            'black_player': self.black_player.display_name
        }
    
    def get_battle_summary(self) -> Dict:
        """获取对战总结"""
        red_stats = self.red_player.get_stats()
        black_stats = self.black_player.get_stats()
        
        return {
            'battle_info': {
                'start_time': self.start_time,
                'duration': time.time() - self.start_time,
                'total_moves': len(self.game.move_history),
                'status': self.status
            },
            'players': {
                'red': red_stats,
                'black': black_stats
            },
            'result': self.get_battle_result(),
            'move_history': self.game.move_history,
            'battle_log': self.battle_log,
            'pgn': self.game.get_pgn()
        }
    
    def pause_battle(self):
        """暂停对战"""
        if self.status == "playing":
            self.status = "paused"
    
    def resume_battle(self):
        """恢复对战"""
        if self.status == "paused":
            self.status = "playing"
    
    def stop_battle(self):
        """停止对战"""
        self.status = "stopped"
    
    def reset_battle(self):
        """重置对战"""
        self.game.reset()
        self.battle_log = []
        self.start_time = time.time()
        self.status = "waiting"
        self.red_player.move_count = 0
        self.red_player.total_thinking_time = 0
        self.black_player.move_count = 0
        self.black_player.total_thinking_time = 0