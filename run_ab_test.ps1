# A/B Test Execution Script
# Automates setup and tracking for Vibecode vs Generic AI comparison

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("setup", "start-generic", "start-vibecode", "analyze")]
    [string]$Action = "setup"
)

$TestDir = ".\ab-test-results"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"

function Show-Banner {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          Vibecode A/B Test Automation                 ║" -ForegroundColor Cyan
    Write-Host "║   Comparing Generic AI vs Vibecode Studio Impact     ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Setup-TestEnvironment {
    Write-Host "🚀 Setting up A/B test environment..." -ForegroundColor Green
    
    # Create test directories
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
        }
    }
    
    # Create prompt file
    $promptContent = @"
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
"@
    
    $promptContent | Out-File -FilePath "$TestDir\universal-prompt.txt" -Encoding UTF8
    Write-Host "  ✓ Created universal prompt file" -ForegroundColor Gray
    
    # Create tracking template
    $trackingTemplate = @"
# Test Log: [TEST_NAME]

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Tester:** $env:USERNAME
**Duration:** [TO BE FILLED]

---

## Timeline

| Time | Event | Notes |
|------|-------|-------|
| 0:00 | Started with prompt | |
| 0:15 | | |
| 0:30 | | |
| 0:45 | | |
| 1:00 | | |
| 1:30 | | |
| 2:00 | Test complete | |

---

## Prompts Used

1. **Initial prompt:** [From universal-prompt.txt]
2. **Follow-up 1:** 
3. **Follow-up 2:** 
4. **Clarifications:** 

---

## Issues Encountered

- [ ] **Issue 1:** 
  - Description:
  - Time to fix:
  - Resolution:

- [ ] **Issue 2:**
  - Description:
  - Time to fix:
  - Resolution:

---

## Manual Interventions

- **Searched docs for:** [topic] - [X minutes]
- **Fixed code manually:** [description] - [X minutes]
- **Asked clarifying questions:** [X times]

---

## Final Statistics

- **Lines of code generated:** 
- **Files created:** 
- **Manual fixes required:** 
- **Time to working demo:** 
- **Compilation errors:** 
- **Runtime errors:** 
- **Test coverage:** 
- **Security issues found:** 

---

## Feature Completeness

| Feature | Implemented | Working | Quality (1-5) | Notes |
|---------|-------------|---------|---------------|-------|
| Email/password auth | ☐ | ☐ | /5 | |
| OAuth (Google) | ☐ | ☐ | /5 | |
| Email verification | ☐ | ☐ | /5 | |
| 2FA/TOTP | ☐ | ☐ | /5 | |
| Password reset | ☐ | ☐ | /5 | |
| RBAC | ☐ | ☐ | /5 | |
| Stripe integration | ☐ | ☐ | /5 | |
| Subscription tiers | ☐ | ☐ | /5 | |
| Usage tracking | ☐ | ☐ | /5 | |
| Task CRUD | ☐ | ☐ | /5 | |
| Task assignment | ☐ | ☐ | /5 | |
| Kanban view | ☐ | ☐ | /5 | |
| Real-time updates | ☐ | ☐ | /5 | |
| Responsive design | ☐ | ☐ | /5 | |
| Testing setup | ☐ | ☐ | /5 | |

---

## Code Quality Assessment

### Authentication (20 points)
- [ ] Modern auth framework used (5 pts)
- [ ] Email verification implemented (5 pts)
- [ ] OAuth with proper security (5 pts)
- [ ] 2FA/TOTP correct implementation (5 pts)

### Payment Integration (20 points)
- [ ] Latest Stripe SDK patterns (5 pts)
- [ ] Webhook signature verification (5 pts)
- [ ] Full subscription lifecycle (5 pts)
- [ ] Usage tracking & enforcement (5 pts)

### Code Quality (25 points)
- [ ] Next.js 15 best practices (5 pts)
- [ ] TypeScript strict mode (5 pts)
- [ ] Error handling (5 pts)
- [ ] File organization (5 pts)
- [ ] Documentation (5 pts)

### Database (15 points)
- [ ] Proper schema design (5 pts)
- [ ] Migrations setup (5 pts)
- [ ] Query optimization (5 pts)

### Testing & Production (10 points)
- [ ] Test coverage (5 pts)
- [ ] Environment validation (3 pts)
- [ ] Error monitoring (2 pts)

### Security (10 points)
- [ ] CSRF protection (3 pts)
- [ ] Rate limiting (3 pts)
- [ ] SQL injection prevention (2 pts)
- [ ] Secrets management (2 pts)

**Total Score:** ___ / 100

---

## Screenshots & Evidence

[Attach screenshots of:]
- Running application
- Code quality examples
- Test results
- Security scan results

---

## Overall Assessment

**Strengths:**
- 
- 

**Weaknesses:**
- 
- 

**Production Readiness:** ☐ Ready ☐ Needs Work ☐ Not Ready

**Would you ship this to production?** ☐ Yes ☐ With modifications ☐ No

---

## Conclusion

[Your summary of this test run]
"@
    
    $trackingTemplate | Out-File -FilePath "$TestDir\logs\TEMPLATE_test-log.md" -Encoding UTF8
    Write-Host "  ✓ Created tracking template" -ForegroundColor Gray
    
    # Create scoring script
    $scoringScript = @"
# Automated Code Analysis

Write-Host "Running automated code quality checks..." -ForegroundColor Cyan

`$projectPath = `$args[0]
if (-not `$projectPath) {
    Write-Host "Usage: .\scoring.ps1 <project-path>" -ForegroundColor Red
    exit 1
}

Set-Location `$projectPath

Write-Host "`n📊 Analysis Results`n" -ForegroundColor Green

# Count files and lines
`$files = Get-ChildItem -Recurse -File -Exclude node_modules,dist,.next
`$totalFiles = `$files.Count
`$totalLines = (`$files | Get-Content | Measure-Object -Line).Lines

Write-Host "Files: `$totalFiles"
Write-Host "Lines: `$totalLines"

# TypeScript check
if (Test-Path "tsconfig.json") {
    Write-Host "`nRunning TypeScript check..."
    npm run type-check 2>&1 | Tee-Object -Variable tscOutput
}

# Linting
if (Test-Path ".eslintrc*") {
    Write-Host "`nRunning ESLint..."
    npm run lint 2>&1 | Tee-Object -Variable lintOutput
}

# Tests
if (Test-Path "jest.config*" -or Test-Path "vitest.config*") {
    Write-Host "`nRunning tests..."
    npm run test 2>&1 | Tee-Object -Variable testOutput
}

# Security audit
Write-Host "`nRunning security audit..."
npm audit --json | ConvertFrom-Json | Tee-Object -Variable auditResults

Write-Host "`n✅ Analysis complete!" -ForegroundColor Green
"@
    
    $scoringScript | Out-File -FilePath "$TestDir\analysis\scoring.ps1" -Encoding UTF8
    Write-Host "  ✓ Created scoring script" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "✅ Setup complete! Test environment ready at: $TestDir" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review the universal prompt: $TestDir\universal-prompt.txt"
    Write-Host "  2. Start Generic AI test: .\run_ab_test.ps1 -Action start-generic"
    Write-Host "  3. Start Vibecode test: .\run_ab_test.ps1 -Action start-vibecode"
    Write-Host "  4. Analyze results: .\run_ab_test.ps1 -Action analyze"
    Write-Host ""
}

function Start-GenericAITest {
    Write-Host "🤖 Starting Generic AI Test..." -ForegroundColor Green
    
    $logFile = "$TestDir\logs\generic-ai_$Timestamp.md"
    Copy-Item "$TestDir\logs\TEMPLATE_test-log.md" $logFile
    (Get-Content $logFile) -replace '\[TEST_NAME\]', 'Generic AI (GitHub Copilot)' | Set-Content $logFile
    
    Write-Host ""
    Write-Host "📝 Instructions for Generic AI Test:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open VS Code in: $TestDir\generic-ai-test"
    Write-Host "2. Initialize Next.js project:"
    Write-Host "   npx create-next-app@latest . --typescript --tailwind --app --eslint" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Open the universal prompt file:"
    Write-Host "   $TestDir\universal-prompt.txt" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Use GitHub Copilot Chat to implement features"
    Write-Host "5. Track your progress in: $logFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏱️  Start timer now! (2 hour limit)" -ForegroundColor Red
    Write-Host ""
    
    # Open tracking log
    code $logFile
    
    Write-Host "Press Enter when test is complete..."
    Read-Host
    
    Write-Host "✅ Generic AI test logged!" -ForegroundColor Green
}

function Start-VibeCodeTest {
    Write-Host "🎯 Starting Vibecode Studio Test..." -ForegroundColor Green
    
    $logFile = "$TestDir\logs\vibecode_$Timestamp.md"
    Copy-Item "$TestDir\logs\TEMPLATE_test-log.md" $logFile
    (Get-Content $logFile) -replace '\[TEST_NAME\]', 'Vibecode Studio' | Set-Content $logFile
    
    Write-Host ""
    Write-Host "📝 Instructions for Vibecode Test:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Open terminal in: $TestDir\vibecode-test"
    Write-Host "2. Initialize Next.js project:"
    Write-Host "   npx create-next-app@latest . --typescript --tailwind --app --eslint" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "3. Launch Vibecode Studio:"
    Write-Host "   & '$PSScriptRoot\run.ps1'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Provide the universal prompt to Vibecode"
    Write-Host "5. Let multi-agent system work"
    Write-Host "6. Track progress in: $logFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏱️  Start timer now! (2 hour limit)" -ForegroundColor Red
    Write-Host ""
    
    # Open tracking log
    code $logFile
    
    Write-Host "Press Enter when test is complete..."
    Read-Host
    
    Write-Host "✅ Vibecode test logged!" -ForegroundColor Green
}

function Analyze-Results {
    Write-Host "📊 Analyzing Test Results..." -ForegroundColor Green
    Write-Host ""
    
    # Find most recent logs
    $genericLog = Get-ChildItem "$TestDir\logs" -Filter "generic-ai_*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $vibeCodeLog = Get-ChildItem "$TestDir\logs" -Filter "vibecode_*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if (-not $genericLog -or -not $vibeCodeLog) {
        Write-Host "❌ Missing test logs. Please run both tests first." -ForegroundColor Red
        return
    }
    
    Write-Host "Found test logs:" -ForegroundColor Cyan
    Write-Host "  Generic AI: $($genericLog.Name)"
    Write-Host "  Vibecode: $($vibeCodeLog.Name)"
    Write-Host ""
    
    # Create comparison report
    $comparisonReport = @"
# A/B Test Comparison Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

---

## Test Files

- **Generic AI Log:** $($genericLog.Name)
- **Vibecode Log:** $($vibeCodeLog.Name)

---

## Quick Comparison

| Metric | Generic AI | Vibecode Studio | Winner |
|--------|-----------|----------------|--------|
| Total Score | ___ / 100 | ___ / 100 | |
| Time to completion | | | |
| Features completed | | | |
| Code quality | | | |
| Security issues | | | |
| Test coverage | | | |
| Production ready | ☐ Yes ☐ No | ☐ Yes ☐ No | |

---

## Detailed Analysis

### Authentication Quality
- **Generic AI:** 
- **Vibecode:** 
- **Winner:** 

### Payment Integration
- **Generic AI:** 
- **Vibecode:** 
- **Winner:** 

### Code Architecture
- **Generic AI:** 
- **Vibecode:** 
- **Winner:** 

### Testing & Quality
- **Generic AI:** 
- **Vibecode:** 
- **Winner:** 

---

## ROI Calculation

### Generic AI
- Time spent: ___ hours
- Additional fixes needed: ___ hours
- **Total:** ___ hours

### Vibecode Studio
- Time spent: ___ hours
- Additional fixes needed: ___ hours
- **Total:** ___ hours

**Time Saved:** ___ hours
**Cost Saved (at `$100/hr):** `$___
**Percentage Improvement:** ___%

---

## Key Findings

### Strengths of Vibecode:
1. 
2. 
3. 

### Where Generic AI Competed:
1. 
2. 

### Most Impactful Skills Used:
- [ ] better-auth
- [ ] payment-integration
- [ ] web-frameworks
- [ ] databases
- [ ] testing

---

## Code Examples to Highlight

### Example 1: Authentication Setup
[Add side-by-side comparison]

### Example 2: Payment Webhooks
[Add side-by-side comparison]

### Example 3: Database Queries
[Add side-by-side comparison]

---

## Recommendation

Based on this test:
- [ ] Vibecode Studio shows clear superiority
- [ ] Generic AI is competitive
- [ ] Mixed results - context dependent

**For production projects, use:** _______________

**Estimated ROI per project:** _______________

---

## Next Steps

1. [ ] Share results with stakeholders
2. [ ] Create demo presentation
3. [ ] Document specific use cases where Vibecode excels
4. [ ] Plan wider rollout / marketing
"@
    
    $reportPath = "$TestDir\analysis\comparison_$Timestamp.md"
    $comparisonReport | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Host "✅ Comparison report created: $reportPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Fill in the comparison report with data from test logs"
    Write-Host "2. Run automated analysis on both projects"
    Write-Host "3. Take screenshots of key code differences"
    Write-Host "4. Create presentation from findings"
    Write-Host ""
    
    code $reportPath
}

# Main execution
Show-Banner

switch ($Action) {
    "setup" { Setup-TestEnvironment }
    "start-generic" { Start-GenericAITest }
    "start-vibecode" { Start-VibeCodeTest }
    "analyze" { Analyze-Results }
    default { 
        Write-Host "Invalid action. Use: setup, start-generic, start-vibecode, or analyze" -ForegroundColor Red
    }
}
