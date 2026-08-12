[CmdletBinding(SupportsShouldProcess)]
param(
    [string]$Config = (Join-Path (Split-Path -Parent $PSScriptRoot) "config\branch_governance.json"),
    [string]$EvidenceDir = (Join-Path (Split-Path -Parent $PSScriptRoot) "generated\branch-governance")
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required."
}

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "GitHub CLI is not authenticated. Run: gh auth login"
}

if (-not (Test-Path $Config)) {
    throw "Configuration file not found: $Config"
}

$cfg = Get-Content $Config -Raw | ConvertFrom-Json
$org = $cfg.organization
$repos = @($cfg.repositories)
$minimumApprovals = [int]$cfg.required_approving_review_count
$requireCodeOwners = [bool]$cfg.require_code_owner_reviews
$dismissStale = [bool]$cfg.dismiss_stale_reviews
$lastPushApproval = [bool]$cfg.require_last_push_approval

New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null

$summary = @()

function Invoke-GhJson {
    param(
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [switch]$AllowFailure
    )
    $output = & gh @Arguments 2>&1
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        if ($AllowFailure) {
            return [pscustomobject]@{
                Success = $false
                ExitCode = $code
                Raw = ($output -join "`n")
                Json = $null
            }
        }
        throw "gh $($Arguments -join ' ') failed:`n$($output -join "`n")"
    }

    $raw = ($output -join "`n")
    $obj = $null
    if ($raw.Trim()) {
        try { $obj = $raw | ConvertFrom-Json } catch {}
    }

    return [pscustomobject]@{
        Success = $true
        ExitCode = 0
        Raw = $raw
        Json = $obj
    }
}

foreach ($repoName in $repos) {
    $repo = "$org/$repoName"
    Write-Host "`n=== $repo ===" -ForegroundColor Cyan

    $repoInfo = Invoke-GhJson -Arguments @("api","repos/$repo")
    $branch = $repoInfo.Json.default_branch
    if (-not $branch) {
        throw "Could not determine default branch for $repo"
    }

    $before = Invoke-GhJson -Arguments @(
        "api",
        "repos/$repo/branches/$branch/protection"
    ) -AllowFailure

    $beforePath = Join-Path $EvidenceDir "$repoName-before.json"
    if ($before.Success) {
        $before.Raw | Set-Content $beforePath
    } else {
        @{
            repository = $repo
            default_branch = $branch
            protected = $false
            api_result = $before.Raw
        } | ConvertTo-Json -Depth 10 | Set-Content $beforePath
    }

    if (-not $before.Success) {
        # No classic branch protection exists. Create the minimum protection
        # needed for EMS-CTRL-011 without introducing unrelated requirements.
        $payload = @{
            required_status_checks = $null
            enforce_admins = $false
            required_pull_request_reviews = @{
                dismiss_stale_reviews = $dismissStale
                require_code_owner_reviews = $requireCodeOwners
                required_approving_review_count = $minimumApprovals
                require_last_push_approval = $lastPushApproval
            }
            restrictions = $null
        }

        $payloadPath = Join-Path $EvidenceDir "$repoName-create-protection.json"
        $payload | ConvertTo-Json -Depth 10 | Set-Content $payloadPath

        if ($PSCmdlet.ShouldProcess(
            "$repo ($branch)",
            "Create branch protection requiring PR review and Code Owner review"
        )) {
            & gh api `
                --method PUT `
                "repos/$repo/branches/$branch/protection" `
                --input $payloadPath | Out-Null

            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create branch protection for $repo"
            }
        }
    }
    else {
        # Protection already exists. Patch ONLY pull-request review settings.
        # Preserve any approval count above our baseline.
        $reviewResult = Invoke-GhJson -Arguments @(
            "api",
            "repos/$repo/branches/$branch/protection/required_pull_request_reviews"
        ) -AllowFailure

        $existingApprovals = 0
        if ($reviewResult.Success -and $reviewResult.Json.required_approving_review_count -ne $null) {
            $existingApprovals = [int]$reviewResult.Json.required_approving_review_count
        }
        $targetApprovals = [Math]::Max($minimumApprovals, $existingApprovals)

        $payload = @{
            require_code_owner_reviews = $requireCodeOwners
            required_approving_review_count = $targetApprovals
        }

        # Only set these if there was no existing review configuration. This avoids
        # modifying established review behavior unnecessarily.
        if (-not $reviewResult.Success) {
            $payload.dismiss_stale_reviews = $dismissStale
            $payload.require_last_push_approval = $lastPushApproval
        }

        $payloadPath = Join-Path $EvidenceDir "$repoName-patch-reviews.json"
        $payload | ConvertTo-Json -Depth 10 | Set-Content $payloadPath

        if ($PSCmdlet.ShouldProcess(
            "$repo ($branch)",
            "Require pull-request approval and Code Owner review"
        )) {
            if ($reviewResult.Success) {
                & gh api `
                    --method PATCH `
                    "repos/$repo/branches/$branch/protection/required_pull_request_reviews" `
                    --input $payloadPath | Out-Null
            }
            else {
                # Branch is protected, but pull-request reviews are not configured.
                # The sub-resource does not exist yet, so update the full protection
                # while preserving known top-level values.
                $current = $before.Json

                $fullPayload = @{
                    required_status_checks = $null
                    enforce_admins = [bool]$current.enforce_admins.enabled
                    required_pull_request_reviews = @{
                        dismiss_stale_reviews = $dismissStale
                        require_code_owner_reviews = $requireCodeOwners
                        required_approving_review_count = $targetApprovals
                        require_last_push_approval = $lastPushApproval
                    }
                    restrictions = $null
                }

                # Preserve current status-check configuration if present.
                if ($current.required_status_checks) {
                    $contexts = @()
                    if ($current.required_status_checks.contexts) {
                        $contexts = @($current.required_status_checks.contexts)
                    }
                    $fullPayload.required_status_checks = @{
                        strict = [bool]$current.required_status_checks.strict
                        contexts = $contexts
                    }
                }

                $fullPath = Join-Path $EvidenceDir "$repoName-update-protection.json"
                $fullPayload | ConvertTo-Json -Depth 10 | Set-Content $fullPath

                & gh api `
                    --method PUT `
                    "repos/$repo/branches/$branch/protection" `
                    --input $fullPath | Out-Null
            }

            if ($LASTEXITCODE -ne 0) {
                throw "Failed to update review protection for $repo"
            }
        }
    }

    if ($WhatIfPreference) {
        $summary += [pscustomobject]@{
            Repository = $repo
            DefaultBranch = $branch
            BeforeProtected = $before.Success
            Result = "WHATIF"
        }
        continue
    }

    $after = Invoke-GhJson -Arguments @(
        "api",
        "repos/$repo/branches/$branch/protection"
    ) -AllowFailure

    $afterPath = Join-Path $EvidenceDir "$repoName-after.json"
    if ($after.Success) {
        $after.Raw | Set-Content $afterPath
    }

    $prRequired = $false
    $codeOwnerRequired = $false
    $approvals = 0

    if ($after.Success -and $after.Json.required_pull_request_reviews) {
        $prRequired = $true
        $codeOwnerRequired = [bool]$after.Json.required_pull_request_reviews.require_code_owner_reviews
        $approvals = [int]$after.Json.required_pull_request_reviews.required_approving_review_count
    }

    $status = if ($prRequired -and $codeOwnerRequired -and $approvals -ge 1) { "PASS" } else { "WARNING" }

    $summary += [pscustomobject]@{
        Repository = $repo
        DefaultBranch = $branch
        BeforeProtected = $before.Success
        PullRequestRequired = $prRequired
        CodeOwnerReviewRequired = $codeOwnerRequired
        ApprovalsRequired = $approvals
        EMS_CTRL_011 = $status
    }
}

Write-Host "`n=== EMS Branch Governance Summary ===" -ForegroundColor Green
$summary | Format-Table -AutoSize

$summary | ConvertTo-Json -Depth 10 |
    Set-Content (Join-Path $EvidenceDir "branch-governance-summary.json")
