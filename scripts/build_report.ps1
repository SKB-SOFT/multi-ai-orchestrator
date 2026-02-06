param(
    [string]$Input = "docs/report-generated.md",
    [string]$Output = "docs/report.pdf"
)

if (-Not (Test-Path $Input)) {
    Write-Error "Input report not found: $Input. Generate it first with python server/scripts/generate_report.py"
    exit 1
}

$Pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-Not $Pandoc) {
    Write-Error "pandoc not found. Install it from https://pandoc.org/installing.html"
    exit 1
}

pandoc $Input -o $Output
Write-Host "Report generated: $Output"
