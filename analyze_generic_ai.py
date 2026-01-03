"""
Analyze the Generic AI's TaskFlow code using Long CoT Scanner
"""
import os
import sys
from pathlib import Path
from core.longcot_scanner import LongCoTScanner

def analyze_generic_ai_code():
    """Run Long CoT analysis on generic AI's generated TaskFlow app"""
    
    generic_ai_path = "ab-test-results/generic-ai-test"
    
    print("=" * 70)
    print("  A/B TEST: Long CoT Analysis of Generic AI's Code")
    print("=" * 70)
    print(f"\n📂 Analyzing: {generic_ai_path}")
    print("🎯 Objective: Validate '80% complete' claim\n")
    
    # Initialize Long CoT Scanner
    scanner = LongCoTScanner(project_path=generic_ai_path)
    
    # Run analysis
    results = scanner.scan_with_longcot()
    
    # Extract key metrics
    print("\n" + "=" * 70)
    print("  LONG COT ANALYSIS RESULTS")
    print("=" * 70)
    
    # Architecture analysis
    arch = results.get('architecture', {})
    print(f"\n🏗️  ARCHITECTURE:")
    print(f"   Type: {arch.get('type', 'unknown')}")
    print(f"   Description: {arch.get('description', 'N/A')}")
    print(f"   Confidence: {arch.get('confidence', 0):.1%}")
    
    # Module analysis
    modules = results.get('modules', {})
    print(f"\n🧩  MODULES ANALYZED: {len(modules)}")
    
    total_files = 0
    total_loc = 0
    low_confidence_modules = []
    
    for mod_name, mod_data in modules.items():
        files = mod_data.get('file_count', 0)
        loc = mod_data.get('lines_of_code', 0)
        conf = mod_data.get('confidence', 0)
        complexity = mod_data.get('complexity', 'unknown')
        
        total_files += files
        total_loc += loc
        
        print(f"   • {mod_name}/ - {files} files, {loc} LOC, {complexity} complexity")
        print(f"     Confidence: {conf:.1%}")
        
        if conf < 0.5:
            low_confidence_modules.append((mod_name, conf))
    
    print(f"\n   Total: {total_files} files, {total_loc:,} LOC")
    
    # Critical paths
    critical = results.get('critical_paths', {})
    core_mods = critical.get('core_modules', [])
    print(f"\n⚡  CRITICAL PATHS:")
    print(f"   Core modules: {len(core_mods)}")
    for mod in core_mods:
        deps = mod.get('dependency_count', 0)
        print(f"      → {mod.get('name', 'unknown')} ({deps} deps)")
    
    # Entry points
    entry_points = critical.get('entry_points', [])
    if entry_points:
        print(f"   Entry points: {len(entry_points)}")
        for ep in entry_points[:3]:  # Show first 3
            print(f"      → {ep}")
    
    # Reasoning quality
    stats = results.get('statistics', {})
    print(f"\n🧠  REASONING QUALITY:")
    print(f"   Reasoning depth: {stats.get('reasoning_steps', 0)} steps")
    print(f"   Reflections: {stats.get('reflection_count', 0)}")
    print(f"   Backtracks: {stats.get('backtrack_count', 0)}")
    print(f"   Average confidence: {stats.get('avg_confidence', 0):.1%}")
    
    # Issues and warnings
    print(f"\n⚠️   ISSUES DETECTED:")
    
    if low_confidence_modules:
        print(f"   • {len(low_confidence_modules)} modules with low confidence (<50%):")
        for mod_name, conf in low_confidence_modules:
            print(f"      - {mod_name}: {conf:.1%}")
    else:
        print(f"   ✅ All modules have acceptable confidence (≥50%)")
    
    reflections = results.get('reflections', [])
    warnings = [r for r in reflections if 'warning' in r.lower() or 'issue' in r.lower()]
    
    if warnings:
        print(f"\n   • {len(warnings)} warnings from reflection:")
        for w in warnings[:3]:  # Show first 3
            print(f"      - {w}")
    
    insights = results.get('validated_insights', [])
    if insights and isinstance(insights, list):
        print(f"\n✅  VALIDATED INSIGHTS:")
        for insight in list(insights)[:3]:  # Show first 3
            print(f"   ✓ {insight}")
    
    # Overall verdict
    overall_conf = stats.get('avg_confidence', 0)
    print(f"\n" + "=" * 70)
    print("  VERDICT")
    print("=" * 70)
    
    if overall_conf >= 0.8:
        verdict = "🟢 HIGH QUALITY"
        status = "Excellent architecture and implementation"
    elif overall_conf >= 0.6:
        verdict = "🟡 ACCEPTABLE QUALITY"
        status = "Good implementation with some concerns"
    else:
        verdict = "🔴 LOW QUALITY"
        status = "Significant issues detected"
    
    print(f"\n{verdict}")
    print(f"Overall Confidence: {overall_conf:.1%}")
    print(f"Status: {status}")
    
    # Compare with claim
    print(f"\n📊 CLAIM VALIDATION:")
    print(f"   Generic AI claimed: 80% complete")
    print(f"   Long CoT measured: {overall_conf:.1%} confidence")
    
    if abs(overall_conf - 0.8) < 0.1:
        print(f"   ✅ Claim appears ACCURATE")
    elif overall_conf < 0.7:
        print(f"   ⚠️  Claim may be OPTIMISTIC")
    else:
        print(f"   ✅ Quality EXCEEDS claimed completeness")
    
    print(f"\n📄 Detailed reports saved to: {generic_ai_path}/.vibecode/longcot/")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    analyze_generic_ai_code()
