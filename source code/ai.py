import time
from config import AI, HUMAN, SCORE, DEFAULT_DEPTH
from board import Board
from evaluator import evaluate

INF = float("inf")


def _block_bonus(board, r, c, player, maximize):
    """Thưởng thêm nếu nước (r,c) chặn đe dọa của đối thủ."""
    opponent = HUMAN if player == AI else AI
    bonus = 0
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for dr, dc in directions:
        cnt = 0
        nr, nc = r + dr, c + dc
        while 0 <= nr < board.size and 0 <= nc < board.size and board.grid[nr][nc] == opponent:
            cnt += 1
            nr += dr
            nc += dc
        nr, nc = r - dr, c - dc
        while 0 <= nr < board.size and 0 <= nc < board.size and board.grid[nr][nc] == opponent:
            cnt += 1
            nr -= dr
            nc -= dc
        if cnt >= 3:
            bonus += 10000
        elif cnt >= 2:
            bonus += 1000
    return bonus if maximize else -bonus


class SearchResult:
    """Kết quả một lần tìm kiếm AI."""
    def __init__(self):
        self.move: tuple[int, int] | None = None
        self.value: int  = 0
        self.states: int = 0         
        self.elapsed: float = 0.0     
        self.depth: int  = 0
        self.algorithm: str = ""

    def __str__(self):
        return (f"[{self.algorithm}] depth={self.depth} "
                f"move={self.move} value={self.value} "
                f"states={self.states} time={self.elapsed:.4f}s")

def minimax(board: Board, depth: int, is_maximizing: bool,
            counter: list) -> int:
    """Minimax thuần túy (không cắt nhánh).

    Args:
        board: Trạng thái bàn cờ hiện tại.
        depth: Độ sâu còn lại.
        is_maximizing: True nếu lượt AI (MAX), False nếu lượt HUMAN (MIN).
        counter: list 1 phần tử dùng để đếm số trạng thái (pass-by-ref).

    Returns:
        Giá trị đánh giá của trạng thái.
    """
    counter[0] += 1
    done, winner = board.game_over()
    if done:
        if winner == AI:
            return SCORE["WIN"] + depth   
        elif winner == HUMAN:
            return -(SCORE["WIN"] + depth)
        else:
            return 0
    if depth == 0:
        return evaluate(board)

    moves = board.get_valid_moves()

    if is_maximizing:   
        best = -INF
        for (r, c) in moves:
            board.place(r, c, AI)
            val = minimax(board, depth - 1, False, counter)
            board.undo()
            if val > best:
                best = val
        return best
    else: 
        best = INF
        for (r, c) in moves:
            board.place(r, c, HUMAN)
            val = minimax(board, depth - 1, True, counter)
            board.undo()
            if val < best:
                best = val
        return best


def best_move_minimax(board: Board, depth: int = DEFAULT_DEPTH,
                      player: int = AI) -> SearchResult:
    """Tìm nước đi tốt nhất bằng Minimax.

    Args:
        player: AI (-1) tìm MAX, HUMAN (1) tìm MIN.
    """
    result = SearchResult()
    result.algorithm = "Minimax"
    result.depth = depth

    counter  = [0]
    maximize = (player == AI)
    best_val = -INF if maximize else INF
    best_mv  = None

    start = time.perf_counter()

    moves = board.get_valid_moves()
    for (r, c) in moves:
        board.place(r, c, player)
        val = minimax(board, depth - 1, not maximize, counter)
        board.undo()

        block = _block_bonus(board, r, c, player, maximize)
        adjusted = val + block * 0.001
        if maximize:
            if adjusted > best_val or best_mv is None:
                best_val = adjusted
                best_mv  = (r, c)
        else:
            if adjusted < best_val or best_mv is None:
                best_val = adjusted
                best_mv  = (r, c)

    result.elapsed = time.perf_counter() - start
    result.states  = counter[0]
    result.move    = best_mv
    if best_mv:
        board.place(*best_mv, player)
        result.value = minimax(board, depth - 1, not maximize, [0])
        board.undo()
    return result


def alpha_beta(board: Board, depth: int, alpha: float, beta: float,
               is_maximizing: bool, counter: list) -> int:
    """Minimax với cắt nhánh Alpha-Beta.

    Args:
        alpha: Giá trị tốt nhất MAX đã đạt được trên đường đi.
        beta:  Giá trị tốt nhất MIN đã đạt được trên đường đi.
        Cắt nhánh khi beta <= alpha.
    """
    counter[0] += 1

    done, winner = board.game_over()
    if done:
        if winner == AI:
            return SCORE["WIN"] + depth
        elif winner == HUMAN:
            return -(SCORE["WIN"] + depth)
        else:
            return 0
    if depth == 0:
        return evaluate(board)

    moves = board.get_valid_moves()

    if is_maximizing:
        best = -INF
        for (r, c) in moves:
            board.place(r, c, AI)
            val = alpha_beta(board, depth - 1, alpha, beta, False, counter)
            board.undo()
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if beta <= alpha:          
                break
        return best
    else:
        best = INF
        for (r, c) in moves:
            board.place(r, c, HUMAN)
            val = alpha_beta(board, depth - 1, alpha, beta, True, counter)
            board.undo()
            if val < best:
                best = val
            if best < beta:
                beta = best
            if beta <= alpha:    
                break
        return best


def best_move_alphabeta(board: Board, depth: int = DEFAULT_DEPTH,
                        player: int = AI) -> SearchResult:
    """Tìm nước đi tốt nhất bằng Alpha-Beta pruning.

    Args:
        player: AI (-1) tìm MAX, HUMAN (1) tìm MIN.
    """
    result = SearchResult()
    result.algorithm = "Alpha-Beta"
    result.depth = depth

    counter  = [0]
    maximize = (player == AI)
    best_val = -INF if maximize else INF
    best_mv  = None

    start = time.perf_counter()

    moves = board.get_valid_moves()
    for (r, c) in moves:
        board.place(r, c, player)
        val = alpha_beta(board, depth - 1, -INF, INF, not maximize, counter)
        board.undo()

        block    = _block_bonus(board, r, c, player, maximize)
        adjusted = val + block * 0.001

        if maximize:
            if adjusted > best_val or best_mv is None:
                best_val = adjusted
                best_mv  = (r, c)
        else:
            if adjusted < best_val or best_mv is None:
                best_val = adjusted
                best_mv  = (r, c)

    result.elapsed = time.perf_counter() - start
    result.states  = counter[0]
    result.move    = best_mv
    if best_mv:
        board.place(*best_mv, player)
        result.value = alpha_beta(board, depth - 1, -INF, INF, not maximize, [0])
        board.undo()
    return result