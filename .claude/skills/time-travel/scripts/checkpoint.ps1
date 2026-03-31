<#
.SYNOPSIS
    Creates a git checkpoint for Time Travel recovery.

.DESCRIPTION
    Creates a named save point using git branch or stash.
    Checkpoints enable rollback to known-good states.

.PARAMETER CheckpointName
    Name for the checkpoint (e.g., tt_build_20260117_143000)

.PARAMETER Description
    Human-readable description of the checkpoint

.PARAMETER Method
    Checkpoint method: "branch" (default) or "stash"

.PARAMETER CheckpointsFile
    Path to checkpoints.json file (optional, for ADW integration)

.EXAMPLE
    .\checkpoint.ps1 -CheckpointName "tt_build_20260117_143000" -Description "Before build phase"

.EXAMPLE
    .\checkpoint.ps1 -CheckpointName "tt_manual_save" -Description "Manual save point" -Method "stash"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$CheckpointName,

    [Parameter(Mandatory=$true)]
    [string]$Description,

    [ValidateSet("branch", "stash")]
    [string]$Method = "branch",

    [string]$CheckpointsFile = ""
)

# Ensure we're in a git repository
try {
    $gitRoot = git rev-parse --show-toplevel 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Not in a git repository"
        exit 1
    }
} catch {
    Write-Error "Git command failed: $_"
    exit 1
}

# Get current commit hash
$currentCommit = git rev-parse HEAD
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to get current commit"
    exit 1
}

# Check for uncommitted changes
$status = git status --porcelain
$hasChanges = $null -ne $status -and $status.Length -gt 0

# Create checkpoint based on method
$checkpointData = @{
    name = $CheckpointName
    method = $Method
    commit = $currentCommit
    timestamp = (Get-Date -Format "o")
    description = $Description
    hasUncommittedChanges = $hasChanges
}

if ($Method -eq "branch") {
    # Check if branch already exists
    $branchExists = git rev-parse --verify $CheckpointName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Warning "Branch $CheckpointName already exists, using as checkpoint"
    } else {
        # Create lightweight branch at current commit
        git branch $CheckpointName 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create checkpoint branch: $CheckpointName"
            exit 1
        }
    }
    Write-Host "Created checkpoint branch: $CheckpointName" -ForegroundColor Green

} elseif ($Method -eq "stash") {
    if ($hasChanges) {
        # Stash changes with descriptive message
        $stashMessage = "${CheckpointName}: $Description"
        git stash push -m $stashMessage 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to stash changes"
            exit 1
        }

        # Get stash reference
        $stashRef = git stash list | Select-String -Pattern $CheckpointName | Select-Object -First 1
        if ($stashRef) {
            $checkpointData["stashRef"] = ($stashRef -split ":")[0]
        }

        Write-Host "Stashed changes as: $CheckpointName" -ForegroundColor Green

        # Apply stash back to keep working directory intact
        git stash apply 2>&1 | Out-Null

    } else {
        Write-Warning "No uncommitted changes to stash, creating branch checkpoint instead"
        $checkpointData["method"] = "branch"
        git branch $CheckpointName 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to create checkpoint branch"
            exit 1
        }
        Write-Host "Created checkpoint branch (no changes to stash): $CheckpointName" -ForegroundColor Green
    }
}

# Update checkpoints file if specified
if ($CheckpointsFile -and (Test-Path (Split-Path $CheckpointsFile -Parent))) {
    try {
        if (Test-Path $CheckpointsFile) {
            $existingData = Get-Content $CheckpointsFile -Raw | ConvertFrom-Json
            $checkpoints = @($existingData.checkpoints)
        } else {
            $checkpoints = @()
        }

        $checkpoints += $checkpointData

        $fileData = @{
            checkpoints = $checkpoints
            lastUpdated = (Get-Date -Format "o")
        }

        $fileData | ConvertTo-Json -Depth 10 | Set-Content $CheckpointsFile
        Write-Host "Updated checkpoints file: $CheckpointsFile" -ForegroundColor Cyan
    } catch {
        Write-Warning "Failed to update checkpoints file: $_"
    }
}

# Output checkpoint data as JSON for parsing by caller
$checkpointData | ConvertTo-Json -Depth 5
