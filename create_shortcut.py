import os
import subprocess
from pathlib import Path

proj_dir = Path(__file__).parent.resolve()
vbs_path = proj_dir / "Launch_Silent.vbs"
edge_exe = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

ps_commands = f"""
$ws = New-Object -ComObject WScript.Shell
$destPaths = @(
    [Environment]::GetFolderPath('Desktop'),
    (Join-Path $env:USERPROFILE 'Desktop')
) | Select-Object -Unique

foreach ($d in $destPaths) {{
    if (Test-Path $d) {{
        $linkPath = Join-Path $d 'E.C.H.O.-7 Terminal.lnk'
        $s = $ws.CreateShortcut($linkPath)
        $s.TargetPath = 'wscript.exe'
        $s.Arguments = '\"{vbs_path}\"'
        $s.WorkingDirectory = '\"{proj_dir}\"'
        $s.Description = 'Launch E.C.H.O.-7 Social Robot Voice Terminal'
        if (Test-Path '{edge_exe}') {{
            $s.IconLocation = '{edge_exe},0'
        }} else {{
            $s.IconLocation = 'shell32.dll,14'
        }}
        $s.Save()
        Write-Output "Created: $linkPath"
    }}
}}
"""

res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_commands], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print("Error:", res.stderr)
