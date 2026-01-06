

## 1. 背景与目标
### 1.1 背景
+ 公共实验空间内的电脑都在同一个局域网（LAN）。
+ 有一台 **Windows 显微镜控制电脑**：负责采集图像并保存到本地文件夹。
+ 有一台 **Linux 服务器**：已安装 Matlab，且部署有用于图像分析的 Matlab 程序包（以下简称“分析包”）。

### 1.2 目标
开发一个部署在实验室内部、通过浏览器访问的 Web APP，实现：

1. 实验人员在网页上提交“分析任务”，任务输入为显微镜电脑采集的图像文件夹。
2. Web APP 连接 Linux 服务器，在服务器端启动 Matlab 调用分析包完成计算。
3. 输出结果为 CSV 表格，可在 Web APP 上查看状态并下载到本地。
4. 支持多人同时提交任务：必须有任务队列、状态展示、日志/进度、任务历史。
5. 前端能设置/选择文件路径、查看 Matlab/分析包版本、查看服务器运行状态。

---

## 2. 角色与使用场景
### 2.1 角色
+ **实验人员（User）**：提交任务、查看队列、下载结果。
+ **管理员（Admin，可选）**：管理用户、配置路径白名单、并发限制、查看系统健康、清理历史任务等。

### 2.2 核心用户故事（User Stories）
1. 我在网页上选择“显微镜图像文件夹路径”，点击提交，系统开始排队分析。
2. 我能看到当前队列里有哪些任务、谁提交的、排到第几、预计/实际开始时间。
3. 我能在任务详情页看到“运行中/完成/失败”、进度、关键日志。
4. 完成后我能下载 CSV（单个或打包 ZIP），并看到结果摘要（例如行数、关键指标）。
5. 我能在系统信息页看到：Matlab 版本、分析包版本、服务器 CPU/内存/磁盘、当前运行任务数等。
6. 多个人同时点提交时，不会把 Matlab 许可或服务器资源打爆：系统按队列受控执行。

---

## 3. 关键约束与假设（一定要在开工前定稿）
### 3.1 图像数据如何让 Linux 服务器读到？
浏览器无法直接让服务器读取“用户电脑本地 C 盘路径”，所以**路径必须从服务器视角可访问**。建议三选一：

**方案 A（推荐）：Windows 共享文件夹 + Linux 挂载 SMB**

+ Windows 显微镜电脑将图像目录共享：如 `\\MICROSCOPE-PC\MicroscopeImages\`
+ Linux 服务器挂载为本地目录：如 `/mnt/microscope_images/`
+ Web APP 只允许选择 `/mnt/microscope_images/...` 下的路径（或基于任务输入一个相对路径）
+ ✅ 最稳定、无需上传、数据不搬运
+ ⚠️ 需要 IT/管理员配置共享权限与挂载（建议只读）

**方案 B：Windows 上跑一个轻量“采集代理”同步到服务器**

+ 显微镜电脑采集完自动把数据 rsync/sftp 到服务器固定目录
+ ✅ 服务器端简单、安全可控
+ ⚠️ 需要额外开发/部署 Windows Agent

**方案 C：Web 上传**

+ 用户在网页上传图片/压缩包到服务器再分析
+ ✅ 最通用
+ ⚠️ 大图像集上传慢、占带宽，不推荐做主路径

> 本文后续默认采用 **方案 A**。如果现场网络权限不允许 SMB，再切换 B。
>

### 3.2 Matlab 许可与并发
+ 若 Matlab 许可有限或分析包占资源：建议 **限制同时运行的 Matlab 进程数**（默认 1 个），其它任务排队。

---

## 4. 功能需求（FR）
### FR-1 认证与权限
+ 实验室内网访问，仍建议登录（最少做到“谁提交的任务可追溯”）。
+ 角色：User / Admin（可选）。
+ 可选：IP 白名单（仅允许内网网段）。

### FR-2 新建分析任务（核心）
用户可在“新建任务”页配置：

+ **输入路径**：服务器可访问的图像目录（例如 `/mnt/microscope_images/exp_2026_01_06/run1/`）
+ **输出命名**：任务名/实验编号/备注
+ **分析包版本**：默认当前版本；如未来支持多版本可切换
+ **参数**（按分析包需要）：如通道、阈值、ROI、时间点范围等
+ 点击“提交”后生成任务 ID，进入队列

校验：

+ 路径必须在允许的根目录白名单下（防止读系统敏感目录）
+ 路径存在且可读
+ 目录内文件数/大小可选做提示

### FR-3 队列与任务生命周期
任务状态机（建议）：

+ `PENDING`（等待）
+ `RUNNING`（运行）
+ `SUCCEEDED`（完成）
+ `FAILED`（失败）
+ `CANCELLED`（取消）

队列要求：

+ FIFO 默认；可选优先级（Admin）
+ 显示排队序号、提交时间、预计开始（可估算）
+ 支持取消 PENDING 任务；RUNNING 的取消视 Matlab 支持（通常做“请求取消”，由脚本轮询退出）

### FR-4 任务详情页：进度、日志、结果
+ 展示：输入路径、参数、提交人、开始/结束时间、耗时
+ **进度**：至少做到阶段性（例如 “扫描文件/预处理/分析/导出CSV”）
+ **日志**：展示 Matlab stdout/stderr 或日志文件 tail
+ **结果**：提供 CSV 下载按钮；可显示摘要（行数、列名、关键指标预览前 50 行）

### FR-5 结果下载
+ 下载方式：
    - 单个 CSV 直下
    - 若有多个输出（CSV+图+报告）：打包 ZIP
+ 支持“结果保留策略”：如保留 30 天，管理员可清理

### FR-6 系统信息页（服务器状态 + 版本）
+ Matlab 版本（例如 `ver('MATLAB')`）
+ 分析包版本（来自包内 `VERSION.txt` 或 `packageInfo()`）
+ 服务器状态：
    - CPU / Memory / Disk 使用率
    - 当前 RUNNING 数量、队列长度
    - 最近失败任务数（可选）
+ Worker/队列组件状态（如 Redis/Celery health）

### FR-7 审计与追溯
+ 记录：谁、什么时候、用什么参数、跑了哪个输入目录、输出文件哈希（可选）

---

## 5. 非功能需求（NFR）
+ **NFR-1 可用性**：内网稳定运行；断网/刷新不影响任务执行。
+ **NFR-2 安全**：
    - 输入路径白名单限制 + 防路径穿越
    - 下载只允许访问该任务输出目录
    - 日志脱敏（如果包含路径/用户名等可选）
+ **NFR-3 性能**：
    - 大目录扫描需分页/异步
    - Matlab 运行由 Worker 异步执行，Web 请求不阻塞
+ **NFR-4 可维护**：
    - 分析包作为“可替换模块”，升级不改 Web 主体
    - 配置（白名单、并发数、Matlab 路径）集中化
+ **NFR-5 可观测性**：
    - 结构化日志
    - 任务指标（成功率、平均耗时）
    - 失败可追踪（保存 Matlab log）

---

## 6. 总体架构（推荐实现）
### 6.1 组件
+ **前端**：Web UI（React/Vue 任一）
+ **后端 API**：Python FastAPI（或 Node/Java 均可）
+ **任务队列**：Redis + Worker（Celery/RQ/自研均可）
+ **数据库**：PostgreSQL（小规模也可 SQLite，但多人并发建议 PG）
+ **文件存储**：
    - 输入：Linux 挂载的显微镜共享目录 `/mnt/microscope_images`
    - 输出：服务器本地目录 `/data/app_outputs/<job_id>/`

### 6.2 数据流
1. 用户提交任务 → API 写入 DB（PENDING）→ 推送到队列
2. Worker 取任务 → 调用 Matlab 批处理运行分析包 → 输出 CSV 到输出目录
3. Worker 更新 DB 状态 + 写日志/进度文件
4. 前端轮询/WS 获取状态 → 完成后提供下载

### 6.3 Matlab 调用方式（Linux）
建议用 batch 模式：

+ `matlab -batch "run('/opt/analysis/run_job.m')"`  
或
+ `matlab -nodisplay -nosplash -r "try; run_job('config.json'); catch e; disp(getReport(e)); exit(1); end; exit(0);"`

> 强烈建议：**Web APP 将任务参数写成一个 job_config.json**，Matlab 脚本读取该 JSON 并输出统一格式结果与进度。
>

---

## 7. 分析包接口约定（给 Matlab 开发/封装的人）
### 7.1 输入
`job_config.json`（示例）

```json
{
  "job_id": "J20260106_000123",
  "input_dir": "/mnt/microscope_images/exp_001/run1",
  "output_dir": "/data/app_outputs/J20260106_000123",
  "params": {
    "channel": "GFP",
    "threshold": 0.35
  }
}
```

### 7.2 输出
+ 必须输出：`result.csv`
+ 建议输出：
    - `progress.json`（实时更新进度）
    - `run.log`（详细日志）
    - `summary.json`（关键指标摘要、行数、字段说明）

`progress.json`（示例）

```json
{
  "stage": "ANALYZING",
  "percent": 42,
  "message": "Processing frame 210/500",
  "updated_at": "2026-01-06T12:34:56Z"
}
```

### 7.3 返回码
+ 0：成功
+ 非 0：失败（错误信息写入 `run.log`，并在 stdout 输出简要摘要）

---

## 8. API 设计（示例）
### 8.1 认证
+ `POST /api/login`
+ `POST /api/logout`
+ `GET /api/me`

### 8.2 任务
+ `POST /api/jobs` 创建任务
    - body: input_dir, params, job_name
+ `GET /api/jobs` 列表（支持 status 过滤、分页）
+ `GET /api/jobs/{job_id}` 详情（含状态、进度、日志摘要）
+ `POST /api/jobs/{job_id}/cancel` 取消
+ `GET /api/jobs/{job_id}/download` 下载结果（csv 或 zip）

### 8.3 系统状态
+ `GET /api/system/status`（CPU/MEM/DISK、队列长度、worker 状态）
+ `GET /api/system/versions`（Matlab 版本、分析包版本）

### 8.4 路径（可选增强）
+ `GET /api/fs/list?path=/mnt/microscope_images/exp_001`  
用于前端“浏览目录选择输入路径”（只允许白名单根目录下）

---

## 9. 数据模型（DB 表建议）
### 9.1 jobs 表（核心）
+ job_id (PK)
+ user_id
+ job_name
+ input_dir
+ output_dir
+ params_json
+ status (PENDING/RUNNING/…)
+ queue_position（可选冗余）
+ created_at / started_at / finished_at
+ error_message（短）
+ result_csv_path
+ package_version
+ matlab_version

### 9.2 job_events 表（审计/日志索引，可选）
+ id
+ job_id
+ ts
+ level
+ message

---

## 10. 前端页面清单
1. **登录页**（可选）
2. **Dashboard**
    - 系统状态卡片（CPU/MEM/DISK/队列长度）
    - Matlab/分析包版本
3. **新建任务**
    - 输入路径选择（输入框 + “浏览”）
    - 参数表单
    - 提交
4. **任务列表/队列**
    - 过滤：我的任务/全部、状态
    - 排队序号、状态、提交人、提交时间、耗时
5. **任务详情**
    - 状态、进度条、阶段
    - 日志窗口（实时刷新）
    - 下载按钮
    - 失败时展示 error_message + 日志链接

---

## 11. 关键工程细节（避免踩坑）
### 11.1 路径安全
+ 后端必须验证 `input_dir` 在允许根目录列表内，例如只允许：
    - `/mnt/microscope_images`
    - `/data/uploads`（如果有上传）
+ 禁止 `..`、符号链接逃逸（需 realpath 后再判断前缀）

### 11.2 并发控制
+ 配置项：`MAX_CONCURRENT_MATLAB=1`（默认）
+ Worker 侧用 semaphore 或队列并发数限制
+ 避免同一输入目录被重复跑（可选：对 input_dir 做去重锁）

### 11.3 进度展示
+ 最简单可靠：Matlab 定期写 `progress.json`，后端读取返回前端
+ 日志：Worker 将 stdout/stderr 重定向到 `run.log`

### 11.4 失败诊断
+ Worker 捕获进程返回码
+ 截取 `run.log` 最后 N 行写入 DB 的 `error_message` 便于列表页快速查看

---

## 12. 开发伪代码（核心流程）
下面用“Python + FastAPI + Redis队列 + Worker”写伪代码，软件团队可按自己技术栈映射实现。

### 12.1 后端：创建任务
```plain
POST /api/jobs(body):
  user = require_login()
  input_dir = body.input_dir
  params = body.params
  job_name = body.job_name

  real_input = realpath(input_dir)
  assert real_input starts_with any(ALLOWED_INPUT_ROOTS)
  assert exists(real_input) and is_dir(real_input)

  job_id = generate_job_id()
  output_dir = "/data/app_outputs/" + job_id
  mkdir(output_dir)

  write_json(output_dir + "/job_config.json", {
     job_id, input_dir: real_input, output_dir, params
  })

  job = DB.insert("jobs", {
     job_id, user_id: user.id, job_name,
     input_dir: real_input, output_dir,
     params_json: params, status: "PENDING",
     created_at: now()
  })

  QUEUE.push(job_id)   // e.g. Redis list / Celery task
  return { job_id }
```

### 12.2 Worker：主循环（队列取任务 → 调 Matlab）
```plain
worker_loop():
  while true:
    job_id = QUEUE.pop_blocking()
    if job_id is None: continue

    job = DB.get_job(job_id)
    if job.status != "PENDING": continue  // 避免重复

    DB.update_job(job_id, {status:"RUNNING", started_at: now()})

    cfg_path = job.output_dir + "/job_config.json"
    log_path = job.output_dir + "/run.log"

    // 并发控制（确保同一时间最多 N 个 Matlab）
    acquire(MATLAB_SEMAPHORE)

    try:
      matlab_cmd = build_matlab_command(cfg_path)
      exit_code = run_process(matlab_cmd, stdout_to=log_path, stderr_to=log_path)

      if exit_code == 0 and exists(job.output_dir + "/result.csv"):
         DB.update_job(job_id, {
           status:"SUCCEEDED",
           finished_at: now(),
           result_csv_path: job.output_dir + "/result.csv"
         })
      else:
         err_tail = tail(log_path, 80)
         DB.update_job(job_id, {
           status:"FAILED",
           finished_at: now(),
           error_message: summarize(err_tail)
         })

    except Exception e:
      append(log_path, "\n[worker_exception]" + str(e))
      DB.update_job(job_id, {status:"FAILED", finished_at: now(), error_message: str(e)})

    finally:
      release(MATLAB_SEMAPHORE)
```

### 12.3 构造 Matlab 命令
```plain
build_matlab_command(cfg_path):
  // 推荐：Matlab 入口 run_job.m 读取 cfg_path JSON
  entry = "/opt/analysis/run_job.m"
  // -batch 更干净（不同版本兼容性略有差异，团队可按版本调整）
  return [
    "matlab",
    "-batch",
    "try, run('" + entry + "'); catch e, disp(getReport(e)); exit(1); end; exit(0);"
  ]
```

> 更推荐的做法：`run_job(cfg_path)`，把 cfg_path 作为参数传进去，避免脚本内 hardcode。命令可变为：  
`matlab -batch "run_job('.../job_config.json')"`
>

### 12.4 后端：查询任务状态（含进度）
```plain
GET /api/jobs/{job_id}:
  user = require_login()
  job = DB.get_job(job_id)
  assert user_can_view(job)

  progress_file = job.output_dir + "/progress.json"
  if exists(progress_file):
     progress = read_json(progress_file)
  else:
     progress = null

  log_tail = tail(job.output_dir + "/run.log", 200) if exists else ""

  return { job fields..., progress, log_tail }
```

### 12.5 后端：下载结果
```plain
GET /api/jobs/{job_id}/download:
  user = require_login()
  job = DB.get_job(job_id)
  assert user_can_view(job)
  assert job.status == "SUCCEEDED"

  file = job.output_dir + "/result.csv"
  assert realpath(file) starts_with job.output_dir  // 防越权
  return send_file(file, filename=job.job_name + ".csv")
```

### 12.6 取消任务
```plain
POST /api/jobs/{job_id}/cancel:
  user = require_login()
  job = DB.get_job(job_id)
  assert user_can_cancel(job)

  if job.status == "PENDING":
     DB.update_job(job_id, {status:"CANCELLED", finished_at: now()})
     QUEUE.remove(job_id) // 若队列支持移除；不支持就靠 worker 跳过
  else if job.status == "RUNNING":
     // 软取消：写一个 cancel.flag，Matlab 代码每处理若干文件检查一次
     write_file(job.output_dir + "/cancel.flag", "1")
     DB.insert_event(job_id, "cancel_requested")
  return ok
```

---

## 13. 验收标准（建议写进交付里）
1. **单人流程**：提交 → RUNNING → SUCCEEDED → 下载 CSV 成功，CSV 内容正确。
2. **多人并发**：3 人同时提交，队列按顺序执行；并发数不超过配置值；状态显示正确。
3. **失败可诊断**：人为制造错误（路径不存在/Matlab 报错），任务状态 FAILED，日志可见。
4. **安全**：输入路径不在白名单时拒绝；下载无法访问其它任务目录。
5. **版本展示**：页面能显示 Matlab 版本 + 分析包版本。
6. **系统状态**：CPU/MEM/DISK 与队列长度能显示，刷新不崩。

---

## 14. 风险与对策（提前说清楚能省很多沟通）
+ **风险：Windows 共享权限/SMB 挂载不稳定**  
对策：优先只读共享；服务器端固定挂载；必要时启用 Agent 同步（方案 B）。
+ **风险：Matlab 许可限制导致并发失败**  
对策：默认并发=1；后续按许可扩容；队列强制串行。
+ **风险：分析包升级导致参数不兼容**  
对策：job_config.json 做版本字段；分析包提供向后兼容或后端做参数校验。
+ **风险：目录里文件巨大导致扫描慢**  
对策：异步扫描；进度分阶段；必要时缓存目录清单。

---

如果你愿意，我也可以把这份内容按你们公司常用格式再“工程化”一下（例如：PRD + SRS 分离、接口文档按 OpenAPI、任务拆分成 Jira Epic/Story），但即使不做，那份团队也已经能直接开工了。你接下来只需要把两点定下来：**（1）你们图像路径到底走 SMB 挂载还是 Windows Agent 同步；（2）Matlab 允许同时跑几个进程**。

