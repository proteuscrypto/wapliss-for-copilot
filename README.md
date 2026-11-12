<p align="center">
  <img src="assets/icon.png" alt="Wapliss logo" width="120" />
</p>

<h1 align="center">Wapliss WhatsApp for GitHub Copilot</h1>

<p align="center">
  <strong>Connect your own WhatsApp to GitHub Copilot with the Wapliss MCP server.</strong><br />
  Read and summarize chats and groups, and send messages, files, locations and polls, always with your confirmation.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-25D366" alt="License: MIT" />
  <img src="https://img.shields.io/badge/MCP-2026--07--28%20%7C%202025--11--25-128C7E" alt="MCP" />
  <img src="https://img.shields.io/badge/GitHub%20Copilot-plugin-128C7E" alt="GitHub Copilot" />
  <img src="https://img.shields.io/badge/version-1.0.0-25D366" alt="Version" />
  <img src="https://img.shields.io/badge/Agent%20Plugins-1.0-24292f" alt="Agent Plugins" />
  <img src="https://img.shields.io/badge/VS%20Code-install-007ACC" alt="VS Code" />
</p>

<p align="center">
  <a href="https://wapliss.com/">Website</a> ·
  <a href="https://wapliss.com/integrations#copilot">GitHub Copilot guide</a> ·
  <a href="https://wapliss.com/integraciones#copilot">Guía en español</a> ·
  <a href="#example-prompts">Examples</a> ·
  <a href="#faq">FAQ</a> ·
  <a href="#wapliss-plugins">Other assistants</a>
</p>

---

## What is Wapliss?

[Wapliss](https://wapliss.com/), by [NetDigitalTech LLC](https://netdigitaltech.com/), is a WhatsApp gateway for AI assistants. You
link your WhatsApp number once with a QR code, authorize your assistant, and
the assistant can read your chats and groups and send WhatsApp messages for
you through a standard [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) server. A free plan is available, with no credit card required.

This repository is the official **GitHub Copilot package** of Wapliss
(Agent Plugins 1.0 package with a remote MCP server and an Agent Skill). It only points GitHub Copilot to the hosted Wapliss MCP
server; it stores no account data, messages or credentials.

## Compatibility

| Surface | How | Status |
| --- | --- | --- |
| Copilot CLI | `copilot plugin marketplace add proteuscrypto/wapliss-for-copilot` then `copilot plugin install wapliss-whatsapp@wapliss` | Works (tested with Copilot CLI 1.0.109) |
| VS Code (Copilot Chat, agent mode) | **Chat: Install Plugin from Source** → `https://github.com/proteuscrypto/wapliss-for-copilot`, or the MCP install link below | Supported (Agent Plugins 1.0) |
| GitHub Copilot app | **Customize → Plugins** → add marketplace `proteuscrypto/wapliss-for-copilot` | Supported (Agent Plugins 1.0) |
| Copilot cloud agent | Not recommended: it runs unattended and cannot complete the browser sign-in | — |

## Quick start

1. Create a free account at [wapliss.com](https://wapliss.com/) and link your
   phone once at [wapliss.com/app/connect](https://wapliss.com/app/connect).
2. Install the plugin:

   ```bash
   # Copilot CLI: add this repository as a marketplace, then install
   copilot plugin marketplace add proteuscrypto/wapliss-for-copilot
   copilot plugin install wapliss-whatsapp@wapliss
   ```

   **VS Code:** enable `chat.plugins.enabled`, run **Chat: Install Plugin from
   Source** and paste `https://github.com/proteuscrypto/wapliss-for-copilot`.
   Only the MCP server, without the skill:
   [Install in VS Code](https://vscode.dev/redirect/mcp/install?name=wapliss&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fwapliss.com%2Fmcp%2Fv1%22%7D)
   · [Install in VS Code Insiders](https://insiders.vscode.dev/redirect/mcp/install?name=wapliss&config=%7B%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fwapliss.com%2Fmcp%2Fv1%22%7D&quality=insiders).
3. When Copilot asks to authenticate the `wapliss` server, sign in to Wapliss
   in the browser and approve access (OAuth, no keys to copy).
4. In agent mode, ask: *"Show me my latest WhatsApp messages"*.

## Example prompts

| Goal | Ask  |
| --- | --- |
| Catch up | "Show me my latest WhatsApp messages" |
| Summarize a group | "Summarize what was said today in my family group" |
| Read a chat | "Read my last 20 messages with Ana and tell me what she needs" |
| Group info | "Who are the admins of the work group?" |
| Send a message | "Send 'On my way, 10 minutes' to +1 555 010 2030" |
| Send a file | "Send this PDF to Laura: https://example.com/quote.pdf" |
| Share a location | "Send the office location to the project group" |
| Run a poll | "Create a poll in the team group: Friday or Monday?" |
| Check the account | "Check my Wapliss account and today's usage" |

Tips: name the chat or group as it appears in WhatsApp, or use the number with
country code. The assistant shows you the recipient and the text before
sending when anything is ambiguous.

## What it can do (16 tools)

| Area | Tools | What they do |
| --- | --- | --- |
| Chats and groups | `get_chats`, `get_chat_history`, `get_message` | List and search your conversations, read a chat or group in order, get one message |
| Latest activity | `get_last_incoming_messages`, `get_last_outgoing_messages` | What you received or sent recently, across all chats |
| Groups | `get_group` | Name, description, admins and participants |
| Send | `send_text_message`, `send_image`, `send_document`, `send_audio`, `send_video`, `send_location`, `send_contact`, `send_poll`, `forward_messages` | Text, files by public URL, locations, contact cards, polls and forwards |
| Account | `get_account_status` | Plan, linked number, daily usage and quota |

Every tool declares MCP annotations (`readOnlyHint`, `destructiveHint`,
`idempotentHint`, `openWorldHint`). Send tools are marked destructive, so the
assistant asks for confirmation. A successful send means the message was
**queued** (with a `queue_id`), not yet delivered.

## How it works

```text
VS Code / Copilot CLI / Copilot app
        |  OAuth 2.1: discovery, dynamic client registration, PKCE S256
        v
https://wapliss.com/mcp/v1   (Streamable HTTP, MCP 2026-07-28 and 2025-11-25)
        |
Wapliss WhatsApp engine  --->  WhatsApp
```

`mcp.json` (Agent Plugins 1.0):

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
  "mcpServers": {
    "wapliss": { "type": "streamable-http", "url": "https://wapliss.com/mcp/v1" }
  }
}
```

- Protected resource metadata: `https://wapliss.com/.well-known/oauth-protected-resource/mcp/v1`
- Authorization server metadata: `https://wapliss.com/.well-known/oauth-authorization-server`
- Scopes: `wapliss:mcp`, `whatsapp:read`, `whatsapp:write`
- `/mcp/v1` serves stable English tool definitions; the plugin contains no
  credentials and no `headers`.

## Security and privacy

- **Your own account only.** The assistant can reach only the WhatsApp account
  linked to your Wapliss account, and only when you ask.
- **No credentials in the chat.** Never paste passwords, API keys, QR data or
  session data into a conversation; this package contains none either.
- **Confirmation before sending.** Ambiguous recipients or texts are confirmed
  first; bulk or unsolicited messaging is not allowed.
- **Revocable at any time** from the Wapliss dashboard.
- **Limits:** daily plan quota and 60 MCP calls per minute per user.
- [Privacy policy](https://wapliss.com/privacy-policy) ·
  [Terms of service](https://wapliss.com/terms-of-service)

## FAQ

**Is it free?** Yes, there is a free plan to start, with no credit card.

**Does it use the official WhatsApp Business Platform?** No. Wapliss links
your number as a WhatsApp linked device, like WhatsApp Web, so it works with
your personal or business number without a Meta Business account. Use it for
your own conversations and follow WhatsApp's terms.

**Can the assistant send messages on its own?** No. It only acts when you ask,
confirms ambiguous sends and refuses bulk or unsolicited messages.

**Where are my messages stored?** In your private Wapliss account, so the
assistant can read them when you ask. What the assistant reads is processed by
its AI provider. See the [privacy policy](https://wapliss.com/privacy-policy).

**Can I use several assistants at once?** Yes. Each one is authorized
separately and can be revoked separately.

**Does it need a GitHub Copilot paid plan?** No. Agent plugins and MCP
servers work on every Copilot plan, including Free.

**Why sign in with the browser?** Copilot handles MCP authorization with OAuth
(dynamic client registration), so you never copy API keys into settings.

## Troubleshooting

| Message from Wapliss | What it means | What to do |
| --- | --- | --- |
| `account_awaiting_qr` / `instance_not_connected` | No phone is linked to this Wapliss account | Link it at [wapliss.com/app/connect](https://wapliss.com/app/connect) |
| `account_disconnected` | WhatsApp closed the linked session | Scan the QR code again |
| `quota_exceeded` | Daily message quota reached | Wait for the reset or upgrade the plan |
| Rate limit (`-32300` / HTTP 429) | More than 60 calls in a minute | Wait the seconds indicated |
| `chat_not_found` | No chat matches the name or number | Search with another name or the full number with country code |

## Package layout

```text
plugin.json                       Agent Plugins 1.0 manifest (root, closed schema)
mcp.json                          Remote MCP server (Streamable HTTP, OAuth handled by Copilot)
skills/wapliss-whatsapp/SKILL.md  Agent Skill: when and how to use the tools safely
assets/icon.png                   512 × 512 icon
.github/plugin/marketplace.json   Makes this repository a one-plugin marketplace ("wapliss")
scripts/validate.py               Manifest, MCP and skill checks (--live checks the endpoint)
```

## Validate

```bash
python3 scripts/validate.py          # Agent Plugins 1.0 manifest, mcp.json and skill checks
python3 scripts/validate.py --live   # + public endpoint and OAuth metadata
copilot plugin marketplace add ./ && copilot plugin install wapliss-whatsapp@wapliss   # install smoke test
```

Bump `version` in `plugin.json` and `.github/plugin/marketplace.json` for every
release, and tag it (`v1.0.0`) for marketplace listings.

## Wapliss plugins

Wapliss works the same way in every assistant: one account, one linked phone,
the same 16 tools.

| Assistant | Where it works | Format | Get it |
| --- | --- | --- | --- |
| Claude | Claude.ai, Claude Desktop, Claude Code | Custom connector / Claude plugin | [github.com/proteuscrypto/wapliss-whatsapp-for-claude](https://github.com/proteuscrypto/wapliss-whatsapp-for-claude) |
| ChatGPT | ChatGPT web and desktop | ChatGPT plugin (Agent Plugins) / custom MCP connector | [github.com/proteuscrypto/wapliss-for-chatgpt](https://github.com/proteuscrypto/wapliss-for-chatgpt) |
| Gemini | Gemini app, Gemini CLI, Antigravity | Connected app, Gemini CLI extension, Antigravity plugin | [github.com/proteuscrypto/wapliss-for-gemini](https://github.com/proteuscrypto/wapliss-for-gemini) |
| DeepSeek | DeepSeek Harness (dsh) | dsh bundle | [github.com/proteuscrypto/wapliss-for-deepseek](https://github.com/proteuscrypto/wapliss-for-deepseek) |
| **GitHub Copilot** | VS Code, Copilot CLI, Copilot app | Agent Plugins 1.0 | this repository |
| Grok | Grok Build, grok.com connectors, xAI API | Grok Build plugin / custom MCP connector | [github.com/proteuscrypto/wapliss-for-grok](https://github.com/proteuscrypto/wapliss-for-grok) |
| Microsoft 365 Copilot | Microsoft 365 Copilot (work accounts), Teams, Outlook | Declarative agent with a remote MCP action | [github.com/proteuscrypto/wapliss-for-m365-copilot](https://github.com/proteuscrypto/wapliss-for-m365-copilot) |
| Any MCP client | Clients with remote MCP (Streamable HTTP) | OAuth 2.1, or a personal API key | [wapliss.com/integrations#mcp](https://wapliss.com/integrations#mcp) |

## Credits and support

- **Created and maintained by [NetDigitalTech LLC](https://netdigitaltech.com/)**
  ([GitHub](https://github.com/netdigitaltech)), the company that created and owns
  [Wapliss](https://wapliss.com/). NetDigitalTech builds web, mobile and AI
  applications. Albuquerque, New Mexico, USA · commerce@netdigitaltech.com
- Support: [open an issue](https://github.com/proteuscrypto/wapliss-for-copilot/issues) in this repository.
- Integration guides: [English](https://wapliss.com/integrations#copilot) ·
  [Español](https://wapliss.com/integraciones#copilot)

## Español

**Wapliss WhatsApp para GitHub Copilot**: conecta tu propio WhatsApp a
GitHub Copilot con el servidor MCP de Wapliss. Lee y resume chats y grupos y
envía mensajes, archivos, ubicaciones y encuestas, siempre con tu confirmación.

Cómo empezar: crea tu cuenta gratis y vincula tu teléfono; en Copilot CLI
ejecuta `copilot plugin marketplace add proteuscrypto/wapliss-for-copilot` y `copilot plugin install wapliss-whatsapp@wapliss`; en VS Code,
**Chat: Install Plugin from Source** con la URL del repositorio. Cuando Copilot
lo pida, inicia sesión en Wapliss y autoriza el acceso.

Ejemplos: *"Muéstrame mis últimos mensajes de WhatsApp"*, *"Resume lo que se
habló hoy en el grupo de la familia"*, *"Envía 'Llego en 10 minutos' a
+54 9 11 5555 0100"*. Creado y mantenido por **[NetDigitalTech LLC](https://netdigitaltech.com/)**,
la empresa creadora y dueña de [Wapliss](https://wapliss.com/). Guía completa:
[wapliss.com/integraciones#copilot](https://wapliss.com/integraciones#copilot).

## Trademarks and license

GitHub and GitHub Copilot are trademarks of GitHub, Inc. Visual Studio Code is a trademark of Microsoft Corporation. WhatsApp is a trademark of Meta Platforms, Inc. Wapliss is
an independent service and is not affiliated with, sponsored or endorsed by
Meta, WhatsApp, GitHub or Microsoft.

Released under the [MIT License](LICENSE). © 2026 NetDigitalTech LLC, creator and owner of Wapliss.
