# 大模型象棋对战系统

一个基于大语言模型的象棋对战系统，支持不同大模型（如OpenAI o3 vs DeepSeek）进行象棋对弈，提供实时的2D可视化棋盘和详细的对战分析。

## 功能特点

- 🤖 **多模型支持**: 支持OpenAI GPT系列、DeepSeek、Claude等大模型
- ♟️ **实时对战**: 两个大模型自动进行象棋对弈
- 🎨 **2D可视化**: 清晰的2D棋盘界面，实时显示棋局变化
- 📝 **文本描述**: 详细的棋局文字描述和模型思考过程
- 📊 **对战分析**: 完整的棋谱记录和对战统计
- 🔄 **实时更新**: WebSocket实时通信，无需刷新页面

## 技术架构

- **后端**: Python + Flask + Flask-SocketIO
- **前端**: HTML + CSS + JavaScript
- **象棋引擎**: python-chess库
- **API调用**: OpenAI API、DeepSeek API等
- **实时通信**: WebSocket

## 项目结构

```
chess-llm-battle/
├── app.py                  # 主应用文件
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── README.md             # 项目说明
├── models/               # 核心模块
│   ├── __init__.py
│   ├── chess_game.py     # 象棋游戏逻辑
│   ├── llm_player.py     # 大模型玩家
│   └── battle.py         # 对战管理
├── templates/            # HTML模板
│   └── index.html        # 主页面
└── static/              # 静态文件
    ├── css/
    │   └── style.css     # 样式文件
    └── js/
        └── chess.js      # 前端JavaScript
```

## 安装部署

### 1. 环境要求

- Python 3.8+
- pip包管理器

### 2. 克隆项目

```bash
git clone https://github.com/your-username/chess-llm-battle.git
cd chess-llm-battle
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
nano .env
```

在`.env`文件中配置你的API密钥：

```env
# OpenAI API配置
OPENAI_API_KEY=sk-your-actual-openai-api-key

# DeepSeek API配置
DEEPSEEK_API_KEY=sk-your-actual-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# Flask配置
SECRET_KEY=your-random-secret-key
```

### 5. 启动应用

```bash
python app.py
```

### 6. 访问系统

打开浏览器访问：http://localhost:5000

## 使用说明

### 1. 配置模型

1. 在左侧控制面板中选择红方和黑方的大模型
2. 填入相应的API密钥
3. 设置显示名称（可选）

### 2. 开始对战

1. 点击"开始对战"按钮
2. 系统将自动开始两个模型的对弈
3. 观察棋盘上的实时变化

### 3. 观察对战

- **棋盘区域**: 显示当前棋局状态
- **思考过程**: 显示模型的分析和策略
- **棋谱记录**: 完整的对战历史
- **对战日志**: 详细的操作记录

### 4. 对战控制

- **停止对战**: 中途停止当前对战
- **重置游戏**: 清空所有记录，重新开始

## 支持的模型

### OpenAI系列
- GPT-4
- GPT-4 Turbo  
- OpenAI o3-mini
- OpenAI o3

### DeepSeek系列
- DeepSeek Chat
- DeepSeek Coder

### Claude系列
- Claude 3 Sonnet
- Claude 3 Opus

## API配置说明

### OpenAI API
```python
# 需要配置
OPENAI_API_KEY = "sk-your-key"
```

### DeepSeek API
```python
# 需要配置
DEEPSEEK_API_KEY = "sk-your-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
```

### Claude API
```python
# 需要配置
CLAUDE_API_KEY = "your-key"
```

## 开发说明

### 核心模块

1. **ChessGame**: 象棋游戏核心逻辑
   - 棋盘状态管理
   - 合法性检查
   - 游戏结束判定

2. **LLMPlayer**: 大模型玩家
   - API调用封装
   - 提示词构建
   - 响应解析

3. **ChessBattle**: 对战管理
   - 对战流程控制
   - 日志记录
   - 结果统计

### 前端组件

1. **ChessBoardRenderer**: 棋盘渲染器
   - 2D Canvas绘制
   - 棋子显示
   - 移动高亮

2. **Socket事件处理**: 实时通信
   - 棋步更新
   - 思考状态
   - 游戏结果

## 故障排除

### 常见问题

1. **API调用失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 验证API配额是否充足

2. **棋步解析错误**
   - 模型返回格式不正确
   - 提示词需要优化
   - 增加错误处理逻辑

3. **界面显示异常**
   - 检查浏览器控制台错误
   - 确认静态文件加载正常
   - 验证WebSocket连接状态

### 调试模式

启用Flask调试模式：

```bash
export FLASK_ENV=development
python app.py
```

## 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目链接: https://github.com/your-username/chess-llm-battle
- 问题反馈: https://github.com/your-username/chess-llm-battle/issues

## 更新日志

### v1.0.0 (2024-08-07)
- 初始版本发布
- 支持OpenAI和DeepSeek模型对战
- 实现2D棋盘可视化
- 添加实时WebSocket通信
- 完整的对战记录和分析功能