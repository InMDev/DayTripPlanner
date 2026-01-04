import re

def check_ux_improvements():
    with open('templates/index.html', 'r') as f:
        content = f.read()

    # Check for aria-labels in static inputs
    aria_label_patterns = [
        r'aria-label="Activity Name"',
        r'aria-label="Activity Cost"',
        r'aria-label="Activity Duration"',
        r'aria-label="Activity Rank"'
    ]

    for pattern in aria_label_patterns:
        if not re.search(pattern, content):
            print(f"FAILED: Missing static aria-label matching {pattern}")
            return False

    # Check for aria-label in Remove button (static and dynamic)
    if 'aria-label="Remove activity"' not in content:
        print("FAILED: Missing aria-label for Remove button")
        return False

    # Check for is-loading logic
    loading_logic = [
        r'classList\.add\(\'is-loading\'\)',
        r'classList\.remove\(\'is-loading\'\)',
        r'setAttribute\(\'disabled\'',
        r'removeAttribute\(\'disabled\''
    ]

    for pattern in loading_logic:
        if not re.search(pattern, content):
            print(f"FAILED: Missing loading logic matching {pattern}")
            return False

    print("SUCCESS: All UX checks passed!")
    return True

if __name__ == "__main__":
    if not check_ux_improvements():
        exit(1)
