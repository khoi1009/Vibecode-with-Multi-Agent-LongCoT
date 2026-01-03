"""
Test Long CoT Integration with Orchestrator
Validates that Long CoT scanner is properly integrated
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.orchestrator import Orchestrator


def test_longcot_integration():
    """Test Long CoT integration with orchestrator"""
    
    print("="*70)
    print("🧪 TESTING LONG COT INTEGRATION")
    print("="*70)
    
    # Initialize orchestrator (should auto-run Long CoT scan)
    workspace = Path.cwd()
    print(f"\n📂 Workspace: {workspace}")
    print("\n1️⃣ Initializing Orchestrator (will trigger Long CoT scan)...")
    print("-"*70)
    
    orchestrator = Orchestrator(workspace)
    
    # Check if Long CoT analysis ran
    print("\n" + "="*70)
    print("2️⃣ VALIDATION CHECKS")
    print("="*70)
    
    checks = []
    
    # Check 1: Long CoT scanner initialized
    check1 = hasattr(orchestrator, 'longcot_scanner')
    checks.append(("Long CoT Scanner Initialized", check1))
    print(f"\n✓ Long CoT Scanner: {'✅ PASS' if check1 else '❌ FAIL'}")
    
    # Check 2: Analysis completed
    check2 = orchestrator.longcot_analysis is not None
    checks.append(("Long CoT Analysis Completed", check2))
    print(f"✓ Analysis Completed: {'✅ PASS' if check2 else '❌ FAIL'}")
    
    if check2:
        # Check 3: Architecture detected
        arch = orchestrator.longcot_analysis.get('architecture', {})
        arch_type = arch.get('type', 'unknown')
        arch_conf = arch.get('confidence', 0.0)
        
        check3 = arch_conf > 0.5
        checks.append(("Architecture Confidence > 50%", check3))
        
        print(f"\n📊 ANALYSIS RESULTS:")
        print(f"   • Architecture: {arch_type}")
        print(f"   • Confidence: {arch_conf:.1%} {'✅ PASS' if check3 else '❌ FAIL'}")
        
        # Check 4: Modules analyzed
        modules = orchestrator.longcot_analysis.get('modules', {})
        check4 = len(modules) > 0
        checks.append(("Modules Analyzed", check4))
        print(f"   • Modules: {len(modules)} {'✅ PASS' if check4 else '❌ FAIL'}")
        
        # Check 5: Critical paths identified
        critical = orchestrator.longcot_analysis.get('critical_paths', {})
        core_modules = critical.get('core_modules', [])
        entry_points = critical.get('entry_points', [])
        
        check5 = len(core_modules) > 0 or len(entry_points) > 0
        checks.append(("Critical Paths Identified", check5))
        print(f"   • Core Modules: {len(core_modules)} {'✅ PASS' if check5 else '❌ FAIL'}")
        print(f"   • Entry Points: {len(entry_points)}")
        
        # Check 6: Overall confidence
        overall_conf = orchestrator.longcot_analysis['statistics']['avg_confidence']
        check6 = overall_conf > 0.7
        checks.append(("Overall Confidence > 70%", check6))
        print(f"   • Overall Confidence: {overall_conf:.1%} {'✅ PASS' if check6 else '❌ FAIL'}")
    
    # Check 7: Status includes Long CoT info
    print(f"\n3️⃣ CHECKING ORCHESTRATOR STATUS")
    print("-"*70)
    status = orchestrator.get_status()
    check7 = 'longcot' in status
    checks.append(("Status Includes Long CoT", check7))
    
    print(f"\n📋 Status Report:")
    for key, value in status.items():
        if key == 'longcot':
            print(f"   • {key}: {value} {'✅ PASS' if check7 else '❌ FAIL'}")
        else:
            print(f"   • {key}: {value}")
    
    # Check 8: Test confidence-based routing
    print(f"\n4️⃣ TESTING CONFIDENCE-BASED ROUTING")
    print("-"*70)
    
    if orchestrator.longcot_analysis:
        confidence = orchestrator.longcot_analysis['statistics']['avg_confidence']
        
        if confidence >= 0.8:
            print(f"✅ HIGH CONFIDENCE MODE ({confidence:.1%})")
            print(f"   → Safe for autonomous execution")
            check8 = True
        elif confidence >= 0.5:
            print(f"⚠️  MEDIUM CONFIDENCE ({confidence:.1%})")
            print(f"   → Proceed with caution, manual review advised")
            check8 = True
        else:
            print(f"❌ LOW CONFIDENCE ({confidence:.1%})")
            print(f"   → Requires approval for destructive operations")
            check8 = True
        
        checks.append(("Confidence Routing Works", check8))
    else:
        checks.append(("Confidence Routing Works", False))
        print("❌ No analysis available for routing test")
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print(f"\nResults: {passed}/{total} checks passed")
    print("\nDetailed Results:")
    for i, (name, result) in enumerate(checks, 1):
        status_icon = "✅" if result else "❌"
        print(f"  {i}. {status_icon} {name}")
    
    # Final verdict
    print("\n" + "="*70)
    if passed == total:
        print("🎉 ALL TESTS PASSED! Long CoT integration successful!")
    elif passed >= total * 0.7:
        print("⚠️  MOSTLY PASSING: Integration works but has minor issues")
    else:
        print("❌ TESTS FAILED: Integration needs fixes")
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    try:
        success = test_longcot_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST CRASHED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
