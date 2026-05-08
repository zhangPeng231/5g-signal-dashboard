# 📡 5G 信号可视化看板

> 🚀 **"Code with AI" 极客探索赛** - 5G 信号数据可视化挑战

基于 **Streamlit** + **PyDeck** + **Plotly** 构建的交互式 5G 路测数据可视化 Web 看板。

---

## ✨ 功能特性

### 🟢 基础关卡（已完成）

| 功能 | 说明 |
|------|------|
| **数据加载** | 使用 pandas 读取 CSV 格式的 5G 信号数据 |
| **2D 信号地图** | PyDeck 交互式散点地图，RSRP 四色编码：<br>🟢 绿色(>-90dBm) 🟡 黄绿(-90~-100dBm) 🟠 橙色(-100~-110dBm) 🔴 红色(<=-110dBm) |
| **数据概览图表** | 频段柱状图、终端饼图、RSRP 直方图、下载速率箱线图 |

### 🟡 进阶关卡（已完成）

| 功能 | 说明 |
|------|------|
| **侧边栏联动筛选** | 支持频段/RSRP/SINR/终端类型/下载速率多维度实时筛选，地图与图表即时联动更新 |
| **3D 极客视觉** | PyDeck ColumnLayer 3D 柱状图，柱子高度代表下载速率，颜色代表信号强度 |
| **工程化素养** | 完整代码注释 + 17 个单元测试 + 模块化架构 |

### 🎨 界面特色

- 科技紫蓝渐变主题风格
- HTML/CSS 自定义卡片式统计面板
- 2D/3D 地图 Tab 切换
- 地图旁实时信号质量饼图
- RSRP 与 SINR 相关性散点分析
- 小提琴图展示速率分布
- 频段对比统计表格
- CSV 数据导出功能

---

## 📸 运行截图

- `screenshots/screenshot_1_overview.png` - 2D 地图 + 统计面板 + 分析图表
- `screenshots/screenshot_3_3dmap.png` - 3D 柱状图视角

---

## 🛠️ 安装与运行

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

依赖包：
- streamlit >= 1.30.0
- pandas >= 2.0.0
- numpy >= 1.24.0
- pydeck >= 0.8.0
- plotly >= 5.18.0

### 启动应用

```bash
streamlit run app.py
```

应用将在浏览器中打开，默认地址：`http://localhost:8501`

### 运行测试

```bash
python tests/test_app.py
```

---

## 📁 项目结构

```
5g-dashboard/
├── app.py              # 主应用（Streamlit UI）
├── utils.py            # 核心工具函数（数据加载、颜色映射）
├── requirements.txt    # Python 依赖
├── README.md           # 项目说明文档
├── AI_PROMPTS.md       # AI 交互日志
├── data/
│   └── signal_samples.csv  # 5G 信号模拟数据（500条）
├── tests/
│   ├── __init__.py
│   └── test_app.py     # 单元测试（17个测试用例）
└── screenshots/
    ├── screenshot_1_overview.png
    └── screenshot_3_3dmap.png
```

---

## 📊 数据说明

数据集 `data/signal_samples.csv` 包含 500 条 5G 路测模拟数据：

| 字段 | 说明 |
|------|------|
| Latitude | 纬度坐标 |
| Longitude | 经度坐标 |
| CellID | 小区标识 |
| Band | 频段 (n28 / n41 / n78) |
| RSRP_dBm | 参考信号接收功率 (dBm) |
| SINR_dB | 信噪比 (dB) |
| TerminalType | 终端类型 (Smartphone / CPE / IoT) |
| Download_Mbps | 下载速率 (Mbps) |

---

## 🤖 AI 开发说明

本项目采用 AI 辅助编程方式开发。详见 `AI_PROMPTS.md` 文件，记录了与 AI Coding Agent 的完整交互过程。

---

## 🏆 比赛信息

- **比赛仓库**: [besa-2026/code-with-ai-contest](https://github.com/besa-2026/code-with-ai-contest)
- **赛题**: 5G 信号可视化看板挑战
- **提交 Tag**:
  - `basic-done` - 基础关卡完成
  - `advanced-done` - 进阶关卡完成

---

## 📄 开源协议

本项目为 "Code with AI" 比赛参赛作品。
