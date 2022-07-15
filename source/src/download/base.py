import os
import requests
import zipfile
import shutil

class DataDownload:
    def __init__(self, logger, savePath, requestUrl, prefNum, dataType):
        self.logger = logger
        self.savePath = savePath
        self.requestUrl = requestUrl
        self.prefNum = prefNum,
        self.dataType = dataType
        logger.info('{}作業開始'.format(dataType))
    
    def is_dir_and_make_dirs(self):
        try:
            if not os.path.exists(self.savePath):
                os.makedirs(self.savePath)
                self.logger.info('ディレクトリ：{}を新たに作成しました'.format(self.savePath))
            else:
                self.logger.info('ディレクトリ：{}は存在します'.format(self.savePath))
            return
        except Exception as e:
            raise
    
    def download_file_and_save(self):
        try:
            filename = self.requestUrl.split('/')[-1]
            self.logger.info('ファイル名：{}のダウンロードを開始します'.format(filename))
            r = requests.get(self.requestUrl, stream=True)
            filepath = self.savePath + filename
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=2048):
                    if chunk:
                        f.write(chunk)
                        f.flush()
            self.logger.info('ファイル名：{}のダウンロード処理が完了しました'.format(filename))
            
            # zipファイルの場合は展開する
            if zipfile.is_zipfile(filepath):
                self.logger.info('ファイル名：{}の展開処理を開始します'.format(filename))
                shutil.unpack_archive(filepath, self.savePath)
                self.logger.info('ファイル名：{}の展開処理が完了しました'.format(filename))
            return
        except Exception as e:
            raise
