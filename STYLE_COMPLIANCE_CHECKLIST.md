# STYLE Compliance Checklist

**ALL violations are serious. Check systematically.**

## 1. IMPORT VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Breaks test isolation, pollutes global path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### ✅ CORRECT APPROACH:
```python
# Use proper package structure
from utils.segment_analysis import analyze_curve_segments
from atpoe_working import generate_nested_curve_simple
```

**Check:** No `sys.path.append()` anywhere in test files

## 2. DOCUMENTATION VIOLATIONS

### ❌ NEVER DO THIS:
```python
def my_function():
    """Does something."""
    pass
```

### ✅ CORRECT APPROACH:
```python
def my_function():
    """
    Date: 2024-12-19
    Description: One-line summary of what the function does.
    """
    pass
```

**Check:** Every function has date stamp and one-line description

## 3. TEST VIOLATIONS

### ❌ NEVER DO THIS:
```python
def test_something():
    result = my_function()
    print(f"Result: {result}")  # No assertions!
```

### ✅ CORRECT APPROACH:
```python
def test_something():
    result = my_function()
    assert result == expected_value, f"Expected {expected_value}, got {result}"
```

**Check:** Every test has at least one assertion or exception test

### ❌ NEVER DO THIS:
```python
# Direct float equality
assert result == 10.0
```

### ✅ CORRECT APPROACH:
```python
# Use pytest.approx for floats
assert result == pytest.approx(10.0)
```

**Check:** No `==` for float comparisons

## 4. CODE ORGANIZATION VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Test helper function that might be useful elsewhere
def analyze_data(data):
    # Complex analysis logic
    pass
```

### ✅ CORRECT APPROACH:
```python
# Ask: Should this be in utils/ instead of tests/?
# If generally useful -> move to utils/
# If test-specific -> keep in tests/
```

**Check:** Test helper functions are in appropriate location

## 5. PROCESS VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Adding major functionality without asking
def new_major_feature():
    # Lots of new code
    pass
```

### ✅ CORRECT APPROACH:
```python
# Ask to rerun system before major changes
# Break into smaller steps
# Get permission before proceeding
```

**Check:** Major changes are broken into smaller steps

## 6. VALIDATION VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Using code without testing it first
new_function = copy_pasted_from_main_module()
```

### ✅ CORRECT APPROACH:
```python
# Test new code with simple case first
result = new_function(simple_input)
assert result == expected_output
```

**Check:** All new code is validated before use

## 7. INCREMENTAL CHANGE VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Multiple major changes at once
def massive_refactor():
    # Changes imports, adds functions, modifies tests
    pass
```

### ✅ CORRECT APPROACH:
```python
# One small change at a time
# Test each change
# Ask permission between steps
```

**Check:** Changes are incremental and tested

## SYSTEMATIC CHECKING PROCESS

1. **Scan for imports** - Look for `sys.path.append()`
2. **Check docstrings** - Every function has date and description
3. **Verify assertions** - Every test has assertions
4. **Check float comparisons** - No `==` for floats
5. **Review code placement** - Utils vs tests appropriate?
6. **Validate new code** - Test before use
7. **Check process** - Incremental changes, permission asked

## EXAMPLES OF BAD STYLE FOUND

### In test_geometric_lines.py:
```python
# ❌ VIOLATION: sys.path.append
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ❌ VIOLATION: Missing date stamp
def generate_nested_polyline_simple():
    """Generate a nested polyline..."""  # Missing date!

# ❌ VIOLATION: Copied code without validation
def generate_nested_polyline_simple():  # Copied from main module
    # 50 lines of copied code
```

### In test_segment_analysis.py:
```python
# ❌ VIOLATION: Missing date stamp
def test_segment_analysis():
    """Test the segment analysis functions."""  # Missing date!
```

## 8. FILE PATH VIOLATIONS

### ❌ NEVER DO THIS:
```python
# Using os.getcwd() or Path.cwd()
output_file = os.path.join(os.getcwd(), "temp/file.png")
output_path = Path.cwd() / "temp" / "file.png"

# Checking for absolute paths
if not os.path.isabs(output_file):
    output_file = os.path.join(os.getcwd(), output_file)

# Using "/" operator with Path - WRONG
output_path = Path("temp") / "file.png"
output_path = Path("temp") / "subdirectory" / "file.png"
```

### ✅ CORRECT APPROACH:
```python
# Use Path constructor with multiple arguments
from pathlib import Path
output_path = Path("temp", "file.png")

# Only write to temp directory or its descendants
temp_dir = Path("temp")
output_file = Path(temp_dir, "diagram.png")

# For subdirectories, use multiple arguments in constructor
subdir_path = Path("temp", "subdirectory", "file.png")
```

**Check:** No `os.getcwd()` or `Path.cwd()` anywhere
**Check:** All outputs go to `temp/` directory or subdirectories  
**Check:** Always ask permission before using `mkdir`
**Check:** Never use "/" in filename strings - use Path constructor arguments only
**Check:** Never use "/" operator with Path - use Path(arg1, arg2, arg3) constructor

## REMINDER: ALL VIOLATIONS ARE SERIOUS

- Import violations break test isolation
- Documentation violations break debugging
- Test violations break reliability
- Process violations break stability
- Organization violations break maintainability
- File path violations break security

**Check systematically. Don't prioritize. Fix all violations.**

