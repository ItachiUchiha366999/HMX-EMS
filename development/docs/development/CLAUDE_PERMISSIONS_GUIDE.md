# Claude Permissions Configuration Guide

## Quick Enable/Disable Auto-Permissions

### Location
Configuration file: `~/.claude.json` (or `/home/frappe/.claude.json`)

### Enable Auto-Permissions (No Approval Required)

Edit `~/.claude.json` and ensure these settings are in place:

```json
{
  "tokenBudget": 64000,
  "projects": {
    "/workspace": {
      "allowedTools": [
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Glob",
        "Grep",
        "Task",
        "TodoWrite",
        "WebFetch",
        "WebSearch",
        "NotebookEdit",
        "AskUserQuestion"
      ],
      "hasTrustDialogAccepted": true,
      "hasClaudeMdExternalIncludesApproved": true,
      "hasClaudeMdExternalIncludesWarningShown": true
    },
    "/workspace/development": {
      "allowedTools": [
        "Read",
        "Write",
        "Edit",
        "Bash",
        "Glob",
        "Grep",
        "Task",
        "TodoWrite",
        "WebFetch",
        "WebSearch",
        "NotebookEdit",
        "AskUserQuestion"
      ],
      "hasTrustDialogAccepted": true,
      "hasClaudeMdExternalIncludesApproved": true,
      "hasClaudeMdExternalIncludesWarningShown": true
    }
  }
}
```

### Disable Auto-Permissions (Require Approval)

```json
{
  "projects": {
    "/workspace": {
      "allowedTools": [],
      "hasTrustDialogAccepted": false,
      "hasClaudeMdExternalIncludesApproved": false
    },
    "/workspace/development": {
      "allowedTools": [],
      "hasTrustDialogAccepted": false,
      "hasClaudeMdExternalIncludesApproved": false
    }
  }
}
```

## Token Budget Settings

Adjust the context window size by changing `tokenBudget`:

- **32,000**: More economical, shorter context
- **64,000**: Balanced (recommended)
- **128,000**: Long context, higher cost
- **200,000**: Maximum context window

```json
{
  "tokenBudget": 64000
}
```

## Available Tools

You can selectively allow specific tools:

- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Glob` - Search for files by pattern
- `Grep` - Search file contents
- `Task` - Launch specialized agents
- `TodoWrite` - Task management
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web
- `NotebookEdit` - Edit Jupyter notebooks
- `AskUserQuestion` - Ask clarifying questions

## After Making Changes

1. Save the `~/.claude.json` file
2. Restart your Claude session (close and reopen VSCode extension or start new conversation)
3. Changes will take effect in the new session

## Quick Commands

### View current config
```bash
cat ~/.claude.json
```

### Backup config before changes
```bash
cp ~/.claude.json ~/.claude.json.backup
```

### Restore from backup
```bash
cp ~/.claude.json.backup ~/.claude.json
```

## Troubleshooting

**Permissions still asking for approval?**
- Check that the project path matches your working directory exactly
- Restart your Claude session
- Verify no organization-level policies are overriding settings
- Check the `tengu_disable_bypass_permissions_mode` flag is `false`

**Need different settings per project?**
Add separate entries in the `projects` object with different paths:

```json
{
  "projects": {
    "/trusted/project": {
      "allowedTools": ["Read", "Write", "Edit", "Bash"],
      "hasTrustDialogAccepted": true
    },
    "/untrusted/project": {
      "allowedTools": [],
      "hasTrustDialogAccepted": false
    }
  }
}
```

## Security Note

Auto-accepting permissions means Claude can execute commands and modify files without asking. Only enable this for trusted projects where you're comfortable with autonomous actions.
