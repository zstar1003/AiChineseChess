#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试应用启动脚本
"""

print("开始测试应用启动...")

try:
    print("1. 导入Flask...")
    from flask import Flask
    print("✓ Flask导入成功")
    
    print("2. 导入Flask-SocketIO...")
    from flask_socketio import SocketIO
    print("✓ Flask-SocketIO导入成功")
    
    print("3. 导入配置...")
    from config import Config
    print("✓ 配置导入成功")
    
    print("4. 导入模型...")
    from models.chess_game import ChessGame
    from models.llm_player import LLMPlayer
    from models.battle import ChessBattle
    print("✓ 所有模型导入成功")
    
    print("5. 创建Flask应用...")
    app = Flask(__name__)
    app.config.from_object(Config)
    socketio = SocketIO(app, cors_allowed_origins="*")
    print("✓ Flask应用创建成功")
    
    print("6. 测试基本功能...")
    game = ChessGame()
    print(f"✓ 象棋游戏创建成功，初始FEN: {game.get_board_state()}")
    
    print("\n🎉 所有测试通过！应用可以正常启动。")
    print("现在可以运行: python app.py")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()