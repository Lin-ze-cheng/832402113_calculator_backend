# Calculator Backend

基于 FastAPI 和 SQLite 的计算器后端。后端负责输入校验、安全表达式解析、计算、异常处理和历史记录持久化。

作者：832402113 林泽成

GitHub 仓库：<https://github.com/Lin-ze-cheng/832402113_calculator_backend>

## 技术栈

- Python
- FastAPI
- SQLite
- Pytest

## 环境与启动

需要 Python 3.10 或更高版本，推荐 Python 3.12。

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

接口文档：<http://127.0.0.1:8000/docs>

## 数据库

首次启动时会自动创建：

```text
data/calculator.db
```

历史记录表包含 `id`、`expression`、`result` 和 `created_at`。

部署时可以通过环境变量指定数据库位置：

```text
CALCULATOR_DB_PATH=/持久化磁盘/calculator.db
```

## 跨域配置

本地开发默认允许所有来源。生产部署时建议设置实际前端域名：

```text
CALCULATOR_CORS_ORIGINS=https://你的前端域名.example
```

多个域名用英文逗号分隔。

## API

| 方法 | 地址 | 用途 |
|---|---|---|
| GET | `/api/health` | 服务健康检查 |
| POST | `/api/calculate` | 计算表达式并保存历史 |
| GET | `/api/history` | 查询历史记录 |
| DELETE | `/api/history/{id}` | 删除指定历史记录 |
| DELETE | `/api/history` | 清空全部历史记录 |

## 测试

```powershell
python -m pytest
```

## 部署提醒

如果部署平台的文件系统在重启时会被重置，不应继续使用该平台的本地 SQLite 文件作为正式数据库。请改用持久磁盘，或将数据库层改为云 MySQL/PostgreSQL。

仓库中包含 `Dockerfile`，支持容器部署。部署平台需要将容器端口设置为 `8000`，并根据实际情况配置：

```text
CALCULATOR_CORS_ORIGINS=https://你的前端域名.example
CALCULATOR_DB_PATH=/持久化磁盘/calculator.db
```
