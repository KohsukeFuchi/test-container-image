from unittest import result
import geopandas as gpd
import pandas as pd
import numpy as np
import os
from shapely.ops import unary_union

class ShpReadAndEdit:
    def __init__(self, logger):
        self.logger = logger
        logger.info('ジオメトリ編集作業開始')
    
    """
        複数のshapeファイルを纏めて読む
    """
    def read_many_file(self, pathlist):
        try:
            gdf_list = []
            for path in pathlist:
                gdf = gpd.read_file(path)
                gdf_list.append(gdf)
                self.logger.info('Shapeファイル : {} を読み込みました'.format(path.split('/')[-1]))
                self.logger.info(gdf.head())
            return gdf_list
        except Exception as e:
            raise
    
    """
        shapeファイルをGeoDataFrame形式で読み込む
    """
    def read_file(self, path, encoder):
        try:
            gdf = gpd.read_file(path, encoding=encoder)
            self.logger.info('Shapeファイル : {} を読み込みました'.format(path.split('/')[-1]))
            self.logger.info(gdf.head())
            return gdf
        except Exception as e:
            raise
    
    """
        GeoDataFrameをShapeファイルとして保存する
    """
    def save_file(self, gdf, save_dir, filename):
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            gdf.to_file(save_dir + filename, encoding='utf8')
            self.logger.info('ファイル名：{}を保存しました'.format(filename))
            return
        except Exception as e:
            raise
    
    """
        DataFrameをCSVファイルとして保存する
    """
    def save_df_to_csv(self, df, save_dir, filename):
        try:
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            df.to_csv(save_dir + filename, index=False)
            self.logger.info('ファイル名：{}を保存しました'.format(filename))
            return
        except Exception as e:
            raise

    """
        複数のGeoDataFrameを縦方向に結合して1つのGeoDataFrameにする
    """
    def concat_gdf(self, gdf_list):
        try:
            cgdf = gpd.GeoDataFrame(
                pd.concat(
                    gdf_list,
                    ignore_index=True
                )
            )
            return cgdf
        except Exception as e:
            raise

    """
        複数のファイルパスリストから1つのGeoDataFrameとして読み込む
    """    
    def concat_gdf_from_path(self, path_list, encoder):
        try:
            gdf_list = []
            for path in path_list:
                gdf = self.read_file(path, encoder)
                gdf_list.append(gdf)
        
            cgdf = self.concat_gdf(gdf_list)
            return cgdf
        except Exception as e:
            raise
    

    """
        指定したカラムをユニークに1つのポリゴンの結合する
    """
    def gdf_unique_union_polygon(self, gdf, key_columns, feature_column_name):
        try:
            self.logger.info('ポリゴンの結合処理開始')
            # 指定したカラムのユニークなリストとして取り出す
            key_column_list = np.array([i if i is not None else '不明' for i in gdf[key_columns].tolist()])
            unique_key_column_array = np.unique(key_column_list)

            # ジオメトリをNumpy Arrayに変換する
            np_geom_array = np.array(gdf.geometry.tolist())

            # 結合結果を格納するリスト
            union_key_list = []
            union_geom_list = []

            for i in unique_key_column_array:
                # 指定したカラムの行列から，一致するidxのリストを取得する
                match_idx_array = np.where(key_column_list == i)[0]
                match_geom = np_geom_array[match_idx_array]

                if len(match_geom) == 0:
                    self.logger.info('要素：{}は一致するgeometryがありませんでした'.format(i))
                    continue

                # 一致したカラムのindexを参考にポリゴンを結合する
                union_geom = unary_union(match_geom)
                self.logger.info('要素 : {}のUNIONジオメトリを作成しました'.format(i))

                union_key_list.append(i)
                union_geom_list.append(union_geom)
            
            gdf = gpd.GeoDataFrame(
                {
                    feature_column_name: union_key_list,
                },
                geometry=union_geom_list,
                crs='EPSG:4326'
            )
            return gdf
            
        except Exception as e:
            raise

    """
    空間Indexによる交差検証
    """
    def geom_intersects_from_spatial_idx(self, spatial_idx, series, gdf):
        try:
            possible_matches_idx = list(spatial_idx.intersection(series.geometry.bounds))
            possible_matches = gdf.iloc[possible_matches_idx]
            precise_matches = possible_matches[possible_matches.intersects(series.geometry)]
            return precise_matches
        except Exception as e:
            raise

    """
        メッシュと対象ポリゴンの重なっている割合を算出する
    """
    def gdf_to_msh_about_percentage(self, gdf, msh, feature_name):
        try:
            spatial_idx = gdf.sindex
            # 結果格納用のDict Key Arrayを宣言
            key_column_list = np.array([i if i is not None else '不明' for i in gdf[feature_name].tolist()])
            unique_feature_array = np.unique(key_column_list)
            dict_key_array = np.insert(unique_feature_array, 0, 'msh_code')

            # 結果格納用のList
            result_list = []

            # 各メッシュごとに重なっているポリゴンとその重なっている面積比を算出
            for i in range(len(msh)):
                row_result_dict = dict.fromkeys(
                    dict_key_array,
                    0
                )
                row = msh.iloc[i]
                msh_code = row.mesh_cd
                row_result_dict['msh_code'] = msh_code

                # 以下のようにしなければGeoSeriesにならない
                row_geom = msh.iloc[[i]]

                precise_matches = self.geom_intersects_from_spatial_idx(spatial_idx, row, gdf)

                if len(precise_matches) == 0:
                    continue
                
                for j in range(len(precise_matches)):
                    pmi = precise_matches.iloc[j]
                    # ポリゴンの種類名を取得
                    key_name = pmi[feature_name]
                    intersect_area = row_geom.geometry.intersection(pmi.geometry).area.values[0]
                    msh_area = row_geom.geometry.area.values[0]
                    intersect_percentage = round(intersect_area / msh_area, 4)
                    row_result_dict[key_name] = row_result_dict[key_name] + intersect_percentage

                result_list.append(row_result_dict)
            
            # Dict in ListからDataFrameを生成
            df = pd.DataFrame(result_list)
            return df
        except Exception as e:
            raise

