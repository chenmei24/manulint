# manulint · 论文投稿前自查工具

> 投稿前 5 分钟，查出可能导致**直接拒稿（desk rejection）**的硬伤。

期刊编辑每天处理大量投稿，很多稿件不是因为学术水平被拒，而是死在格式与规范上：
伦理声明缺失、p = 0.000、图片分辨率不够、参考文献编号断裂……这些本可以在投稿前 5 分钟自己查出来。

manulint 就是做这件事的：**规则式自查，不碰你的学术内容，只查规范问题**。

## 它是什么 / 不是什么

- ✅ 是：一套投稿前 checklist 的自动化实现，规则来自期刊《作者指南》与审稿常见退稿理由
- ❌ 不是：AI 润色、AI 审稿；**不能替代同行评议**，也不评判你的学术观点

## 安装

```bash
pip install manulint
```

## 用法

```bash
# 终端直接出报告
manulint paper.docx

# 同时生成 Markdown 报告（可发给合作者/导师）
manulint paper.md --md report.md

# 在报告末尾附上你的润色服务链接（引流用）
manulint paper.docx --md report.md --cta "https://your-service-link"
```

支持 `.docx` / `.md` / `.txt`。`.docx` 内嵌图片会额外做分辨率检查。

## 检查项（v0.1）

| 类别 | 规则示例 |
|---|---|
| 结构 | IMRaD 章节是否齐全（摘要/引言/方法/结果/讨论/参考文献） |
| 伦理 | 伦理审查声明、知情同意声明是否缺失 |
| 统计 | `p = 0.000`（应为 `p < 0.001`）、p 值大小写与空格、样本量是否报告、检验方法是否写明、有 p 值无置信区间 |
| 图片 | 内嵌图片有效分辨率是否 ≥ 300 dpi（仅 docx） |
| 参考文献 | 编号是否连续、有无重复条目 |
| 语言格式 | 中文标点混入英文稿、连续双空格、`Fig.`/`Figure` 混用 |
| 元信息 | 标题是否过长、摘要字数提示 |

每项按严重程度分为 ❌严重 / ⚠️建议修改 / ℹ️提示，并给出百分制得分与投稿建议。

## 示例

```
manulint 检查完成 | 得分 76/100 | 小修后投稿
--------------------------------------------------------
❌ [严重] 未检测到章节，多数期刊要求完整的 IMRaD 结构
❌ [严重] 发现 1 处 p = 0.000，应写为 p < 0.001（p 值不可能恰为 0）
↳ p=0.000
⚠️ [建议修改] 未找到伦理审查（IRB/伦理委员会）声明，人体/动物研究投稿通常必填
⚠️ [建议修改] 报告了 p 值但未见置信区间（CI）/效应量，建议补充
...
```

## 路线图

- [] 目标期刊模板（不同期刊字数/结构要求一键切换）
- [] CONSORT / STROBE / PRISMA 条款覆盖度检查
- [] 参考文献 DOI 有效性校验
- [] Web 版（拖文件即查）

欢迎提 Issue 分享你遇到过的奇葩退稿理由，我会把它变成一条检查规则。

## 免责声明

本工具为启发式规则检查，不能保证发现所有问题，也不保证"高分稿件必被接收"。投稿前请务必核对目标期刊的《作者指南》。

## License

MIT

---

## English summary

**manulint** is a rule-based pre-submission checklist for academic manuscripts.
It scans `.docx` / `.md` / `.txt` manuscripts for common desk-rejection triggers —
missing ethics statements, malformed p-values (`p = 0.000`), low figure resolution,
broken reference numbering, mixed CJK punctuation, and more — then produces a
scored report. It does not judge scientific merit and is not a substitute for
peer review.

```bash
pip install manulint
manulint paper.docx --md report.md
```
