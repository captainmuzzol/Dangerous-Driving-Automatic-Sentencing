# 危险驾驶自动量刑系统
#### @time: 2023/8/26 17:34
#### @author: 许钦滔
#### @version: 2.6

## 项目介绍
本项目是一个自动化的危险驾驶量刑系统，可以根据案件信息自动生成量刑建议。同时生成（不）起诉书、公诉意见书、认罪认罚具结书（基础模板）、讯问笔录（基础模板）、审查报告（新增了标记事实页码功能）等文书，系统能够识别并分析酒精含量、犯罪情节、前科劣迹等关键信息，为司法实践提供辅助决策支持。

## 环境要求
- Python 3.8+
- 相关Python包（见下方安装说明）

## 安装说明

1. 克隆项目到本地：
```bash
git clone https://github.com/captainmuzzol/Dangerous-Driving-Automatic-Sentencing.git
cd Dangerous-Driving-Automatic-Sentencing
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 模板文件配置说明

**重要提示：** 模板文件夹不包含在代码仓库中，需要手动创建。

### 创建模板步骤：

1. 在项目根目录下创建`模板`文件夹
2. 在`模板`文件夹中添加以下必要文件：

#### 配置文件
   - `inquisitor.txt`：讯问人信息配置文件，用于存储讯问人员的基本信息
   - `LX_change.txt`：量刑变更配置文件，用于记录量刑调整的相关信息

#### 文书模板
   - `讯问笔录.docx`：用于生成标准格式的讯问笔录
   - `认罪认罚具结书.docx`：用于生成认罪认罚具结书
   - `不起诉决定书.docx`：用于生成不起诉决定书
   - `起诉书.docx`：用于生成起诉书
   - `公诉意见书.docx`：用于生成公诉意见书
   - `落实"三个规定"报告表.docx`：用于生成落实三个规定的报告表
   - `审查报告.docx`：用于生成案件审查报告
   - `（检察官姓名）/不诉审查报告.docx`：用于生成不起诉案件的审查报告
   - `（检察官姓名）/起诉审查报告.docx`：用于生成起诉案件的审查报告

#### 提示
可以参考“模板.zip”内的文件结构和内容（因为有部分内容不宜展示，故而加密不予直接使用，请谅解。）

### 模板文件要求
1. 配置文件格式要求：
   - `inquisitor.txt`和`LX_change.txt`必须使用GBK编码
   - 文件内容需按照系统规定的格式填写

2. 文书模板要求：
   - 所有文书模板必须使用.docx格式
   - 模板中需包含相应的占位符（如{基础信息}、{姓名}等）
   - 模板格式需符合司法文书规范

3. 目录结构要求：
   - 所有模板文件必须放在项目根目录下的`模板`文件夹中
   - 部分特殊模板需放在`模板/（检察官姓名）/`子目录下

### 注意事项
- 模板文件夹不包含在代码仓库中，需要手动创建和配置
- 请确保所有模板文件的文件名与系统要求完全一致
- 建议在使用前备份原始模板文件
- 修改模板内容时需保持占位符的完整性

## 使用说明

1. 运行主程序：
```bash
python MainWindow.py
```

2. 在界面中导入案件文件
3. 系统将自动分析并生成量刑建议

## 主要功能

### 1. 案件文书智能解析
- 支持PDF格式的案件文书自动解析
- 智能识别并提取案件关键信息，包括嫌疑人信息、案发时间地点、案件细节等
- 自动扫描和定位文书中的重要章节（如讯问笔录、归案经过、检验鉴定等）

### 2. 量刑标准智能计算
- 自动识别和分析血液中的酒精含量数据
- 智能判断量刑情节（如是否有前科、是否无证驾驶、是否造成他人伤害等）
- 根据法律规定和量刑标准，自动计算建议刑期

### 3. 文书自动生成
- 支持自动生成标准化的量刑文书
- 提供Word格式的文书输出
- 自动套用文书模板，确保格式规范统一

### 4. 便捷的用户界面
- 图形化操作界面，简单直观
- 支持文件拖拽导入功能
- 实时显示处理进度和结果

### 5. 辅助功能
- 支持扫描仪直接扫描文件
- 自动格式化案件信息
- 智能识别和转换数字格式（阿拉伯数字与中文数字互转）

## 注意事项
- 请确保模板文件格式正确
- 输入文件需符合指定格式要求
- 建议定期备份重要数据

## 文件说明
- `MainWindow.py`: 主程序入口
- `WXJS_newPdfget.py`: PDF文件解析模块
- `ExtraDef.py`: 辅助函数定义
- `ScbgScan.py`: 扫描功能模块

## 许可证
本项目采用 MIT 许可证。这意味着您可以自由地使用、修改和分发本软件，但需要保留原始许可证和版权声明。详细信息请查看 [LICENSE](LICENSE) 文件。