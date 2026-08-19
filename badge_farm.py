"""Fake windowed game processes so Discord's game detection sees them as real games.

For each game in the roster, a copy of pythonw.exe is staged under .fake_games/
renamed as the game's executable and launched running a tiny off-screen Tk
window titled with the game's name. Discord's observer matches processes by
executable name + window title and reports them as detected games, which feeds
the profile badges on Discord's ~24h analytics cycle.

Usage:
    python badge_farm.py --each 8
    python badge_farm.py --games celeste.exe --each 30
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STAGE_DIR = SCRIPT_DIR / ".fake_games"
CURRENT_FILE = STAGE_DIR / "current.json"
STATE_FILE = SCRIPT_DIR / ".badge_farm_state.json"


def find_pythonw() -> Path | None:
    exe = Path(sys.executable).resolve()
    if exe.name.lower() == "pythonw.exe":
        return exe
    candidate = exe.with_name("pythonw.exe")
    if candidate.exists():
        return candidate
    for p in shutil.which("pythonw") or []:
        if p:
            q = Path(p)
            if q.exists():
                return q
    base = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python"
    if base.is_dir():
        for d in sorted(base.glob("Python3*"), reverse=True):
            c = d / "pythonw.exe"
            if c.exists():
                return c
    return None


PYTHONW = find_pythonw()

GAMES = [
    ("1129504660135366739", "NEEDY STREAMER OVERLOAD", "needy girl overdose/windose.exe"),
    ("447509870510473216", "Yume Nikki", "yumenikki/rpg_rt.exe"),
    ("1402416901551816837", "Celeste", "celeste.exe"),
    ("1165771599031566346", "The Coffin of Andy and Leyley", "the coffin of andy and leyley/game.exe"),
    ("1124352279512895578", "Doki Doki Literature Club Plus!", "doki doki literature club plus/doki doki literature club plus.exe"),
    ("363409849859571722", "Undertale", "undertale.exe"),
    ("1379852275454836837", "DELTARUNE", "deltarune/deltarune.exe"),
    ("451544770876145664", "OneShot", "oneshot.exe"),
    ("1124351759591161996", "OMORI", "omori/omori.exe"),
    ("484572816977428490", "LISA", "lisa.exe"),
    ("1124355546561130496", "Corpse Party", "corpse party/corpseparty.exe"),
    ("1124354212495642698", "Mad Father", "mad father/game.exe"),
    ("1124355558682677268", "Misao: Definitive Edition", "misao/game.exe"),
    ("1124355525182767144", "The Witch's House MV", "the witch's house mv/game.exe"),
    ("496761451738955804", "Fran Bow", "fran bow.exe"),
    ("1124354662825476156", "Frog Fractions: Game of the Decade Edition", "frog fractions game of the decade edition/frog fractions game of the decade edition.exe"),
    ("1124354183814991963", "Hypnospace Outlaw", "hypnospace outlaw/hypnos.exe"),
    ("1124351719950798848", "Noita", "noita/noita.exe"),
    ("1124352106107777134", "Rain World", "rain world/rainworld.exe"),
    ("1124354595276206181", "SIGNALIS", "signalis/signalis.exe"),
    ("1124353032528871474", "Pathologic 2", "pathologic/pathologic.exe"),
    ("1124352654575939624", "Everhood", "everhood/everhood.exe"),
    ("363431029484027904", "Hollow Knight", "hollow_knight.exe"),
    ("462829880615370762", "To the Moon", "to the moon.exe"),
    ("451541089912881162", "Night in the Woods", "night in the woods.exe"),
    ("1124353234715299880", "Oxenfree", "oxenfree/oxenfree.exe"),
    ("1124351860376096858", "Outer Wilds", "outer wilds/outerwilds.exe"),
    ("696065774061879446", "Return of the Obra Dinn", "obradinn/obradinn.exe"),
    ("504073562785579018", "The Beginner's Guide", "beginnersguide.exe"),
    ("450401603669721089", "The Stanley Parable", "the stanley parable/stanley.exe"),
    ("876570707306381342", "Disco Elysium", "disco elysium/disco.exe"),
    ("1124352142589833286", "Pizza Tower", "pizza tower/pizzatower.exe"),
    ("1124351888737972295", "Katana ZERO", "katana zero/katana zero.exe"),
    ("1124351726158352456", "Inscryption", "inscryption/inscryption.exe"),
    ("480963716934795264", "Danganronpa: Trigger Happy Havoc", "danganronpa.exe"),
    ("503578473227354112", "Danganronpa 2: Goodbye Despair", "dr2_us.exe"),
    ("1129504315137085523", "Danganronpa V3: Killing Harmony", "danganronpa v3 killing harmony/dangan3win.exe"),
    ("505520072870199335", "VA-11 HALL-A", "va-11 hall a.exe"),
    ("504052730042646579", "STEINS;GATE", "steins;gate/game.exe"),
    ("363430002181668864", "Cuphead", "cuphead.exe"),
    ("1402418344912752671", "Terraria", "terraria.exe"),
    ("1402418342127472751", "Hades", "hades.exe"),
    ("1124351854831222945", "ULTRAKILL", "ultrakill/ultrakill.exe"),
    ("1124352518533697646", "Library Of Ruina", "library of ruina/libraryofruina.exe"),
    ("1309730178863464458", "ATLYSS", "atlyss/atlyss.exe"),
    ("1161090883496714250", "Pseudoregalia", "win64/pseudoregalia-win64-shipping.exe"),
    ("1245451690459533334", "Looking Up I See Only A Ceiling", "looking up i see only a ceiling/luisoac.exe"),
    ("1124360227626692608", "If Found", "if found/iffound.exe"),
    ("1129504116796837939", "A Dance of Fire and Ice", "a dance of fire and ice/a dance of fire and ice.exe"),
    ("1440552261897031690", "Z.A.T.O. // I Love the World and Everything In It", "z.a.t.o.  i love the world and everything in it/zato.exe"),
    ("1129504149915050055", "Muse Dash", "muse dash/musedash.exe"),
    ("1402416657674277097", "Transistor", "transistor.exe"),
    ("358420454764969994", "The Binding of Isaac: Rebirth", "isaac-ng.exe"),
    ("1402418087793528862", "Risk of Rain 2", "risk of rain 2.exe"),
    ("363413202090065920", "Enter the Gungeon", "enter the gungeon/etg.exe"),
    ("450024058348634112", "Wizard of Legend", "wizardoflegend.exe"),
    ("1402418571715543120", "Bloons TD 6", "bloonstd6.exe"),
    ("1402418440685486130", "Among Us", "among us/among us.exe"),
    ("1295159185926783037", "WEBFISHING", "webfishing/webfishing.exe"),
    ("1124359620673163344", "YUMENIKKI -DREAM DIARY-", "yumenikki -dream diary-/yumenikki.exe"),
    ("1124353185335758948", "Milk outside a bag of milk outside a bag of milk", "windows-i686/pmkm2.exe"),
    ("1124352888014127124", "WORLD OF HORROR", "woh/worldofhorror.exe"),
    ("1124354493094580414", "FAITH", "faith/faith.exe"),
    ("1124353797687365713", "Iron Lung", "iron lung/iron lung.exe"),
    ("1124354836226396170", "Lost in Vivo", "lost in vivo/liv.exe"),
    ("501209864333164546", "Darkwood", "darkwood.exe"),
    ("425748259408183306", "Cry of Fear", "cof.exe"),
    ("1253862151660240916", "Stay Out of the House", "stay out of the house/stay out of the house.exe"),
    ("491427187442974749", "Pony Island", "ponyisland.exe"),
    ("1124355959918182400", "The Hex", "the hex/thehex.exe"),
    ("1129504726409543760", "There Is No Game: Wrong Dimension", "there is no game - wrong dimension/ting.exe"),
    ("1124355743341101106", "Kentucky Route Zero", "kentuckyroutezero/kentuckyroutezero.exe"),
    ("1124360294009946112", "NORCO", "norco/norco.exe"),
    ("1124359183517634651", "Dropsy", "dropsy/dropsy.exe"),
    ("1129504432829235365", "Sally Face", "sally face/sally face.exe"),
    ("1124352639883296878", "Little Misfortune", "little misfortune/little misfortune.exe"),
    ("1124352914157220000", "A Short Hike", "a short hike/ashorthike.exe"),
    ("1124352877381562479", "Donut County", "donut county/donutcounty.exe"),
    ("1124355043689254953", "Wandersong", "pc/wandersong.exe"),
    ("1124356150238920854", "Chicory: A Colorful Tale", "pc/chicory.exe"),
    ("1124354181772361728", "Gorogoa", "gorogoa/gorogoa.exe"),
    ("1124355120415658065", "Manifold Garden", "manifold garden/manifoldgarden.exe"),
    ("1124352039397380096", "Superliminal", "superliminal/superliminalsteam.exe"),
    ("451550717673472030", "FEZ", "fez.exe"),
    ("496540068442537984", "Braid", "braid.exe"),
    ("425441571656433664", "Hyper Light Drifter", "hyperlightdrifter.exe"),
    ("1124354147664281601", "Her Story", "her story/herstory.exe"),
    ("1124355294600904704", "Gone Home", "gone home/gonehome.exe"),
    ("1124352424275099669", "What Remains of Edith Finch", "win64/finchgame.exe"),
    ("1124357391341867068", "Heaven's Vault", "heaven's vault/heaven's vault.exe"),
    ("1124359975712608256", "The House in Fata Morgana", "the house in fata morgana/fata.exe"),
    ("1124355889059610654", "Zero Escape: Zero Time Dilemma", "zero escape/zero escape.exe"),
    ("1124352486308855898", "One Step From Eden", "one step from eden/osfe.exe"),
    ("1124351844743917688", "Loop Hero", "loop hero/loop hero.exe"),
    ("1176930144091373578", "The Last Faith", "the last faith/the last faith.exe"),
    ("505506583304732695", "Touhou 10: Mountain of Faith", "th10.exe"),
    ("1124353810505154590", "SEPTEMBER 1999", "september1999/september1999.exe"),
]


def norm_path(p: Path) -> str:
    return str(p).replace("\\", "/").lower()


def write_window_script(title: str) -> Path:
    script = STAGE_DIR / "tkwindow.py"
    script.write_text(
        "import tkinter as tk\n"
        "root = tk.Tk()\n"
        f"root.title({title!r})\n"
        'root.geometry("300x100+10000+10000")\n'
        "root.attributes('-topmost', True)\n"
        "root.mainloop()\n",
        encoding="utf-8",
    )
    return script


def stage_exe(exe: str) -> Path:
    STAGE_DIR.mkdir(exist_ok=True)
    target = STAGE_DIR / exe.replace("/", "\\")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        try:
            os.link(PYTHONW, target)
        except OSError:
            shutil.copy2(PYTHONW, target)
    return target


def kill_path(path: Path) -> None:
    quoted = str(path).replace("'", "''")
    ps = (
        "Get-Process -ErrorAction SilentlyContinue | ForEach-Object { "
        f"try {{ if ($_.Path -eq '{quoted}') {{ "
        "Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue "
        "} } catch { } }"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, timeout=60)


def cleanup_staged() -> None:
    if not STAGE_DIR.is_dir():
        return
    for exe in STAGE_DIR.rglob("*.exe"):
        kill_path(exe)


def write_current(game: tuple, pid: int, exe_path: Path) -> None:
    gid, name, exe = game
    payload = {
        "id": gid,
        "name": name,
        "exe": exe,
        "exePath": norm_path(exe_path),
        "pid": pid,
        "ts": int(time.time()),
    }
    CURRENT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_state() -> list:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    return []


def save_state(seen: list) -> None:
    STATE_FILE.write_text(json.dumps(seen, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Badge farm - fake windowed game rotation.")
    parser.add_argument("--each", type=int, default=8, help="minutes per fake game")
    parser.add_argument("--each-seconds", type=int, default=0,
                        help="seconds per fake game (overrides --each; for fast cycling)")
    parser.add_argument("--once", help="run a single named exe once then exit (testing)")
    parser.add_argument("--games",
                        help="comma-separated exe names to run (filter of the roster)")
    parser.add_argument("--rounds", type=int, default=0, help="full passes (0 = forever)")
    parser.add_argument("--list", action="store_true", help="print games and exit")
    args = parser.parse_args()

    if args.list:
        for gid, name, exe in GAMES:
            print(f"{name}  {exe}  {gid}")
        return 0

    if args.once:
        games = [g for g in GAMES if g[2].lower() == args.once.lower()] or [("", args.once, args.once)]
        args.rounds = 1
    elif args.games:
        wanted = [x.strip().lower() for x in args.games.split(",") if x.strip()]
        games = [g for g in GAMES if g[2].lower() in wanted]
        if not games:
            games = [("", wanted[0], wanted[0])]
    else:
        games = list(GAMES)

    each = max(1, args.each)
    each_sec = args.each_seconds if args.each_seconds > 0 else each * 60

    if PYTHONW is None or not PYTHONW.exists():
        print("error: could not find pythonw.exe - make sure Python for Windows is installed.")
        return 1

    print(f"{len(games)} games, {each_sec}s each")

    cleanup_staged()

    seen = load_state()
    offset = 0
    if seen:
        try:
            last = seen[-1]
            offset = (next(i for i, g in enumerate(games) if g[2] == last) + 1) % len(games)
        except (ValueError, StopIteration):
            pass

    try:
        round_no = 0
        while True:
            for gid, name, exe in games[offset:] + games[:offset]:
                seen.append(exe)
                save_state(seen)

                target = stage_exe(exe)
                script = write_window_script(name)
                print(f"[{time.strftime('%H:%M:%S')}] Launching fake game: {name} ({exe})")

                proc = subprocess.Popen([str(target), str(script)], cwd=str(STAGE_DIR))
                time.sleep(3)
                write_current((gid, name, exe), proc.pid, target)
                print(f"    pid {proc.pid}")
                time.sleep(max(1, each_sec - 3))

                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                kill_path(target)

            offset = 0
            round_no += 1
            if args.rounds and round_no >= args.rounds:
                break
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        cleanup_staged()

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
