from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import json
import time
from models.chess_game import ChessGame
from models.llm_player import LLMPlayer
from models.battle import ChessBattle
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局变量存储当前对战
current_battle = None

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/start_battle', methods=['POST'])
def start_battle():
    """开始对战"""
    global current_battle
    
    data = request.json
    red_config = data.get('red_player')
    black_config = data.get('black_player')
    
    try:
        # 创建玩家实例（传入socketio实例以支持流式输出）
        # 红方使用DeepSeek-V3模型，通过SiliconFlow API
        red_player = LLMPlayer(
            model_name="deepseek-ai/DeepSeek-V3",
            api_key=red_config['api_key'],
            base_url="https://api.siliconflow.cn/v1",  # 继续使用SiliconFlow API
            display_name=red_config.get('display_name', "DeepSeek-V3"),
            socketio=socketio
        )
        
        black_player = LLMPlayer(
            model_name=black_config['model_name'],
            api_key=black_config['api_key'],
            base_url=black_config.get('base_url'),
            display_name=black_config['display_name'],
            socketio=socketio
        )
        
        # 创建对战实例
        current_battle = ChessBattle(red_player, black_player)
        
        # 启动对战（在后台线程中）
        socketio.start_background_task(run_battle)
        
        return jsonify({"status": "success", "message": "对战已开始"})
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def run_battle():
    """运行对战（后台任务）"""
    global current_battle
    
    if not current_battle:
        print("错误: 没有当前对战实例")
        return
    
    print("开始运行对战...")
    
    while not current_battle.game.is_game_over():
        try:
            # 获取当前玩家
            current_player = (current_battle.red_player 
                            if current_battle.game.current_player == "red" 
                            else current_battle.black_player)
            
            print(f"当前轮到: {current_player.display_name}")
            
            # 发送思考状态
            socketio.emit('thinking', {
                'player': current_player.display_name,
                'message': f'{current_player.display_name} 正在思考...'
            })
            
            # 使用真实的模型接入获取棋步
            print(f"{current_player.display_name} 正在思考...")
            
            # 获取当前棋盘状态和合法棋步
            print(f"当前棋盘状态:\n{current_battle.game.get_board_unicode()}")
            legal_moves = current_battle.game.get_legal_moves()
            print(f"当前合法棋步数量: {len(legal_moves)}")
            
            # 调用真实的AI模型获取棋步
            board_state = current_battle.game.get_board_state()
            move_history = current_battle.game.move_history
            move_result = current_player.get_move(board_state, move_history)
            
            print(f"AI返回的棋步结果: {move_result}")
            
            if move_result and move_result['move'] and current_battle.game.make_move(move_result['move']):
                # 记录棋步
                current_battle.log_move(current_player.display_name, move_result)
                
                # 获取更新后的棋盘状态
                updated_board_state = current_battle.game.get_board_state()
                board_unicode = current_battle.game.get_board_unicode()
                
                print(f"棋步执行成功，更新后的棋盘状态: {updated_board_state}")
                print(f"棋盘Unicode显示:\n{board_unicode}")
                
                # 发送棋步更新事件
                move_data = {
                    'player': current_player.display_name,
                    'player_color': current_battle.game.current_player,  # 注意：这里是下一个玩家的颜色
                    'move': move_result['move'],
                    'thinking': move_result.get('thinking', ''),
                    'board_state': updated_board_state,
                    'board_unicode': board_unicode,
                    'move_count': len(current_battle.game.move_history),
                    'history': current_battle.battle_log[-10:],  # 最近10步
                    'current_player': current_battle.game.current_player,
                    'is_game_over': current_battle.game.is_game_over()
                }
                
                print(f"准备发送move_made事件: {move_data}")
                socketio.emit('move_made', move_data)
                print(f"move_made事件已发送")
                
                # 强制刷新Socket.IO
                socketio.sleep(0.1)
                
                print(f"{current_player.display_name} 走了: {move_result['move']}")
                
                # 短暂延迟，便于观察
                time.sleep(1)
                
            else:
                # 无效棋步，结束游戏
                print(f"无效棋步: {move_result}")
                socketio.emit('game_error', {
                    'message': f'{current_player.display_name} 产生了无效棋步'
                })
                break
                
        except Exception as e:
            print(f"对战过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
            socketio.emit('game_error', {'message': f'对战出错: {str(e)}'})
            break
    
    # 游戏结束，发送结果
    try:
        result = current_battle.get_battle_result()
        socketio.emit('game_over', {
            'result': result,
            'total_moves': len(current_battle.game.move_history),
            'battle_log': current_battle.battle_log
        })
        print(f"游戏结束: {result}")
    except Exception as e:
        print(f"发送游戏结束信息时出错: {e}")

@app.route('/api/stop_battle', methods=['POST'])
def stop_battle():
    """停止对战"""
    global current_battle
    current_battle = None
    return jsonify({"status": "success", "message": "对战已停止"})

@app.route('/api/get_battle_status', methods=['GET'])
def get_battle_status():
    """获取对战状态"""
    global current_battle
    
    if not current_battle:
        return jsonify({"status": "no_battle"})
    
    return jsonify({
        "status": "active",
        "board_state": current_battle.game.get_board_state(),
        "move_count": len(current_battle.game.move_history),
        "current_player": current_battle.game.current_player,
        "is_game_over": current_battle.game.is_game_over()
    })

if __name__ == '__main__':
    try:
        print("正在启动AI象棋对战系统...")
        print("访问地址: http://localhost:5003")
        socketio.run(app, debug=True, host='0.0.0.0', port=5003)
    except Exception as e:
        print(f"启动应用时发生错误: {e}")
        import traceback
        traceback.print_exc()
