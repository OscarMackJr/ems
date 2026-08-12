# HS-SECURITY-DATA-GOVERNANCE
# Wave 2B.2 disabled collector scaffold.
# Controls: EMS-CTRL-023;EMS-CTRL-024;EMS-CTRL-063;EMS-CTRL-065;EMS-CTRL-066
# MUST emit direct operating evidence only; never infer PASS from catalogs, policy, scope, or prior compliance.
[CmdletBinding()]
param([string]$EMSPath="C:\temp\standars\ems")
$ErrorActionPreference="Stop"
throw "HS-SECURITY-DATA-GOVERNANCE is scaffolded but not implemented. Implement source-specific operating evidence collection before enabling."
