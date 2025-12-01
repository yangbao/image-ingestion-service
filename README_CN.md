# 图像接入微服务（Image Ingestion Microservice）
*生产级、高可用、可扩展、可云化切换的接入服务*

## 📑 目录
- [1. 介绍](#1-介绍)
- [4.1 启动与运行](#41-启动与运行)
  - [A. Docker 构建与运行](#a-docker-构建与运行)
  - [B. curl 示例](#b-curl-示例)
- [4.2 设计理念](#42-设计理念)
  - [A. 分层架构与代码结构](#a-分层架构与代码结构)
  - [B. 生产可用性与可测试性](#b-生产可用性与可测试性)
- [4.3 本地到生产的切换](#43-本地到生产的切换)
  - [A-env-配置示例](#a-env-配置示例)
  - [B-configpy-读取方式](#b-configpy-读取方式)
  - [C-存储后端的动态切换](#c-存储后端的动态切换)
  - [D-生产环境需要补充的实现](#d-生产环境需要补充的实现)
- [4.4 面向中国市场的架构愿景](#44-面向中国市场的架构愿景)
  - [1-端到端数据管道](#1-端到端数据管道)
  - [2-数据主权](#2-数据主权)
  - [3-跨境数据同步](#3-跨境数据同步)
  - [4-可扩展性与高可用](#4-可扩展性与高可用)
  - [5-多云策略](#5-多云策略)

---

## 1. 介绍

本项目实现了一个基于 **FastAPI + SQLAlchemy ORM + Docker** 的**图像接入微服务**，  
用于下一代 AI 图像平台的数据入口（Image Ingestion Service）。

该服务负责：

- 接收用户上传的图片
- 执行基础合规校验（如大小限制）
- 将文件委托给存储后端（本地 / 云存储）
- 将元数据写入数据库（如文件名、路径、时间戳、校验状态）

核心设计思想是：

> **将存储（Storage）与数据库（Database）等外部依赖彻底解耦**，  
> 使同一套代码可以：
> - 在本地使用 LocalUploader + SQLite 运行
> - 在生产环境切换为 阿里云 OSS + PostgreSQL  
> 且只需修改配置，而无需重构代码。

---

## 4.1 启动与运行

### A. Docker 构建与运行

#### 1. 构建镜像

```bash
docker build -t image-ingestion-service .
```

#### 2. 本地模拟模式运行

默认使用：

- `STORAGE_BACKEND=local`
- `DATABASE_URL=sqlite:///./images.db`

```bash
docker run -d --name ingestion-app -p 8000:8000 image-ingestion-service
```

#### 3. “生产模拟模式”运行

模拟：

- 使用 OSS 作为存储后端
- 使用 PostgreSQL 作为数据库

```bash
docker run -d --name ingestion-prod-sim -p 8000:8000   -e STORAGE_BACKEND="oss"   -e DATABASE_URL="postgresql+psycopg2://user:password@db-host:5432/dbname"   -e OSS_BUCKET="prod-image-bucket-cn"   image-ingestion-service
```

#### 4. 访问服务

- 基础地址：`http://localhost:8000`
- Swagger UI：`http://localhost:8000/docs`

---

### B. curl 示例

假设当前目录有 `my_image.png`：

```bash
curl -X POST "http://localhost:8000/upload"      -H "accept: application/json"      -H "Content-Type: multipart/form-data"      -F "file=@./my_image.png;type=image/png"
```

---

## 4.2 设计理念

### A. 分层架构与代码结构

项目采用清晰的**分层架构**，以实现最大化的职责分离（Separation of Concerns）：

| 组件                | 作用                          | 设计原则                         |
|---------------------|-------------------------------|----------------------------------|
| `app/main.py`       | API 路由入口                   | 通过依赖注入编排业务逻辑        |
| `app/config.py`     | 配置中心                       | 使用 Pydantic 统一管理配置       |
| `app/storage/`      | 存储抽象层                     | 使用 `Protocol` 定义统一接口     |
| `app/database.py`   | 数据库初始化与会话管理         | 封装数据库连接与 Session         |
| `app/models.py`     | ORM 模型定义                   | 基于 SQLAlchemy 的表结构定义     |
| `app/compliance.py` | 合规校验逻辑                   | 集中处理市场/合规相关规则        |
| `app/schemas.py`    | Pydantic 模型（请求/响应校验） | 防止非法输入，保证接口一致性     |

这种结构使得路由层、业务规则、存储实现和数据库访问彼此独立，便于扩展与维护。

---

### B. 生产可用性与可测试性

#### 1. 选择 FastAPI 的原因

- 原生支持 **异步（async）**，适合 I/O 密集型的上传场景
- 内置 **Pydantic 校验**，减少手工校验负担
- 自动生成 **Swagger 文档**，便于调试与对接
- 友好的 **依赖注入机制**，方便注入配置、DB Session、Storage 等组件

#### 2. 选择 SQLAlchemy ORM 的原因

- 屏蔽数据库差异：可以平滑地从 SQLite 迁移到 PostgreSQL
- 提高可维护性：数据库访问与业务逻辑解耦
- 更利于测试：可以使用内存数据库或 Mock 进行单元测试

#### 3. StorageUploader 抽象层的意义

`StorageUploader` 抽象用于：

- 统一 LocalUploader、AlibabaOSSUploader 等不同实现
- 让接入层逻辑 **不依赖具体存储厂商**
- 单元测试中可以轻松用 Mock 代替真实存储

#### 4. 独立的 `validate_content` 模块

将 `validate_content` 抽出为单独模块是为了：

- 将 **合规/风控逻辑** 与路由/控制器逻辑分离
- 为未来接入：
  - 图像内容审核 API
  - 中国本地合规检查（涉政/涉黄/敏感内容）
  - 自研 ML 审核模型  
 预留扩展点
- 让 `upload_image` 这一核心接口更聚焦于“编排流程”，而非“具体校验细节”

---

## 4.3 本地到生产的切换

本项目的一个关键设计目标是：

> **本地环境 → 生产环境 的切换只依赖配置变化，而非代码修改。**

所有运行参数都集中在 `app/config.py` 中，通过 Pydantic Settings 从 `.env` 读取。

---

### A. `.env` 配置示例

```env
ENV=prod
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
STORAGE_BACKEND=oss
OSS_BUCKET=prod-image-bucket-cn
```

---

### B. config.py 读取方式

`config.py` 中类似如下：

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    env: str = "local"
    database_url: str = "sqlite:///./images.db"
    storage_backend: str = "local"
    oss_bucket: str = "dev-bucket"

    class Config:
        env_file = ".env"

settings = Settings()
```

这样所有环境相关参数均通过 `settings` 对象访问，避免硬编码。

---

### C. 存储后端的动态切换

工厂方法 `get_uploader()` 根据配置返回不同实现：

```python
from app.config import settings
from app.storage.local import LocalUploader
# from app.storage.alibaba_oss import AlibabaOSSUploader

def get_uploader():
    if settings.storage_backend == "local":
        return LocalUploader()
    elif settings.storage_backend == "oss":
        return AlibabaOSSUploader(bucket=settings.oss_bucket)
    return LocalUploader()
```

`main.py` 中只依赖 `get_uploader()`，**并不知道具体的存储实现类型**，从而实现解耦。

---

### D. 生产环境需要补充的实现

真正上线生产环境时，开发者只需在 `AlibabaOSSUploader.save()` 中补充阿里云 OSS SDK 调用，例如：

```python
class AlibabaOSSUploader(StorageUploader):
    def __init__(self, bucket: str):
        self.bucket = bucket
        # 初始化 OSS SDK 客户端
        # self.client = ...

    def save(self, file: UploadFile, destination: str) -> str:
        # 伪代码：
        # object_key = f"{destination}/{file.filename}"
        # self.client.put_object(self.bucket, object_key, file.file)
        # return f"oss://{self.bucket}/{object_key}"
        raise NotImplementedError("生产环境中接入阿里云 OSS")
```

配合 `.env` 的修改，即可完成从本地到生产的平滑迁移。

---

## 4.4 面向中国市场的架构愿景

本节从中国市场、多云部署和合规要求出发，说明该接入服务在整体架构中的位置。

---

### 1. 端到端数据管道

典型生产场景下的整体链路如下：

```text
用户上传
  → 图像接入服务（Ingestion Service）
  → 对象存储（OSS/COS）
  → 元数据数据库（PostgreSQL/RDS）
  → 向量数据库（Milvus 等）
  → 下游 AI 服务（训练 / 推理 / 分析）
```

每一层都可以独立扩展、独立部署在中国云环境中。

---

### 2. 数据主权

为满足《数据安全法》《个人信息保护法（PIPL）》等要求：

- 所有 **原始图像、用户元数据、PII** 必须保留在中国大陆节点
- 建议采用 **阿里云 / 腾讯云 的中国区 Region** 作为主要部署地
- 使用：
  - VPC 专有网络
  - 安全组与 ACL
  - RAM/IAM 精细化权限控制  
  将中国区与海外区进行**网络与权限上的隔离**

任何跨境访问都必须经过严格审批与技术隔离。

---

### 3. 跨境数据同步

如需将部分数据同步到海外（如总部进行模型评估或业务分析），应遵循：

- 仅同步 **脱敏 / 匿名化 / 聚合后的数据**
- 在中国区内部署 **数据脱敏与聚合服务**，负责：
  - 消费原始日志与事件
  - 产出统计指标、模型表现概要、Embedding 分布等
- 数据通过：
  - 专线（如 Express Connect）
  - 加密 VPN 通道  
  安全传输至海外
- 每一种新的数据出境路径，都需经过：
  - 数据出境安全评估
  - 法务与合规审核

这样既保障了合规性，又能在一定程度上支持全球化业务与模型优化。

---

### 4. 可扩展性与高可用

要支撑 **百万级别/日 的上传量**，架构需具备：

- **无状态接入层**：图像接入服务本身不持久化状态，方便水平扩展
- 基于 Kubernetes（ACK/TKE）：
  - 多副本部署
  - HPA 自动扩缩容
  - 就绪/存活探针及滚动升级
- 对象存储（OSS/COS）提供几乎无限的存储容量
- 数据库层可通过：
  - 主从复制与读写分离
  - 连接池
  - 分库分表或分布式数据库（如 TiDB）  
  进一步提升吞吐量与可用性
- 通过 Kafka/RocketMQ 等消息队列，将上传与后续处理解耦，缓冲流量峰值

---

### 5. 多云策略

在中国市场采用多云策略可以：

- 提升整体容灾能力（如阿里云为主、腾讯云为备）
- 避免单一厂商锁定
- 适配不同客户/行业对云平台的偏好

基础设施层可以通过：

- Terraform（IaC）
- Helm Chart（K8s 部署模板）

进行统一管理；监控层则可使用：

- Prometheus + Grafana
- 配合云厂商原生监控服务

实现对整套多云架构的统一观测与管理。
