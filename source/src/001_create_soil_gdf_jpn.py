from numpy import save
import pandas
import os
from logs.sets import logs
from download.base import DataDownload
from geom.base import ShpReadAndEdit
from glob import glob
import warnings

warnings.simplefilter('ignore')
"""_summary_
土壌データの取得
REQUEST URL : https://nlftp.mlit.go.jp/kokjo/tochimizu/F2/GIS/*.zip
"""
class SoilDataDownload(DataDownload):
    def __init__(self, logger, savePath, dataType):
        super().__init__(logger, savePath, dataType)
    
    def __del__(self):
        logger.info('{}作業終了'.format(dataType))

class SoilDataReadAndEdit(ShpReadAndEdit):
    def __init__(self, logger):
        super().__init__(logger)
    
    def __del__(self):
        logger.info('土壌ジオメトリ編集作業完了')

if __name__ == '__main__':
    # ベースディレクトリ
    baseDir = os.environ['basedir']
    # リクエストURL
    URL = "https://nlftp.mlit.go.jp/kokjo/tochimizu/F2/GIS/{}.zip"
    # ログ
    logger = logs(baseDir + '/src/logs/log')
    # データ保存ディレクトリ
    savePath = baseDir + '/data/soil/'
    # データの種類の決定
    dataType = 'soil'
    sdd = SoilDataDownload(
        logger=logger,
        savePath=savePath,
        dataType=dataType
    )

    sra = SoilDataReadAndEdit(
        logger=logger
    )

    try:
        sdd.is_dir_and_make_dirs()

        geo_path_list_dict = {
            'soil' : [],
            'geological_polygon' : [],
            'geological_line' : [],
        }

        for prefNum in range(1, 48):
            shp_path_list = sdd.download_file_and_save(URL, str(prefNum).zfill(2))

            if len(shp_path_list) == 0:
                logger.info('ダウンロードしたファイルがありませんでした')
                continue
            
            for path in shp_path_list:
                if path.endswith('土壌分類（ポリゴン）.shp'):
                    geo_path_list_dict['soil'].append(path)
                elif path.endswith('表層地質（ポリゴン）.shp'):
                    geo_path_list_dict['geological_polygon'].append(path)
                elif path.endswith('表層地質（ライン）.shp'):
                    geo_path_list_dict['geological_line'].append(path)
        
        # 全国版のGeoDataFrameを保存するPath
        jpn_gdf_dir = savePath + 'all/'
        # 全国版のメッシュポリゴンを読み取る
        msh = sra.read_file(baseDir + '/data/mesh/mesh4.shp', 'utf8')

        # 複数のShapeファイルを1つにまとめる
        for key, item in geo_path_list_dict.items():
            logger.info('カテゴリ：{}のGeoDataFrame郡を1つにまとめます'.format(key))
            cgdf = sra.concat_gdf_from_path(item, 'cp932')
            sra.save_file(cgdf, jpn_gdf_dir, key + '.shp')

            # メッシュに変換してCSVファイルとして保存する
            logger.info('カテゴリ：{}をメッシュに変換します'.format(key))
            df = sra.gdf_to_msh_about_percentage(cgdf, msh, '属性1')
            sra.save_df_to_csv(df, savePath + 'csv/all/', key + '.csv')

            
    except Exception as e:
        logger.exception(e)
    
    finally:
        del sdd, sra
        logger.info('処理を終了しました')
