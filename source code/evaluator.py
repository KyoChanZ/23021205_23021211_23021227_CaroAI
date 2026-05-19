from config import BOARD_SIZE, WIN_LENGTH, EMPTY, HUMAN, AI, SCORE

def _count_sequence(grid, r: int, c: int, dr: int, dc: int,
                    player: int, size: int) -> tuple[int, int]:
    """Đếm số quân liên tiếp của player bắt đầu từ (r,c) theo hướng (dr,dc).
    Trả về (count, open_ends) - số đầu mở (0,1,2).
    """
    count = 0
    nr, nc = r, c
    while (0 <= nr < size and 0 <= nc < size and
           grid[nr][nc] == player):
        count += 1
        nr += dr
        nc += dc

    open_ends = 0
    if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == EMPTY:
        open_ends += 1
    pr, pc = r - dr, c - dc
    if 0 <= pr < size and 0 <= pc < size and grid[pr][pc] == EMPTY:
        open_ends += 1
    return count, open_ends


def _score_for_player(grid, player: int, size: int) -> int:
    """Tính tổng điểm cho player dựa trên các chuỗi quân."""
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    visited = set()
    total = 0

    for r in range(size):
        for c in range(size):
            if grid[r][c] != player:
                continue
            for dr, dc in directions:
                pr, pc = r - dr, c - dc
                if (0 <= pr < size and 0 <= pc < size and
                        grid[pr][pc] == player):
                    continue  

                key = (r, c, dr, dc)
                if key in visited:
                    continue
                visited.add(key)

                count, open_ends = _count_sequence(
                    grid, r, c, dr, dc, player, size)

                if count <= 0:
                    continue

                if count >= WIN_LENGTH:
                    total += SCORE["WIN"]
                elif count == WIN_LENGTH - 1:
                    if open_ends == 2:
                        total += SCORE["FOUR_OPEN"]
                    elif open_ends == 1:
                        total += SCORE["FOUR_HALF"]
                elif count == WIN_LENGTH - 2:
                    if open_ends == 2:
                        total += SCORE["THREE_OPEN"]
                    elif open_ends == 1:
                        total += SCORE["THREE_HALF"]
                elif count == WIN_LENGTH - 3:
                    if open_ends == 2:
                        total += SCORE["TWO_OPEN"]
                    elif open_ends == 1:
                        total += SCORE["TWO_HALF"]

    return total


def evaluate(board) -> int:
    """Hàm đánh giá tổng hợp: điểm AI - điểm HUMAN.
    Dương tốt cho AI, âm tốt cho HUMAN.
    """
    grid = board.grid
    size = board.size

    ai_score    = _score_for_player(grid, AI,    size)
    human_score = _score_for_player(grid, HUMAN, size)
    return ai_score - 2 * human_score
