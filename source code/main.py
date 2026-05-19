import sys


def main():
    if "--benchmark" in sys.argv:
        from benchmark import run_benchmark
        depths = [1, 2, 3]
        for arg in sys.argv[1:]:
            if arg.startswith("--depths="):
                depths = list(map(int, arg.split("=")[1].split(",")))
        run_benchmark(depths)
    else:
        from ui import GameUI
        game = GameUI()
        game.run()


if __name__ == "__main__":
    main()
