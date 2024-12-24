import pandas as pd
import geopandas as gpd
import numpy as np
import pyproj
import datetime as dt
import sys

sys.stdout.reconfigure(encoding='utf-8')

gis_file_eupmyeondong = resourceFolder + '/읍면동.shp' # 읍면동 
gis_file_road = resourceFolder + '/LinkShape.shp' #도로이름 - 30분 소요

gis_df_eupmyeondong = gpd.read_file(gis_file_eupmyeondong, encoding='euc-kr')
gis_df_road = gpd.read_file(gis_file_road, encoding='euc-kr')

# Speed-up by Spatial-Indexing
gis_df_road_sindex = gis_df_road.geometry.sindex

def get_address(latitude, longitude):
    # kr2000 좌표 사용이 필요한 경우
    # wgs84 = pyproj.CRS("EPSG:4326")  # WGS84 좌표계
    # gps_kr2000 = {}
    # kr2000 = pyproj.CRS("EPSG:5186")  # EPSG:5186 좌표계
    # transformer = pyproj.Transformer.from_crs(wgs84, kr2000, always_xy=True)
    # gps_kr2000['lat'], gps_kr2000['lon'] = transformer.transform(gps_wgs84['lon'], gps_wgs84['lat'])
    # print(gps_kr2000['lat'])
    # print(gps_kr2000['lon'])
    # point_kr2000 = gpd.GeoSeries(gpd.points_from_xy([gps_kr2000['lon']],[gps_kr2000['lat']]))

    try:
        point_wgs84 = gpd.GeoSeries(gpd.points_from_xy([longitude],[latitude]))
        eupmyeondong = gis_df_eupmyeondong[gis_df_eupmyeondong.geometry.contains(point_wgs84[0])]
        address = []
        do = eupmyeondong['FIRST_Do'].values[0]
        if do:
            address.append(do.encode("utf-8"))
        else:
            address.append(None)
        gu = eupmyeondong['FIRST_Gu'].values[0]
        if gu:
            address.append(gu.encode("utf-8"))
        else:
            address.append(None)
        dong = eupmyeondong['FIRST_Dong'].values[0]
        if dong:
            address.append(dong.encode("utf-8"))
        else:
            address.append(None)
        
        nearest_node = gis_df_road_sindex.nearest(point_wgs84[0], return_all=False)
        closest_road_name = gis_df_road.iloc[nearest_node[1,0]]['Road_name']
        if closest_road_name:
            address.append(closest_road_name.encode("utf-8"))
        else:
            address.append(None)
        return address
    except:
        return [None,None,None,None]

# gps_wgs84 = {}
# for spartial indexing
# gps_wgs84['lat'] = 37.4827461
# gps_wgs84['lon'] = 127.0528412
address = get_address(37.4827461,127.0528412)

# gis_file_eupmyeondong = '/notebook/hmryu/GIS/읍면동.shp' # 읍면동 
# gis_file_sigungu = '/notebook/hmryu/GIS/시군구.shp' #시군구
# gis_file_sido = '/notebook/hmryu/GIS/도광역시.shp' #시도
# gis_file_road = '/notebook/hmryu/GIS/LinkShape.shp' #도로이름 - 30분 소요

# start = dt.datetime.now()
# gis_df_eupmyeondong = gpd.read_file(gis_file_eupmyeondong, encoding='euc-kr')
# end = dt.datetime.now()
# print('gis_df_eupmyeondong laoded : %2.1f sec'%((end-start).total_seconds()))


# start = dt.datetime.now()
# gis_df_sigungu = gpd.read_file(gis_file_sigungu, encoding='euc-kr')
# end = dt.datetime.now()
# print('gis_df_sigungu laoded : %2.1f sec'%((end-start).total_seconds()))

# start = dt.datetime.now()
# gis_df_sido = gpd.read_file(gis_file_sido, encoding='euc-kr')
# end = dt.datetime.now()            
# print('gis_df_sido laoded : %2.1f sec'%((end-start).total_seconds()))
      
# start = dt.datetime.now()      
# gis_df_road = gpd.read_file(gis_file_road, encoding='euc-kr')
# end = dt.datetime.now()  
# print('gis_df_road laoded: %2.1f min'%((end-start).total_seconds()/60))

# data = pd.read_csv('/notebook/hmryu/GIS/tbl_mems_trip.csv')
# gps_wgs84_lat = list(data['latitude'].values)
# gps_wgs84_lon = list(data['longitude'].values)

# gps_kr2000_lat = []
# gps_kr2000_lon = []
# point_kr2000 = []
# point_wgs84 = []

# cnt = len(data)
# i = 0
# i_past = 0

# wgs84 = pyproj.CRS("EPSG:4326")  # WGS84 좌표계
# kr2000 = pyproj.CRS("EPSG:5186")  # EPSG:5186 좌표계
# transformer = pyproj.Transformer.from_crs(wgs84, kr2000, always_xy=True)
# gps_kr2000_lat, gps_kr2000_lon = transformer.transform(gps_wgs84_lon,gps_wgs84_lat)
    
# point_kr2000 = gpd.GeoSeries(gpd.points_from_xy(gps_kr2000_lon,gps_kr2000_lat))
# point_wgs84 = gpd.GeoSeries(gpd.points_from_xy(gps_wgs84_lon,gps_wgs84_lat))


# sido=[]
# sigungu = []
# eupmyeondong_1 = []
# eupmyeondong_2 = []

# cnt = len(point_wgs84)
# i = 0
# i_past = 0

# for point in point_wgs84 :
    
#     i = i + 1
#     if int(i/cnt*100) != i_past:
#         print("%d%%(%d/%d)" %(int(i/cnt*100),i,cnt), end='')
#     i_past = int(i/cnt*100)
    
#     if len(gis_df_sido[gis_df_sido.geometry.contains(point)]) > 0 :    
#         sido.append(gis_df_sido[gis_df_sido.geometry.contains(point)]['FIRST_Do'].values[0])
#     else :
#         sido.append('')        
        
#     if len(gis_df_sigungu[gis_df_sigungu.geometry.contains(point)]) > 0 :            
#         sigungu.append(gis_df_sigungu[gis_df_sigungu.geometry.contains(point)]['FIRST_Gu'].values[0])
#     else :
#         sigungu.append('')        
        
#     if len(gis_df_eupmyeondong[gis_df_eupmyeondong.geometry.contains(point)]) > 0 :
#         eupmyeondong_1.append(gis_df_eupmyeondong[gis_df_eupmyeondong.geometry.contains(point)]['FIRST_Gu'].values[0])
#         eupmyeondong_2.append(gis_df_eupmyeondong[gis_df_eupmyeondong.geometry.contains(point)]['FIRST_Dong'].values[0])
#     else:
#         eupmyeondong_1.append('')
#         eupmyeondong_2.append('')
#     print('.',end='')

#     data['sido'] = sido
#     data['sigungu'] = sigungu
#     data['eupmyeondong'] = eupmyeondong_2

    
#     import math

# closest_road_name = []

# cnt = len(point_wgs84)
# i = 0
# i_past = 0

# for point in point_wgs84 :

#     i = i + 1
#     if int(i/cnt*100) != i_past:
#         print("%d%%(%d/%d)" %(int(i/cnt*100),i,cnt), end='')
#     i_past = int(i/cnt*100)    
    
#     gis_df_road['distance'] = gis_df_road.distance(point)

#     if math.isnan(gis_df_road['distance'].idxmin()) != True :
#         closest_road = gis_df_road.loc[gis_df_road['distance'].idxmin()]
#         closest_road_name.append(closest_road['Road_name']) 
#     else : 
#         closest_road_name.append('') 
        
#     print('.',end='')


# math.isnan(gis_df_road['distance'].idxmin())
# gis_df_road.loc[gis_df_road['distance'].idxmin()]
# closest_road_name
# point_wgs84
# gis_df_sido[gis_df_sido.geometry.contains(point_wgs84)]['FIRST_Do'].values[0]

# point_kr2000
# data.to_csv('data.csv')