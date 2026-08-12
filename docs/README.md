# Wave 1 Adjudication Fix

The initial adjudication builder used `REVIEW` as the generic fallback for WARNING rows,
while the controlled disposition schema intentionally allowed only:

- REMEDIATE
- COLLECTOR_REVIEW
- POLICY_REVIEW
- CONFIRM_NA
- ACCEPT
- EXCEPTION_REQUEST
- DEFER

This patch removes the ambiguous `REVIEW` state.

Generic WARNING outcomes now default to:

`COLLECTOR_REVIEW`

## Apply

```powershell
.\scripts\Apply-Adjudication-Fix.ps1
```

Then rerun:

```powershell
cd C:\temp\standars\Pass4_5
.\scripts\Run-Wave1Adjudication.ps1
```

Expected validation result:

`PASS`
