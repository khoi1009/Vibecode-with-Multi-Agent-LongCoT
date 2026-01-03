# Cleanup script for GitHub Release
$folders_to_remove = @(
    "modern_logistics",
    "crypto_tracker",
    "nebula_board",
    "secure_fintech",
    "secure_ecommerce",
    "secure_enterprise",
    "social_agent",
    "complex_secure",
    "investor_demo",
    "ab-test-results",
    "high_confidence",
    # "venv", # Keep venv for local usage, ignored by git
    "__pycache__",
    "backend", 
    "frontend"
)

$files_to_remove = @(
    "debug_skills.py",
    "demo_build.py",
    "qa_report.log"
)

foreach ($folder in $folders_to_remove) {
    if (Test-Path $folder) {
        Write-Host "Removing $folder..."
        Remove-Item -Recurse -Force $folder
    }
}

foreach ($file in $files_to_remove) {
    if (Test-Path $file) {
        Write-Host "Removing $file..."
        Remove-Item -Force $file
    }
}

Write-Host "Cleanup Complete. Ready for git add."
