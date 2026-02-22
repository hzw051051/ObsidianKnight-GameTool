"""临时脚本：添加max_log_lines属性到Config类"""
import re

# 读取文件
with open('src/config_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到adb_port属性后添加max_log_lines
pattern = r'(@property\s+def adb_port\(self\) -> int:.*?return self\._config\.get\("adb_port", 5555\))'
replacement = r'\1\n    \n    @property\n    def max_log_lines(self) -> int:\n        """日志最大行数"""\n        return self._config.get("max_log_lines", 500)'

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回文件
with open('src/config_loader.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ 已添加max_log_lines属性到Config类")
