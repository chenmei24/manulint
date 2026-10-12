# manulint · 论文投稿前规则自查

**在本地检查论文的格式与报告规范，无需 API 密钥。**

[English](README.md) · [合成示例报告](samples/synthetic_report.md) · [反馈问题](https://github.com/chenmei24/manulint/issues)

支持 Word（`.docx`）、Markdown 和纯文本。检查 `p = 0.000`、参考文献内容重复、编号缺失或重复，以及 Word 内嵌图片的有效分辨率。原始研究、综述、病例报告采用不同规则，避免给所有文稿强行套用 IMRaD。

**这是启发式规则检查。分数未经验证，不能表示“可投稿”“小修后投稿”，也不评价科学质量或伦理充分性。**

## 安装和一键体验

需要 Python 3.9 及以上。安装当前 PyPI 版本：

```bash
python -m pip install --upgrade manulint
```

本文对应 0.1.1；如 PyPI 最新版尚未更新，请安装仓库版本：

```bash
git clone https://github.com/chenmei24/manulint.git
cd manulint
python -m pip install .
python -m manulint.demo --out-dir demo-output
```

一键示例生成虚构的 `.md` 和 `.docx` 文稿，以及 `demo-output/report.md`。图片故意设置为低分辨率，参考文献故意设置重复和缺号；不包含患者数据，也不支持任何科研结论。已有示例文件不会被覆盖，再运行请更换输出目录。

## 使用方法

```bash
manulint paper.docx --md report.md
manulint review.md --article-type review --language en --md review-report.md
manulint case.docx --article-type case-report --language zh
manulint paper.docx --p-style upper --md report.md
```

| 参数 | 默认值 | 用途 |
|---|---|---|
| `--article-type original\|review\|case-report` | `original` | 原始研究、综述、病例报告的通用规则；并非目标期刊模板 |
| `--language en\|zh\|auto` | `auto` | 稿件语言，影响标点与摘要计数；报告输出为英文 |
| `--p-style lower\|upper\|either` | `either` | 按目标期刊指定小写或大写，默认两者均可 |
| `--md OUT.md` | 不保存 | 输出 Markdown 报告；输出路径必须与源文稿不同 |
| `--cta https://...` | 无 | 在报告中附加自己的服务网址 |
| `--version` | — | 查看安装版本 |

退出码 `0` 表示检查执行完成，即使存在问题也可能返回 `0`；`2` 表示空白/损坏/不支持的输入、无效选项或报告写入失败。空文稿不会生成分数与报告。

## 检查内容

| 类别 | 检查内容 | 解释边界 |
|---|---|---|
| 结构 | 章节标题识别、不同文章类型的必要章节、披露声明标题 | 没找到标题不等于内容一定缺失 |
| 伦理 | 伦理委员会/IRB、知情同意关键词，综述默认跳过 | 出现关键词不等于伦理审批或知情同意有效、完整 |
| 统计 | `p = 0.000`、运算符空格、指定的 p/P 大小写、样本量/检验/置信区间表述 | 不重新计算数据，不判断检验是否合适；仅原始研究检查样本量和检验名称 |
| 图片 | 根据 Word relationship ID 匹配每次引用，取横向与纵向 DPI 的较小值 | 300 dpi 为筛查阈值，需核对期刊；矢量和不支持的图片明确提示跳过 |
| 文献 | 编号缺失、编号重复、顺序、去编号后相同文本 | 不验证 DOI、文献真实性或文内引用对应关系 |
| 语言格式 | 英文稿混入中文标点、多重空格、Fig./Figure 混用 | 不做语法润色，自动语言识别可能出错 |
| 元信息 | 摘要计数不包含标题和结构式标签、英文标题长度 | 英文按空白分词，中文计汉字；可能与期刊计数方法不同 |

## 使用限制

Word 按正文顺序读取段落与表格，并检查现代正文图片；页眉页脚、文本框、脚注、公式、图表、旧式 VML 图片、修订文本等不完整覆盖。同一图片在不同位置以不同大小显示，会分别计算横纵方向分辨率；裁剪和期刊图像类型要求仍需人工核对。

章节识别依赖常见中英文标题。结构式摘要优先在后续“关键词”或“引言”处结束；缺少这些边界时可能难以准确区分摘要小标题与正文标题。文献编号支持 `[1]`、`(1)`、`1.`、`1)`，下一已识别章节或 Markdown 标题后停止读取；编号文献的续行会合并，作者年份式重复以非空行比较。

所有读取和检查均在本地完成，不下载远程 Markdown 图片。报告可能包含稿件片段或文件名，分享前请自行确认。

分数公式为 `max(0, 100 - 3 × 标记规则数 - 警告数)`。权重未经验证，相关问题可能被分别扣分；100 分也不代表科学质量、伦理充分性或接收概率。请逐项处理报告，并核对目标期刊《作者指南》。

## 开发和反馈

请使用不含患者信息、保密稿件的合成示例反馈问题。详见 [贡献说明](CONTRIBUTING.md) 与 [版本记录](CHANGELOG.md)。

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

CI 已配置 Linux/Windows 与 Python 3.9、3.11、3.13；标签触发的 PyPI 发布会先执行回归测试与包检查。

## 许可

[MIT](LICENSE)。

## Related tools / 相关工具

- [Medical-imaging manifest audits](https://github.com/chenmei24/dicleak)
- [Traceable clinical CSV QA](https://github.com/chenmei24/clinical-imaging-data-qa-demo)

[Launch tutorials and share images / 推广教程与展示图](docs/launch/README.md)
