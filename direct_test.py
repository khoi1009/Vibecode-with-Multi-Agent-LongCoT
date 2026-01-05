#!/usr/bin/env python3
"""
Direct Option 4 Test - Uses keyboard automation
"""

import sys
import time
import subprocess
from pathlib import Path

# Fix Windows encoding
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("  DIRECT OPTION 4 TEST")
print("=" * 60)
print()
print("This will:")
print("  1. Run vibecode_studio.py")
print("  2. Select Option 4 (New Fullstack App)")
print("  3. Enter project details")
print("  4. Approve the plan")
print()
print("Project: test-quick-blog")
print("Desc: A simple blog with Next.js, homepage and about page")
print()

input("Press Enter to start...")

# Prepare input
inputs = [
    "4",  # Option 4
    "test-quick-blog",  # Project name
    "A simple blog platform with Next.js. Include homepage with welcome message and about page. Use Tailwind CSS for styling.",  # Description
    "y",  # Approve plan
    "0"   # Exit after completion
]

input_string = "\n".join(inputs) + "\n"

print("\nStarting Vibecode Studio...")
print("(This will take 3-5 minutes)")
print()

try:
    process = subprocess.Popen(
        [sys.executable, "vibecode_studio.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Send input
    process.stdin.write(input_string)
    process.stdin.close()
    
    # Stream output in real-time
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    
    print("\n" + "=" * 60)
    print("  VERIFICATION")
    print("=" * 60)
    
    project_dir = Path("test-quick-blog")
    
    if project_dir.exists():
        print(f"✓ Project created: {project_dir}")
        
        files = list(project_dir.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        print(f"✓ Files generated: {file_count}")
        
        if (project_dir / "docs" / "vibecode_plan.md").exists():
            print("✓ Architecture plan created")
        
        if (project_dir / "package.json").exists():
            print("✓ package.json exists")
        
        print("\nNext steps:")
        print(f"  cd {project_dir}")
        print("  npm install")
        print("  npm run dev")
    else:
        print("✗ Project not created")
        print("Check output above for errors")

except Exception as e:
    print(f"\nError: {e}")
    sys.exit(1)
