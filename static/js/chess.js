// 全局变量
let socket;
let gameState = {
    isPlaying: false,
    currentPlayer: 'red',
    moveCount: 0,
    startTime: null,
    boardState: null
};

// 更新当前执棋方显示
function updateCurrentPlayer(player) {
    const currentPlayerText = document.getElementById('current-player-text');
    if (currentPlayerText) {
        if (player === 'red') {
            currentPlayerText.textContent = '当前轮到红方执棋';
            currentPlayerText.className = 'red-turn';
        } else {
            currentPlayerText.textContent = '当前轮到黑方执棋';
            currentPlayerText.className = 'black-turn';
        }
    }
}

// 添加思考过程到指定的思考框
function addThinkingProcess(player, message) {
    const isRed = player === 'red' || player.includes('红方') || player.includes('OpenAI') || player.includes('GPT');
    const thinkingBoxId = isRed ? 'red-thinking-process' : 'black-thinking-process';
    const thinkingBox = document.getElementById(thinkingBoxId);
    
    if (thinkingBox) {
        // 创建思考项
        const thinkingItem = document.createElement('div');
        thinkingItem.className = `thinking-item ${isRed ? 'red-thinking' : 'black-thinking'}`;
        
        // 添加时间戳
        const timestamp = document.createElement('div');
        timestamp.className = 'thinking-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        // 添加思考内容
        const thinkingText = document.createElement('div');
        thinkingText.className = 'thinking-text';
        thinkingText.textContent = message;
        
        thinkingItem.appendChild(timestamp);
        thinkingItem.appendChild(thinkingText);
        
        // 如果是第一条消息，清空默认文本
        if (thinkingBox.innerHTML.includes('等待') || thinkingBox.innerHTML.includes('开始思考')) {
            thinkingBox.innerHTML = '';
        }
        
        thinkingBox.appendChild(thinkingItem);
        
        // 自动滚动到底部
        thinkingBox.scrollTop = thinkingBox.scrollHeight;
    }
}

// 清空思考过程
function clearThinkingProcess(player) {
    const isRed = player === 'red' || player.includes('红方') || player.includes('OpenAI') || player.includes('GPT');
    const thinkingBoxId = isRed ? 'red-thinking-process' : 'black-thinking-process';
    const thinkingBox = document.getElementById(thinkingBoxId);
    
    if (thinkingBox) {
        thinkingBox.innerHTML = `<p>等待${isRed ? '红方' : '黑方'}开始思考...</p>`;
    }
}

// 流式输出思考过程（模拟打字机效果）
function streamThinkingProcess(player, message, speed = 50) {
    const isRed = player === 'red' || player.includes('红方') || player.includes('OpenAI') || player.includes('GPT');
    const thinkingBoxId = isRed ? 'red-thinking-process' : 'black-thinking-process';
    const thinkingBox = document.getElementById(thinkingBoxId);
    
    if (thinkingBox) {
        // 创建思考项
        const thinkingItem = document.createElement('div');
        thinkingItem.className = `thinking-item ${isRed ? 'red-thinking' : 'black-thinking'}`;
        
        // 添加时间戳
        const timestamp = document.createElement('div');
        timestamp.className = 'thinking-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        // 添加思考内容容器
        const thinkingText = document.createElement('div');
        thinkingText.className = 'thinking-text';
        
        thinkingItem.appendChild(timestamp);
        thinkingItem.appendChild(thinkingText);
        
        // 如果是第一条消息，清空默认文本
        if (thinkingBox.innerHTML.includes('等待') || thinkingBox.innerHTML.includes('开始思考')) {
            thinkingBox.innerHTML = '';
        }
        
        thinkingBox.appendChild(thinkingItem);
        
        // 流式输出文字
        let index = 0;
        const typeWriter = () => {
            if (index < message.length) {
                thinkingText.textContent += message.charAt(index);
                index++;
                thinkingBox.scrollTop = thinkingBox.scrollHeight;
                setTimeout(typeWriter, speed);
            }
        };
        
        typeWriter();
    }
}

// 实时流式输出思考过程（用于Socket.IO流式数据）
let currentStreamingElements = {};

function streamThinkingProcessRealtime(player, content) {
    const thinkingBoxId = `${player}-thinking-process`;
    const thinkingBox = document.getElementById(thinkingBoxId);
    
    console.log(`streamThinkingProcessRealtime调用: player=${player}, thinkingBoxId=${thinkingBoxId}`);
    console.log('thinkingBox元素:', thinkingBox);
    
    if (!thinkingBox) {
        console.error(`找不到思考区元素: ${thinkingBoxId}`);
        return;
    }
    
    // 如果是第一次为该玩家创建流式元素
    if (!currentStreamingElements[player]) {
        console.log(`为${player}创建新的流式元素`);
        
        // 如果是第一条消息，清空默认文本
        if (thinkingBox.innerHTML.includes('等待') || thinkingBox.innerHTML.includes('开始思考')) {
            thinkingBox.innerHTML = '';
            console.log(`清空${player}的默认文本`);
        }
        
        // 创建思考项
        const thinkingItem = document.createElement('div');
        thinkingItem.className = `thinking-item ${player === 'red' ? 'red-thinking' : 'black-thinking'}`;
        
        // 添加时间戳
        const timestamp = document.createElement('div');
        timestamp.className = 'thinking-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString();
        
        // 添加思考内容容器
        const thinkingText = document.createElement('div');
        thinkingText.className = 'thinking-text';
        thinkingText.id = `${player}-current-stream`;
        
        thinkingItem.appendChild(timestamp);
        thinkingItem.appendChild(thinkingText);
        thinkingBox.appendChild(thinkingItem);
        
        // 保存当前流式元素的引用
        currentStreamingElements[player] = thinkingText;
        console.log(`${player}的流式元素已创建并保存`);
    }
    
    // 追加内容到当前流式元素
    const streamElement = currentStreamingElements[player];
    if (streamElement) {
        streamElement.textContent += content;
        thinkingBox.scrollTop = thinkingBox.scrollHeight;
        console.log(`成功向${player}的思考区添加内容: "${content.substring(0, 20)}..."`);
    } else {
        console.error(`${player}的流式元素不存在`);
    }
}

// 清理流式输出状态
function clearStreamingState(player) {
    if (currentStreamingElements[player]) {
        delete currentStreamingElements[player];
    }
}

// 中国象棋棋盘渲染器
class ChessBoardRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // 增大的中国象棋棋盘尺寸比例 (9:10)
        this.boardWidth = 520;   // 9列
        this.boardHeight = 580;  // 10行
        this.margin = 40;
        
        this.canvas.width = this.boardWidth + this.margin * 2;
        this.canvas.height = this.boardHeight + this.margin * 2;
        
        this.cellWidth = this.boardWidth / 8;   // 8个间隔，9条线
        this.cellHeight = this.boardHeight / 9; // 9个间隔，10条线
        
        this.pieces = {};
        this.lastMove = null;
        
        this.initializePieces();
        this.drawBoard();
        this.showInitialPosition();
    }
    
    initializePieces() {
        // 中国象棋棋子字符
        this.pieces = {
            'K': '帅', 'A': '仕', 'B': '相', 'N': '馬', 'R': '车', 'C': '炮', 'P': '兵',
            'k': '将', 'a': '士', 'b': '象', 'n': '馬', 'r': '車', 'c': '炮', 'p': '卒'
        };
    }
    
    drawBoard() {
        // 清空画布
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制传统木质背景
        this.ctx.fillStyle = '#F5DEB3';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 绘制棋盘边框
        this.ctx.strokeStyle = '#8B4513';
        this.ctx.lineWidth = 3;
        this.ctx.strokeRect(this.margin - 2, this.margin - 2, this.boardWidth + 4, this.boardHeight + 4);
        
        // 设置线条样式
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 1.5;
        
        // 绘制横线（10条）
        for (let i = 0; i <= 9; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(this.margin, this.margin + i * this.cellHeight);
            this.ctx.lineTo(this.margin + this.boardWidth, this.margin + i * this.cellHeight);
            this.ctx.stroke();
        }
        
        // 绘制竖线（9条）- 楚河汉界中间不连接
        for (let i = 0; i <= 8; i++) {
            // 上半部分竖线（黑方区域）
            this.ctx.beginPath();
            this.ctx.moveTo(this.margin + i * this.cellWidth, this.margin);
            this.ctx.lineTo(this.margin + i * this.cellWidth, this.margin + 4 * this.cellHeight);
            this.ctx.stroke();
            
            // 下半部分竖线（红方区域）
            this.ctx.beginPath();
            this.ctx.moveTo(this.margin + i * this.cellWidth, this.margin + 5 * this.cellHeight);
            this.ctx.lineTo(this.margin + i * this.cellWidth, this.margin + this.boardHeight);
            this.ctx.stroke();
        }
        
        // 绘制九宫格斜线
        this.drawPalaceDiagonals();
        
        // 绘制楚河汉界
        this.drawRiverBoundary();
        
        // 绘制兵卒位置标记
        this.drawPositionMarkers();
    }
    
    drawPalaceDiagonals() {
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 1.5;
        
        // 黑方九宫格斜线（顶部）
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin + 3 * this.cellWidth, this.margin);
        this.ctx.lineTo(this.margin + 5 * this.cellWidth, this.margin + 2 * this.cellHeight);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin + 5 * this.cellWidth, this.margin);
        this.ctx.lineTo(this.margin + 3 * this.cellWidth, this.margin + 2 * this.cellHeight);
        this.ctx.stroke();
        
        // 红方九宫格斜线（底部）
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin + 3 * this.cellWidth, this.margin + 7 * this.cellHeight);
        this.ctx.lineTo(this.margin + 5 * this.cellWidth, this.margin + 9 * this.cellHeight);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo(this.margin + 5 * this.cellWidth, this.margin + 7 * this.cellHeight);
        this.ctx.lineTo(this.margin + 3 * this.cellWidth, this.margin + 9 * this.cellHeight);
        this.ctx.stroke();
    }
    
    drawRiverBoundary() {
        // 绘制楚河汉界文字
        this.ctx.fillStyle = '#8B4513';
        this.ctx.font = 'bold 18px SimHei, Microsoft YaHei, Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        const riverY = this.margin + 4.5 * this.cellHeight;
        
        this.ctx.fillText('楚河', this.margin + 2 * this.cellWidth, riverY);
        this.ctx.fillText('汉界', this.margin + 6 * this.cellWidth, riverY);
    }
    
    drawPositionMarkers() {
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 1;
        
        // 兵卒位置标记
        const positions = [
            // 黑方兵卒位置 (第3行)
            [0, 3], [2, 3], [4, 3], [6, 3], [8, 3],
            // 红方兵卒位置 (第6行)
            [0, 6], [2, 6], [4, 6], [6, 6], [8, 6],
            // 炮的位置 (第2行和第7行)
            [1, 2], [7, 2], [1, 7], [7, 7]
        ];
        
        positions.forEach(([col, row]) => {
            const x = this.margin + col * this.cellWidth;
            const y = this.margin + row * this.cellHeight;
            const size = 4;
            
            // 绘制十字标记
            this.ctx.beginPath();
            this.ctx.moveTo(x - size, y);
            this.ctx.lineTo(x + size, y);
            this.ctx.moveTo(x, y - size);
            this.ctx.lineTo(x, y + size);
            this.ctx.stroke();
        });
    }
    
    drawCoordinates() {
        this.ctx.fillStyle = '#8B4513';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // 列标识 (a-i) - 底部
        for (let i = 0; i < 9; i++) {
            const letter = String.fromCharCode(97 + i);
            this.ctx.fillText(letter, this.margin + i * this.cellWidth, this.canvas.height - 10);
        }
        
        // 行标识 (0-9) - 左侧
        for (let i = 0; i <= 9; i++) {
            this.ctx.fillText(i.toString(), 15, this.margin + i * this.cellHeight);
        }
    }
    
    showInitialPosition() {
        // 显示初始棋子位置
        const initialBoard = "rnbakabnr/........./.c.....c./p.p.p.p.p/........./........./P.P.P.P.P/.C.....C./........./RNBAKABNR";
        this.updateBoard(initialBoard);
    }
    
    updateBoard(boardState) {
        console.log('updateBoard被调用，棋盘状态:', boardState);
        
        if (!boardState) {
            console.error('棋盘状态为空');
            return;
        }
        
        // 清空棋盘并重绘
        console.log('开始重绘棋盘...');
        this.drawBoard();
        console.log('棋盘重绘完成');
        
        // 解析棋盘状态
        const rows = boardState.split('/');
        console.log('解析后的行数据:', rows);
        
        for (let row = 0; row < 10; row++) {
            if (rows[row]) {
                console.log(`处理第${row}行: ${rows[row]}`);
                for (let col = 0; col < 9; col++) {
                    const piece = rows[row][col];
                    if (piece && piece !== '.') {
                        console.log(`在位置(${col}, ${row})绘制棋子: ${piece}`);
                        this.drawPiece(col, row, piece);
                    }
                }
            }
        }
        
        // 高亮最后一步
        if (this.lastMove) {
            console.log('高亮最后一步:', this.lastMove);
            this.highlightMove(this.lastMove);
        }
        
        console.log('棋盘更新完成');
    }
    
    drawPiece(col, row, piece) {
        const x = this.margin + col * this.cellWidth;
        const y = this.margin + row * this.cellHeight;
        const radius = Math.min(this.cellWidth, this.cellHeight) * 0.4;
        
        // 绘制棋子阴影
        this.ctx.beginPath();
        this.ctx.arc(x + 2, y + 2, radius, 0, 2 * Math.PI);
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        this.ctx.fill();
        
        // 绘制棋子背景
        this.ctx.beginPath();
        this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
        
        if (piece === piece.toUpperCase()) {
            // 红方棋子 - 浅色背景
            this.ctx.fillStyle = '#FFF8DC';
        } else {
            // 黑方棋子 - 深色背景
            this.ctx.fillStyle = '#2F2F2F';
        }
        this.ctx.fill();
        
        // 绘制棋子边框
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // 绘制棋子文字
        const pieceText = this.pieces[piece] || piece;
        this.ctx.font = `bold ${Math.min(this.cellWidth, this.cellHeight) * 0.5}px SimHei, Microsoft YaHei, Arial`;
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        
        // 设置文字颜色
        if (piece === piece.toUpperCase()) {
            this.ctx.fillStyle = '#DC143C';  // 红方文字
        } else {
            this.ctx.fillStyle = '#FFFFFF';  // 黑方文字
        }
        
        this.ctx.fillText(pieceText, x, y);
    }
    
    highlightMove(move) {
        if (!move || !move.from || !move.to) return;
        
        const fromCol = move.from.charCodeAt(0) - 97;
        const fromRow = parseInt(move.from[1]);
        const toCol = move.to.charCodeAt(0) - 97;
        const toRow = parseInt(move.to[1]);
        
        // 高亮起始位置
        this.highlightSquare(fromCol, fromRow, '#FFD700', 0.4);
        // 高亮目标位置
        this.highlightSquare(toCol, toRow, '#FF6B6B', 0.4);
    }
    
    highlightSquare(col, row, color, alpha) {
        const x = this.margin + (col + 0.5) * this.cellSize;
        const y = this.margin + (row + 0.5) * this.cellSize;
        const size = this.cellSize * 0.7;
        
        this.ctx.fillStyle = color;
        this.ctx.globalAlpha = alpha;
        this.ctx.fillRect(x - size/2, y - size/2, size, size);
        this.ctx.globalAlpha = 1.0;
    }
    
    setLastMove(moveStr) {
        if (moveStr && moveStr.length >= 4) {
            this.lastMove = {
                from: moveStr.substring(0, 2),
                to: moveStr.substring(2, 4)
            };
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // 初始化Socket.IO连接
    socket = io();
    
    // 初始化棋盘渲染器
    window.boardRenderer = new ChessBoardRenderer('chess-board');
    
    // 绑定事件监听器
    bindEventListeners();
    
    // 初始化Socket事件
    initializeSocketEvents();
    
    console.log('中国象棋应用初始化完成');
}

function bindEventListeners() {
    // 开始对战按钮
    document.getElementById('start-battle').addEventListener('click', startBattle);
    
    // 停止对战按钮
    document.getElementById('stop-battle').addEventListener('click', stopBattle);
    
    // 重置游戏按钮
    document.getElementById('reset-battle').addEventListener('click', resetBattle);
    
    // 模型选择变化
    document.getElementById('red-model').addEventListener('change', updateModelSettings);
    document.getElementById('black-model').addEventListener('change', updateModelSettings);
}

function initializeSocketEvents() {
    console.log('开始初始化Socket事件监听器...');
    
    // 连接状态
    socket.on('connect', function() {
        updateConnectionStatus('已连接');
        console.log('Socket连接成功');
        console.log('Socket ID:', socket.id);
        
        // 连接成功后立即测试事件接收
        console.log('测试Socket.IO事件接收...');
        
        // 连接成功后重新绑定事件监听器
        bindThinkingStreamEvent();
    });
    
    socket.on('disconnect', function() {
        updateConnectionStatus('连接断开');
        console.log('Socket连接断开');
    });
    
    // 游戏事件
    socket.on('thinking', function(data) {
        console.log('收到thinking事件:', data);
        showThinkingStatus(data.player, data.message);
    });
    
    // 初始绑定thinking_stream事件
    bindThinkingStreamEvent();
    
    socket.on('move_made', function(data) {
        console.log('收到move_made事件:', data);
        handleMoveMade(data);
    });
    
    socket.on('game_over', function(data) {
        console.log('收到game_over事件:', data);
        handleGameOver(data);
    });
    
    socket.on('game_error', function(data) {
        console.log('收到game_error事件:', data);
        handleGameError(data);
    });
    
    // 添加通用事件监听器来捕获所有事件
    socket.onAny(function(eventName, ...args) {
        console.log(`收到Socket.IO事件: ${eventName}`, args);
    });
    
    console.log('Socket事件监听器初始化完成');
}

// 单独的函数来绑定thinking_stream事件
function bindThinkingStreamEvent() {
    console.log('绑定thinking_stream事件监听器...');
    
    // 移除之前的监听器（如果存在）
    socket.off('thinking_stream');
    
    // 新增：处理流式思考过程
    socket.on('thinking_stream', function(data) {
        console.log('=== 收到thinking_stream事件 ===');
        console.log('原始数据:', data);
        console.log('数据类型:', typeof data);
        console.log('JSON字符串:', JSON.stringify(data));
        
        // 确保数据格式正确
        if (!data || typeof data !== 'object') {
            console.error('thinking_stream数据格式错误:', data);
            return;
        }
        
        if (data.is_complete) {
            // 思考完成，添加分隔线和清理状态
            console.log(`${data.player}思考完成`);
            const playerBox = document.getElementById(`${data.player}-thinking-process`);
            if (playerBox) {
                playerBox.innerHTML += '<hr style="margin: 10px 0; border: 1px solid rgba(255,255,255,0.2);">';
                playerBox.scrollTop = playerBox.scrollHeight;
            }
            // 清理流式状态
            clearStreamingState(data.player);
            return;
        }
        
        // 流式添加思考内容
        if (data.content && data.content.length > 0) {
            console.log(`=== 开始处理思考内容 ===`);
            console.log(`玩家: ${data.player}`);
            console.log(`内容长度: ${data.content.length}`);
            console.log(`内容预览: "${data.content.substring(0, 50)}..."`);
            console.log(`目标思考区ID: ${data.player}-thinking-process`);
            
            // 检查思考区是否存在
            const thinkingBox = document.getElementById(`${data.player}-thinking-process`);
            console.log('思考区元素查找结果:', thinkingBox);
            
            if (!thinkingBox) {
                console.error(`找不到思考区元素: ${data.player}-thinking-process`);
                // 列出所有可能的思考区元素
                const allThinkingElements = document.querySelectorAll('[id*="thinking"]');
                console.log('页面中所有包含thinking的元素:', allThinkingElements);
                for (let i = 0; i < allThinkingElements.length; i++) {
                    console.log(`  - ${allThinkingElements[i].id}: ${allThinkingElements[i].tagName}`);
                }
                return;
            }
            
            console.log('找到思考区元素，调用streamThinkingProcessRealtime');
            streamThinkingProcessRealtime(data.player, data.content);
            console.log('=== 思考内容处理完成 ===');
        } else {
            console.warn('收到空内容的thinking_stream事件，内容:', data.content);
        }
    });
    
    console.log('thinking_stream事件监听器绑定完成');
}

function startBattle() {
    const redConfig = getPlayerConfig('red');
    const blackConfig = getPlayerConfig('black');
    
    if (!validateConfig(redConfig) || !validateConfig(blackConfig)) {
        alert('请填写完整的模型配置信息');
        return;
    }
    
    showLoading(true);
    
    fetch('/api/start_battle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            red_player: redConfig,
            black_player: blackConfig
        })
    })
    .then(response => response.json())
    .then(data => {
        showLoading(false);
        if (data.status === 'success') {
            gameState.isPlaying = true;
            gameState.startTime = new Date();
            console.log('中国象棋对战已开始');
            updateControlButtons(true);
            clearGameInfo();
        } else {
            alert('启动对战失败: ' + data.message);
        }
    })
    .catch(error => {
        showLoading(false);
        console.error('启动对战错误:', error);
        alert('启动对战时发生错误');
    });
}

function stopBattle() {
    fetch('/api/stop_battle', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            gameState.isPlaying = false;
            updateGameStatus('对战已停止');
            updateControlButtons(false);
            hideThinkingStatus();
        }
    })
    .catch(error => {
        console.error('停止对战错误:', error);
    });
}

function resetBattle() {
    if (confirm('确定要重置游戏吗？这将清除所有对战记录。')) {
        gameState = {
            isPlaying: false,
            currentPlayer: 'red',
            moveCount: 0,
            startTime: null,
            boardState: null
        };
        
        // 重置界面
        updateGameStatus('等待开始');
        updateControlButtons(false);
        clearGameInfo();
        boardRenderer.drawBoard();
        boardRenderer.showInitialPosition();  // 重新显示初始位置
        
        // 重置统计信息
        document.getElementById('current-round').textContent = '0';
        document.getElementById('total-moves').textContent = '0';
        document.getElementById('battle-duration').textContent = '00:00';
        
        console.log('中国象棋游戏已重置');
    }
}

function getPlayerConfig(player) {
    const prefix = player === 'red' ? 'red' : 'black';
    
    const config = {
        model_name: document.getElementById(`${prefix}-model`).value,
        api_key: document.getElementById(`${prefix}-api-key`).value,
        display_name: document.getElementById(`${prefix}-display-name`).value
    };
    
    // 添加base_url（红方和黑方都需要）
    const baseUrlInput = document.getElementById(`${prefix}-base-url`);
    if (baseUrlInput && baseUrlInput.value.trim()) {
        config.base_url = baseUrlInput.value.trim();
    }
    
    return config;
}

function validateConfig(config) {
    return config.model_name && config.api_key && config.display_name;
}

function updateModelSettings() {
    // 根据选择的模型更新默认设置
    const redModel = document.getElementById('red-model').value;
    const blackModel = document.getElementById('black-model').value;
    
    // 更新红方显示名称（使用硅基流动API）
    if (redModel.includes('deepseek-r1')) {
        if (redModel.includes('distill-llama')) {
            document.getElementById('red-display-name').value = 'DeepSeek-R1-Distill-Llama-70B';
        } else if (redModel.includes('distill-qwen')) {
            document.getElementById('red-display-name').value = 'DeepSeek-R1-Distill-Qwen-32B';
        } else {
            document.getElementById('red-display-name').value = 'DeepSeek-R1';
        }
        document.getElementById('red-base-url').value = 'https://api.siliconflow.cn/v1';
    }
    
    // 更新黑方显示名称（只有Gemini-2.5-Flash）
    if (blackModel.includes('gemini')) {
        document.getElementById('black-display-name').value = 'Gemini-2.5-Flash';
        document.getElementById('black-base-url').value = 'https://generativelanguage.googleapis.com/v1beta';
    }
}

function showThinkingStatus(player, message) {
    const isRed = player.includes('OpenAI') || player.includes('o3') || player.includes('GPT');
    const thinkingElement = document.getElementById(isRed ? 'red-thinking' : 'black-thinking');
    
    if (thinkingElement) {
        thinkingElement.textContent = message;
        thinkingElement.style.display = 'block';
    }
    
    // 更新思考过程面板
    const thinkingProcess = document.getElementById('thinking-process');
    thinkingProcess.innerHTML = `
        <div class="thinking-item">
            <strong>${player}</strong>: ${message}
        </div>
    `;
}

function hideThinkingStatus() {
    const redThinking = document.getElementById('red-thinking');
    const blackThinking = document.getElementById('black-thinking');
    if (redThinking) {
        redThinking.style.display = 'none';
    }
    if (blackThinking) {
        blackThinking.style.display = 'none';
    }
}

function handleMoveMade(data) {
    console.log('收到中国象棋棋步:', data);
    console.log('棋盘状态数据:', data.board_state);
    console.log('当前boardRenderer:', boardRenderer);
    
    // 隐藏思考状态
    hideThinkingStatus();
    
    // 更新棋盘
    if (data.board_state) {
        console.log('开始更新棋盘...');
        boardRenderer.updateBoard(data.board_state);
        console.log('棋盘更新完成');
        
        boardRenderer.setLastMove(data.move);
        console.log('最后一步设置完成:', data.move);
        
        gameState.boardState = data.board_state;
        console.log('游戏状态已更新');
    } else {
        console.error('没有收到棋盘状态数据');
    }
    
    // 更新统计信息
    gameState.moveCount = data.move_count || 0;
    document.getElementById('total-moves').textContent = gameState.moveCount;
    document.getElementById('current-round').textContent = Math.ceil(gameState.moveCount / 2);
    
    // 更新最后一步信息
    const lastMoveText = `${data.player} 走了: ${data.move}`;
    document.getElementById('last-move-text').textContent = lastMoveText;
    
    // 更新思考过程
    if (data.thinking) {
        const thinkingProcess = document.getElementById('thinking-process');
        thinkingProcess.innerHTML = `
            <div class="thinking-item">
                <strong>${data.player}</strong><br>
                <div class="thinking-content">${data.thinking}</div>
            </div>
        `;
    }
    
    // 更新棋谱历史
    updateMoveHistory(data.history || []);
    
    // 更新对战日志
    addBattleLogEntry(`${data.player} 走了 ${data.move}`, 'move');
    
    // 更新对战时长
    updateBattleDuration();
}

function handleGameOver(data) {
    console.log('中国象棋游戏结束:', data);
    
    gameState.isPlaying = false;
    hideThinkingStatus();
    console.log('对战结束');
    updateControlButtons(false);
    
    // 显示游戏结果
    const gameResult = document.getElementById('game-result');
    gameResult.innerHTML = `
        <div class="result-info">
            <h4>中国象棋对战结果</h4>
            <p><strong>${data.result}</strong></p>
            <p>总步数: ${data.total_moves}</p>
            <p>对战时长: ${formatDuration(Date.now() - gameState.startTime)}</p>
        </div>
    `;
    
    // 添加到对战日志
    addBattleLogEntry(`游戏结束: ${data.result}`, 'result');
    
    // 高亮获胜方
    highlightWinner(data.result);
}

function handleGameError(data) {
    console.error('中国象棋游戏错误:', data);
    
    gameState.isPlaying = false;
    hideThinkingStatus();
    updateGameStatus('对战出错');
    updateControlButtons(false);
    
    // 显示错误信息
    addBattleLogEntry(`错误: ${data.message}`, 'error');
    alert(`对战出现错误: ${data.message}`);
}

function updateConnectionStatus(status) {
    const element = document.getElementById('connection-status');
    if (element) {
        element.textContent = `连接状态: ${status}`;
    }
}

function updateGameStatus(status) {
    const element = document.getElementById('game-status');
    if (element) {
        element.textContent = `游戏状态: ${status}`;
    }
}

function updateControlButtons(isPlaying) {
    document.getElementById('start-battle').disabled = isPlaying;
    document.getElementById('stop-battle').disabled = !isPlaying;
}

function clearGameInfo() {
    // 清空思考过程
    const thinkingProcess = document.getElementById('thinking-process');
    if (thinkingProcess) {
        thinkingProcess.innerHTML = '<p>等待模型开始思考...</p>';
    }
    
    // 清空棋谱历史
    const moveHistory = document.getElementById('move-history');
    if (moveHistory) {
        moveHistory.innerHTML = '<p>暂无棋谱记录</p>';
    }
    
    // 清空对战日志
    const battleLog = document.getElementById('battle-log');
    if (battleLog) {
        battleLog.innerHTML = '<p>等待对战开始...</p>';
    }
    
    // 清空游戏结果
    const gameResult = document.getElementById('game-result');
    if (gameResult) {
        gameResult.innerHTML = '<p>对战尚未结束</p>';
    }
    
    // 重置最后一步信息
    const lastMoveText = document.getElementById('last-move-text');
    if (lastMoveText) {
        lastMoveText.textContent = '等待开始中国象棋对战...';
    }
}

function updateMoveHistory(history) {
    const moveHistoryElement = document.getElementById('move-history');
    
    if (!history || history.length === 0) {
        moveHistoryElement.innerHTML = '<p>暂无棋谱记录</p>';
        return;
    }
    
    let historyHtml = '';
    history.forEach((entry, index) => {
        const moveNumber = Math.ceil((index + 1) / 2);
        const isRed = (index % 2) === 0;
        
        historyHtml += `
            <div class="move-item">
                <span class="move-number">${moveNumber}${isRed ? '.' : '...'}</span>
                <span class="move-notation">${entry.move}</span>
                <span class="move-player">(${entry.player})</span>
            </div>
        `;
    });
    
    moveHistoryElement.innerHTML = historyHtml;
    moveHistoryElement.scrollTop = moveHistoryElement.scrollHeight;
}

function addBattleLogEntry(message, type = 'info') {
    const battleLog = document.getElementById('battle-log');
    const timestamp = new Date().toLocaleTimeString();
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.innerHTML = `
        <div class="log-time">${timestamp}</div>
        <div class="log-message">${message}</div>
    `;
    
    // 如果是第一条记录，清空默认文本
    if (battleLog.innerHTML.includes('等待对战开始')) {
        battleLog.innerHTML = '';
    }
    
    battleLog.appendChild(logEntry);
    battleLog.scrollTop = battleLog.scrollHeight;
}

function highlightWinner(result) {
    // 根据结果高亮获胜方
    const redPlayerInfo = document.querySelector('.player-red');
    const blackPlayerInfo = document.querySelector('.player-black');
    
    // 移除之前的高亮
    redPlayerInfo.classList.remove('winner-highlight');
    blackPlayerInfo.classList.remove('winner-highlight');
    
    if (result.includes('红方')) {
        redPlayerInfo.classList.add('winner-highlight');
    } else if (result.includes('黑方')) {
        blackPlayerInfo.classList.add('winner-highlight');
    }
}

function updateBattleDuration() {
    if (!gameState.startTime) return;
    
    const duration = Date.now() - gameState.startTime;
    document.getElementById('battle-duration').textContent = formatDuration(duration);
}

function formatDuration(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function showLoading(show) {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// 定时更新对战时长
setInterval(() => {
    if (gameState.isPlaying && gameState.startTime) {
        updateBattleDuration();
    }
}, 1000);

// 页面卸载时断开Socket连接
window.addEventListener('beforeunload', function() {
    if (socket) {
        socket.disconnect();
    }
});
