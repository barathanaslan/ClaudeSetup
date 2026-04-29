#!/bin/bash
# ClaudeSetup — Syncs skills, agents, and CLAUDE.md to ~/.claude/
# Run this after cloning or after pulling updates.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/backup-$(date +%Y%m%d-%H%M%S)"

echo "ClaudeSetup — Syncing to $CLAUDE_DIR"
echo "Source: $SCRIPT_DIR"
echo ""

# Create ~/.claude if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# --- Backup existing files if they exist and aren't already symlinks to us ---
backup_if_needed() {
    local target="$1"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "  Backing up existing $target -> $BACKUP_DIR/"
        cp -r "$target" "$BACKUP_DIR/"
    fi
}

# --- Symlink a file or directory ---
link_item() {
    local src="$1"
    local dest="$2"

    if [ -L "$dest" ]; then
        local current_target
        current_target="$(readlink "$dest")"
        if [ "$current_target" = "$src" ]; then
            echo "  Already linked: $dest"
            return
        fi
        rm "$dest"
    fi

    backup_if_needed "$dest"

    # Remove existing target to replace with symlink
    if [ -e "$dest" ]; then
        rm -rf "$dest"
    fi

    ln -s "$src" "$dest"
    echo "  Linked: $dest -> $src"
}

# --- CLAUDE.md ---
echo "Setting up CLAUDE.md..."
link_item "$SCRIPT_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"

# --- settings.json ---
echo "Setting up settings.json..."
link_item "$SCRIPT_DIR/settings.json" "$CLAUDE_DIR/settings.json"

# --- Skills ---
echo "Setting up skills..."
mkdir -p "$CLAUDE_DIR/skills"
for skill_dir in "$SCRIPT_DIR/skills"/*/; do
    if [ -d "$skill_dir" ]; then
        skill_name="$(basename "$skill_dir")"
        link_item "$skill_dir" "$CLAUDE_DIR/skills/$skill_name"
    fi
done

# --- Commands ---
echo "Setting up commands..."
mkdir -p "$CLAUDE_DIR/commands"
for cmd_file in "$SCRIPT_DIR/commands"/*.md; do
    if [ -f "$cmd_file" ]; then
        cmd_name="$(basename "$cmd_file")"
        link_item "$cmd_file" "$CLAUDE_DIR/commands/$cmd_name"
    fi
done

echo ""
echo "Done. Installed:"
echo "  - CLAUDE.md (global)"
echo "  - settings.json (global)"
echo "  - $(ls -d "$SCRIPT_DIR/skills"/*/ 2>/dev/null | wc -l | tr -d ' ') skills"
echo "  - $(ls "$SCRIPT_DIR/commands"/*.md 2>/dev/null | wc -l | tr -d ' ') commands"
echo ""
if [ -d "$BACKUP_DIR" ]; then
    echo "Backups saved to: $BACKUP_DIR"
fi
echo ""
echo "To update after changes: git pull && ./setup.sh"
