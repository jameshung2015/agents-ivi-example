# Chrome DevTools MCP 集成指南

本项目已集成 **Chrome DevTools MCP** (Model Context Protocol) 用于音乐播放工具的浏览器自动化。

## 概述

- **旧方案**: 基于 Selenium + webdriver-manager
- **新方案**: 基于 Chrome DevTools MCP (CDP)
  - 优势: 更稳定的元素定位、更好的开发者工具支持、与 Claude/Cursor 等 AI 工具原生集成
  - 要求: 需要 Node.js v20+ 和 npm

## 环境要求

### 必需

1. **Node.js**: v20.19 或更新的 LTS 版本
   ```powershell
   node --version
   npm --version
   ```

2. **Chrome**: 当前稳定版或更新版本（已在 Windows 中默认位置安装）

3. **Python 依赖**: 已在 `requirements.txt` 中

### 安装 Chrome DevTools MCP

两种方式选择其一：

**方式1: 自动启动（推荐 Claude/Cursor 用户）**

如果使用 Claude Desktop、Cursor 等支持 MCP 的客户端，参考以下配置：

在客户端配置中添加（如 Claude Desktop 的 `~/AppData/Local/Claude/claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--headless=false", "--isolated=true"]
    }
  }
}
```

**方式2: 手动运行（用于测试）**

```bash
npx -y chrome-devtools-mcp@latest --headless=false --isolated=true
```

## 项目中的 CDP 工具

### `qq_music_search_cdp`

搜索 QQ 音乐歌曲。该工具返回操作指令而不是直接执行，由 MCP 客户端解释和执行。

**输入**:
- `song_name` (str): 歌曲或歌手名

**输出**: 
- 返回 MCP 客户端需要执行的浏览器操作步骤
- 格式: `{"locator": "<element_uid>", "title": "<song_title>"}`

**工作流**:
1. 打开 QQ 音乐网页
2. 填充搜索框
3. 提交搜索
4. 返回第一个结果的元素 UID

### `qq_music_play_cdp`

根据搜索结果播放歌曲。

**输入**:
- `element_locator` (str): 搜索工具返回的元素 UID

**输出**: 
- 播放状态或错误信息

## 使用示例

### 场景 1: 使用 Claude Desktop

1. 将 MCP 配置加入 Claude Desktop 配置文件
2. 启动 Claude Desktop 和本 Streamlit 应用
3. 在 Claude 中提示: "播放周杰伦的青花瓷"
4. Claude 会调用 `qq_music_search_cdp` 工具
5. Chrome DevTools MCP 执行浏览器操作
6. 返回结果给 Claude
7. Claude 调用 `qq_music_play_cdp` 播放

### 场景 2: 使用本地 Streamlit 应用

1. 启动 MCP 服务:
   ```bash
   npx -y chrome-devtools-mcp@latest --headless=false --isolated=true
   ```

2. 启动 Streamlit 应用:
   ```bash
   cd lc-map_music
   streamlit run app/frontend/app.py
   ```

3. 在应用中选择"音乐Agent"并输入歌曲名

## 配置选项

Chrome DevTools MCP 支持以下常用选项（在 `mcp-config.json` 中配置）:

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--headless` | 是否无头模式运行 | false |
| `--isolated` | 使用临时用户数据目录 | false |
| `--channel` | Chrome 频道 (stable/beta/canary/dev) | stable |
| `--viewport` | 初始视口大小，如 "1280x720" | 自动 |

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| `npx: command not found` | 安装 Node.js 和 npm |
| Chrome 未找到 | 检查 Chrome 是否已安装在默认位置，或使用 `--executablePath` 指定路径 |
| 端口冲突 | MCP 服务器默认使用端口 9222；确保未被占用 |
| 元素选择器失效 | QQ 音乐网页可能更新；需要在开发工具中检查最新的 CSS 选择器 |

## 后续增强

- [ ] 为 Agent 添加 CDP 工具的显式文档
- [ ] 增加 transit（公交）路线支持
- [ ] 缓存 POI 搜索结果
- [ ] 集成网络性能分析工具（利用 CDP 的性能追踪）
- [ ] 添加截图和调试日志导出

## 相关资源

- [Chrome DevTools MCP GitHub](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [MCP 文档](https://modelcontextprotocol.io/)
- [Chrome DevTools 工具参考](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md)
- [Chrome 远程调试文档](https://developer.chrome.com/docs/devtools/remote-debugging/)
