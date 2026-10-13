# Registers LavCamFilter.dll as a DirectShow source filter so it shows up
# in the Windows camera list. Run from an elevated PowerShell prompt.

param(
    [string]$DllPath = ".\native\vcam_filter\bin\Release\LavCamFilter.dll"
)

$regasm = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\RegAsm.exe"
if (-not (Test-Path $regasm)) {
    Write-Error "RegAsm not found. Install .NET Framework 4.x."
    exit 1
}
if (-not (Test-Path $DllPath)) {
    Write-Error "DLL not found at $DllPath. Build native/vcam_filter first."
    exit 1
}
& $regasm /codebase $DllPath
Write-Host "LavCamFilter registered. Restart any app that enumerates cameras."