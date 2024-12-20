import multiprocessing

bind = '127.0.0.1:8000'
workers = 2 + 1

accesslog = '/var/tmp/askme_garoev.gunicorn.log'
