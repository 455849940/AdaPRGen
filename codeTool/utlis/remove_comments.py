import re

def remove_comments(code):
    """
    Remove comments from the code, including single-line and multi-line comments.

    Args:
        code (str): Code string containing comments.

    Returns:
        str: Code string with comments removed.
    """
    single_line_comment_pattern = r'//.*?$|#.*?$'
    multi_line_comment_pattern = r'/\*.*?\*/|\'\'\'.*?\'\'\'|""".*?"""'
    
    pattern = re.compile(
        single_line_comment_pattern + '|' + multi_line_comment_pattern,
        re.DOTALL | re.MULTILINE
    )

    cleaned_code = re.sub(pattern, '', code)
    
    return cleaned_code

code_with_comments = "import sys\n\n#\u6700\u5927\u516c\u7d04\u6570\ndef gcd(x, y):\n    s = x / y\n    r = x % y\n    if r == 0:\n        return y\n    else:\n        return gcd(y, r)\n\n#\u6700\u5c0f\u516c\u500d\u6570\ndef lcm(x, y):\n    return x*y/gcd(x, y)\n\ndef main():\n    #print (\"a\")\n    for line in iter(sys.stdin.readline, \"\"):\n        print (line)\n        #tmp = sys.stdin.readline().split(\" \")\n        #print (\"b\")\n        tmp = line.split(\" \")\n    \n        a = int(tmp[0])\n        b = int(tmp[1])\n        #print (\"a=\"+str(a))\n        #print (\"b=\"+str(b))\n        #b = sys.stdin.readline()\n        #print (\"d\")\n        if a > b:\n            c = a\n            d = b\n        else:\n            c = b\n            d = a\n\n        print (str(gcd(c, d)) + \" \" + str(int(lcm(c,d))))\n\n        #tmp = sys.stdin.readline()\n        #if len(tmp) == 1:\n        #    break\n        #else:\n        #    tmp = tmp.split(\" \")\n\n    #print (\"exit\")\n     \nif __name__ == \"__main__\":\n    main()"

cleaned_code = remove_comments(code_with_comments)

print("ok")
print(cleaned_code)

