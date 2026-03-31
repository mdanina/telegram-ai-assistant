#!/bin/bash
#
# revert.sh - Reverts to a git checkpoint for Time Travel recovery
#
# Usage:
#   ./revert.sh --name "tt_build_20260117_143000"
#   ./revert.sh --name "tt_build_20260117_143000" --hard-reset
#   ./revert.sh --name "tt_build_20260117_143000" --no-preserve-changes
#
# Options:
#   --name, -n              Checkpoint name to revert to (required)
#   --hard-reset, -h        Perform hard reset (destructive)
#   --preserve-changes, -p  Stash current changes before revert (default: true)
#   --no-preserve-changes   Don't stash current changes
#   --checkpoints-file, -f  Path to checkpoints.json (optional)
#

set -e

# Default values
HARD_RESET="false"
PRESERVE_CHANGES="true"
CHECKPOINTS_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name|-n)
            CHECKPOINT_NAME="$2"
            shift 2
            ;;
        --hard-reset|-h)
            HARD_RESET="true"
            shift
            ;;
        --preserve-changes|-p)
            PRESERVE_CHANGES="true"
            shift
            ;;
        --no-preserve-changes)
            PRESERVE_CHANGES="false"
            shift
            ;;
        --checkpoints-file|-f)
            CHECKPOINTS_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$CHECKPOINT_NAME" ]]; then
    echo "Error: --name is required"
    exit 1
fi

# Ensure we're in a git repository
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get current state info
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
CURRENT_COMMIT=$(git rev-parse HEAD)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Check for uncommitted changes
HAS_CHANGES="false"
if [[ -n $(git status --porcelain) ]]; then
    HAS_CHANGES="true"
fi

# Initialize revert tracking variables
PRESERVED_CHANGES="false"
PRESERVE_STASH_NAME=""
REVERT_METHOD="unknown"

# Preserve current changes if requested and changes exist
if [[ "$PRESERVE_CHANGES" == "true" && "$HAS_CHANGES" == "true" ]]; then
    PRESERVE_STASH_NAME="pre-revert-$(date +%Y%m%d_%H%M%S)"
    echo "Preserving current changes to stash: $PRESERVE_STASH_NAME"

    if git stash push -m "$PRESERVE_STASH_NAME"; then
        PRESERVED_CHANGES="true"
        echo "Changes preserved successfully"
    else
        echo "Warning: Failed to preserve changes, continuing anyway"
    fi
fi

# Determine checkpoint type
IS_BRANCH="false"
IS_STASH="false"
STASH_REF=""

# Check if it's a branch
if git rev-parse --verify "$CHECKPOINT_NAME" >/dev/null 2>&1; then
    IS_BRANCH="true"
fi

# Check if it's a stash
STASH_MATCH=$(git stash list | grep "$CHECKPOINT_NAME" | head -1)
if [[ -n "$STASH_MATCH" ]]; then
    IS_STASH="true"
    STASH_REF=$(echo "$STASH_MATCH" | cut -d: -f1)
fi

# Perform the revert
if [[ "$HARD_RESET" == "true" && "$IS_BRANCH" == "true" ]]; then
    # Hard reset to branch (most destructive)
    echo "Performing hard reset to: $CHECKPOINT_NAME"
    if ! git reset --hard "$CHECKPOINT_NAME"; then
        echo "Error: Hard reset failed"
        exit 1
    fi
    REVERT_METHOD="hard_reset"
    echo "Hard reset completed successfully"

elif [[ "$IS_BRANCH" == "true" ]]; then
    # Check for uncommitted changes that would block checkout
    if [[ -n $(git status --porcelain) ]]; then
        echo "Warning: Uncommitted changes detected, attempting checkout anyway"
    fi

    # Checkout the branch
    echo "Checking out checkpoint: $CHECKPOINT_NAME"
    if ! git checkout "$CHECKPOINT_NAME" 2>&1; then
        if [[ "$HARD_RESET" == "false" ]]; then
            echo "Error: Checkout failed. Use --hard-reset to force, or commit/stash changes first."
            exit 1
        fi
    fi
    REVERT_METHOD="checkout"
    echo "Checkout completed successfully"

elif [[ "$IS_STASH" == "true" ]]; then
    # Apply the stash
    echo "Applying stash: $STASH_REF ($CHECKPOINT_NAME)"
    if ! git stash apply "$STASH_REF"; then
        echo "Error: Failed to apply stash: $STASH_REF"
        exit 1
    fi
    REVERT_METHOD="stash_apply"
    echo "Stash applied successfully"

else
    echo "Error: Checkpoint not found: $CHECKPOINT_NAME"
    echo "Available branches:"
    git branch --list "tt_*" 2>/dev/null || echo "  (none)"
    echo "Available stashes with 'tt_':"
    git stash list | grep "tt_" 2>/dev/null || echo "  (none)"
    exit 1
fi

# Update checkpoints file if specified
if [[ -n "$CHECKPOINTS_FILE" && -f "$CHECKPOINTS_FILE" ]]; then
    if command -v jq >/dev/null 2>&1; then
        REVERT_EVENT=$(cat <<EOF
{
    "fromCheckpoint": "$CURRENT_COMMIT",
    "toCheckpoint": "$CHECKPOINT_NAME",
    "timestamp": "$TIMESTAMP",
    "method": "$REVERT_METHOD",
    "preservedChanges": $PRESERVED_CHANGES
}
EOF
)
        jq --argjson revert "$REVERT_EVENT" '.reverts = (.reverts // []) + [$revert] | .lastUpdated = "'"$TIMESTAMP"'"' "$CHECKPOINTS_FILE" > "${CHECKPOINTS_FILE}.tmp"
        mv "${CHECKPOINTS_FILE}.tmp" "$CHECKPOINTS_FILE"
        echo "Updated checkpoints file with revert event"
    else
        echo "Warning: jq not installed, cannot update checkpoints file"
    fi
fi

# Output revert summary as JSON
cat <<EOF

Revert Summary:
{
    "checkpointName": "$CHECKPOINT_NAME",
    "fromBranch": "$CURRENT_BRANCH",
    "fromCommit": "$CURRENT_COMMIT",
    "timestamp": "$TIMESTAMP",
    "hadUncommittedChanges": $HAS_CHANGES,
    "preservedChanges": $PRESERVED_CHANGES,
    "preserveStashName": "$PRESERVE_STASH_NAME",
    "method": "$REVERT_METHOD"
}
EOF
