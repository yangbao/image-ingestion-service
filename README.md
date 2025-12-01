# image-ingestion-service
take-home challenge

## Project Structure
  
    app/
        __init__.py
        main.py              # FastAPI entry point (defines routes/endpoints)
                             # FastAPI 入口文件（定义路由/接口）
    
        config.py            # Configuration management (env variables, settings for dev/prod)
                             # 配置管理（环境变量、开发/生产配置）
    
        models.py            # SQLAlchemy ORM models (DB table definitions)
                             # SQLAlchemy ORM 模型（数据库表结构）
    
        database.py          # Database initialization & session management
                             # 数据库初始化与会话管理

    storage/
          __init__.py
          base.py            # Abstract interface for storage uploaders (base class)
                             # 存储上传抽象接口（基类）
    
          local.py           # Local file system uploader implementation
                             # 本地文件系统上传实现
    
          # alibaba_oss.py   # Placeholder for future Alibaba Cloud OSS uploader implementation
                             # 预留阿里云 OSS 上传实现（未来扩展）
    
        compliance.py        # Content validation / compliance check placeholder logic
                             # 内容校验/合规检查占位逻辑
    
        schemas.py           # Pydantic schemas for request/response validation
                             # Pydantic 模型（请求/响应验证）

      tests/
        test_upload.py       # Basic unit test for upload behavior (optional)
                             # 上传逻辑的基础单元测试（可选）

    Dockerfile             # Docker build instructions for containerized deployment
                         # Docker 构建指令（用于容器化部署）

    requirements.txt       # Python dependencies required by the application
                         # Python 依赖包列表

    README.md              # Project overview, setup instructions, API documentation
                         # 项目介绍、安装指南和 API 文档
# Image Ingestion Microservice
*A Production-Ready, Configurable, Cloud-Extensible Ingestion Service*

## 📑 Table of Contents
- [1. Introduction](#1-introduction)
- [4.1 Setup and Execution](#41-setup-and-execution)
  - [A. Build & Run with Docker](#a-build--run-with-docker)
  - [B. curl Example](#b-curl-example)
- [4.2 Design Philosophy](#42-design-philosophy)
  - [A. Code Structure & Layered Architecture](#a-code-structure--layered-architecture)
  - [B. Production Readiness & Testability](#b-production-readiness--testability)
- [4.3 Bridging to Production](#43-bridging-to-production)
  - [A. Local → Alibaba Cloud OSS](#a-local--alibaba-cloud-oss)
  - [B. SQLite → PostgreSQL](#b-sqlite--postgresql)
- [4.4 Architectural Vision for China Market](#44-architectural-vision-for-china-market)
  - [1. Data Sovereignty](#1-data-sovereignty)
  - [2. Cross-Border Data Sync](#2-cross-border-data-sync)
  - [3. Scalability & Resilience](#3-scalability--resilience)

---

## 1. Introduction
This project implements a **highly available**, **configurable**, and **cloud-extensible** Image Ingestion Microservice using:

- **FastAPI**
- **SQLAlchemy ORM**
- **Docker**

The service functions as the **entry point** to a next-generation AI image platform.

The core architectural principle is:

> **Decoupling all external dependencies (Storage / Database)**  
> to support seamless migration from a simulation environment to real-world production stacks  
> (e.g., Alibaba Cloud OSS and PostgreSQL),  
> with minimal code changes and maximum configurability.

---

## 4.1 Setup and Execution

###  Running Directly with Python/Uvicorn (Recommended for Development)
This method allows you to debug the code directly in your local environment.
1. Set Up Project Structure
    First, please ensure your project file structure is organized as planned within the image-ingestion-service directory:
2. Install Dependencies
    Open your command line or terminal, navigate to the project root directory (image-ingestion-service/), and execute the following commands to install all required Python packages:
    ```
   # It is recommended to create a Python virtual environment first
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # venv\Scripts\activate  # Windows
    
    # Install dependencies
    pip install -r requirements.txt
   ```
3. Run the Service
  After installing dependencies and activating the virtual environment, use Uvicorn to run the FastAPI application.
    ```
    # Command format: uvicorn [module_path]:[FastAPI_instance_name] --reload --host 0.0.0.0 --port 8000
       uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Upon successful service startup:
   You can access the API documentation and test the endpoints by navigating to http://127.0.0.1:8000/docs in your browser.

    The service will use default configuration: files will be saved locally in the ./uploads/ai_platform_images/ directory, and metadata will be stored in the ./images.db SQLite file.

### A. Build & Run with Docker

#### 1. Build the Docker Image
```bash
docker build -t image-ingestion-service .
```

#### 2. Run (Local Simulation Mode)
Uses:
- STORAGE_MODE=local
- SQLite database

```bash
docker run -d --name ingestion-app -p 8000:8000 image-ingestion-service
```

#### 3. Run (Production Simulation Mode)
```bash
docker run -d --name ingestion-prod-sim -p 8000:8000   -e STORAGE_MODE="oss"   -e DATABASE_URL="postgresql+psycopg2://user:password@db-host:5432/dbname"   -e OSS_BUCKET="prod-image-bucket-cn"   image-ingestion-service
```

#### 4. Access the API
| Endpoint | URL |
|----------|-----|
| Base URL | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

---

### B. curl Example
```bash
curl -X POST "http://localhost:8000/upload"      -H "accept: application/json"      -H "Content-Type: multipart/form-data"      -F "file=@./my_image.png;type=image/png"
```

---

## 4.2 Design Philosophy

### A. Code Structure & Layered Architecture
| Component | Purpose | Design Principle |
|----------|---------|------------------|
| app/main.py | API Router / Entry point | Dependency Injection |
| app/config.py | Config layer | Centralized env config |
| app/storage/ | Storage abstraction | Python Protocol |
| app/database.py / models.py | Persistence | ORM portability |
| app/compliance.py | Business logic | Central rule enforcement |

---

### B. Production Readiness & Testability
- Strong decoupling through DI  
- Mockable storage & DB layers  
- SQLAlchemy enables seamless SQLite ↔ PostgreSQL switching  
- FastAPI provides async performance & automatic validation  

---

## 4.3 Bridging to Production

### A. Local → Alibaba Cloud OSS
| Variable | Local | Production | Change Needed |
|----------|--------|------------|----------------|
| STORAGE_MODE | local | oss | None (factory auto-loads OSS uploader) |
| OSS_BUCKET | default | prod-images-cn-north | Implement OSS SDK call |

### B. SQLite → PostgreSQL
| Variable | Local | Production | Change Needed |
|----------|--------|------------|----------------|
| DATABASE_URL | sqlite:///./images.db | postgresql+psycopg2://... | None |

---

## 4.4 Architectural Vision for China Market

### 1. Data Sovereignty
All Chinese user data must remain **inside Mainland China**.  
Enforce via:
- Region-isolated deployment  
- VPC restrictions  
- IAM/RAM tight permissions  
- No outbound access without approval  

### 2. Cross-Border Data Sync
Only **anonymized, aggregated** data may leave China.  
Pipeline:
1. Masking/Anonymization Service  
2. Secure tunnel (Express Connect / VPN)  
3. Compliance review & approval  

### 3. Scalability & Resilience
- Multi-AZ Kubernetes deployment  
- Autoscaling via HPA  
- Event-driven ingestion → Kafka/RocketMQ  
- OSS/COS provide massive storage capacity  
- DB scalability via read-write splitting or sharding  

---

