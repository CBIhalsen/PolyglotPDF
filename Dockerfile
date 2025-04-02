
# 1. 使用官方 Python 3.9 的精简版镜像作为基础
FROM python:3.9-slim

# 2. 如果你需要一些系统库支持，可在此处安装
#    比如安装 gcc、libssl-dev 等 (仅举例)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libssl-dev \
#     && rm -rf /var/lib/apt/lists/*

# 3. 设置工作目录
WORKDIR /app

# 4. 将 requirements.txt 复制到容器内
COPY requirements.txt /app/

# 5. 安装 Python 依赖包
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制项目源代码到容器内
COPY . /app

# 7. 暴露端口 12226（如你的项目需要此端口）
EXPOSE 12226

# 8. 容器启动时，默认执行 Python 脚本
CMD ["python", "app.py"]
