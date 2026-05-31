"""
Mini Dungeon RPG - Terminal Edition
"""
import random
import os
import time

# ── ANSI Colors ──────────────────────────────────────────────
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def clr(text, color): return f"{color}{text}{RESET}"
def bold(text):       return f"{BOLD}{text}{RESET}"

# ── Map ───────────────────────────────────────────────────────
MAP_W, MAP_H = 16, 8
ROOMS = ["entrance", "forest", "cave", "ruins", "dungeon", "boss"]

def make_map():
    grid = [["." for _ in range(MAP_W)] for _ in range(MAP_H)]
    # walls
    for y in range(MAP_H):
        grid[y][0] = grid[y][MAP_W-1] = "#"
    for x in range(MAP_W):
        grid[0][x] = grid[MAP_H-1][x] = "#"
    # random walls
    for _ in range(18):
        x, y = random.randint(1, MAP_W-2), random.randint(1, MAP_H-2)
        grid[y][x] = "#"
    # enemies (E) and items (*)
    for _ in range(5):
        while True:
            x, y = random.randint(1, MAP_W-2), random.randint(1, MAP_H-2)
            if grid[y][x] == ".":
                grid[y][x] = "E"; break
    for _ in range(3):
        while True:
            x, y = random.randint(1, MAP_W-2), random.randint(1, MAP_H-2)
            if grid[y][x] == ".":
                grid[y][x] = "*"; break
    # boss
    while True:
        x, y = random.randint(MAP_W-4, MAP_W-2), random.randint(1, MAP_H-2)
        if grid[y][x] == ".":
            grid[y][x] = "B"; break
    # exit
    while True:
        x, y = random.randint(MAP_W-4, MAP_W-2), random.randint(1, MAP_H-2)
        if grid[y][x] == ".":
            grid[y][x] = "X"; break
    # player start
    px, py = 1, 1
    grid[py][px] = "@"
    return grid, px, py

def draw_map(grid, px, py):
    legend = {
        "#": clr("█", GRAY),
        ".": clr("·", GRAY),
        "@": clr("@", CYAN),
        "E": clr("E", RED),
        "*": clr("*", YELLOW),
        "B": clr("B", RED),
        "X": clr("X", GREEN),
    }
    print()
    for y, row in enumerate(grid):
        print("  " + "".join(legend.get(c, c) for c in row))
    print()

# ── Enemies ───────────────────────────────────────────────────
ENEMIES = [
    {"name": "Slime",   "hp": 8,  "atk": 3,  "def": 0, "xp": 10, "gold": 5},
    {"name": "Goblin",  "hp": 12, "atk": 5,  "def": 1, "xp": 20, "gold": 10},
    {"name": "Orc",     "hp": 20, "atk": 8,  "def": 2, "xp": 35, "gold": 20},
    {"name": "Dragon",  "hp": 40, "atk": 14, "def": 4, "xp": 100,"gold": 50},  # boss
]

def make_enemy(is_boss=False):
    e = dict(ENEMIES[3] if is_boss else random.choice(ENEMIES[:3]))
    e["max_hp"] = e["hp"]
    return e

# ── Player ────────────────────────────────────────────────────
def make_player(name):
    return {
        "name": name, "hp": 30, "max_hp": 30,
        "atk": 6, "def": 1, "xp": 0, "level": 1,
        "gold": 0, "potions": 2,
        "xp_next": 30,
    }

def hp_bar(hp, max_hp, width=16):
    filled = int(hp / max_hp * width)
    bar = "█" * filled + "░" * (width - filled)
    color = GREEN if hp / max_hp > 0.5 else (YELLOW if hp / max_hp > 0.25 else RED)
    return clr(f"[{bar}]", color) + f" {hp}/{max_hp}"

def show_status(p):
    print(f"\n  {clr(p['name'], CYAN)} " +
          f"Lv.{clr(str(p['level']), YELLOW)}  " +
          f"HP {hp_bar(p['hp'], p['max_hp'])}  " +
          f"ATK:{clr(str(p['atk']), RED)} DEF:{clr(str(p['def']), BLUE)}  " +
          f"XP:{p['xp']}/{p['xp_next']}  " +
          f"Gold:{clr(str(p['gold']), YELLOW)}  " +
          f"Potions:{clr(str(p['potions']), GREEN)}")

def level_up(p):
    p["level"] += 1
    p["xp_next"] = int(p["xp_next"] * 1.8)
    p["max_hp"] += 8
    p["hp"] = p["max_hp"]
    p["atk"] += 2
    p["def"] += 1
    print(clr(f"\n  ★ LEVEL UP! → Lv.{p['level']}  HP↑  ATK↑  DEF↑", YELLOW))

# ── Combat ────────────────────────────────────────────────────
def combat(p, enemy):
    print(f"\n  {clr('⚔ BATTLE', RED)} {clr(enemy['name'], RED)} が現れた！")
    time.sleep(0.4)
    while True:
        print(f"\n  {clr(p['name'], CYAN)}: HP {hp_bar(p['hp'], p['max_hp'])}")
        print(f"  {clr(enemy['name'], RED)}: HP {hp_bar(enemy['hp'], enemy['max_hp'])}")
        print(f"  行動: {bold('[a]')}ttack  {bold('[p]')}otion({p['potions']})  {bold('[r]')}un")
        cmd = input("  > ").strip().lower()

        if cmd == "a":
            dmg = max(1, p["atk"] - enemy["def"] + random.randint(-2, 2))
            enemy["hp"] -= dmg
            print(clr(f"  → {dmg} ダメージ！", GREEN))
            if enemy["hp"] <= 0:
                xp, gold = enemy["xp"], enemy["gold"]
                p["xp"] += xp; p["gold"] += gold
                print(clr(f"  {enemy['name']} を倒した！  +{xp}XP  +{gold}G", YELLOW))
                if p["xp"] >= p["xp_next"]:
                    level_up(p)
                return "win"

        elif cmd == "p":
            if p["potions"] > 0:
                heal = 15
                p["hp"] = min(p["max_hp"], p["hp"] + heal)
                p["potions"] -= 1
                print(clr(f"  ポーションを使った。+{heal}HP", GREEN))
            else:
                print(clr("  ポーションがない！", RED)); continue

        elif cmd == "r":
            if random.random() < 0.5:
                print(clr("  逃げた！", CYAN)); return "ran"
            else:
                print(clr("  逃げられなかった！", RED))
        else:
            continue

        # enemy turn
        edm = max(1, enemy["atk"] - p["def"] + random.randint(-2, 2))
        p["hp"] -= edm
        print(clr(f"  {enemy['name']} の攻撃！ {edm} ダメージ！", RED))
        if p["hp"] <= 0:
            return "dead"

# ── Item pickup ───────────────────────────────────────────────
def pick_item(p):
    roll = random.random()
    if roll < 0.4:
        p["potions"] += 1
        print(clr("  ポーション を手に入れた！", GREEN))
    elif roll < 0.7:
        g = random.randint(8, 25)
        p["gold"] += g
        print(clr(f"  {g} ゴールド を拾った！", YELLOW))
    elif roll < 0.9:
        p["atk"] += 1
        print(clr("  武器を強化した！ ATK+1", RED))
    else:
        p["def"] += 1
        print(clr("  鎧を手に入れた！ DEF+1", BLUE))

# ── Main loop ─────────────────────────────────────────────────
def clear(): os.system("cls" if os.name == "nt" else "clear")

def intro():
    clear()
    title = r"""
    ╔══════════════════════════════════╗
    ║   M I N I   D U N G E O N  RPG  ║
    ╚══════════════════════════════════╝
    """
    print(clr(title, CYAN))
    print("  操作: w/a/s/d で移動  |  X でゴール  |  E で戦闘\n")
    name = input(clr("  冒険者の名前を入力してください: ", YELLOW)).strip() or "勇者"
    return name

def main():
    name = intro()
    p = make_player(name)
    grid, px, py = make_map()
    boss_beaten = False

    clear()
    print(clr(f"\n  ようこそ、{name}！ダンジョンへ！", CYAN))
    print(clr("  操作: w/a/s/d=移動  q=終了", GRAY))

    while True:
        draw_map(grid, px, py)
        show_status(p)

        cmd = input(clr("\n  移動(wasd) / q=終了 > ", WHITE)).strip().lower()
        if cmd == "q":
            print(clr("\n  冒険を終了します。またね！\n", CYAN)); break

        dx, dy = 0, 0
        if   cmd == "w": dy = -1
        elif cmd == "s": dy =  1
        elif cmd == "a": dx = -1
        elif cmd == "d": dx =  1
        else: continue

        nx, ny = px + dx, py + dy
        if not (0 <= nx < MAP_W and 0 <= ny < MAP_H): continue
        cell = grid[ny][nx]
        if cell == "#": continue

        # move
        grid[py][px] = "."
        grid[ny][nx] = "@"
        px, py = nx, ny
        clear()

        if cell == "E":
            result = combat(p, make_enemy())
            if result == "dead":
                print(clr("\n  ☠ あなたは倒れた... GAME OVER\n", RED))
                break
            input(clr("\n  [Enter] で続ける...", GRAY))
            clear()

        elif cell == "*":
            print(clr("\n  アイテムを発見！", YELLOW))
            pick_item(p)
            input(clr("  [Enter] で続ける...", GRAY))
            clear()

        elif cell == "B":
            if not boss_beaten:
                print(clr("\n  !! ボスが現れた !!  逃げることはできない！", RED))
                time.sleep(0.5)
                result = combat(p, make_enemy(is_boss=True))
                if result == "dead":
                    print(clr("\n  ☠ ボスに敗れた... GAME OVER\n", RED))
                    break
                boss_beaten = True
                p["gold"] += 50
                print(clr("\n  ボスを倒した！ +50G  出口(X)を目指せ！", YELLOW))
            else:
                print(clr("\n  ボスはもう倒れている。", GRAY))
            input(clr("  [Enter] で続ける...", GRAY))
            clear()

        elif cell == "X":
            if boss_beaten:
                clear()
                print(clr(f"""
  ╔═══════════════════════════════════╗
  ║         🎉 CONGRATULATIONS!       ║
  ╚═══════════════════════════════════╝
  {name} はダンジョンを制覇した！
  最終レベル: {p['level']}   獲得ゴールド: {p['gold']}G
""", YELLOW))
                break
            else:
                print(clr("\n  ボスを倒さないと出口は開かない！", RED))
                grid[py][px] = "X"
                px -= dx; py -= dy
                grid[py][px] = "@"
                input(clr("  [Enter] で続ける...", GRAY))
                clear()

if __name__ == "__main__":
    main()
