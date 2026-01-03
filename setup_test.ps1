# Quick Setup for A/B Test
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          Vibecode A/B Test Setup                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "🚀 Setting up A/B test environment..." -ForegroundColor Green

$TestDir = ".\ab-test-results"

# Create directories
$dirs = @(
    "$TestDir\generic-ai-test",
    "$TestDir\vibecode-test",
    "$TestDir\logs",
    "$TestDir\screenshots",
    "$TestDir\analysis"
)

foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  ✓ Created: $dir" -ForegroundColor Gray
    } else {
        Write-Host "  ✓ Exists: $dir" -ForegroundColor DarkGray
    }
}

# Create universal prompt file
$promptContent = @'
Build a modern task management SaaS application called "TaskFlow" with the following features:

AUTHENTICATION & USER MANAGEMENT:
- Email/password authentication with email verification
- Google OAuth login
- Password reset functionality
- Two-factor authentication (TOTP)
- Role-based access: Admin, Manager, Member
- User profile management

SUBSCRIPTION & PAYMENTS:
- Three pricing tiers: Free (5 tasks), Pro (`$9/mo, 100 tasks), Business (`$29/mo, unlimited)
- Stripe integration for subscription management
- Customer portal for plan upgrades/cancellations
- Trial period: 14 days for Pro tier
- Usage tracking and enforcement

CORE FEATURES:
- Create, edit, delete tasks
- Assign tasks to team members
- Task priorities (Low, Medium, High, Urgent)
- Due dates with notifications
- Task comments and attachments
- Kanban board view
- List view with filters and sorting
- Real-time updates when team members make changes

TECHNICAL REQUIREMENTS:
- Next.js 15 with App Router and Server Components
- TypeScript throughout
- Modern UI with Tailwind CSS
- PostgreSQL database
- Proper error handling and loading states
- Responsive design (mobile-first)
- SEO optimization for marketing pages
- Comprehensive testing setup

DELIVERABLES:
- Complete source code
- Database schema and migrations
- Environment setup documentation
- Deployment configuration
- README with setup instructions
'@

$promptContent | Out-File -FilePath "$TestDir\universal-prompt.txt" -Encoding UTF8
Write-Host "  ✓ Created universal prompt file" -ForegroundColor Gray

# Create quick tracking template
$trackingContent = @'
# A/B Test Tracking Log

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Tester:** $env:USERNAME
**Test Type:** [Generic AI / Vibecode Studio]

## Timeline
- START: [Time]
- MILESTONE 1: [Time - What was accomplished]
- MILESTONE 2: [Time - What was accomplished]
- END: [Time]

## Prompts Used
1. [Initial prompt from universal-prompt.txt]
2. [Follow-up prompt]
3. [Clarifications]

## Issues Encountered
- Issue 1: [Description] - Time to fix: [X min]
- Issue 2: [Description] - Time to fix: [X min]

## Manual Fixes Required
- [Description of manual intervention]

## Final Score
Total Points: ___ / 100

### Breakdown:
- Code Quality (25): ___ 
- Authentication (20): ___
- Payments (20): ___
- Database (15): ___
- Testing (10): ___
- Security (10): ___

## Notes
[Your observations]
'@

$trackingContent | Out-File -FilePath "$TestDir\logs\tracking-template.md" -Encoding UTF8
Write-Host "  ✓ Created tracking template" -ForegroundColor Gray

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Test Environment Ready:" -ForegroundColor Yellow
Write-Host "  → Location: $TestDir"
Write-Host "  → Universal Prompt: $TestDir\universal-prompt.txt"
Write-Host "  → Tracking Template: $TestDir\logs\tracking-template.md"
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "OPTION A - FULL 4-HOUR TEST:" -ForegroundColor White
Write-Host "  1. Test with Generic AI (2 hours)" -ForegroundColor Gray
Write-Host "     • cd $TestDir\generic-ai-test"
Write-Host "     • npx create-next-app@latest . --typescript --tailwind --app"
Write-Host "     • Use GitHub Copilot with the universal prompt"
Write-Host "     • Track progress in logs folder"
Write-Host ""
Write-Host "  2. Test with Vibecode Studio (2 hours)" -ForegroundColor Gray
Write-Host "     • cd $TestDir\vibecode-test"
Write-Host "     • npx create-next-app@latest . --typescript --tailwind --app"
Write-Host "     • Run Vibecode: & '.\vibecode_studio.py'"
Write-Host "     • Provide the universal prompt"
Write-Host ""
Write-Host "OPTION B - QUICK 30-MIN DEMO:" -ForegroundColor White
Write-Host "  • Review EXPECTED_DIFFERENCES.md for code examples"
Write-Host "  • Use pre-written comparisons for presentation"
Write-Host "  • Skip full implementation"
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "  • Full Plan: AB_TEST_PLAN.md"
Write-Host "  • Quick Guide: QUICK_START_CHECKLIST.md"
Write-Host "  • Visual Overview: VISUAL_SUMMARY.md"
Write-Host "  • Code Examples: EXPECTED_DIFFERENCES.md"
Write-Host ""
Write-Host "Would you like to:" -ForegroundColor Yellow
Write-Host "  [1] Start Generic AI test now"
Write-Host "  [2] Start Vibecode test now"
Write-Host "  [3] Review documentation first"
Write-Host "  [4] Do quick 30-min demo instead"
Write-Host ""
$choice = Read-Host "Enter choice (1-4, or Enter to decide later)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "🤖 STARTING GENERIC AI TEST" -ForegroundColor Green
        Write-Host ""
        Write-Host "Instructions:" -ForegroundColor Yellow
        Write-Host "1. Open new VS Code window in: $TestDir\generic-ai-test"
        Write-Host "2. Initialize Next.js:" -ForegroundColor Cyan
        Write-Host "   npx create-next-app@latest . --typescript --tailwind --app --eslint"
        Write-Host "3. Copy prompt from: $TestDir\universal-prompt.txt" -ForegroundColor Cyan
        Write-Host "4. Use GitHub Copilot to implement features"
        Write-Host "5. Track time and progress"
        Write-Host ""
        Write-Host "⏱️  START YOUR TIMER NOW!" -ForegroundColor Red
        Write-Host ""
        code "$TestDir\universal-prompt.txt"
        code "$TestDir\logs\tracking-template.md"
        code "$TestDir\generic-ai-test"
    }
    "2" {
        Write-Host ""
        Write-Host "🎯 STARTING VIBECODE TEST" -ForegroundColor Green
        Write-Host ""
        Write-Host "Instructions:" -ForegroundColor Yellow
        Write-Host "1. Open new VS Code window in: $TestDir\vibecode-test"
        Write-Host "2. Initialize Next.js:" -ForegroundColor Cyan
        Write-Host "   npx create-next-app@latest . --typescript --tailwind --app --eslint"
        Write-Host "3. Copy prompt from: $TestDir\universal-prompt.txt" -ForegroundColor Cyan
        Write-Host "4. Run Vibecode Studio and provide prompt"
        Write-Host "5. Track time and progress"
        Write-Host ""
        Write-Host "⏱️  START YOUR TIMER NOW!" -ForegroundColor Red
        Write-Host ""
        code "$TestDir\universal-prompt.txt"
        code "$TestDir\logs\tracking-template.md"
        code "$TestDir\vibecode-test"
    }
    "3" {
        Write-Host ""
        Write-Host "📚 Opening documentation..." -ForegroundColor Green
        code "VISUAL_SUMMARY.md"
        code "AB_TEST_PLAN.md"
    }
    "4" {
        Write-Host ""
        Write-Host "⚡ QUICK 30-MIN DEMO MODE" -ForegroundColor Green
        Write-Host ""
        Write-Host "Opening comparison examples..." -ForegroundColor Yellow
        code "EXPECTED_DIFFERENCES.md"
        code "VISUAL_SUMMARY.md"
        Write-Host ""
        Write-Host "Use these pre-written examples in your presentation!" -ForegroundColor Cyan
    }
    default {
        Write-Host ""
        Write-Host "✅ Environment ready! Run this script again when you're ready to start." -ForegroundColor Green
    }
}

Write-Host ""
