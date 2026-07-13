from AIcheck import *

# 添加缓存机制
_evaluation_cache = {}

def get_board_hash(board):
    """快速生成棋盘哈希值"""
    return hash(tuple(tuple(row) for row in board))

def store_cache(cache_key,result):
    # 限制缓存大小
    if len(_evaluation_cache) > 10000:
        _evaluation_cache.clear()
    # 存入缓存
    _evaluation_cache[cache_key] = result


def evaluation(board, current_player, focused_player):
    """评估函数 - 带缓存优化版本"""
    # 生成缓存键
    board_hash = get_board_hash(board)
    cache_key = (board_hash, current_player, focused_player)
    
    # 检查缓存
    if cache_key in _evaluation_cache:
        return _evaluation_cache[cache_key]
    
    # 使用缓存的count_pattern函数
    result = 0

    my_win, my_force, my_sente, my_offense = count_pattern(board, focused_player)
    oppo_win, oppo_force, oppo_sente, oppo_offense = count_pattern(board, 3-focused_player)

    if current_player == focused_player:
        if my_win:
            result = 1000000
            store_cache(cache_key,result)
            return result
        if oppo_win:
            result = -1000000
            store_cache(cache_key,result)
            return result

        if my_force:
            result = 1000000
            store_cache(cache_key,result)
            return result
        if oppo_force > 1:
            result = -1000000
            store_cache(cache_key,result)
            return result
        elif oppo_force == 1:
            if oppo_sente:
                result = -60000*oppo_sente
                store_cache(cache_key,result)
                return result
            if my_sente > 1:
                result = 30000*my_sente
                store_cache(cache_key,result)
                return result
            
            result += (my_sente-0.5)*1000
            result += my_offense*100
            result -= oppo_offense*100

            store_cache(cache_key,result)
            return result
        
        else:
            if my_sente:
                result = 60000*my_sente
                store_cache(cache_key,result)
                return result
            if oppo_sente > 1:
                result = -30000*oppo_sente
                store_cache(cache_key,result)
                return result

            result += (oppo_sente-0.5)*1000
            result += my_offense*100
            result -= oppo_offense*100

            store_cache(cache_key,result)
            return result
        
    else:
        return -evaluation(board, current_player, 3-focused_player)
    
    

def evaluate_point(board, r, c, focus_player):
    score = 0
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
    size = len(board)
    
    for dr, dc in directions:
        consecutive = 1
        blocks = 0
        
        nr, nc = r + dr, c + dc
        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == focus_player:
            consecutive += 1
            nr += dr; nc += dc
        if nr < 0 or nr >= size or nc < 0 or nc >= size or board[nr][nc] != 0:
            blocks += 1
            
        nr, nc = r - dr, c - dc
        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == focus_player:
            consecutive += 1
            nr -= dr; nc -= dc
        if nr < 0 or nr >= size or nc < 0 or nc >= size or board[nr][nc] != 0:
            blocks += 1
            
        if consecutive >= 5:
            score += 100000
        elif consecutive == 4:
            if blocks == 0:
                score += 10000
            elif blocks == 1:
                score += 1000
        elif consecutive == 3:
            if blocks == 0:
                score += 1000
            elif blocks == 1:
                score += 100
        elif consecutive == 2:
            if blocks == 0:
                score += 100
            elif blocks == 1:
                score += 10
                
    return score