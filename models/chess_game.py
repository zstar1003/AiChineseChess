from typing import List, Optional, Dict, Tuple
import time
import copy

class ChessGame:
    """中国象棋游戏核心逻辑类"""
    
    def __init__(self):
        self.board = self.init_board()
        self.move_history = []
        self.current_player = "red"  # red=红方, black=黑方
        self.start_time = time.time()
        self.move_times = []
        
        # 棋子名称映射
        self.piece_names = {
            'K': '帅', 'A': '仕', 'B': '相', 'N': '马', 'R': '车', 'C': '炮', 'P': '兵',
            'k': '将', 'a': '士', 'b': '象', 'n': '马', 'r': '车', 'c': '炮', 'p': '卒'
        }
        
    def init_board(self) -> List[List[str]]:
        """初始化中国象棋棋盘"""
        board = [
            ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],  # 黑方后排
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],    # 空行
            ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],    # 黑炮
            ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],    # 黑兵
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],    # 楚河汉界
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],    # 楚河汉界
            ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],    # 红兵
            ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],    # 红炮
            ['.', '.', '.', '.', '.', '.', '.', '.', '.'],    # 空行
            ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']    # 红方后排
        ]
        return board
    
    def make_move(self, move_str: str) -> bool:
        """执行棋步
        
        Args:
            move_str: 棋步字符串，如 "a0a1" 或中文记谱法如 "炮二平五"
            
        Returns:
            bool: 是否成功执行棋步
        """
        try:
            # 解析棋步
            if len(move_str) == 4 and move_str[0].isalpha():
                # 坐标格式：如 "a0a1"
                from_pos = self.coord_to_pos(move_str[:2])
                to_pos = self.coord_to_pos(move_str[2:])
            else:
                # 中文记谱法：如 "炮二平五"
                from_pos, to_pos = self.parse_chinese_notation(move_str)
                
            if from_pos is None or to_pos is None:
                return False
                
            # 检查是否为合法棋步
            if self.is_valid_move(from_pos, to_pos):
                # 执行移动
                piece = self.board[from_pos[0]][from_pos[1]]
                captured_piece = self.board[to_pos[0]][to_pos[1]]
                
                self.board[to_pos[0]][to_pos[1]] = piece
                self.board[from_pos[0]][from_pos[1]] = '.'
                
                # 记录棋步
                self.move_history.append({
                    'move': move_str,
                    'from_pos': from_pos,
                    'to_pos': to_pos,
                    'piece': piece,
                    'captured': captured_piece,
                    'player': self.current_player,
                    'timestamp': time.time(),
                    'notation': self.pos_to_chinese_notation(from_pos, to_pos, piece)
                })
                
                self.switch_player()
                return True
            else:
                return False
                
        except Exception as e:
            print(f"棋步解析错误: {e}")
            return False
    
    def coord_to_pos(self, coord: str) -> Optional[Tuple[int, int]]:
        """将坐标转换为位置 (行, 列)"""
        if len(coord) != 2:
            return None
        col = ord(coord[0].lower()) - ord('a')  # a-i -> 0-8
        row = int(coord[1])  # 0-9
        if 0 <= col <= 8 and 0 <= row <= 9:
            return (row, col)
        return None
    
    def pos_to_coord(self, pos: Tuple[int, int]) -> str:
        """将位置转换为坐标"""
        row, col = pos
        return chr(ord('a') + col) + str(row)
    
    def parse_chinese_notation(self, notation: str) -> Tuple[Optional[Tuple[int, int]], Optional[Tuple[int, int]]]:
        """解析中文记谱法"""
        # 这里简化处理，实际需要复杂的中文记谱解析
        # 暂时返回None，让系统使用坐标格式
        return None, None
    
    def pos_to_chinese_notation(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], piece: str) -> str:
        """将移动转换为中文记谱法"""
        piece_name = self.piece_names.get(piece, piece)
        from_col = ['一', '二', '三', '四', '五', '六', '七', '八', '九'][from_pos[1]]
        to_col = ['一', '二', '三', '四', '五', '六', '七', '八', '九'][to_pos[1]]
        
        if from_pos[1] == to_pos[1]:  # 直进直退
            if from_pos[0] > to_pos[0]:
                action = '进'
                steps = from_pos[0] - to_pos[0]
            else:
                action = '退'
                steps = to_pos[0] - from_pos[0]
            return f"{piece_name}{from_col}{action}{['一', '二', '三', '四', '五', '六', '七', '八', '九'][steps-1]}"
        else:  # 平移
            return f"{piece_name}{from_col}平{to_col}"
    
    def is_valid_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """检查移动是否合法"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # 检查边界
        if not (0 <= to_row <= 9 and 0 <= to_col <= 8):
            return False
            
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        
        # 检查是否有棋子
        if piece == '.':
            return False
            
        # 检查是否是当前玩家的棋子
        if self.current_player == "red" and piece.islower():
            return False
        if self.current_player == "black" and piece.isupper():
            return False
            
        # 检查是否吃自己的棋子
        if target != '.':
            if (piece.isupper() and target.isupper()) or (piece.islower() and target.islower()):
                return False
        
        # 根据棋子类型检查移动规则
        return self.check_piece_move_rules(piece.lower(), from_pos, to_pos)
    
    def check_piece_move_rules(self, piece_type: str, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """检查特定棋子的移动规则"""
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        if piece_type == 'k':  # 将/帅
            # 只能在九宫格内移动，每次一格
            if self.current_player == "red":
                if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                    return False
            else:
                if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                    return False
            return abs(from_row - to_row) + abs(from_col - to_col) == 1
            
        elif piece_type == 'a':  # 士/仕
            # 只能在九宫格内斜着移动
            if self.current_player == "red":
                if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                    return False
            else:
                if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                    return False
            return abs(from_row - to_row) == 1 and abs(from_col - to_col) == 1
            
        elif piece_type == 'b':  # 象/相
            # 斜着走两格，不能过河
            if self.current_player == "red" and to_row < 5:
                return False
            if self.current_player == "black" and to_row > 4:
                return False
            if abs(from_row - to_row) == 2 and abs(from_col - to_col) == 2:
                # 检查象眼是否被堵
                eye_row = (from_row + to_row) // 2
                eye_col = (from_col + to_col) // 2
                return self.board[eye_row][eye_col] == '.'
            return False
            
        elif piece_type == 'n':  # 马
            # 马走日字
            row_diff = abs(from_row - to_row)
            col_diff = abs(from_col - to_col)
            if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
                # 检查马腿是否被堵
                if row_diff == 2:
                    leg_row = from_row + (1 if to_row > from_row else -1)
                    leg_col = from_col
                else:
                    leg_row = from_row
                    leg_col = from_col + (1 if to_col > from_col else -1)
                return self.board[leg_row][leg_col] == '.'
            return False
            
        elif piece_type == 'r':  # 车
            # 直线移动，路径不能有棋子
            if from_row == to_row:  # 横向移动
                start_col = min(from_col, to_col) + 1
                end_col = max(from_col, to_col)
                for col in range(start_col, end_col):
                    if self.board[from_row][col] != '.':
                        return False
                return True
            elif from_col == to_col:  # 纵向移动
                start_row = min(from_row, to_row) + 1
                end_row = max(from_row, to_row)
                for row in range(start_row, end_row):
                    if self.board[row][from_col] != '.':
                        return False
                return True
            return False
            
        elif piece_type == 'c':  # 炮
            # 直线移动，吃子时需要跳过一个棋子
            target = self.board[to_row][to_col]
            if from_row == to_row:  # 横向移动
                start_col = min(from_col, to_col) + 1
                end_col = max(from_col, to_col)
                pieces_between = sum(1 for col in range(start_col, end_col) if self.board[from_row][col] != '.')
                if target == '.':
                    return pieces_between == 0
                else:
                    return pieces_between == 1
            elif from_col == to_col:  # 纵向移动
                start_row = min(from_row, to_row) + 1
                end_row = max(from_row, to_row)
                pieces_between = sum(1 for row in range(start_row, end_row) if self.board[row][from_col] != '.')
                if target == '.':
                    return pieces_between == 0
                else:
                    return pieces_between == 1
            return False
            
        elif piece_type == 'p':  # 兵/卒
            # 过河前只能向前，过河后可以左右移动
            if self.current_player == "red":
                if from_row > 4:  # 未过河
                    return to_row == from_row - 1 and to_col == from_col
                else:  # 已过河
                    return (to_row == from_row - 1 and to_col == from_col) or \
                           (to_row == from_row and abs(to_col - from_col) == 1)
            else:  # 黑方
                if from_row < 5:  # 未过河
                    return to_row == from_row + 1 and to_col == from_col
                else:  # 已过河
                    return (to_row == from_row + 1 and to_col == from_col) or \
                           (to_row == from_row and abs(to_col - from_col) == 1)
        
        return False
    
    def switch_player(self):
        """切换当前玩家"""
        self.current_player = "black" if self.current_player == "red" else "red"
    
    def get_board_state(self) -> str:
        """获取当前棋盘状态（FEN格式改为自定义格式）"""
        board_str = ""
        for row in self.board:
            board_str += "".join(row) + "/"
        return board_str.rstrip("/")
    
    def get_board_unicode(self) -> str:
        """获取棋盘的Unicode字符串表示"""
        result = "  a b c d e f g h i\n"
        for i, row in enumerate(self.board):
            result += f"{i} "
            for piece in row:
                if piece == '.':
                    result += "· "
                else:
                    result += f"{self.piece_names.get(piece, piece)} "
            result += f"{i}\n"
        result += "  a b c d e f g h i"
        return result
    
    def is_game_over(self) -> bool:
        """判断游戏是否结束"""
        # 检查是否有将/帅被吃
        red_king_exists = False
        black_king_exists = False
        
        for row in self.board:
            for piece in row:
                if piece == 'K':
                    red_king_exists = True
                elif piece == 'k':
                    black_king_exists = True
        
        return not (red_king_exists and black_king_exists)
    
    def get_game_result(self) -> str:
        """获取游戏结果"""
        if not self.is_game_over():
            return "游戏进行中"
        
        red_king_exists = any('K' in row for row in self.board)
        black_king_exists = any('k' in row for row in self.board)
        
        if red_king_exists and not black_king_exists:
            return "红方获胜"
        elif black_king_exists and not red_king_exists:
            return "黑方获胜"
        else:
            return "平局"
    
    def get_legal_moves(self) -> List[str]:
        """获取当前所有合法棋步"""
        legal_moves = []
        for from_row in range(10):
            for from_col in range(9):
                piece = self.board[from_row][from_col]
                if piece == '.':
                    continue
                    
                # 检查是否是当前玩家的棋子
                if self.current_player == "red" and piece.islower():
                    continue
                if self.current_player == "black" and piece.isupper():
                    continue
                
                # 尝试所有可能的目标位置
                for to_row in range(10):
                    for to_col in range(9):
                        if self.is_valid_move((from_row, from_col), (to_row, to_col)):
                            move = self.pos_to_coord((from_row, from_col)) + self.pos_to_coord((to_row, to_col))
                            legal_moves.append(move)
        
        return legal_moves
    
    def get_move_count(self) -> int:
        """获取总步数"""
        return len(self.move_history)
    
    def get_last_move(self) -> Optional[Dict]:
        """获取最后一步棋"""
        if self.move_history:
            return self.move_history[-1]
        return None
    
    def reset(self):
        """重置游戏"""
        self.board = self.init_board()
        self.move_history = []
        self.current_player = "red"
        self.start_time = time.time()
        self.move_times = []
    
    def get_position_evaluation(self) -> float:
        """简单的局面评估（基于材料价值）"""
        piece_values = {
            'k': 1000, 'a': 20, 'b': 20, 'n': 40, 'r': 90, 'c': 45, 'p': 10,
            'K': 1000, 'A': 20, 'B': 20, 'N': 40, 'R': 90, 'C': 45, 'P': 10
        }
        
        red_value = 0
        black_value = 0
        
        for row in self.board:
            for piece in row:
                if piece != '.':
                    value = piece_values.get(piece, 0)
                    if piece.isupper():
                        red_value += value
                    else:
                        black_value += value
        
        return (red_value - black_value) / 100.0  # 归一化
    
    def undo_last_move(self) -> bool:
        """撤销最后一步棋"""
        if not self.move_history:
            return False
            
        last_move = self.move_history.pop()
        from_pos = last_move['from_pos']
        to_pos = last_move['to_pos']
        piece = last_move['piece']
        captured = last_move['captured']
        
        # 恢复棋盘状态
        self.board[from_pos[0]][from_pos[1]] = piece
        self.board[to_pos[0]][to_pos[1]] = captured
        
        self.switch_player()
        return True