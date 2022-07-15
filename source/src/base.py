import pandas
import os
from logs.sets import logs

if __name__ == '__main__':
    logger = logs(os.environ['basedir'] + '/src/logs/log')
    try:
        print('a')
    except Exception as e:
        logger.exception(e)
