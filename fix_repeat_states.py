"""临时脚本：为所有需要点击的状态添加重复处理机制"""

# 读取文件
with open('src/state_machine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到并替换主循环逻辑（大约第175-195行）
new_lines = []
in_loop = False
replaced = False

for i, line in enumerate(lines):
    # 检测是否进入需要修改的区域
    if '# 检测当前状态' in line and not replaced:
        in_loop = True
        # 插入新逻辑
        new_lines.append(line)  # 保留注释
        new_lines.append('                state = self.recognizer.detect_state(screen)\n')
        new_lines.append('                \n')
        new_lines.append('                # 状态切换检测\n')
        new_lines.append('                state_changed = (state != self._last_state)\n')
        new_lines.append('                \n')
        new_lines.append('                if state_changed:\n')
        new_lines.append('                    self._log(f"[状态切换] {state.name}")\n')
        new_lines.append('                    self._last_state = state\n')
        new_lines.append('                \n')
        new_lines.append('                # 需要重复处理的状态（应对游戏卡顿）\n')
        new_lines.append('                # 所有需要点击操作的状态都应该重复执行\n')
        new_lines.append('                from .game_state import GameState\n')
        new_lines.append('                repeat_states = [\n')
        new_lines.append('                    GameState.LEVEL_PREPARE,      # 开始界面\n')
        new_lines.append('                    GameState.CARD_SELECTION,     # 卡牌选择\n')
        new_lines.append('                    GameState.OBSTACLE_CHOICE,    # 障碍物选择\n')
        new_lines.append('                    GameState.VICTORY             # 胜利界面\n')
        new_lines.append('                ]\n')
        new_lines.append('                \n')
        new_lines.append('                # 状态切换时处理，或特定状态重复处理\n')
        new_lines.append('                if state_changed or state in repeat_states:\n')
        new_lines.append('                    self._handle_state(state, screen)\n')
        new_lines.append('                \n')
        
        # 跳过原来的逻辑（第180-187行）
        skip_count = 0
        for j in range(i+1, len(lines)):
            if 'except Exception' in lines[j]:
                break
            skip_count += 1
        
        # 跳过这些行
        for _ in range(skip_count):
            next(enumerate(lines[i+1:]), None)
        
        replaced = True
        continue
    
    # 如果已经替换过，检查是否到达except
    if replaced and 'except Exception' in line:
        in_loop = False
        new_lines.append(line)
        continue
    
    # 如果在修改区域内且还没替换，跳过
    if in_loop and not '# 检测当前状态' in line:
        if 'except Exception' in line:
            in_loop = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

# 写回文件
with open('src/state_machine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ 已为所有状态添加重复处理机制")
print("   - LEVEL_PREPARE (开始界面)")
print("   - CARD_SELECTION (卡牌选择)")
print("   - OBSTACLE_CHOICE (障碍物选择)")
print("   - VICTORY (胜利界面)")
