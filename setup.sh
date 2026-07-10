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

# --- Personal scripts (~/bin) ---
# Portable helpers that should exist on every machine (e.g. `cuda` for the
# tailnet GPU box). Machine-specific scripts (archive-*.sh) stay out of the repo.
echo "Setting up ~/bin scripts..."
mkdir -p "$HOME/bin"
chmod +x "$SCRIPT_DIR/bin/cuda" 2>/dev/null || true
for bin_file in "$SCRIPT_DIR/bin"/*; do
    if [ -f "$bin_file" ]; then
        bin_name="$(basename "$bin_file")"
        link_item "$bin_file" "$HOME/bin/$bin_name"
    fi
done

# --- Prune orphaned symlinks pointing into this repo ---
# Removes symlinks under ~/.claude whose target is inside $SCRIPT_DIR but
# no longer exists (e.g. a skill/command/agent that was deleted upstream).
# Only touches symlinks owned by us — leaves unrelated files alone.
echo "Pruning orphaned symlinks..."
prune_orphans() {
    local dir="$1"
    [ -d "$dir" ] || return 0
    local removed=0
    for entry in "$dir"/* "$dir"/.[!.]*; do
        [ -L "$entry" ] || continue
        local target
        target="$(readlink "$entry")"
        case "$target" in
            "$SCRIPT_DIR"/*)
                if [ ! -e "$entry" ]; then
                    rm "$entry"
                    echo "  Removed orphan: $entry -> $target"
                    removed=$((removed + 1))
                fi
                ;;
        esac
    done
    # Drop the parent dir if it's now empty (e.g. ~/.claude/agents)
    if [ -d "$dir" ] && [ -z "$(ls -A "$dir")" ]; then
        rmdir "$dir"
        echo "  Removed empty dir: $dir"
    fi
}
prune_orphans "$CLAUDE_DIR/skills"
prune_orphans "$CLAUDE_DIR/commands"
prune_orphans "$CLAUDE_DIR/agents"
prune_orphans "$HOME/bin"

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
