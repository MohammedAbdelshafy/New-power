# Antigravity ⇄ GitHub ⇄ Claude Code, with Telegram/Discord updates

This repo is wired so you can give an order from anywhere, have it applied, and
get a ping on Telegram or Discord. **GitHub is the shared brain** that connects
Claude Code (here), your local Antigravity IDE, and opencode.

```
You (here / phone)  --order-->  Claude Code (web)  --git push-->  GitHub repo
                                                                     |
                             Antigravity / opencode (your machine) <-+   git pull
                                                                     |
                                             on push / issue / PR events
                                                                     v
                                             GitHub Actions: notify.yml
                                                                     |
                                              +----------------------+----------------------+
                                              v                                             v
                                          Telegram bot                                Discord webhook
```

There is no private API that pushes commands straight into a running Antigravity
session. The reliable bridge is Git: work lands in the repo, your local tools
pull it, and notifications tell you when something happened.

---

## 1. One-time setup: notification secrets

Go to **GitHub repo → Settings → Secrets and variables → Actions → New repository
secret** and add whichever channel(s) you want. You can enable one or both.

### Telegram
1. In Telegram, message **@BotFather** → `/newbot` → follow prompts → copy the
   **bot token**.
2. Message **@userinfobot** (or add your bot to a group and use its id) to get
   your **chat id**.
3. Add secrets:
   - `TELEGRAM_BOT_TOKEN` = the token from BotFather
   - `TELEGRAM_CHAT_ID` = your chat id
4. Send your bot any message once so it's allowed to reply to you.

### Discord
1. In your server: **Server Settings → Integrations → Webhooks → New Webhook**,
   pick a channel, **Copy Webhook URL**.
2. Add secret:
   - `DISCORD_WEBHOOK_URL` = the copied URL

Once secrets exist, every push / issue / PR triggers `.github/workflows/notify.yml`
and you get a message. Missing channels are skipped silently — nothing breaks if
you set up only one.

Test it without any code change: **Actions → Notify (Telegram / Discord) → Run
workflow**, type a message, run. You should get the ping.

---

## 2. Giving orders (two ways)

### A. Direct — tell Claude Code here
Say what you want in this session. Claude applies it and pushes to the branch.
Your local Antigravity/opencode picks it up on the next `git pull`. You get a
Telegram/Discord ping from the push.

### B. Durable queue — GitHub Issues
Open an Issue describing the task (from the GitHub app on your phone, too). This
is a persistent "order" that both a Claude session and a local Antigravity agent
can read. Issue open/close events also notify you.

---

## 3. Wiring up the local side (Antigravity + opencode)

On your machine, clone the repo once and keep it synced:

```bash
git clone https://github.com/mohammedabdelshafy/new-power.git
cd new-power
```

Open that same folder in **Antigravity** and in **opencode**. Now all three
tools (Claude Code web, Antigravity, opencode) operate on one repo.

**Pull before you work, push when done:**
```bash
git pull origin main            # or the active feature branch
# ...Antigravity/opencode make changes...
git add -A && git commit -m "..." && git push
```

Optional: auto-pull every 30s so Antigravity always sees the latest orders/code:
```bash
while true; do git pull --quiet; sleep 30; done
```

---

## 4. Let Antigravity/opencode post their own updates

`scripts/notify.sh` sends a line to the same Telegram/Discord channels. Point
your local agent at it so it can report progress:

```bash
export TELEGRAM_BOT_TOKEN=...   # same values as the GitHub secrets
export TELEGRAM_CHAT_ID=...
export DISCORD_WEBHOOK_URL=...

./scripts/notify.sh "Antigravity: started the task ✅"
echo "tests passed" | ./scripts/notify.sh
```

Put those `export` lines in a local `.env` you source (do **not** commit real
tokens). Then Antigravity can call `./scripts/notify.sh "..."` at the end of a
run, or you can hook it into a build/test script.

---

## 5. Quick reference

| I want to…                       | Do this |
|----------------------------------|---------|
| Give an order and have it applied| Tell Claude Code here, or open a GitHub Issue |
| See the change on my machine     | `git pull` in the Antigravity/opencode folder |
| Get pinged on activity           | Add the Telegram/Discord secrets (section 1) |
| Have Antigravity ping me         | Call `./scripts/notify.sh "message"` (section 4) |
| Test notifications now           | Actions tab → Run the "Notify" workflow |
