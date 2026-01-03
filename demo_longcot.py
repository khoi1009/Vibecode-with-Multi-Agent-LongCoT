"""
Demo: Long Chain-of-Thought Scanner
Test the new ToT-based reasoning on Vibecode itself
"""

import sys
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from core.longcot_scanner import LongCoTScanner


def main():
    print("=" * 70)
    print("  DEMO: Long Chain-of-Thought Scanner")
    print("  Testing on Vibecode Studio itself")
    print("=" * 70)
    
    # Scan current directory
    project_path = Path(__file__).parent
    scanner = LongCoTScanner(project_path)
    
    print(f"\n📂 Project: {project_path}")
    print(f"🎯 Objective: Demonstrate Long CoT vs traditional scanning\n")
    
    # Run Long CoT scan
    results = scanner.scan_with_longcot()
    
    # Show key insights
    print("\n" + "=" * 70)
    print("  KEY INSIGHTS FROM LONG COT REASONING")
    print("=" * 70)
    
    print(f"\n🏗️  ARCHITECTURE:")
    print(f"   Type: {results['architecture']['type']}")
    print(f"   {results['architecture']['description']}")
    print(f"   Confidence: {results['architecture']['confidence']:.1%}")
    
    print(f"\n🧩  MODULES ANALYZED:")
    for module_name, module_data in results['modules'].items():
        print(f"   • {module_name}/ - {module_data['file_analysis']['total_files']} files, "
              f"{module_data['file_analysis']['total_lines']} LOC "
              f"({module_data['file_analysis']['complexity_estimate']} complexity)")
    
    print(f"\n⚡  CRITICAL PATHS:")
    if results['critical_paths']['entry_points']:
        print(f"   Entry points: {len(results['critical_paths']['entry_points'])}")
        for ep in results['critical_paths']['entry_points'][:3]:
            print(f"      → {ep['file']}")
    
    if results['critical_paths']['core_modules']:
        print(f"   Core modules: {len(results['critical_paths']['core_modules'])}")
        for cm in results['critical_paths']['core_modules'][:3]:
            print(f"      → {cm['name']} ({cm['dependency_count']} deps)")
    
    print(f"\n🧠  REASONING QUALITY:")
    stats = results['statistics']
    print(f"   Reasoning depth: {stats['reasoning_depth']} steps")
    print(f"   Reflections: {stats['reflection_count']}")
    print(f"   Average confidence: {stats['avg_confidence']:.1%}")
    
    print(f"\n💭  REFLECTIONS:")
    for i, reflection in enumerate(results['reasoning_chain']['reflections'], 1):
        print(f"   {i}. {reflection}")
    
    print(f"\n✅  VALIDATED INSIGHTS:")
    for insight in results['validated_insights']['validated_insights']:
        print(f"   {insight}")
    
    if results['validated_insights']['warnings']:
        print(f"\n⚠️   WARNINGS:")
        for warning in results['validated_insights']['warnings']:
            print(f"   {warning}")
    
    print("\n" + "=" * 70)
    print("  COMPARISON: Long CoT vs Traditional Scanning")
    print("=" * 70)
    
    print("\n📊 Traditional Scanner:")
    print("   ❌ Linear file enumeration")
    print("   ❌ No reasoning about architecture")
    print("   ❌ No confidence scores")
    print("   ❌ No reflection or validation")
    print("   ❌ Limited context understanding")
    
    print("\n🧠 Long CoT Scanner:")
    print("   ✅ Tree-of-Thought exploration")
    print("   ✅ Multi-hypothesis generation")
    print(f"   ✅ Confidence tracking ({stats['avg_confidence']:.1%} final)")
    print(f"   ✅ {stats['reflection_count']} reflection steps")
    print("   ✅ Hierarchical understanding")
    print("   ✅ Critical path identification")
    
    print("\n" + "=" * 70)
    print(f"  Reports saved to: {scanner.longcot_dir}/")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    results = main()
    
    print("\n🎉 Demo complete!")
    print("\nNext steps:")
    print("1. Check .vibecode/longcot/ for detailed reports")
    print("2. Compare with traditional scanner output")
    print("3. Integrate into orchestrator.py")
    print("4. Test on larger codebases (100K+ LOC)")
