# Radar Social

**Social media research with real data, free, built for Brazilian Portuguese (works for any market).**

A skill for AI agents (Claude Code, Cursor, Codex, Gemini CLI and others) that turns "what should I post?" into an answer backed by numbers, links and ready-to-use content ideas.

[Português](README.md)

## What it does

- **Outliers:** finds the posts that performed far above the account's own normal, per format, explains why and suggests 5 ideas.
- **Comments:** sorts comments into questions, objections, complaints, content requests, purchase intent and praise, understanding Brazilian slang, "kkkk" and irony.
- **Competitors:** fair comparison (each account measured against its own baseline), active ads and open gaps.
- **Best time to post:** day of week and time slot that work best for that specific account, in your time zone.
- **Before and after:** did the campaign work? Separates volume (posted more) from quality (each post did better).
- **Client report:** plain-language report with sources and limitations.

## Why it is different

- **Actually free.** Uses the official, free YouTube and Meta APIs with keys you create yourself. No subscription, no credits, no middleman.
- **Works with no key at all** to start: public YouTube feed or any CSV export (TikTok, Kwai, LinkedIn, your dashboard).
- **Math done by code.** Dependency-free Python scripts compute everything, so results are reproducible and auditable.
- **Privacy first.** Never stores or shows who wrote a comment.

## Install

```bash
npx skills add venancioguga/radar-social
```

Claude Code plugin:

```
/plugin marketplace add venancioguga/radar-social
/plugin install radar-social@radar-social
```

Requires Python 3.9+. Free API keys: see [`guias/chaves.md`](skills/radar-social/guias/chaves.md) (in Portuguese; the steps are the standard Google Cloud and Meta for Developers flows).

## License

MIT. Made by [Guga Venancio](https://github.com/venancioguga). A [Guve](https://guve.io) project.
