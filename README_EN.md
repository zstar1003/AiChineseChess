# AI Chinese Chess Battle System

An AI-powered Chinese Chess battle platform based on Large Language Models, supporting real-time matches between various mainstream AI models.

<div align="center">、
  <h4>
    <a href="README.md">🇨🇳 中文</a>
    <span> | </span>
    <a href="README_EN.md">🇬🇧 English</a>
  </h4>
</div>

## 🎯 Key Features

- **Multi-Model Support**: Integrated with DeepSeek, Gemini, Qwen and other LLMs
- **Real-time Battle**: Socket.IO-based real-time communication with streaming thought process display
- **Smart Moves**: AI models choose from legal moves to avoid invalid moves
- **Beautiful Interface**: Modern web UI with chess board visualization and thinking process display
- **Auto Retry**: Built-in retry mechanism ensures stable battles

## 🏗️ Project Structure

```
AiChineseChess/
├── app.py                 # Flask main application, Socket.IO server
├── config.py             # Configuration file
├── requirements.txt      # Python dependencies
├── api_key.txt          # API key configuration
├── models/              # Core model modules
│   ├── chess_game.py    # Chess game logic
│   ├── llm_player.py    # AI player implementation
│   └── battle.py        # Battle management
├── static/              # Static resources
│   ├── css/
│   │   └── style.css    # Stylesheet
│   └── js/
│       └── chess.js     # Frontend JavaScript logic
├── templates/           # HTML templates
│   └── index.html       # Main page
└── test_*.py           # Test files
```

## 🚀 Quick Start

### Requirements

- Python 3.8+
- Flask
- Flask-SocketIO
- requests
- google-genai (optional, for Gemini models)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure API Keys

Configure your API keys in the `api_key.txt` file:

```
your_api_key_here
```

### Start Application

```bash
python app.py
```

Visit `http://localhost:5003` to start using.

## 🎮 Usage Guide

### 1. Select AI Models

- **Red Player**: Supports DeepSeek-V3, Qwen and other models
- **Black Player**: Supports DeepSeek, Gemini and other models

### 2. Start Battle

1. Select AI models for red and black players on the interface
2. Click "Start Battle" button
3. Watch AI real-time thinking and chess playing process

### 3. Features

- **Real-time Thinking Display**: View AI's thinking process and strategic analysis
- **Move History**: Complete game records and move replay
- **Auto Scroll**: Game information automatically scrolls to latest content
- **Error Handling**: Smart retry mechanism handles API timeouts and invalid moves

## 🔧 Technical Architecture

### Backend Tech Stack

- **Flask**: Web framework
- **Flask-SocketIO**: Real-time communication
- **Python**: Core logic implementation

### Frontend Tech Stack

- **HTML5/CSS3**: Interface layout and styling
- **JavaScript**: Interactive logic
- **Socket.IO Client**: Real-time communication

### AI Model Integration

- **SiliconFlow API**: Unified model calling interface
- **Streaming Output**: Supports real-time thinking process display
- **Multi-model Adaptation**: Compatible with different API formats

## 🎯 Core Functions

### AI Player System (`models/llm_player.py`)

- Unified interface supporting multiple AI models
- Streaming thinking process output
- Smart prompt construction including legal moves list
- Automatic AI response parsing and move extraction

### Chess Game Engine (`models/chess_game.py`)

- Complete Chinese chess rules implementation
- Legal move generation and validation
- Game state management
- Chess board visualization

### Battle Management System (`models/battle.py`)

- Battle flow control
- Move recording and history management
- Game result statistics

### Real-time Communication (`app.py`)

- Socket.IO event handling
- Background task management
- Error handling and retry mechanism

## 🔍 API Reference

### REST API

- `POST /api/start_battle` - Start battle
- `POST /api/stop_battle` - Stop battle
- `GET /api/get_battle_status` - Get battle status

### Socket.IO Events

- `thinking` - AI thinking status
- `thinking_stream` - Streaming thinking content
- `move_made` - Move completed
- `game_over` - Game over
- `game_error` - Game error

## 🛠️ Development Guide

### Adding New AI Models

1. Add new API calling method in `models/llm_player.py`
2. Add model options in `templates/index.html`
3. Update model configuration in `static/js/chess.js`

### Customizing Chess Board Style

Modify relevant style classes in `static/css/style.css`:

- `.chess-board` - Chess board container
- `.chess-piece` - Chess piece style
- `.thinking-content` - Thinking box style

### Debugging and Testing

- Use `test_deepseek.py` to test API connections
- Check browser console for detailed logs
- Check Flask console output for backend status

## 📝 Changelog

### v1.0.0 (Current Version)

- ✅ Multi-AI model support
- ✅ Real-time streaming thinking display
- ✅ Smart legal move prompts
- ✅ Auto retry mechanism
- ✅ Beautiful web interface
- ✅ Complete chess rules implementation

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve the project!