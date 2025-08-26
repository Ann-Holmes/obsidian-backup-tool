# Obsidian Vault Backup Tool

一个简单的 Python 工具，用于备份 Obsidian vault 到本地目录，并支持版本管理。

## 功能特性

- ✅ 完整的 Obsidian vault 备份（包括隐藏文件和配置）
- ✅ 带时间戳的备份文件命名
- ✅ 自动版本管理（保留指定数量的最新备份）
- ✅ 详细的日志记录
- ✅ 错误处理和验证
- ✅ 无需外部依赖（仅使用 Python 标准库）

## 安装要求

- Python 3.6+
- 无需额外安装包

## 使用方法

### 1. 配置备份设置

编辑 `backup_config.ini` 文件，设置你的 Obsidian vault 路径和备份目录：

```ini
[backup]
# Obsidian vault 目录路径
vault_path = /Users/yourname/Documents/ObsidianVault

# 备份文件存储目录
backup_dir = /Users/yourname/Backups/Obsidian

# 保留的备份版本数量
retain_count = 5
```

### 2. 运行备份

```bash
# 直接运行
python obsidian_backup.py

# 或设置为可执行文件
chmod +x obsidian_backup.py
./obsidian_backup.py
```

### 3. 定时备份（macOS）

使用 crontab 设置定时备份：

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * /usr/bin/python3 /path/to/obsidian_backup.py

# 或者每小时备份一次
0 * * * * /usr/bin/python3 /path/to/obsidian_backup.py
```

## 备份文件命名

备份文件使用以下格式命名：
```
obsidian_backup_YYYYMMDD_HHMMSS.zip
```

例如：`obsidian_backup_20250101_143022.zip`

## 日志文件

工具会生成 `obsidian_backup.log` 文件，包含详细的备份操作记录。

## 退出代码

- `0`: 备份成功
- `1`: 备份失败

## 注意事项

1. **文件锁定**: 虽然 macOS 通常没有严格的文件锁定，但如果 Obsidian 正在运行并写入文件，备份可能会捕获到不一致的状态。建议在 Obsidian 未使用时进行备份。

2. **磁盘空间**: 确保备份目录有足够的磁盘空间。

3. **权限**: 确保 Python 有权限读取 vault 目录和写入备份目录。

## 故障排除

如果遇到问题，检查 `obsidian_backup.log` 文件获取详细错误信息。

常见问题：
- 配置文件路径错误
- 权限不足
- 磁盘空间不足

## 扩展功能

未来可以考虑添加：
- WebDAV 远程备份支持
- 加密备份功能
- 增量备份支持
- 邮件通知功能
