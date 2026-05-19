import random
import pygame
import sys
import threading
from config import (
    BOARD_SIZE, CELL_SIZE, MARGIN, PANEL_WIDTH,
    BOARD_PX, WINDOW_W, WINDOW_H,
    C_BG, C_GRID, C_CELL_EVEN, C_CELL_ODD,
    C_HUMAN, C_AI, C_PANEL, C_TEXT, C_SUBTEXT,
    C_HIGHLIGHT, C_WIN_CELL, C_BTN, C_BTN_HOVER, C_BTN_TEXT,
    HUMAN, AI, EMPTY, DEFAULT_DEPTH,
)
from board import Board
from ai import best_move_minimax, best_move_alphabeta, SearchResult

MODE_HVAI = 0  
MODE_MVSM = 1 

def cell_center(row: int, col: int) -> tuple[int, int]:
    """Tọa độ pixel tâm của ô (row, col)."""
    x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + row * CELL_SIZE + CELL_SIZE // 2
    return x, y

def px_to_cell(x: int, y: int) -> tuple[int, int]:
    """Click pixel → ô lưới."""
    col = (x - MARGIN) // CELL_SIZE
    row = (y - MARGIN) // CELL_SIZE
    return row, col

def cell_rect(row: int, col: int) -> pygame.Rect:
    """Hình chữ nhật của ô (row, col)."""
    x = MARGIN + col * CELL_SIZE
    y = MARGIN + row * CELL_SIZE
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

class Button:
    def __init__(self, x, y, w, h, text, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, surface):
        color = C_BTN_HOVER if self.hovered else C_BTN
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        lbl = self.font.render(self.text, True, C_BTN_TEXT)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width() // 2,
                           self.rect.centery - lbl.get_height() // 2))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class TurnSelectScreen:
    """Hiển thị trước mỗi ván: chọn máy đi trước hay đi sau."""

    def __init__(self, screen, fonts):
        self.screen = screen
        self.font_lg, self.font_md, self.font_sm = fonts

    def run(self) -> int:
        """Trả về HUMAN (người đi trước) hoặc AI (máy đi trước)."""
        W, H = self.screen.get_size()
        clock = pygame.time.Clock()

        btn_w, btn_h = 240, 60
        gap = 20
        total_h = btn_h * 2 + gap
        start_y = H // 2 - total_h // 2 + 30

        bx = W // 2 - btn_w // 2
        choices = [
            {"text": "Ban di truoc  (X)",  "color": (50, 100, 180),
             "hover": (70, 130, 220), "value": HUMAN},
            {"text": "May di truoc  (O)",  "color": (160, 50, 50),
             "hover": (200, 70, 70),  "value": AI},
        ]
        buttons = []
        for i, ch in enumerate(choices):
            rect = pygame.Rect(bx, start_y + i * (btn_h + gap), btn_w, btn_h)
            buttons.append((rect, ch))

        while True:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, ch in buttons:
                        if rect.collidepoint(pos):
                            return ch["value"]
            self.screen.fill(C_BG)

            title = self.font_lg.render("CHON LUOT DI", True, (200, 220, 255))
            self.screen.blit(title, (W // 2 - title.get_width() // 2, H // 2 - 130))

            sub = self.font_md.render("Ai se di nuoc dau tien?", True, C_SUBTEXT)
            self.screen.blit(sub, (W // 2 - sub.get_width() // 2, H // 2 - 90))

            for rect, ch in buttons:
                hovered = rect.collidepoint(pos)
                color = ch["hover"] if hovered else ch["color"]
                pygame.draw.rect(self.screen, color, rect, border_radius=12)
                if hovered:
                    pygame.draw.rect(self.screen, (255, 255, 255), rect, 2, border_radius=12)
                lbl = self.font_md.render(ch["text"], True, (255, 255, 255))
                self.screen.blit(lbl, (rect.centerx - lbl.get_width() // 2,
                                       rect.centery - lbl.get_height() // 2))

            note = self.font_sm.render("X luon di truoc, O di sau", True, C_SUBTEXT)
            self.screen.blit(note, (W // 2 - note.get_width() // 2,
                                    start_y + total_h + 20))

            pygame.display.flip()
            clock.tick(60)

class GameUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("Caro AI - Minimax & Alpha-Beta")

        self.font_lg = pygame.font.Font(None, 28)
        self.font_md = pygame.font.Font(None, 22)
        self.font_sm = pygame.font.Font(None, 18)
        self.font_piece = pygame.font.Font(None, int(CELL_SIZE * 0.7))

        self.use_alphabeta = True
        self.depth = DEFAULT_DEPTH
        self.mode = MODE_HVAI
        self.ai_goes_first = False

        self._board_lock = threading.Lock()

        self.ai_thread: threading.Thread | None = None
        self.ai_result: SearchResult | None = None
        self.ai_thinking = False
        self._ai_playing_for = AI

        first = TurnSelectScreen(self.screen,
                                 (self.font_lg, self.font_md, self.font_sm)).run()
        self.ai_goes_first = (first == AI)

        self.reset_game()
        self._make_buttons()

    def _make_buttons(self):
        bx = BOARD_PX + 15
        bw = PANEL_WIDTH - 30
        self.btn_new        = Button(bx, WINDOW_H - 240, bw,      40, "New Game",       self.font_md)
        self.btn_toggle     = Button(bx, WINDOW_H - 190, bw,      40, "AI: Alpha-Beta", self.font_md)
        self.btn_mode       = Button(bx, WINDOW_H - 140, bw,      40, "Mode: Human vs AI", self.font_md)
        self.btn_depth_down = Button(bx,                  WINDOW_H - 88, bw // 2 - 4, 34, "Depth -", self.font_md)
        self.btn_depth_up   = Button(bx + bw // 2 + 4,   WINDOW_H - 88, bw // 2 - 4, 34, "Depth +", self.font_md)

    def reset_game(self):
        self.board = Board(BOARD_SIZE)
        self.game_done = False
        self.winner = None
        self.win_cells: list[tuple[int, int]] = []
        self.last_result: SearchResult | None = None
        self.log: list[str] = []
        self.ai_thinking = False
        self.ai_result = None
        self._pending_player = None  
        if self.mode == MODE_MVSM:
            first = self._first_player()
            self.current_player = first
            self._start_ai_thread(first)
        else:
            if self.ai_goes_first:
                self.current_player = AI
                self._start_ai_thread(AI)
            else:
                self.current_player = HUMAN

    def run(self):
        clock = pygame.time.Clock()

        while True:
            mouse_pos = pygame.mouse.get_pos()
            for btn in [self.btn_new, self.btn_toggle, self.btn_mode,
                        self.btn_depth_up, self.btn_depth_down]:
                btn.check_hover(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.USEREVENT:
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                    if self._pending_player is not None and not self.game_done:
                        self._start_ai_thread(self._pending_player)
                        self._pending_player = None

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

            if self.ai_thinking and self.ai_result is not None:
                self._apply_ai_result()

            self._draw()
            clock.tick(60)

    def _handle_click(self, pos):
        if self.btn_new.is_clicked(pos):
            if not self.ai_thinking:
                if self.mode == MODE_HVAI:
                    first = TurnSelectScreen(
                        self.screen,
                        (self.font_lg, self.font_md, self.font_sm)).run()
                    self.ai_goes_first = (first == AI)
            self.reset_game()
            return
        if self.btn_toggle.is_clicked(pos):
            self.use_alphabeta = not self.use_alphabeta
            self.btn_toggle.text = ("AI: Alpha-Beta" if self.use_alphabeta
                                    else "AI: Minimax")
            return
        if self.btn_mode.is_clicked(pos):
            self.mode = MODE_MVSM if self.mode == MODE_HVAI else MODE_HVAI
            self.btn_mode.text = ("Mode: Human vs AI" if self.mode == MODE_HVAI
                                  else "Mode: Machine vs Machine")
            if self.mode == MODE_HVAI:
                first = TurnSelectScreen(
                    self.screen,
                    (self.font_lg, self.font_md, self.font_sm)).run()
                self.ai_goes_first = (first == AI)
            self.reset_game()
            return
        if self.btn_depth_up.is_clicked(pos):
            self.depth = min(self.depth + 1, 5)
            return
        if self.btn_depth_down.is_clicked(pos):
            self.depth = max(self.depth - 1, 1)
            return

        if (not self.game_done and not self.ai_thinking
                and self.current_player == HUMAN
                and self.mode == MODE_HVAI
                and pos[0] < BOARD_PX):
            r, c = px_to_cell(*pos)
            if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
                if self.board.is_valid(r, c):
                    with self._board_lock:
                        self.board.place(r, c, HUMAN)
                    self._check_end()
                    if not self.game_done:
                        self.current_player = AI
                        self._start_ai_thread(AI)

    def _depth_for(self, player):
        """Trả về độ sâu tìm kiếm cho player. Ở chế độ máy vs máy, O được +1 depth để bù."""
        if self.mode == MODE_MVSM and player == AI:
            return min(self.depth + 1, 5)
        return self.depth

    def _first_player(self):
        """Chọn ngẫu nhiên bên đi trước ở chế độ máy vs máy."""
        return random.choice([HUMAN, AI])

    def _start_ai_thread(self, for_player: int = AI):
        """Chạy AI trên thread riêng để UI không bị đơ."""
        self.ai_thinking = True
        self.ai_result = None
        self._ai_playing_for = for_player

        with self._board_lock:
            board_copy = self.board.copy()

        fn = best_move_alphabeta if self.use_alphabeta else best_move_minimax
        depth = self._depth_for(for_player)

        def worker():
            res = fn(board_copy, depth, for_player)
            self.ai_result = res

        self.ai_thread = threading.Thread(target=worker, daemon=True)
        self.ai_thread.start()

    def _apply_ai_result(self):
        self.ai_thinking = False
        res = self.ai_result
        self.ai_result = None
        self.last_result = res
        player = self._ai_playing_for

        log_line = (f"[{res.algorithm}] d={res.depth} "
                    f"mv={res.move} val={res.value} "
                    f"st={res.states} t={res.elapsed:.3f}s")
        print(log_line)
        self.log.append(log_line)
        if len(self.log) > 7:
            self.log.pop(0)

        with self._board_lock:
            if res.move and self.board.is_valid(*res.move):
                self.board.place(*res.move, player)
            elif res.move:
                print(f"[WARN] AI chon o {res.move} da bi danh, bo qua")
                res.move = None
        self._check_end()

        if not self.game_done:
            if self.mode == MODE_MVSM:
                other = HUMAN if player == AI else AI
                self.current_player = other
                self._pending_player = other
                pygame.time.set_timer(pygame.USEREVENT, 500) 
            else:
                self.current_player = HUMAN

    def _check_end(self):
        done, winner = self.board.game_over()
        if done:
            self.game_done = True
            self.winner = winner
            if winner in (HUMAN, AI):
                self.win_cells = self.board.get_win_cells(winner)

    def _draw(self):
        self.screen.fill(C_BG)
        self._draw_cells()
        self._draw_grid()
        self._draw_pieces()
        self._draw_panel()
        pygame.display.flip()

    def _draw_cells(self):
        """Vẽ màu nền xen kẽ cho từng ô vuông."""
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = C_CELL_EVEN if (r + c) % 2 == 0 else C_CELL_ODD
                if (r, c) in self.win_cells:
                    color = C_WIN_CELL
                pygame.draw.rect(self.screen, color, cell_rect(r, c))

    def _draw_grid(self):
        """Vẽ lưới ô vuông."""
        total = BOARD_SIZE * CELL_SIZE
        for i in range(BOARD_SIZE + 1):
            y = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, C_GRID,
                             (MARGIN, y), (MARGIN + total, y), 1)
            x = MARGIN + i * CELL_SIZE
            pygame.draw.line(self.screen, C_GRID,
                             (x, MARGIN), (x, MARGIN + total), 1)

    def _draw_pieces(self):
        last_mv = self.board.move_history[-1] if self.board.move_history else None

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                val = self.board.grid[r][c]
                if val == EMPTY:
                    continue

                cx, cy = cell_center(r, c)
                color  = C_HUMAN if val == HUMAN else C_AI
                sym    = "X" if val == HUMAN else "O"

                if (r, c) == last_mv:
                    rect = cell_rect(r, c).inflate(-2, -2)
                    pygame.draw.rect(self.screen, C_HIGHLIGHT, rect, 3,
                                     border_radius=6)
                lbl = self.font_piece.render(sym, True, color)
                self.screen.blit(lbl, (cx - lbl.get_width() // 2,
                                       cy - lbl.get_height() // 2))

        if self.ai_thinking:
            tick = (pygame.time.get_ticks() // 500) % 2
            if tick:
                if self.mode == MODE_MVSM:
                    name = "AI-X (X)" if self._ai_playing_for == HUMAN else "AI-O (O)"
                    d = self._depth_for(self._ai_playing_for)
                    msg = self.font_md.render(f"{name} dang nghi... d={d}", True, (255, 200, 60))
                else:
                    name = "AI"
                    msg = self.font_md.render(f"{name} dang nghi...", True, (255, 200, 60))
                self.screen.blit(msg, (MARGIN + 4, MARGIN + 4))

    def _draw_panel(self):
        panel_rect = pygame.Rect(BOARD_PX, 0, PANEL_WIDTH, WINDOW_H)
        pygame.draw.rect(self.screen, C_PANEL, panel_rect)

        x = BOARD_PX + 15
        y = 18

        def txt(text, font=None, color=C_TEXT):
            nonlocal y
            f = font or self.font_md
            lbl = f.render(text, True, color)
            self.screen.blit(lbl, (x, y))
            y += lbl.get_height() + 5

        txt("CARO AI", self.font_lg, (200, 220, 255))
        txt("Minimax & Alpha-Beta", self.font_sm, C_SUBTEXT)
        y += 8

        if self.game_done:
            if self.mode == MODE_MVSM:
                if self.winner == HUMAN:
                    txt("AI-X (X) thang!", self.font_lg, (80, 220, 120))
                elif self.winner == AI:
                    txt("AI-O (O) thang!", self.font_lg, (255, 100, 100))
                else:
                    txt("Hoa!", self.font_lg, (255, 215, 0))
            else:
                if self.winner == HUMAN:
                    txt("Ban thang!", self.font_lg, (80, 220, 120))
                elif self.winner == AI:
                    txt("May thang!", self.font_lg, (255, 100, 100))
                else:
                    txt("Hoa!", self.font_lg, (255, 215, 0))
        elif self.ai_thinking:
            if self.mode == MODE_MVSM:
                name = "AI-X (X)" if self._ai_playing_for == HUMAN else "AI-O (O)"
                txt(f"{name} dang nghi...", self.font_md, (255, 200, 60))
            else:
                txt("May dang nghi...", self.font_md, (255, 200, 60))
        else:
            if self.mode == MODE_MVSM:
                name = "AI-X (X)" if self.current_player == HUMAN else "AI-O (O)"
                txt(f"Luot: {name}", self.font_md, C_TEXT)
            else:
                turn = "Luot: Ban (X)" if self.current_player == HUMAN else "Luot: May (O)"
                txt(turn, self.font_md, C_TEXT)

        y += 6
        mode_str = "Human vs AI" if self.mode == MODE_HVAI else "Machine vs Machine"
        txt(f"Che do: {mode_str}", self.font_sm, (200, 200, 160))
        if self.mode == MODE_HVAI:
            first_str = "May di truoc (O)" if self.ai_goes_first else "Ban di truoc (X)"
            first_color = (255, 130, 130) if self.ai_goes_first else (130, 180, 255)
            txt(f"Luot dau: {first_str}", self.font_sm, first_color)
        algo = "Alpha-Beta" if self.use_alphabeta else "Minimax"
        txt(f"Thuat toan: {algo}", self.font_sm, (150, 190, 255))
        if self.mode == MODE_MVSM:
            txt(f"Do sau: X={self.depth} | O={min(self.depth+1,5)}", self.font_sm, C_SUBTEXT)
        else:
            txt(f"Do sau: {self.depth}  (max 5)", self.font_sm, C_SUBTEXT)
        txt(f"Ban co: {BOARD_SIZE}x{BOARD_SIZE}", self.font_sm, C_SUBTEXT)

        if self.last_result:
            r = self.last_result
            y += 10
            pygame.draw.line(self.screen, C_SUBTEXT,
                             (x, y), (x + PANEL_WIDTH - 30, y), 1)
            y += 6
            txt("Nuoc di gan nhat:", self.font_sm, C_SUBTEXT)
            txt(f"  Move : {r.move}", self.font_sm)
            txt(f"  Value: {r.value}", self.font_sm)
            txt(f"  States: {r.states:,}", self.font_sm)
            txt(f"  Time : {r.elapsed:.3f}s", self.font_sm)

        if self.log:
            y += 6
            pygame.draw.line(self.screen, C_SUBTEXT,
                             (x, y), (x + PANEL_WIDTH - 30, y), 1)
            y += 6
            txt("Log:", self.font_sm, C_SUBTEXT)
            for line in self.log[-5:]:
                short = line[:36] + (">" if len(line) > 36 else "")
                txt(short, self.font_sm, (170, 170, 185))
        self.btn_new.draw(self.screen)
        self.btn_toggle.draw(self.screen)
        self.btn_mode.draw(self.screen)
        self.btn_depth_down.draw(self.screen)
        self.btn_depth_up.draw(self.screen)
        lbl = self.font_sm.render("Chinh do sau AI:", True, C_SUBTEXT)
        self.screen.blit(lbl, (x, WINDOW_H - 100))