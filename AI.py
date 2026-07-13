import time
from AIcheck import *
from AIevaluate import *

class AdvancedAI:
    def __init__(self, player = 2, depth=4):
        self.player = player
        self.depth = depth
        self.vcf_depth = 4
        self.memo = {}

    def get_move(self, game):
        start_time = time.time()
        
        vcf_best,_ = self.winning_move(game, self.player, game.candidate_moves, self.vcf_depth)
        if vcf_best:
            if _:
                print(f"可杀棋！")
            return vcf_best
        
        best_val = -float('inf')
        best_move = None
        self.memo.clear()
        
        candidates = self._get_candidates(game)
        if not candidates:
            return (len(game.board) // 2, len(game.board) // 2)
            
        alpha = -float('inf')
        beta = float('inf')
        
        scored_candidates = []
        for r, c in candidates:
            score = evaluate_point(game.board, r, c, self.player) + \
                    evaluate_point(game.board, r, c, 3 - self.player)
            scored_candidates.append((score, r, c))
            
        scored_candidates.sort(reverse=True, key=lambda x: x[0])
        
        for score, r, c in scored_candidates:
            prev_winner = game.winner
            game.board[r][c] = self.player
            if game.check_win(r, c):
                game.winner = self.player
            game.current_player = 3 - self.player
            
            val = self._minimax(game, self.depth - 1, alpha, beta, False)
            
            game.board[r][c] = 0
            game.winner = prev_winner
            game.current_player = self.player

            if val > best_val:
                best_val = val
                best_move = (r, c)
            
            alpha = max(alpha, best_val)
            if alpha >= beta:
                break
        
        end_time = time.time()
        print(f"[AdvancedAI Depth {self.depth}] Decision took {end_time - start_time:.3f}s. Selected: {best_move} with val: {best_val}. Cache: {len(self.memo)}")
        return best_move

    def _minimax(self, game, depth, alpha, beta, is_maximizing):
        if game.winner == self.player:
            return 1000000 + depth  
        elif game.winner == 3 - self.player:
            return -1000000 - depth 
        elif game.is_board_full():
            return 0
            
        if depth == 0:
            if is_maximizing:
                return evaluation(game.board,self.player,self.player)
            else:
                return evaluation(game.board,3-self.player,self.player)

        board_tuple = tuple(tuple(row) for row in game.board)
        if board_tuple in self.memo:
            cached_depth, cached_val = self.memo[board_tuple]
            if cached_depth >= depth:
                return cached_val
        
        candidates = self._get_candidates(game)
        
        if is_maximizing:
            vcf_best,_ = self.winning_move(game, self.player, candidates, self.vcf_depth + (depth-self.depth)//2)
            if vcf_best and _:
                return 1000000 + depth
            max_eval = -float('inf')
            scored_candidates = []
            for r, c in candidates:
                sc = evaluate_point(game.board, r, c, self.player) + evaluate_point(game.board, r, c, 3 - self.player)
                scored_candidates.append((sc, r, c))
            scored_candidates.sort(reverse=True, key=lambda x: x[0])
            
            for score, r, c in scored_candidates:
                prev_winner = game.winner
                game.board[r][c] = self.player
                if game.check_win(r, c):
                    game.winner = self.player
                game.current_player = 3 - self.player
                
                eval_val = self._minimax(game, depth - 1, alpha, beta, False)
                
                game.board[r][c] = 0
                game.winner = prev_winner
                game.current_player = self.player
                
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
                    
            self.memo[board_tuple] = (depth, max_eval)
            return max_eval
        
        else:
            vcf_best,_ = self.winning_move(game, 3-self.player, candidates, self.vcf_depth + (depth-self.depth)//2)
            if vcf_best and _:
                return -1000000 - depth
            
            min_eval = float('inf')
            opponent = 3 - self.player
            
            scored_candidates = []
            for r, c in candidates:
                sc = evaluate_point(game.board, r, c, opponent) + evaluate_point(game.board, r, c, self.player)
                scored_candidates.append((sc, r, c))
            scored_candidates.sort(reverse=True, key=lambda x: x[0])
            
            for score, r, c in scored_candidates:
                prev_winner = game.winner
                game.board[r][c] = opponent
                if game.check_win(r, c):
                    game.winner = opponent
                game.current_player = self.player
                
                eval_val = self._minimax(game, depth - 1, alpha, beta, True)
                
                game.board[r][c] = 0
                game.winner = prev_winner
                game.current_player = opponent
                
                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
                    
            self.memo[board_tuple] = (depth, min_eval)
            return min_eval

    def winning_move(self, game, current_player, candidate_moves, depth):
        if depth <= 0:
            return (None,0)
        board = game.board
        for r,c in candidate_moves:
            board[r][c] = current_player
            if game.check_win(r,c):
                board[r][c] = 0
                return ((r,c),1)
            board[r][c] = 0

        for r,c in candidate_moves:
            board[r][c] = 3-current_player
            if game.check_win(r,c):
                board[r][c] = 0
                return ((r,c),0)
            board[r][c] = 0

        kill, forcing = get_four(game.board,candidate_moves,current_player)
        if kill:
            # print('可杀棋')
            # print(kill[0])
            return (kill[0],1)
        if forcing:
            for move,oppo_move in forcing:
                #print('moni',depth)
                adding1 = self.simulate(game,move,current_player,candidate_moves)
                adding2 = self.simulate(game,oppo_move,3-current_player,candidate_moves)
                nmove,iswinning = self.winning_move(game,current_player,candidate_moves,depth-1)
                self.backset(game,oppo_move,candidate_moves,adding2)
                self.backset(game,move,candidate_moves,adding1)
                if nmove and iswinning:
                    return (move,1)

        return (None,0)

    def _get_candidates(self, game):
        """仅返回已有棋子周围半径为1或2的空位"""
        radius = 1 if self.depth >= 4 else 2
        candidates = set()
        has_stone = False
        board_size = game.board_size
        board = game.board
        
        for r in range(board_size):
            for c in range(board_size):
                if board[r][c] != 0:
                    has_stone = True
                    for dr in range(-radius, radius + 1):
                        for dc in range(-radius, radius + 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < board_size and 0 <= nc < board_size and board[nr][nc] == 0:
                                candidates.add((nr, nc))
        if not has_stone:
            return {(7,7)}
        return candidates

    

    def update_candidates(self,board,candidate:set,move):
        size = len(board)
        adding = set()
        row,col = move
        candidate.discard((row, col))
        
        for r in range(max(0, row-2), min(size, row+3)):
            for c in range(max(0, col-2), min(size, col+3)):
                if board[r][c] == 0:
                    candidate.add((r, c))
                    adding.add((r,c))
        
        return (candidate,adding)
    

    def simulate(self,game,move,current_player,candidate):
        simulate_board = game.board
        r,c = move
        simulate_board[r][c] = current_player
        candidate,adding = self.update_candidates(simulate_board,candidate,move)
        return adding

    def backset(self,game,move,candidate,adding):
        simulate_board = game.board
        r,c = move
        simulate_board[r][c] = 0
        candidate -= adding
        candidate.add((r,c))