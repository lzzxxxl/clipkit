# 剪贴板自动保存

一个简洁高效的 Windows 剪贴板监听工具，自动将剪贴板内容保存到匹配的本地文件中。

## 功能特性

- **智能标题提取**：自动从剪贴板内容中识别文章/文件标题
- **自动匹配保存**：根据标题匹配本地 TXT 文件，自动保存内容
- **Markdown转HTML**：自动将复制的Markdown内容转换为HTML格式
- **WordPress格式处理**：自动识别 `***` 分隔的内容，提取文章正文和元数据
- **匹配字段自定义**：支持用户自定义标题匹配字段，兼容多种格式
- **多主题支持**：支持黑色极简、白色极简、粉色三种主题
- **窗口置顶**：可选择将窗口始终保持在最前面
- **轻量高效**：占用资源少，后台静默运行

## 界面预览

[待添加截图]

## 使用方法

### 方式一：直接运行

1. 双击 `剪贴板自动保存.exe` 运行程序
2. 点击"选择"按钮，选择包含 TXT 文件的文件夹
3. 点击"开始监听"启动剪贴板监控
4. 在任意应用中复制内容，程序自动匹配并保存

### 方式二：从源码运行

```bash
pip install pyperclip markdown
python clipboard_watcher.py
```

### 方式三：打包为 exe

```bash
pip install pyinstaller
pyinstaller 剪贴板自动保存.spec
```

## 工作原理

1. 监听剪贴板变化，检测复制的内容
2. 从内容中提取标题（支持多种格式）
3. 清洗标题（只保留中文、英文、数字）
4. 在指定文件夹中匹配同名的 TXT 文件
5. 如果开启自动保存，内容直接写入匹配的文件
6. 如果内容包含 `***` 分隔符，自动进行 WordPress 格式处理

## 标题识别格式

程序支持识别以下格式的标题：

| 格式 | 示例 |
|------|------|
| `**原文章标题：**` | `**原文章标题：** 如何学习Python` |
| `**原文件标题：**` | `**原文件标题：** 技术文档.txt` |
| `**文章标题：**` | `**文章标题：** 文章标题` |
| `**文件标题：**` | `**文件标题：** 文件标题` |
| `原文章标题：` | `原文章标题：如何学习Python` |
| `原文件标题：` | `原文件标题：技术文档.txt` |
| `文章标题：` | `文章标题：文章标题` |
| `文件标题：` | `文件标题：文件标题` |
| `title:` | `title: Article Title` |
| `<title>` | `<title>页面标题</title>` |

## 自定义匹配字段

在设置中填写自定义字段名（多个用逗号分隔），程序会自动兼容以下三种格式：

| 输入格式 | 匹配示例 |
|----------|----------|
| Markdown加粗 | `**标题：** 内容` |
| 普通中文冒号 | `标题：内容` |
| 普通英文冒号 | `标题:内容` |
| HTML格式 | `<strong>标题：</strong>内容` |

例如：输入 `标题` 或 `标题：`，可匹配以上所有格式。

## WordPress 格式处理

程序支持处理特定格式的剪贴板内容：

### 输入格式

```
[intro部分 - 将被删除]

***

[文章正文 - 将转换为HTML]

***

**标题：** 文章标题
**SEO描述：** SEO描述内容
**别名简短URL：** article-slug
**WordPress标签：** 标签1,标签2
```

### 输出格式

```html
<p>文章正文已转换为HTML格式...</p>

<!-- 标题：文章标题 -->
<!-- SEO描述：SEO描述内容 -->
<!-- 别名简短URL：article-slug -->
<!-- WordPress标签：标签1,标签2 -->
```

### 处理规则

- `***` 之前的 intro 部分会被删除
- 第一个 `***` 之间的内容作为文章正文，转换为 HTML
- 第二个 `***` 之间的内容作为元数据，自动提取字段并添加 HTML 注释
- `***` 之后的内容（如分界线）会被忽略

## 配置文件

程序配置存储在 `watcher_config.json` 中：

```json
{
  "last_folder": "C:/Users/xxx/Documents",
  "auto_save": true,
  "always_on_top": true,
  "theme": "black",
  "markdown_convert": false,
  "match_patterns": "**原文章标题**,**原文件标题**,**文章标题**,**文件标题**"
}
```

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `last_folder` | string | 上次使用的文件夹路径 |
| `auto_save` | boolean | 是否自动保存到匹配文件 |
| `always_on_top` | boolean | 窗口是否置顶 |
| `theme` | string | 主题：`black`、`white` 或 `pink` |
| `markdown_convert` | boolean | 是否启用Markdown转HTML功能 |
| `match_patterns` | string | 自定义匹配字段，多个字段用逗号分隔 |

## 项目结构

```
├── clipboard_watcher.py    # 主程序源代码
├── watcher_config.json     # 配置文件
├── zi.ico                  # 程序图标
├── zi.jpg                  # 图片素材
└── 剪贴板自动保存.spec      # PyInstaller 打包配置
```

## 系统要求

- Windows 操作系统
- 无需 Python 环境（使用打包后的 exe）

## 技术栈

- **GUI**：tkinter（Python 内置）
- **剪贴板**：pyperclip
- **Markdown转换**：markdown
- **打包**：PyInstaller

## License

MIT License