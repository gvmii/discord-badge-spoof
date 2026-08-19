# discord-badge-spoof

Farms Discord's new profile badges (the game variety one, the hours one) by making Discord's game detection genuinely think fake games are running. This works even on Vanilla Discord.

### I know this way of doing is is completely disgusting and overengineered, but I wasn't sure what it would take to make Discord detect them. You could remove half of the code of this repo and it would still work. My bad!

## How it works

Discord figures out what you're "playing" by matching running processes against its internal detectable-games list, and it matches on two things: the **executable name** and the **window title**. So the farm:

1. copies your `pythonw.exe` into `.fake_games/` renamed as a real game's exe (say `celeste.exe`)
2. launches that process running a tiny Tk window whose title is the game's name ("Celeste")
3. parks the window **off-screen** at `+10000+10000` — you never see it, Discord's observer sees it fine
4. Discord detects it as the real game: it shows in your status, shows up under registered games, and the badge counters credit it on Discord's ~24h analytics cycle

No Equicord, no Vencord, no JS, no fingerprints, no touching your token. The whole thing is Discord open + this one script.

## Running it

You need Python 3.10+ on Windows. The script needs `pythonw.exe` and finds it automatically (next to the python you're running it with, on PATH, or in the standard install folders).

```bash
# the full roster, 8 minutes per game
python badge_farm.py --each 8

# longer sessions — better if you're after the playtime-hours badge
python badge_farm.py --each 30

# just specific games
python badge_farm.py --games celeste.exe --each 30
python badge_farm.py --games "hollow_knight.exe,celeste.exe" --each 30

# fast cycling, in seconds per game (handy for checking a game shows up quickly)
python badge_farm.py --each-seconds 30

# one game, one session, then exit
python badge_farm.py --once celeste.exe --each 30

# see the whole roster
python badge_farm.py --list
```

Flags: `--each` (minutes per game, default 8), `--each-seconds` (overrides `--each`), `--games` (comma-separated exe names), `--once` (single game then quit), `--rounds` (how many full passes; 0 = forever), `--list` (print the roster).

## Notes

The game list (`GAMES` in `badge_farm.py`) is hand-picked from Discord's own detectable-games list, mostly indie stuff. Games that have no cover art in Discord's DB got dropped; they don't show a preview and I thought they wouldn't count (turns out they do)

Progress is saved to `.badge_farm_state.json` so it picks up where it left off. Fake processes get cleaned up on exit, and `.fake_games/` rebuilds itself. And remember: badges update on Discord's own cycle (about a day), so results aren't instant.

## The fine print

This is against Discord's ToS, but it's mostly legit. Use it on an account you're okay losing. Detection internals are Discord's to change, so the exe/title trick can break on a client update.