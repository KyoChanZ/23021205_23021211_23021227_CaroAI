import csv
import os
import numpy as np
from board import Board
from ai import best_move_minimax, best_move_alphabeta
from config import HUMAN, AI, EMPTY


def make_board(grid_list: list[list[int]]) -> Board:
    b = Board(9)
    for r, row in enumerate(grid_list):
        for c, val in enumerate(row):
            if val != EMPTY:
                b.grid[r][c] = val
                b.move_history.append((r, c))
    return b

def state_opening():
    b = Board(9)
    b.place(4, 4, HUMAN)
    return b, "State 1: Đầu ván (1 quân)"

def state_midgame():
    g = [[0]*9 for _ in range(9)]
    moves = [(4,4,1),(4,5,-1),(3,4,1),(3,5,-1),(5,4,1),(5,5,-1),(4,3,1),(4,6,-1)]
    b = Board(9)
    for r,c,p in moves:
        b.place(r, c, p)
    return b, "State 2: Giữa ván"

def state_ai_winning():
    b = Board(9)
    for mv in [(4,4,-1),(4,5,-1),(4,6,-1),(3,3,1),(5,5,1)]:
        b.place(*mv)
    return b, "State 3: AI sắp thắng (3 quân liên tiếp)"

def state_human_winning():
    b = Board(9)
    for mv in [(4,4,1),(4,5,1),(4,6,1),(3,3,-1),(2,2,-1)]:
        b.place(*mv)
    return b, "State 4: HUMAN sắp thắng, AI cần chặn"

def state_balanced():
    b = Board(9)
    for mv in [(4,4,1),(4,5,-1),(3,4,1),(3,5,-1),
               (2,4,1),(5,5,-1),(4,3,1),(3,6,-1),
               (4,6,-1),(5,4,1)]:
        b.place(*mv)
    return b, "State 5: Cân bằng, hai bên đều tấn công"

def state_crowded():
    b = Board(9)
    pattern = [
        (2,2,1),(2,3,-1),(2,4,1),(2,5,-1),
        (3,2,-1),(3,3,1),(3,4,-1),(3,5,1),
        (4,2,1),(4,3,-1),(4,4,1),(4,5,-1),
        (5,2,-1),(5,3,1),(5,4,-1),(5,5,1),
    ]
    for r,c,p in pattern:
        b.place(r, c, p)
    return b, "State 6: Nhiều nước đi (bàn cờ dày đặc)"


ALL_STATES = [
    state_opening,
    state_midgame,
    state_ai_winning,
    state_human_winning,
    state_balanced,
    state_crowded,
]

def run_benchmark(depths: list[int] = [1, 2, 3], output_dir="."):
    print("=" * 80)
    print("   BENCHMARK: Minimax vs Alpha-Beta Pruning")
    print("=" * 80)

    all_rows = []   

    for state_fn in ALL_STATES:
        board, label = state_fn()
        print(f"\n{'─'*60}")
        print(f"  {label}")
        print(f"{'─'*60}")
        print(board)
        print()

        header = (f"{'Depth':>6} | {'Algorithm':>12} | "
                  f"{'Move':>10} | {'Value':>8} | "
                  f"{'States':>10} | {'Time(s)':>9} | "
                  f"{'Same?':>6} | {'Reduce%':>8} | {'Speedup':>7}")
        print(header)
        print("-" * len(header))

        state_rows = []

        for d in depths:
            mm = best_move_minimax(board.copy(), d)
            ab = best_move_alphabeta(board.copy(), d)

            same     = mm.move == ab.move
            reduce_  = (1 - ab.states / mm.states) * 100 if mm.states else 0
            speedup  = mm.elapsed / ab.elapsed if ab.elapsed > 0 else float("inf")

            for res, is_ab in [(mm, False), (ab, True)]:
                print(f"{d:>6} | {res.algorithm:>12} | "
                      f"{str(res.move):>10} | {res.value:>8} | "
                      f"{res.states:>10,} | {res.elapsed:>9.4f} | "
                      f"{'  OK' if same else '  --':>6} | "
                      f"{reduce_:>7.1f}% | {speedup:>6.2f}x")

                row = {
                    "state":      label,
                    "depth":      d,
                    "algorithm":  res.algorithm,
                    "move":       str(res.move),
                    "value":      res.value,
                    "states":     res.states,
                    "time_s":     round(res.elapsed, 6),
                    "same_move":  "Yes" if same else "No",
                    "reduction%": round(reduce_, 2),
                    "speedup_x":  round(speedup, 2),
                }
                state_rows.append(row)
                all_rows.append(row)

        for d in depths:
            mm_r = next(r for r in state_rows if r["depth"]==d and r["algorithm"]=="Minimax")
            ab_r = next(r for r in state_rows if r["depth"]==d and r["algorithm"]=="Alpha-Beta")
            print(f"  [d={d}] Cung nuoc di: {'OK' if mm_r['same_move']=='Yes' else 'KHAC'}  "
                  f"Giam trang thai: {ab_r['reduction%']}%  "
                  f"Tang toc: {ab_r['speedup_x']}x")

    print("\n" + "=" * 80)
    print("   TONG HOP: Trung binh ty le giam trang thai theo do sau")
    print("=" * 80)
    for d in depths:
        ab_rows = [r for r in all_rows if r["depth"]==d and r["algorithm"]=="Alpha-Beta"]
        mm_rows = [r for r in all_rows if r["depth"]==d and r["algorithm"]=="Minimax"]
        reductions = [r["reduction%"] for r in ab_rows]
        speedups   = [r["speedup_x"]  for r in ab_rows]
        same_n     = sum(1 for r in ab_rows if r["same_move"]=="Yes")
        avg_red = np.mean(reductions) if reductions else 0
        avg_spd = np.mean(speedups)   if speedups   else 0
        print(f"  Depth {d}: Giam {avg_red:.1f}% trang thai | "
              f"Tang toc {avg_spd:.2f}x | "
              f"Cung nuoc di: {same_n}/{len(ab_rows)}")

    csv_path = os.path.join(output_dir, "benchmark_results.csv")
    fields = ["state","depth","algorithm","move","value",
              "states","time_s","same_move","reduction%","speedup_x"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)

    print(f"\n[OK] Luu ket qua ra: {csv_path}")
    print("Mo file nay bang Excel de dan vao bao cao!")
    print("\nBenchmark hoan tat.")
    return all_rows


if __name__ == "__main__":
    import sys
    depths = [1, 2, 3]
    for arg in sys.argv[1:]:
        if arg.startswith("--depths="):
            depths = list(map(int, arg.split("=")[1].split(",")))
    run_benchmark(depths=depths, output_dir=".")