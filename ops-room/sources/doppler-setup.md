# Doppler Setup Guide for JARVIS OPS

## 1. Install Doppler CLI

```bash
# Linux (one-liner)
curl -Ls --tlsv1.2 --proto "=https" -o /tmp/doppler-install.sh \
  https://cli.doppler.com/install.sh && sh /tmp/doppler-install.sh

# Verify
doppler --version
```

## 2. Authenticate

```bash
doppler login
# Opens browser → log in → token stored in ~/.config/doppler/
```

## 3. Create Projects (one per repo)

```bash
# In the New-power repo
doppler projects create new-power

# In start-of-play
doppler projects create start-of-play

# In jarvis-mbm
doppler projects create jarvis-mbm
```

## 4. Create Configs per Environment

```bash
doppler environments create dev   --project new-power
doppler environments create stg   --project new-power
doppler environments create prd   --project new-power
```

## 5. Add Secrets

```bash
# Example: add Discord webhook
doppler secrets set DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
  --project new-power --config dev

# Example: add Slack webhook
doppler secrets set SLACK_WEBHOOK_URL="https://hooks.slack.com/..." \
  --project new-power --config dev

# Example: add SendGrid key
doppler secrets set SENDGRID_API_KEY="SG.xxx" \
  --project new-power --config dev
```

## 6. Use in JARVIS OPS

```bash
# Sync secrets to shell (source the output)
source <(bash ops-room/sources/doppler-sync.sh --project new-power --config dev)

# Or write to .env (add .env to .gitignore first!)
bash ops-room/sources/doppler-sync.sh --project new-power --config dev --env-file .env

# Then test comms
python3 ops-room/comms/notify.py --test discord
```

## 7. Wire into GitHub Actions (optional)

```yaml
# .github/workflows/deploy.yml
- name: Load secrets
  uses: dopplerhq/cli-action@v3
  with:
    project: new-power
    config: prd
    inject-env-vars: true
```

## Secret Naming Convention

| Secret | Used By |
|--------|---------|
| `DISCORD_WEBHOOK_URL` | ops-room/comms/notify.py |
| `SLACK_WEBHOOK_URL` | ops-room/comms/notify.py |
| `SENDGRID_API_KEY` | ops-room/comms/notify.py |
| `GITHUB_TOKEN` | ops-room/jarvis/research-scan.py |
| `VERCEL_TOKEN` | start-of-play deployments |
