import os
import sys

def find_backtest_examples():
    """Find files that might contain backtest examples"""
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("🔍 Searching for backtest examples...")
    print("=" * 60)
    
    # Files that might contain examples
    search_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'docs/',
    ]
    
    # Also search for Python files that might contain examples
    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py') and 'example' in file.lower():
                search_files.append(os.path.join(root, file))
            elif file.endswith('.py') and 'test' in file.lower():
                search_files.append(os.path.join(root, file))
    
    # Search for BacktesterEngine usage
    for file_path in search_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if 'BacktesterEngine' in content:
                    print(f"📄 Found BacktesterEngine usage in: {file_path}")
                    
                    # Extract lines containing BacktesterEngine
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'BacktesterEngine' in line:
                            print(f"  Line {i+1}: {line.strip()}")
                    print()
                    
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")

if __name__ == "__main__":
    find_backtest_examples()