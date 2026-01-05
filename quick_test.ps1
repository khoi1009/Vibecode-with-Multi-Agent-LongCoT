# Quick Test Script for Vibecode Autonomous Development
# PowerShell version for Windows

Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  VIBECODE AUTONOMOUS DEV - QUICK TEST" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════" -ForegroundColor Cyan

# Test configuration
$ProjectName = "test-blog-app"
$Description = "A simple blog platform with Next.js. Include homepage, post listing, individual post pages, and about page. Use Tailwind CSS."

Write-Host "`n📋 Test Configuration:" -ForegroundColor Yellow
Write-Host "  Project: $ProjectName" -ForegroundColor White
Write-Host "  Description: $Description" -ForegroundColor White

# Run the test
Write-Host "`n🚀 Starting automated test..." -ForegroundColor Green
python test_autonomous_dev.py

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Test completed successfully!" -ForegroundColor Green
} else {
    Write-Host "`n❌ Test failed. Check logs for details." -ForegroundColor Red
}

Write-Host "`n📂 Generated files:" -ForegroundColor Yellow
Write-Host "  • $ProjectName/" -ForegroundColor White
Write-Host "  • $ProjectName/docs/vibecode_plan.md" -ForegroundColor White
Write-Host "  • ${ProjectName}_build_log.txt" -ForegroundColor White

Write-Host "`n🎯 Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review plan: cat $ProjectName/docs/vibecode_plan.md" -ForegroundColor White
Write-Host "  2. Run project: cd $ProjectName; npm run dev" -ForegroundColor White
Write-Host "  3. Open browser: http://localhost:3000" -ForegroundColor White

Read-Host "`nPress Enter to exit"
