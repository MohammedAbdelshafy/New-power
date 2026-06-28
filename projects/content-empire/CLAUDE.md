# Content Empire — JARVIS OPS Session Brain

## Mission
Build and operate a 15-account viral content machine: 5 YouTube channels + 5 Instagram accounts + 5 TikTok accounts. Post daily. Target American viewers (highest CPM). Join all monetization campaigns. Compound growth until all accounts are fully monetized.

## Owner
Mohammed Abdelshafy / Moe — abdelshafyplay@gmail.com

## Account Registry
See `accounts/registry.json` for full account list and status.

## Clip Sources
Primary sources: clipping.com, muslimsclipping.com
Full catalogue: `clips/sources.json`

## Audience Target
- **Primary**: United States (highest CPM, $8–$25 RPM on YouTube)
- **Secondary**: UK, Canada, Australia (tier-1 English markets)
- Peak posting windows: `schedules/posting-schedule.json`
- Content language: English
- Niche strategy: viral Islamic/faith content + AI tools + motivational — highest US engagement

## Platform Rules

### YouTube (5 channels)
- Upload schedule: 1 clip/day minimum per channel
- Format: shorts (under 60s) + long-form (10–20 min compilations)
- YPP eligibility: 1,000 subs + 4,000 watch hours (long-form) OR 1,000 subs + 10M Shorts views
- Revenue: AdSense + channel memberships + Super Thanks
- SEO: optimized titles, descriptions, tags — all English, US-targeted

### Instagram (5 accounts)
- Upload schedule: 2 Reels/day per account
- ManyChat: Comment-to-DM automation active on all viral posts (keyword: "Guide", "Free", topic-specific)
- Reels Play Bonus: invitation-based — focus on hitting 1M+ Reel views to qualify
- Growth hack: use Comment-to-DM CTA on every Reel (proven 59% share-to-like ratio)

### TikTok (5 accounts)
- Upload schedule: 3 clips/day per account
- TikTok Creator Fund: 10,000 followers + 100,000 views in 30 days
- TikTok LIVE: enabled at 1,000 followers — gifts revenue
- US SIM / VPN: post during US hours even if Moe is outside US

## Monetization Campaigns
Full requirements and tracking: `campaigns/monetization.json`

Priority order:
1. YouTube AdSense (highest RPM, most reliable)
2. TikTok Creator Rewards (replaced Creator Fund — $1/1,000 qualified views)
3. Instagram Reels Bonus (invitation only, focus on view volume)

## Engineering Protocol
Follow JARVIS OPS Engineering Protocol from parent session.
All clips processed through `scripts/` automation.
All accounts tracked in `accounts/registry.json`.

## Directory Layout
```
projects/content-empire/
├── CLAUDE.md              ← this file
├── accounts/
│   └── registry.json      ← all 15 accounts (YT + IG + TT)
├── clips/
│   └── sources.json       ← clip source catalogue + discovery tools
├── schedules/
│   └── posting-schedule.json  ← US-optimized posting times per platform
├── campaigns/
│   └── monetization.json  ← YPP, Creator Fund, Reels Bonus requirements
└── scripts/
    └── clip-processor.py  ← clip download + trim + caption + format
```

## Workflow (Repeat Daily)
1. Pull clips from source sites (clipping.com, muslimsclipping.com, others)
2. Run `scripts/clip-processor.py` — trim to optimal length, add captions
3. Post per `schedules/posting-schedule.json` — US peak windows
4. Monitor performance — double down on anything >100k views in 24h
5. Activate ManyChat keyword kickback on every high-performing Reel
6. Track monetization milestones in `campaigns/monetization.json`
