import logging, logging.handlers
import os
import sys
import inspect
from pathlib import Path

app_home = str(Path(__file__).parents[1])
sys.path.append(app_home)

def logs(dirnames):
    # 呼び出し元のファイル名をlogファイルの名前にする
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    filename = module.__file__.split('/')[-1]
    prog_name = filename.split('.')[0]

    #フォーマット
    log_format = logging.Formatter(
        "%(asctime)s [%(levelname)8s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )
    # レベル
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 標準出力へのハンドラ
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)
    logger.addHandler(stdout_handler)

    if not os.path.exists(dirnames):
        os.makedirs(dirnames)

    # ログファイルへのハンドラ
    file_handler = logging.handlers.RotatingFileHandler(
        dirnames + '/' + prog_name + '.log',
        maxBytes = 100000,
        backupCount = 10
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger
