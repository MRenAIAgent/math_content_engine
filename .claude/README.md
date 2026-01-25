# Project-local Claude Code config (`.claude/`)

This repo contains a **project-local copy** of the configs from `everything-claude-code/`, placed here:

- `.claude/agents/`
- `.claude/commands/`
- `.claude/rules/`
- `.claude/skills/`
- `.claude/contexts/`
- `.claude/hooks/` (includes `hooks.json` + shell scripts)
- `.claude/mcp-configs/mcp-servers.json`

## How to enable (recommended: copy/symlink into your user config)

Claude Code’s “manual installation” instructions in `everything-claude-code` target **user-level** paths under `~/.claude/`.

If you want these to actually be active in Claude Code, do one of the following on your machine:

### Option A: Copy into `~/.claude/`

```bash
mkdir -p ~/.claude/{agents,commands,rules,skills}
cp -R .claude/agents/* ~/.claude/agents/
cp -R .claude/commands/* ~/.claude/commands/
cp -R .claude/rules/* ~/.claude/rules/
cp -R .claude/skills/* ~/.claude/skills/
```

- Hooks: merge `.claude/hooks/hooks.json` into your `~/.claude/settings.json` (Claude Code settings).
- MCP: copy desired servers from `.claude/mcp-configs/mcp-servers.json` into your Claude MCP config and replace any `YOUR_*_HERE` placeholders.

### Option B: Symlink (keeps this repo as the source of truth)

```bash
mkdir -p ~/.claude
ln -sfn "$PWD/.claude/agents" ~/.claude/agents
ln -sfn "$PWD/.claude/commands" ~/.claude/commands
ln -sfn "$PWD/.claude/rules" ~/.claude/rules
ln -sfn "$PWD/.claude/skills" ~/.claude/skills
```

## Notes on hooks

The hook commands inside `.claude/hooks/hooks.json` reference paths like `./hooks/...` and `./skills/...`.
Those are intended to be **relative to the Claude config directory** (e.g., `~/.claude/`), so keep the same folder structure when copying/symlinking.

