FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件并安装 (利用 Docker 缓存机制)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个应用代码
COPY app/ ./app/

# 暴露应用端口
EXPOSE 8000

# 运行命令：使用 app/main.py 中的 app 实例
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]