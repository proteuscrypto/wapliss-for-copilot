#!/usr/bin/env python3
"""Validate Wapliss WhatsApp for GitHub Copilot (Agent Plugins 1.0).

Mirrors the awesome-copilot external plugin quality gates (Agent Plugins v1.0.0 manifest
compliance) plus mcp.json and Agent Skills checks. Created by netdigitaltech.

  python3 scripts/validate.py          # static checks
  python3 scripts/validate.py --live   # + public endpoint and OAuth metadata
"""
import json, pathlib, re, struct, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
FAIL = []
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MCP_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
ALLOWED = {"$schema", "name", "version", "description", "author", "homepage", "repository", "license", "keywords", "extensions"}
NAME_RE = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
TOOLS = {"send_text_message", "send_image", "send_document", "send_audio", "send_video", "send_location",
         "send_contact", "send_poll", "forward_messages", "get_chats", "get_chat_history", "get_message",
         "get_last_incoming_messages", "get_last_outgoing_messages", "get_group", "get_account_status"}


def check(name, cond, extra=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond or extra == "" else f"  -> {extra}"))
    if not cond:
        FAIL.append(name)


def static():
    m = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    check("plugin.json at the plugin root", (ROOT / "plugin.json").is_file())
    check("$schema is Agent Plugins 1.0.0", m.get("$schema") == PLUGIN_SCHEMA, m.get("$schema"))
    check("only Agent Plugins 1.0 top-level fields", set(m) <= ALLOWED, set(m) - ALLOWED)
    name = m.get("name", "")
    check("name 1-64 chars, lowercase, no -- or ..", 1 <= len(name) <= 64 and bool(NAME_RE.match(name)), name)
    check("version is SemVer", bool(SEMVER.match(m.get("version", ""))), m.get("version"))
    check("description present", len(m.get("description", "").strip()) >= 40)
    a = m.get("author", {})
    check("author.name netdigitaltech, only name/email/url strings",
          a.get("name") == "netdigitaltech" and set(a) <= {"name", "email", "url"} and all(isinstance(v, str) for v in a.values()), a)
    check("no personal email in the manifest", "email" not in a)
    check("repository is an HTTPS GitHub URL", str(m.get("repository", "")).startswith("https://github.com/"))
    check("license MIT + LICENSE file", m.get("license") == "MIT" and (ROOT / "LICENSE").is_file())
    kw = m.get("keywords", [])
    check("keywords are lowercase hyphenated tags", bool(kw) and all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", k) for k in kw), kw)

    mc = json.loads((ROOT / "mcp.json").read_text(encoding="utf-8"))
    check("mcp.json $schema matches the manifest version", mc.get("$schema") == MCP_SCHEMA, mc.get("$schema"))
    check("mcp.json has only $schema and mcpServers", set(mc) == {"$schema", "mcpServers"}, set(mc))
    srv = mc.get("mcpServers", {}).get("wapliss", {})
    check("server wapliss: streamable-http https://wapliss.com/mcp/v1",
          srv.get("type") == "streamable-http" and srv.get("url") == "https://wapliss.com/mcp/v1", srv)
    check("server entry uses only type/url (no headers, no secrets)", set(srv) <= {"type", "url", "extensions"}, set(srv))
    check("no MCP config inline in plugin.json", "mcpServers" not in json.dumps(m))

    icon = ROOT / "assets" / "icon.png"
    if icon.is_file():
        b = icon.read_bytes()
        ok = b[:8] == b"\x89PNG\r\n\x1a\n"
        w, h = struct.unpack(">II", b[16:24]) if ok else (0, 0)
        check("assets/icon.png is a square PNG >= 256 px", ok and w == h and w >= 256, f"{w}x{h}")

    skills = [d for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file()]
    check("one skill in skills/", len(skills) == 1, [d.name for d in skills])
    for d in skills:
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        check(f"{d.name}: YAML frontmatter", bool(fm))
        if fm:
            name_m = re.search(r"^name:\s*(\S+)", fm.group(1), re.M)
            check(f"{d.name}: name matches directory", bool(name_m) and name_m.group(1) == d.name)
            check(f"{d.name}: description present", "description:" in fm.group(1))
        missing = [t for t in TOOLS if f"`{t}`" not in text]
        check(f"{d.name}: documents all 16 tools", not missing, missing)

    mk = json.loads((ROOT / ".github/plugin/marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in mk.get("plugins", []) if p.get("name") == name), {})
    check("marketplace.json lists the plugin", bool(entry))
    check("marketplace version == plugin version", entry.get("version") == m.get("version"), (entry.get("version"), m.get("version")))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("README: install commands and creator", "copilot plugin install proteuscrypto/wapliss-for-copilot" in readme and "netdigitaltech" in readme)


def live():
    url = "https://wapliss.com/mcp/v1"
    req = urllib.request.Request(url, data=b'{"jsonrpc":"2.0","id":1,"method":"tools/list"}', method="POST",
                                 headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    try:
        urllib.request.urlopen(req, timeout=30)
        check("live: unauthenticated -> 401", False, "200")
    except urllib.error.HTTPError as e:
        www = e.headers.get("WWW-Authenticate", "")
        check("live: unauthenticated -> 401", e.code == 401, e.code)
        check("live: WWW-Authenticate resource_metadata for /mcp/v1", "oauth-protected-resource/mcp/v1" in www, www)
    with urllib.request.urlopen("https://wapliss.com/.well-known/oauth-authorization-server", timeout=30) as r:
        meta = json.loads(r.read())
    check("live: dynamic client registration endpoint", bool(meta.get("registration_endpoint")))
    check("live: PKCE S256", "S256" in meta.get("code_challenge_methods_supported", []))


if __name__ == "__main__":
    static()
    if "--live" in sys.argv:
        live()
    print("\nRESULT:", "ALL PASS" if not FAIL else f"{len(FAIL)} FAILED")
    sys.exit(1 if FAIL else 0)
