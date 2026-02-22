"""删除循环内的错误import语句"""

# 读取文件
with open('src/state_machine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 删除第191行的import语句
new_lines = []
for i, line in enumerate(lines, 1):
    if i == 191 and 'from .game_state import GameState' in line:
        continue  # 跳过这一行
    new_lines.append(line)

# 写回文件
with open('src/state_machine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 已删除循环内的错误import语句")
print(f"   删除前总行数: {len(lines)}")
print(f"   删除后总行数: {len(new_lines)}")
