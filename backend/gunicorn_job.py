from app.configs.config import job_server_port

bind = f'0.0.0.0:{job_server_port}'  # 访问地址
workers = 1  # 任务调度服务，只起一个worker
threads = 4  # 每个worker的线程数
worker_class = 'uvicorn.workers.UvicornWorker'  # 工作模式协程
timeout = 120
keepalive = 5

# 注意：使用 gunicorn 启动时，应该在 backend 目录下运行
# 命令：gunicorn -c gunicorn_job.py scheduledtask.job:job