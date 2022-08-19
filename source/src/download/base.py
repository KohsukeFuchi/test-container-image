import os
import requests
import zipfile
import shutil

class DataDownload:
    def __init__(self, logger, savePath, dataType):
        self.logger = logger
        self.savePath = savePath
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
    
    def download_file_and_save(self, requestUrlDomain, prefNum):
        try:
            # SHAPEファイルを格納するリスト
            shp_file_path_list = []
            requestUrl = requestUrlDomain.format(prefNum)

            filename = requestUrl.split('/')[-1]
            self.logger.info('ファイル名：{}のダウンロードを開始します'.format(filename))
            r = requests.get(requestUrl, stream=True)
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
                # ZIPファイルを展開する
                # 日本語ファイル名なので，文字コードを直して展開する
                with zipfile.ZipFile(filepath) as zf:
                    for info in zf.infolist():
                        info.filename = info.orig_filename.encode('cp437').decode('cp932')
                        if os.sep != '/' and os.sep in info.filename:
                            info.filename = info.filename.replace(os.sep, '/')
                        
                        if info.filename.endswith('.shp'):
                            shp_file_path_list.append(self.savePath + info.filename)

                        zf.extract(info, self.savePath)
                self.logger.info('ファイル名：{}の展開処理が完了しました'.format(filename))
                os.remove(filepath)
            return shp_file_path_list
        except Exception as e:
            raise
