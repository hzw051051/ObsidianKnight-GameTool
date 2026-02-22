# 黑曜石骑士游戏助手 V1

自动刷关卡助手，适用于雷电模拟器9。

## 功能

- 自动开始关卡
- 按权重选择卡牌
- 自动处理障碍物事件
- 通关后自动重试

## 环境要求

- Windows 系统
- Python 3.8+
- 雷电模拟器 9.x
- 模拟器分辨率：1600×900（平板版）

## 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 使用方法

1. 启动雷电模拟器并打开游戏
2. 进入关卡准备界面（开始按钮可见）
3. 运行程序：
   ```bash
   python main.py
   ```
4. 点击「连接模拟器」按钮
5. 点击「开始」按钮
6. 需要停止时点击「停止」按钮

## 配置说明

### 卡牌权重 (`config/card_weights.jsonc`)

```jsonc
{
  "11": 100,   // 升级时恢复生命值 +11
  "58": 60     // 护甲耗尽时恢复12点生命值
}
```

- 数字越大优先级越高
- 不在配置中的卡牌随机选择

### 通用配置 (`config/config.jsonc`)

```jsonc
{
  "obstacle_choice": 3,    // 障碍物默认选第几个 (1/2/3)
  "loop_delay_ms": 500,    // 检测间隔(毫秒)
  "adb_port": 5555         // ADB端口
}
```

## 目录结构

```
黑曜石骑士游戏助手/
├── main.py              # 主程序入口
├── config/              # 配置文件
│   ├── config.jsonc
│   └── card_weights.jsonc
├── src/                 # 源代码
│   ├── adb_controller.py
│   ├── image_recognition.py
│   ├── config_loader.py
│   ├── state_machine.py
│   └── gui.py
├── templates/           # 模板图片 (可选)
└── requirements.txt
```

## 常见问题

**Q: 连接模拟器失败?**
- 确保雷电模拟器已启动
- 检查 ADB 端口是否正确（默认 5555）
- 尝试手动执行: `adb connect 127.0.0.1:5555`

**Q: 识别不准确?**
- 添加模板图片到 `templates/` 目录
- 检查模拟器分辨率是否为 1600×900

**Q: 卡牌ID在哪里看?**
- 卡牌上方的小数字就是ID
