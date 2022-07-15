import pandas
import os
from logs.sets import logs
from download.base import DataDownload

"""_summary_
土壌データの取得
REQUEST URL : https://nlftp.mlit.go.jp/kokjo/tochimizu/F2/GIS/*.zip
"""
class SoilDataDownload(DataDownload):
    def __init__(self, logger, savePath, requestUrl, prefNum, dataType):
        super().__init__(logger, savePath, requestUrl, prefNum, dataType)
    
    def __del__(self):
        logger.info('{}作業終了'.format(dataType))

if __name__ == '__main__':
    # リクエストURL
    URL = "https://nlftp.mlit.go.jp/kokjo/tochimizu/F2/GIS/{}.zip"
    # ログ
    logger = logs(os.environ['basedir'] + '/src/logs/log')
    # データ保存ディレクトリ
    savePath = os.environ['basedir'] + '/data/soid/'
    # 都道府県番号の決定
    prefNum = 44
    # データの種類の決定
    dataType = 'soil'
    sdd = SoilDataDownload(
        logger=logger,
        savePath=savePath,
        requestUrl=URL.format(prefNum),
        prefNum=prefNum,
        dataType=dataType
    )
    try:
        sdd.is_dir_and_make_dirs()
        sdd.download_file_and_save()
    except Exception as e:
        logger.exception(e)
