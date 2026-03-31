#!/bin/bash
#
# checkpoint.sh - Creates a git checkpoint for Time Travel recovery
#
# Usage:
#   ./checkpoint.sh --name "tt_build_20260117_143000" --description "Before build phase"
#   ./checkpoint.sh --name "tt_manual_save" --description "Manual save" --method stash
#
# Options:
#   --name, -n          Checkpoint name (required)
#   --description, -d   Human-readable description (required)
#   --method, -m        Checkpoint method: branch (default) or stash
#   --checkpoints-file  Path to checkpoints.json (optional)
#

set -e

# Default values
METHOD="branch"
CHECKPOINTS_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name|-n)
            CHECKPOINT_NAME="$2"
            shift 2
            ;;
        --description|-d)
            DESCRIPTION="$2"
            shift 2
            ;;
        --method|-m)
            METHOD="$2"
            shift 2
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

if [[ -z "$DESCRIPTION" ]]; then
    echo "Error: --description is required"
    exit 1
fi

if [[ "$METHOD" != "branch" && "$METHOD" != "stash" ]]; then
    echo "Error: --method must be 'branch' or 'stash'"
    exit 1
fi

# Ensure we're in a git repository
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "Error: Not in a git repository"
    exit 1
fi

# Get current commit hash
CURRENT_COMMIT=$(git rev-parse HEAD)

# Check for uncommitted changes
HAS_CHANGES="false"
if [[ -n $(git status --porcelain) ]]; then
    HAS_CHANGES="true"
fi

# Get timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create checkpoint based on method
if [[ "$METHOD" == "branch" ]]; then
    # Check if branch already exists
    if git rev-parse --verify "$CHECKPOINT_NAME" >/dev/null 2>&1; then
        echo "Warning: Branch $CHECKPOINT_NAME already exists, using as checkpoint"
    else
        # Create lightweight branch at current commit
        if ! git branch "$CHECKPOINT_NAME"; then
            echo "Error: Failed to create checkpoint branch: $CHECKPOINT_NAME"
            exit 1
        fi
    fi
    echo "Created checkpoint branch: $CHECKPOINT_NAME"

elif [[ "$METHOD" == "stash" ]]; then
    if [[ "$HAS_CHANGES" == "true" ]]; then
        # Stash changes with descriptive message
        STASH_MESSAGE="${CHECKPOINT_NAME}: $DESCRIPTION"
        if ! git stash push -m "$STASH_MESSAGE"; then
            echo "Error: Failed to stash changes"
            exit 1
        fi

        # Get stash reference
        STASH_REF=$(git stash list | grep "$CHECKPOINT_NAME" | head -1 | cut -d: -f1)

        echo "Stashed changes as: $CHECKPOINT_NAME"

        # Apply stash back to keep working directory intact
        git stash apply >/dev/null 2>&1 || true

    else
        echo "Warning: No uncommitted changes to stash, creating branch checkpoint instead"
        METHOD="branch"
        if ! git branch "$CHECKPOINT_NAME"; then
            echo "Error: Failed to create checkpoint branch"
            exit 1
        fi
        echo "Created checkpoint branch (no changes to stash): $CHECKPOINT_NAME"
    fi
fi

# Update checkpoints file if specified
if [[ -n "$CHECKPOINTS_FILE" ]] && [[ -d "$(dirname "$CHECKPOINTS_FILE")" ]]; then
    # Create JSON entry
    NEW_CHECKPOINT=$(cat <<EOF
{
    "name": "$CHECKPOINT_NAME",
    "method": "$METHOD",
    "commit": "$CURRENT_COMMIT",
    "timestamp": "$TIMESTAMP",
    "description": "$DESCRIPTION",
    "hasUncommittedChanges": $HAS_CHANGES
}
EOF
)

    if [[ -f "$CHECKPOINTS_FILE" ]]; then
        # Append to existing file (requires jq)
        if command -v jq >/dev/null 2>&1; then
            jq --argjson new "$NEW_CHECKPOINT" '.checkpoints += [$new] | .lastUpdated = "'"$TIMESTAMP"'"' "$CHECKPOINTS_FILE" > "${CHECKPOINTS_FILE}.tmp"
            mv "${CHECKPOINTS_FILE}.tmp" "$CHECKPOINTS_FILE"
            echo "Updated checkpoints file: $CHECKPOINTS_FILE"
        else
            echo "Warning: jq not installed, cannot update checkpoints file"
        fi
    else
        # Create new file
        cat > "$CHECKPOINTS_FILE" <<EOF
{
    "checkpoints": [$NEW_CHECKPOINT],
    "lastUpdated": "$TIMESTAMP"
}
EOF
        echo "Created checkpoints file: $CHECKPOINTS_FILE"
    fi
fi

# Output checkpoint data as JSON
cat <<EOF
{
    "name": "$CHECKPOINT_NAME",
    "method": "$METHOD",
    "commit": "$CURRENT_COMMIT",
    "timestamp": "$TIMESTAMP",
    "description": "$DESCRIPTION",
    "hasUncommittedChanges": $HAS_CHANGES
}
EOF
