# Pass 4.5 Remediation Routing

1. Re-route license findings:
```powershell
.\scripts\Reroute-LicenseCompliance.ps1
```

2. Preview tag protection:
```powershell
.\scripts\Set-NonoReleaseTagProtection.ps1 -WhatIf
```

3. Apply:
```powershell
.\scripts\Set-NonoReleaseTagProtection.ps1
```

4. Verify:
```powershell
.\scripts\Test-NonoReleaseTagProtection.ps1
```

EMS-CTRL-020 is intentionally moved to POLICY_REVIEW because a missing LICENSE file is not sufficient evidence of dependency-license noncompliance.
