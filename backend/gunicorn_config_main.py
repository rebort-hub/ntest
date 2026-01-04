import multiprocessing

from config import main_server_port

bind = f'0.0.0.0:{main_server_port}'  # 访问地址
workers = 15 if multiprocessing.cpu_count() * 2 + 1 >= 15 else multiprocessing.cpu_count() * 2 + 1
worker_class = 'uvicorn.workers.UvicornWorker'  # 工作模式协程
threads = 4  # 每个worker的线程数
timeout = 120
keepalive = 5
