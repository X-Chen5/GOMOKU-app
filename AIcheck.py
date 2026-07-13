# 添加全局缓存
_pattern_cache = {}

def get_board_key(board, player):
    """生成棋型检测的缓存键"""
    return (hash(tuple(tuple(row) for row in board)), player)

def count_pattern(board, player):

    #巧思1：分为以下四个棋型
    my_win = [0]            #1.胜型(活四)
    my_force = [0]          #2.迫型(冲四等)
    my_sente = [0]          #3.先手(下一手可形成1)
    my_offense = [0]        #4.进攻(下一手可形成2或3)
    size = len(board)
    opponent = 3 - player

    #内部子函数
    ####################################################################################################
    def pattern_start(x, y, dx, dy):
        """快速检查棋型起点"""
        total_cells = 5
        
        left_block_pos = -3
        prev_x, prev_y = x - dx, y - dy
        pp_x, pp_y = prev_x - dx, prev_y - dy
        
        if 0 <= pp_x < size and 0 <= pp_y < size:
            if board[pp_x][pp_y] == player:
                return
            elif board[pp_x][pp_y] == opponent:
                left_block_pos = -2
        else:
            left_block_pos = -2

        if 0 <= prev_x < size and 0 <= prev_y < size:
            if board[prev_x][prev_y] == player:
                return
            elif board[prev_x][prev_y] == opponent:
                left_block_pos = -1
        else:
            left_block_pos = -1
        
        # 快速检查棋子数量和空格
        right_block_pos = 5
        player_count = 0
        player_pos = []
        
        for k in range(total_cells):
            nx, ny = x + k * dx, y + k * dy
            if not (0 <= nx < size and 0 <= ny < size):
                right_block_pos = k
                break
            cell = board[nx][ny]
            if cell == opponent:
                right_block_pos = k
                break
            elif cell == player:
                player_count += 1
                player_pos.append(k)

        #巧思2：抽象出 spare/occupy/empty,以判断棋型价值(加入offense)
        end_pos = player_pos[-1]
        spare = right_block_pos-left_block_pos-6
        occupy = end_pos+1
        empty = occupy - player_count
        left_block = (left_block_pos == -1)
        right_block = (right_block_pos - end_pos) == 1
        
        if spare < 0:
            return

        if player_count == 1:
            return
        
        elif player_count == 2:
            if left_block or right_block:
                return
            my_offense[0] += (3.5 + spare*0.25 - empty*0.25)
            return
        
        elif player_count == 3:
            if not (left_block or right_block):
                if spare!=0 and empty<=1:
                    my_sente[0] += 1
                    return
                else:
                    my_offense[0] += (3.5 + spare*0.25 - empty*0.25)
                    return
            else:
                my_offense[0] += (3 + spare*0.25 - empty*0.25 - (left_block+right_block)*0.25)
                return

        elif player_count == 4:
            if (not left_block) and (not right_block):
                if empty == 0:
                    my_win[0] += 1
                    return
                else:
                    my_force[0] += 1
                    my_offense[0] += (3 + spare*0.25)
                    return
            else:
                my_force[0] += 1
                my_offense[0] += (2.75 + spare*0.25)
                return
            
    ####################################################################################################
    # 参数验证        
    if player not in (1, 2):
        raise ValueError("玩家编号必须是1或2")
    
    # 生成缓存键
    cache_key = get_board_key(board, player)
    if cache_key in _pattern_cache:
        return _pattern_cache[cache_key]
    
    
    # 四个方向：水平、垂直、右下对角线、左下对角线
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    
    # 只搜索棋盘上有棋子的区域
    for i in range(size):
        for j in range(size):
            if board[i][j] != player:
                continue
            for dx, dy in directions:
                # 检查从(i,j)开始，方向(dx,dy)是否能形成指定棋型
                pattern_start(i, j, dx, dy)
    

    # 限制缓存大小
    if len(_pattern_cache) > 5000:
        _pattern_cache.clear()

    #存入缓存
    win = my_win[0]
    force = my_force[0]
    sente = my_sente[0]
    offense = my_offense[0]
    _pattern_cache[cache_key] = (win,force,sente,offense)
    
    return (win,force,sente,offense)


def get_four(board, candidates: set, current_player) -> tuple:

    if not candidates:
        return ([],[])
    
    kill = []
    forcing = []
    
    for r, c in candidates:
        flag = form_four(board, r, c, current_player)
        if flag == 1:
            kill.append((r, c))
            break
        elif flag == 0:
            continue
        else:
            forcing.append(((r,c),flag))

    
    return (kill,forcing)


def form_four(board, r, c, player):
    
    if board[r][c] != 0:
        return False
    
    opponent = 3-player
    # 模拟下子
    board[r][c] = player

    forced_move =[]

    # 检查四个方向
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    size = len(board)
    
    for dx, dy in directions:
        # 检查这个方向是否能形成活四
        
        # 统计连续棋子数
        count = 1  # 包括当前下的子
        
        # 正向统计
        for k in range(1, 5):  # 最多向前看4个位置
            nr, nc = r + k * dx, c + k * dy
            if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                count += 1
            else:
                # 记录停止的位置
                forward_stop_r, forward_stop_c = nr, nc
                break
        
        # 反向统计
        for k in range(1, 5):  # 最多向后看4个位置
            nr, nc = r - k * dx, c - k * dy
            if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                count += 1
            else:
                # 记录停止的位置
                backward_stop_r, backward_stop_c = nr, nc
                break
        
        # 检查两端是否无阻挡
        # 正向端检查
        forward_blocked = False
        if 0 <= forward_stop_r < size and 0 <= forward_stop_c < size:
            if board[forward_stop_r][forward_stop_c] == opponent:  # 有棋子阻挡
                forward_blocked = True
        # 边界视为阻挡（因为不能再延伸形成五连）
        else:
            forward_blocked = True
        
        # 反向端检查
        backward_blocked = False
        if 0 <= backward_stop_r < size and 0 <= backward_stop_c < size:
            if board[backward_stop_r][backward_stop_c] == opponent:  # 有棋子阻挡
                backward_blocked = True
        # 边界视为阻挡
        else:
            backward_blocked = True
        
        if forward_blocked and backward_blocked:
            continue

        # 活四要求两端都无阻挡
        if not forward_blocked and not backward_blocked:
            if count >= 4:
                # 恢复棋盘
                board[r][c] = 0
                return 1
            else:
                forward_plus = 0
                for k in range(1, 4):  # 最多向后看3个位置
                    nr, nc = forward_stop_r + k * dx, forward_stop_c + k * dy
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                        forward_plus += 1
                    else:
                        break
                if forward_plus+count >= 4:
                    forced_move.append((forward_stop_r, forward_stop_c))

                backward_plus = 0
                for k in range(1, 4):  # 最多向后看3个位置
                    nr, nc = backward_stop_r - k * dx, backward_stop_c - k * dy
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                        backward_plus += 1
                    else:
                        break
                if backward_plus+count >= 4:
                    forced_move.append((backward_stop_r, backward_stop_c))

                
                if count >= 4:
                    pass
        
        else:
            if forward_blocked:
                backward_plus = 0
                for k in range(1, 4):  # 最多向后看3个位置
                    nr, nc = backward_stop_r - k * dx, backward_stop_c - k * dy
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                        backward_plus += 1
                    else:
                        break
                if backward_plus+count >= 4:
                    forced_move.append((backward_stop_r, backward_stop_c))
            
            else:
                forward_plus = 0
                for k in range(1, 4):  # 最多向后看3个位置
                    nr, nc = forward_stop_r + k * dx, forward_stop_c + k * dy
                    if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                        forward_plus += 1
                    else:
                        break
                if forward_plus+count >= 4:
                    forced_move.append((forward_stop_r, forward_stop_c))

        if len(forced_move) > 1:
            board[r][c] = 0
            return 1
    
    # 恢复棋盘
    board[r][c] = 0
    if len(forced_move) == 0:
        return 0
    else:
        return forced_move[0]
