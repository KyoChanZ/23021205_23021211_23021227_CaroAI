import numpy as np
from config import BOARD_SIZE, WIN_LENGTH, EMPTY, HUMAN, AI, NEIGHBOR_RANGE


class Board:
    """Biểu diễn trạng thái bàn cờ bằng mảng numpy 2D."""

    def __init__(self, size: int = BOARD_SIZE):
        self.size = size
        self.grid = np.zeros((size, size), dtype=np.int8)
        self.move_history: list[tuple[int, int]] = []  

    def copy(self) -> "Board":
        new = Board(self.size)
        new.grid = self.grid.copy()
        new.move_history = self.move_history.copy()
        return new

    def place(self, row: int, col: int, player: int) -> None:
        self.grid[row][col] = player
        self.move_history.append((row, col))

    def undo(self) -> None:
        if self.move_history:
            r, c = self.move_history.pop()
            self.grid[r][c] = EMPTY

    def is_valid(self, row: int, col: int) -> bool:
        return (0 <= row < self.size and
                0 <= col < self.size and
                self.grid[row][col] == EMPTY)

    def is_full(self) -> bool:
        return not np.any(self.grid == EMPTY)

    def check_win(self, player: int) -> bool:
        """Trả về True nếu player có WIN_LENGTH quân liên tiếp."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        g = self.grid
        n = self.size

        for r in range(n):
            for c in range(n):
                if g[r][c] != player:
                    continue
                for dr, dc in directions:
                    count = 1
                    nr, nc = r + dr, c + dc
                    while (0 <= nr < n and 0 <= nc < n and
                           g[nr][nc] == player):
                        count += 1
                        nr += dr
                        nc += dc
                    if count >= WIN_LENGTH:
                        return True
        return False

    def get_win_cells(self, player: int) -> list[tuple[int, int]]:
        """Trả về danh sách ô tạo thành chuỗi thắng (dùng để vẽ highlight)."""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        g = self.grid
        n = self.size

        for r in range(n):
            for c in range(n):
                if g[r][c] != player:
                    continue
                for dr, dc in directions:
                    cells = [(r, c)]
                    nr, nc = r + dr, c + dc
                    while (0 <= nr < n and 0 <= nc < n and
                           g[nr][nc] == player):
                        cells.append((nr, nc))
                        nr += dr
                        nc += dc
                    if len(cells) >= WIN_LENGTH:
                        return cells
        return []

    def get_valid_moves(self) -> list[tuple[int, int]]:
        """Chỉ trả về ô trống nằm trong vùng lân cận các quân đã đánh.
        Nếu bàn cờ trống hoàn toàn, trả về ô trung tâm."""
        if not self.move_history:
            mid = self.size // 2
            return [(mid, mid)]

        candidates = set()
        for (r, c) in self.move_history:
            for dr in range(-NEIGHBOR_RANGE, NEIGHBOR_RANGE + 1):
                for dc in range(-NEIGHBOR_RANGE, NEIGHBOR_RANGE + 1):
                    nr, nc = r + dr, c + dc
                    if self.is_valid(nr, nc):
                        candidates.add((nr, nc))
        mid = self.size / 2
        return sorted(candidates,
                       key=lambda pos: (abs(pos[0] - mid) + abs(pos[1] - mid),
                                        pos[0], pos[1]))

    def game_over(self) -> tuple[bool, int | None]:
        """Trả về (done, winner).
        winner = HUMAN | AI | 0 (hòa) | None (chưa xong)."""
        if self.check_win(HUMAN):
            return True, HUMAN
        if self.check_win(AI):
            return True, AI
        if self.is_full():
            return True, 0  
        return False, None

    def __str__(self) -> str:
        sym = {EMPTY: ".", HUMAN: "X", AI: "O"}
        rows = []
        header = "   " + " ".join(f"{c:2}" for c in range(self.size))
        rows.append(header)
        for r in range(self.size):
            line = f"{r:2} " + " ".join(f" {sym[self.grid[r][c]]}" for c in range(self.size))
            rows.append(line)
        return "\n".join(rows)