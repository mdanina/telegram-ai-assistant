<#
.SYNOPSIS
    Reverts to a git checkpoint for Time Travel recovery.

.DESCRIPTION
    Restores the working directory to a previous checkpoint state.
    Supports checkout, stash apply, and hard reset methods.

.PARAMETER CheckpointName
    Name of the checkpoint to revert to (branch name or stash reference)

.PARAMETER HardReset
    Perform a hard reset (destructive - discards all changes)

.PARAMETER PreserveChanges
    Stash current changes before reverting (default: true)

.PARAMETER CheckpointsFile
    Path to checkpoints.json file (optional, for ADW integration)

.EXAMPLE
    .\revert.ps1 -CheckpointName "tt_build_20260117_143000"

.EXAMPLE
    .\revert.ps1 -CheckpointName "tt_build_20260117_143000" -HardReset

.EXAMPLE
    .\revert.ps1 -CheckpointName "tt_build_20260117_143000" -PreserveChanges:$false
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$CheckpointName,

    [switch]$HardReset,

    [bool]$PreserveChanges = $true,

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

# Get current state info
$currentBranch = git rev-parse --abbrev-ref HEAD
$currentCommit = git rev-parse HEAD

# Check for uncommitted changes
$status = git status --porcelain
$hasChanges = $null -ne $status -and $status.Length -gt 0

# Prepare revert data
$revertData = @{
    checkpointName = $CheckpointName
    fromBranch = $currentBranch
    fromCommit = $currentCommit
    timestamp = (Get-Date -Format "o")
    hadUncommittedChanges = $hasChanges
    preservedChanges = $false
    method = "unknown"
}

# Preserve current changes if requested and changes exist
if ($PreserveChanges -and $hasChanges) {
    $preserveStashName = "pre-revert-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "Preserving current changes to stash: $preserveStashName" -ForegroundColor Yellow

    git stash push -m $preserveStashName 2>&1
    if ($LASTEXITCODE -eq 0) {
        $revertData["preservedChanges"] = $true
        $revertData["preserveStashName"] = $preserveStashName
        Write-Host "Changes preserved successfully" -ForegroundColor Green
    } else {
        Write-Warning "Failed to preserve changes, continuing anyway"
    }
}

# Determine checkpoint type and revert method
$isBranch = $false
$isStash = $false

# Check if it's a branch
$branchCheck = git rev-parse --verify $CheckpointName 2>&1
if ($LASTEXITCODE -eq 0) {
    $isBranch = $true
}

# Check if it's a stash
$stashList = git stash list | Select-String -Pattern $CheckpointName
if ($stashList) {
    $isStash = $true
    $stashRef = ($stashList -split ":")[0]
}

# Perform the revert
if ($HardReset -and $isBranch) {
    # Hard reset to branch (most destructive)
    Write-Host "Performing hard reset to: $CheckpointName" -ForegroundColor Red
    git reset --hard $CheckpointName 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Hard reset failed"
        exit 1
    }
    $revertData["method"] = "hard_reset"
    Write-Host "Hard reset completed successfully" -ForegroundColor Green

} elseif ($isBranch) {
    # Check for uncommitted changes that would block checkout
    $currentStatus = git status --porcelain
    if ($null -ne $currentStatus -and $currentStatus.Length -gt 0) {
        Write-Warning "Uncommitted changes detected, attempting checkout anyway"
    }

    # Checkout the branch
    Write-Host "Checking out checkpoint: $CheckpointName" -ForegroundColor Cyan
    $checkoutResult = git checkout $CheckpointName 2>&1
    if ($LASTEXITCODE -ne 0) {
        if ($HardReset -eq $false) {
            Write-Error "Checkout failed. Use -HardReset to force, or commit/stash changes first."
            Write-Error "Error: $checkoutResult"
            exit 1
        }
    }
    $revertData["method"] = "checkout"
    Write-Host "Checkout completed successfully" -ForegroundColor Green

} elseif ($isStash) {
    # Apply the stash
    Write-Host "Applying stash: $stashRef ($CheckpointName)" -ForegroundColor Cyan
    git stash apply $stashRef 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to apply stash: $stashRef"
        exit 1
    }
    $revertData["method"] = "stash_apply"
    $revertData["stashRef"] = $stashRef
    Write-Host "Stash applied successfully" -ForegroundColor Green

} else {
    Write-Error "Checkpoint not found: $CheckpointName"
    Write-Host "Available branches:" -ForegroundColor Yellow
    git branch --list "tt_*" | ForEach-Object { Write-Host "  $_" }
    Write-Host "Available stashes with 'tt_':" -ForegroundColor Yellow
    git stash list | Select-String "tt_" | ForEach-Object { Write-Host "  $_" }
    exit 1
}

# Update checkpoints file if specified
if ($CheckpointsFile -and (Test-Path $CheckpointsFile)) {
    try {
        $existingData = Get-Content $CheckpointsFile -Raw | ConvertFrom-Json

        # Add revert event
        if (-not $existingData.reverts) {
            $existingData | Add-Member -NotePropertyName "reverts" -NotePropertyValue @()
        }

        $revertEvent = @{
            fromCheckpoint = $currentCommit
            toCheckpoint = $CheckpointName
            timestamp = (Get-Date -Format "o")
            method = $revertData["method"]
            preservedChanges = $revertData["preservedChanges"]
        }

        $existingData.reverts += $revertEvent
        $existingData.lastUpdated = (Get-Date -Format "o")

        $existingData | ConvertTo-Json -Depth 10 | Set-Content $CheckpointsFile
        Write-Host "Updated checkpoints file with revert event" -ForegroundColor Cyan
    } catch {
        Write-Warning "Failed to update checkpoints file: $_"
    }
}

# Output revert data as JSON
Write-Host "`nRevert Summary:" -ForegroundColor Cyan
$revertData | ConvertTo-Json -Depth 5
