class GomokuGame:
    """五子棋游戏逻辑类"""
    
    def __init__(self, board_size=15):
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 1  # 1: 黑棋, 2: 白棋
        self.game_over = False
        self.winner = 0
        self.move_history = []
        self.last_move = None
        # 新增：候选落子位置集合
        self.candidate_moves = set()
        self._init_candidate_moves()
        
    def _init_candidate_moves(self):
        """初始化候选落子位置集合，只包含中心点"""
        self.candidate_moves.clear()
        center = self.board_size // 2
        self.candidate_moves.add((center, center))
        
    def reset(self):
        """重置游戏"""
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.move_history = []
        self.last_move = None
        # 重置候选集合
        self._init_candidate_moves()
        
    def make_move(self, row, col):
        """在指定位置落子"""
        if self.game_over or not self.is_valid_move(row, col):
            return False
            
        self.board[row][col] = self.current_player
        self.last_move = (row, col, self.current_player)
        self.move_history.append(self.last_move)
        
        # 新增：更新候选落子位置集合
        self._update_candidate_moves(row, col)
        
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        elif self.is_board_full():
            self.game_over = True
            self.winner = 0  # 平局
            
        if not self.game_over:
            self.current_player = 3 - self.current_player
            
        return True
        
    def _update_candidate_moves(self, row, col):
        """
        更新候选落子位置集合
        1. 从集合中删除已落子的点
        2. 添加以(row, col)为中心的5 * 5区域内非"日"字形的合法位置
        """
        # 1. 删除已落子的点
        self.candidate_moves.discard((row, col))
        
        # 2. 定义"日"字形相对位置（马走日）
        horse_pattern = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        # 3. 添加5 * 5区域内的合法位置，排除"日"字形位置
        for r in range(max(0, row-2), min(self.board_size, row+3)):
            for c in range(max(0, col-2), min(self.board_size, col+3)):
                # 计算相对于中心点的偏移
                dr = r - row
                dc = c - col
                
                # 检查是否为"日"字形位置
                is_horse_position = (dr, dc) in horse_pattern
                
                # 只有空位且不是"日"字形位置才添加
                if self.board[r][c] == 0 and not is_horse_position:
                    self.candidate_moves.add((r, c))
        
    def is_valid_move(self, row, col):
        """检查落子位置是否有效"""
        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            return self.board[row][col] == 0
        return False
        
    def check_win(self, row, col):
        """检查是否获胜"""
        player = self.board[row][col]
        directions = [
            [(0, 1), (0, -1)],   # 水平
            [(1, 0), (-1, 0)],   # 垂直
            [(1, 1), (-1, -1)],  # 主对角线
            [(1, -1), (-1, 1)]   # 副对角线
        ]
        
        for dir_pair in directions:
            count = 1
            
            for dx, dy in dir_pair:
                r, c = row, col
                
                while True:
                    r += dx
                    c += dy
                    
                    if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == player:
                        count += 1
                    else:
                        break
                        
            if count >= 5:
                return True
                
        return False
        
    def is_board_full(self):
        """检查棋盘是否已满"""
        return len(self.move_history)==self.board_size**2
        
    def undo(self, steps=1):
        """悔棋一步或多步"""
        if not self.move_history or self.game_over:
            return False
            
        # 确保不超出历史记录范围
        if steps > len(self.move_history):
            return False
            
        for _ in range(steps):
            if not self.move_history:
                break
            row, col, player = self.move_history.pop()
            self.board[row][col] = 0
            self.current_player = player
            
        # 新增：悔棋后需要重新计算候选集合
        # 重新初始化候选集合，然后根据所有已下棋子重新构建
        self._init_candidate_moves()
        for move in self.move_history:
            r, c, _ = move
            self._update_candidate_moves(r, c)
        
        if self.move_history:
            self.last_move = self.move_history[-1]
        else:
            self.last_move = None
            
        return True
        
    def get_legal_moves(self):
        """获取所有合法落子位置（为AI预留）"""
        moves = []
        for r in range(self.board_size):
            for c in range(self.board_size):
                if self.board[r][c] == 0:
                    moves.append((r, c))
        return moves
