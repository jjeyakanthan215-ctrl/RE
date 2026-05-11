"""
ESCTRIX - Integrated Live Coding Assessment Module
Blueprint: coding_bp
Routes: /coding-test (GET), /coding-test/run (POST)
Supports: Python, JavaScript, Java, C, C++, Shell
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
import subprocess
import sys
import os
import tempfile

coding_bp = Blueprint('coding', __name__)

# Starter code per challenge per language
STARTER_CODES = {
    "python": {
        1: "def reverse_string(s):\n    # Write your solution here\n    pass\n\n# Test your function\nprint(reverse_string('hello'))\nprint(reverse_string('ESCTRIX'))",
        2: "def fizzbuzz(n):\n    # Write your solution here\n    pass\n\n# Test your function\nprint(fizzbuzz(3))\nprint(fizzbuzz(5))\nprint(fizzbuzz(15))\nprint(fizzbuzz(7))",
        3: "def find_duplicates(nums):\n    # Write your solution here\n    pass\n\n# Test your function\nprint(find_duplicates([1, 2, 3, 2, 4, 3]))\nprint(find_duplicates([1, 1, 1, 2]))",
        4: "def two_sum(nums, target):\n    # Write your solution here\n    pass\n\n# Test your function\nprint(two_sum([2, 7, 11, 15], 9))\nprint(two_sum([3, 2, 4], 6))",
        5: "def is_palindrome(s):\n    # Write your solution here\n    pass\n\n# Test your function\nprint(is_palindrome('racecar'))\nprint(is_palindrome('A man a plan a canal Panama'))\nprint(is_palindrome('hello'))"
    },
    "javascript": {
        1: "function reverseString(s) {\n    // Write your solution here\n}\n\n// Test your function\nconsole.log(reverseString('hello'));\nconsole.log(reverseString('ESCTRIX'));",
        2: "function fizzbuzz(n) {\n    // Write your solution here\n}\n\n// Test your function\nconsole.log(fizzbuzz(3));\nconsole.log(fizzbuzz(5));\nconsole.log(fizzbuzz(15));\nconsole.log(fizzbuzz(7));",
        3: "function findDuplicates(nums) {\n    // Write your solution here\n}\n\n// Test your function\nconsole.log(findDuplicates([1, 2, 3, 2, 4, 3]));\nconsole.log(findDuplicates([1, 1, 1, 2]));",
        4: "function twoSum(nums, target) {\n    // Write your solution here\n}\n\n// Test your function\nconsole.log(twoSum([2, 7, 11, 15], 9));\nconsole.log(twoSum([3, 2, 4], 6));",
        5: "function isPalindrome(s) {\n    // Write your solution here\n}\n\n// Test your function\nconsole.log(isPalindrome('racecar'));\nconsole.log(isPalindrome('A man a plan a canal Panama'));\nconsole.log(isPalindrome('hello'));"
    },
    "java": {
        1: "public class Main {\n    public static String reverseString(String s) {\n        // Write your solution here\n        return \"\";\n    }\n\n    public static void main(String[] args) {\n        System.out.println(reverseString(\"hello\"));\n        System.out.println(reverseString(\"ESCTRIX\"));\n    }\n}",
        2: "public class Main {\n    public static String fizzbuzz(int n) {\n        // Write your solution here\n        return \"\";\n    }\n\n    public static void main(String[] args) {\n        System.out.println(fizzbuzz(3));\n        System.out.println(fizzbuzz(5));\n        System.out.println(fizzbuzz(15));\n        System.out.println(fizzbuzz(7));\n    }\n}",
        3: "import java.util.*;\npublic class Main {\n    public static List<Integer> findDuplicates(int[] nums) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n\n    public static void main(String[] args) {\n        System.out.println(findDuplicates(new int[]{1,2,3,2,4,3}));\n    }\n}",
        4: "import java.util.*;\npublic class Main {\n    public static int[] twoSum(int[] nums, int target) {\n        // Write your solution here\n        return new int[]{};\n    }\n\n    public static void main(String[] args) {\n        System.out.println(Arrays.toString(twoSum(new int[]{2,7,11,15}, 9)));\n    }\n}",
        5: "public class Main {\n    public static boolean isPalindrome(String s) {\n        // Write your solution here\n        return false;\n    }\n\n    public static void main(String[] args) {\n        System.out.println(isPalindrome(\"racecar\"));\n        System.out.println(isPalindrome(\"A man a plan a canal Panama\"));\n        System.out.println(isPalindrome(\"hello\"));\n    }\n}"
    },
    "c": {
        1: "#include <stdio.h>\n#include <string.h>\n\nvoid reverseString(char *s, char *result) {\n    // Write your solution here\n    int len = strlen(s);\n    for (int i = 0; i < len; i++) result[i] = s[len - 1 - i];\n    result[len] = '\\0';\n}\n\nint main() {\n    char result[100];\n    reverseString(\"hello\", result);\n    printf(\"%s\\n\", result);\n    reverseString(\"ESCTRIX\", result);\n    printf(\"%s\\n\", result);\n    return 0;\n}",
        2: "#include <stdio.h>\n\nvoid fizzbuzz(int n) {\n    // Write your solution here\n    if (n % 15 == 0) printf(\"FizzBuzz\\n\");\n    else if (n % 3 == 0) printf(\"Fizz\\n\");\n    else if (n % 5 == 0) printf(\"Buzz\\n\");\n    else printf(\"%d\\n\", n);\n}\n\nint main() {\n    fizzbuzz(3);\n    fizzbuzz(5);\n    fizzbuzz(15);\n    fizzbuzz(7);\n    return 0;\n}",
        3: "#include <stdio.h>\n\n// Find duplicates in array\nint main() {\n    int nums[] = {1, 2, 3, 2, 4, 3};\n    int n = 6;\n    // Write your solution here\n    printf(\"Duplicates: \");\n    return 0;\n}",
        4: "#include <stdio.h>\n\nvoid twoSum(int *nums, int n, int target, int *i1, int *i2) {\n    // Write your solution here\n    *i1 = -1; *i2 = -1;\n}\n\nint main() {\n    int nums[] = {2, 7, 11, 15};\n    int i1, i2;\n    twoSum(nums, 4, 9, &i1, &i2);\n    printf(\"[%d, %d]\\n\", i1, i2);\n    return 0;\n}",
        5: "#include <stdio.h>\n#include <string.h>\n#include <ctype.h>\n\nint isPalindrome(char *s) {\n    // Write your solution here (ignore spaces, case)\n    return 0;\n}\n\nint main() {\n    printf(\"%s\\n\", isPalindrome(\"racecar\") ? \"True\" : \"False\");\n    printf(\"%s\\n\", isPalindrome(\"hello\") ? \"True\" : \"False\");\n    return 0;\n}"
    },
    "cpp": {
        1: "#include <iostream>\n#include <string>\n#include <algorithm>\nusing namespace std;\n\nstring reverseString(string s) {\n    // Write your solution here\n    return \"\";\n}\n\nint main() {\n    cout << reverseString(\"hello\") << endl;\n    cout << reverseString(\"ESCTRIX\") << endl;\n    return 0;\n}",
        2: "#include <iostream>\n#include <string>\nusing namespace std;\n\nstring fizzbuzz(int n) {\n    // Write your solution here\n    return \"\";\n}\n\nint main() {\n    cout << fizzbuzz(3) << endl;\n    cout << fizzbuzz(5) << endl;\n    cout << fizzbuzz(15) << endl;\n    cout << fizzbuzz(7) << endl;\n    return 0;\n}",
        3: "#include <iostream>\n#include <vector>\n#include <map>\nusing namespace std;\n\nvector<int> findDuplicates(vector<int> nums) {\n    // Write your solution here\n    return {};\n}\n\nint main() {\n    auto res = findDuplicates({1,2,3,2,4,3});\n    for (int x : res) cout << x << \" \";\n    cout << endl;\n    return 0;\n}",
        4: "#include <iostream>\n#include <vector>\n#include <map>\nusing namespace std;\n\nvector<int> twoSum(vector<int> nums, int target) {\n    // Write your solution here\n    return {};\n}\n\nint main() {\n    auto res = twoSum({2,7,11,15}, 9);\n    cout << \"[\" << res[0] << \", \" << res[1] << \"]\" << endl;\n    return 0;\n}",
        5: "#include <iostream>\n#include <string>\n#include <algorithm>\n#include <cctype>\nusing namespace std;\n\nbool isPalindrome(string s) {\n    // Write your solution here (ignore spaces and case)\n    return false;\n}\n\nint main() {\n    cout << (isPalindrome(\"racecar\") ? \"True\" : \"False\") << endl;\n    cout << (isPalindrome(\"A man a plan a canal Panama\") ? \"True\" : \"False\") << endl;\n    cout << (isPalindrome(\"hello\") ? \"True\" : \"False\") << endl;\n    return 0;\n}"
    },
    "shell": {
        1: "#!/bin/bash\n# Reverse a string\nreverse_string() {\n    echo \"$1\" | rev\n}\n\n# Test your function\nreverse_string 'hello'\nreverse_string 'ESCTRIX'",
        2: "#!/bin/bash\n# FizzBuzz\nfizzbuzz() {\n    local n=$1\n    if (( n % 15 == 0 )); then echo \"FizzBuzz\"\n    elif (( n % 3 == 0 )); then echo \"Fizz\"\n    elif (( n % 5 == 0 )); then echo \"Buzz\"\n    else echo \"$n\"\n    fi\n}\n\nfizzbuzz 3\nfizzbuzz 5\nfizzbuzz 15\nfizzbuzz 7",
        3: "#!/bin/bash\n# Find duplicates in a space-separated list\nnums=(1 2 3 2 4 3)\n# Write your solution here\necho \"${nums[@]}\" | tr ' ' '\\n' | sort | uniq -d",
        4: "#!/bin/bash\n# Two Sum (simplified)\nnums=(2 7 11 15)\ntarget=9\n# Write your solution here\nfor i in \"${!nums[@]}\"; do\n    for j in \"${!nums[@]}\"; do\n        if [[ $i -lt $j && $(( nums[i] + nums[j] )) -eq $target ]]; then\n            echo \"[$i, $j]\"\n        fi\n    done\ndone",
        5: "#!/bin/bash\n# Check palindrome\nis_palindrome() {\n    local s=$(echo \"$1\" | tr -d ' ' | tr '[:upper:]' '[:lower:]')\n    local rev=$(echo \"$s\" | rev)\n    [[ \"$s\" == \"$rev\" ]] && echo \"True\" || echo \"False\"\n}\n\nis_palindrome 'racecar'\nis_palindrome 'A man a plan a canal Panama'\nis_palindrome 'hello'"
    }
}

# Language execution config
LANG_CONFIG = {
    "python":     {"ext": ".py",   "cmd": lambda p: [sys.executable, p]},
    "javascript": {"ext": ".js",   "cmd": lambda p: ["node", p]},
    "java":       {"ext": ".java", "cmd": None},   # handled specially
    "c":          {"ext": ".c",    "cmd": None},   # compile then run
    "cpp":        {"ext": ".cpp",  "cmd": None},   # compile then run
    "shell":      {"ext": ".sh",   "cmd": lambda p: ["bash", p]},
}

CODING_CHALLENGES = [
    {"id": 1, "title": "Reverse a String",  "difficulty": "Easy",
     "description": "Write a function that takes a string and returns it reversed.\n\nExample:\n  reverseString('hello') → 'olleh'\n  reverseString('ESCTRIX') → 'XIRTCSE'"},
    {"id": 2, "title": "FizzBuzz",           "difficulty": "Easy",
     "description": "Write a function that:\n- Returns 'Fizz' if divisible by 3\n- Returns 'Buzz' if divisible by 5\n- Returns 'FizzBuzz' if divisible by both\n- Otherwise returns the number as string\n\nExample:\n  fizzbuzz(3) → 'Fizz'\n  fizzbuzz(15) → 'FizzBuzz'"},
    {"id": 3, "title": "Find Duplicates",    "difficulty": "Medium",
     "description": "Write a function that takes a list/array of numbers and returns all numbers that appear more than once.\n\nExample:\n  findDuplicates([1, 2, 3, 2, 4, 3]) → [2, 3]"},
    {"id": 4, "title": "Two Sum",            "difficulty": "Medium",
     "description": "Write a function that takes an array and target value. Return the indices of two numbers that add up to the target.\n\nExample:\n  twoSum([2, 7, 11, 15], 9) → [0, 1]"},
    {"id": 5, "title": "Valid Palindrome",   "difficulty": "Hard",
     "description": "Write a function that checks if a string is a palindrome. Ignore spaces and capitalization.\n\nExample:\n  isPalindrome('racecar') → True\n  isPalindrome('A man a plan a canal Panama') → True"},
]


@coding_bp.route('/coding-test')
@login_required
def coding_test():
    challenge_id = request.args.get('id', 1, type=int)
    challenge = next((c for c in CODING_CHALLENGES if c['id'] == challenge_id), CODING_CHALLENGES[0])
    # Attach all starter codes for the challenge
    challenge['starter_codes'] = {lang: codes[challenge_id] for lang, codes in STARTER_CODES.items()}
    return render_template('coding.html', challenge=challenge, all_challenges=CODING_CHALLENGES)


@coding_bp.route('/coding-test/run', methods=['POST'])
@login_required
def run_code():
    """Execute user code in multiple languages via sandboxed subprocess."""
    data = request.get_json()
    user_code = data.get('code', '')
    language = data.get('language', 'python').lower()

    if not user_code.strip():
        return jsonify({'output': 'No code to run.', 'success': False})

    if language not in LANG_CONFIG:
        return jsonify({'output': f'Unsupported language: {language}', 'success': False, 'is_error': True})

    config = LANG_CONFIG[language]
    ext = config['ext']
    temp_path = None
    out_path = None

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
            f.write(user_code)
            temp_path = f.name

        # Build command based on language
        if language == 'python':
            cmd = [sys.executable, temp_path]

        elif language == 'javascript':
            cmd = ['node', temp_path]

        elif language == 'java':
            # Java: file must be named Main.java, compile then run
            java_dir = tempfile.mkdtemp()
            java_file = os.path.join(java_dir, 'Main.java')
            with open(java_file, 'w', encoding='utf-8') as jf:
                jf.write(user_code)
            compile_result = subprocess.run(
                ['javac', java_file], capture_output=True, text=True, timeout=10
            )
            if compile_result.returncode != 0:
                return jsonify({'output': compile_result.stderr, 'success': False, 'is_error': True})
            cmd = ['java', '-cp', java_dir, 'Main']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            output = result.stdout
            error = result.stderr
            if error:
                return jsonify({'output': error, 'success': False, 'is_error': True})
            return jsonify({'output': output or '(No output)', 'success': True})

        elif language == 'c':
            out_path = temp_path.replace('.c', '.exe' if os.name == 'nt' else '.out')
            compile_result = subprocess.run(
                ['gcc', temp_path, '-o', out_path], capture_output=True, text=True, timeout=10
            )
            if compile_result.returncode != 0:
                return jsonify({'output': compile_result.stderr, 'success': False, 'is_error': True})
            cmd = [out_path]

        elif language == 'cpp':
            out_path = temp_path.replace('.cpp', '.exe' if os.name == 'nt' else '.out')
            compile_result = subprocess.run(
                ['g++', temp_path, '-o', out_path], capture_output=True, text=True, timeout=10
            )
            if compile_result.returncode != 0:
                return jsonify({'output': compile_result.stderr, 'success': False, 'is_error': True})
            cmd = [out_path]

        elif language == 'shell':
            cmd = ['bash', temp_path]

        # Run the final command
        if not cmd:
             return jsonify({'output': 'Execution failed: No command generated.', 'success': False, 'is_error': True})

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout
        error = result.stderr
        
        # If there's error output but the process finished successfully (exit code 0),
        # we still show the output. Only if exit code != 0 do we treat it as an error.
        if result.returncode != 0:
            return jsonify({'output': error or output, 'success': False, 'is_error': True})
            
        return jsonify({'output': output or '(No output)', 'success': True})

    except FileNotFoundError as e:
        lang_name = language.capitalize()
        return jsonify({'output': f'⚠️ {lang_name} runtime/compiler not found on this system.\nPlease install it and make sure it is in your system PATH.\n\nError: {e}', 'success': False, 'is_error': True})
    except subprocess.TimeoutExpired:
        return jsonify({'output': '⏰ Time Limit Exceeded: Your code took too long to run (5 second limit).', 'success': False, 'is_error': True})
    except Exception as e:
        return jsonify({'output': f'Execution Error: {str(e)}', 'success': False, 'is_error': True})
    finally:
        for path in [temp_path, out_path]:
            if path and os.path.exists(path):
                try: os.remove(path)
                except: pass
