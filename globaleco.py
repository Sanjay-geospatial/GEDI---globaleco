
import geopandas as gpd
import pandas as pd
import h5py 
import matplotlib.pyplot as plt
import contextily as ctx
import requests
import datetime as dt 
import pandas as pd
import geopandas as gpd
import contextily as ctx 
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.ops import orient

class gedi:
    def __init__(self,bound, s_year,s_month,s_day, e_year, e_month, e_day):
        '''
        Takes the required parameters to search for the GEDI L4A datasets

        Args:
            bound : xmin, ymin, xmax, ymax enclosed in  a tuple
            s_year (int) : Start year
            s_month (int) : Start month
            s_day (int) : Start day
            e_year (int) : End year
            e_month (int) : End month
            e_day (int) : End day
        
        '''
        self.bound = bound
        self.s_year = s_year
        self.s_month = s_month
        self.s_day = s_day
        self.e_year = e_year
        self.e_month = e_month
        self.e_day = e_day

    def get_links(self):
        '''
        Gets all the urls for GEDI L4A datset for the specified ROI and time

        Returns:
            Returns a dataframe containing the URLs and their size
        
        '''
        doi = '10.3334/ORNLDAAC/2056'
    
        cmrurl='https://cmr.earthdata.nasa.gov/search/' 

        doisearch = cmrurl + 'collections.json?doi=' + doi
        response = requests.get(doisearch)
        response.raise_for_status()
        concept_id = response.json()['feed']['entry'][0]['id']

        start_date = dt.datetime(self.s_year, self.s_month, self.s_day) # specify your own start date
        end_date = dt.datetime(self.e_year, self.e_month, self.e_day)

        dt_format = '%Y-%m-%dT%H:%M:%SZ'
        temporal_str = start_date.strftime(dt_format) + ',' + end_date.strftime(dt_format)

        bound_str = ','.join(map(str, self.bound))

        page_num = 1
        page_size = 2000 # CMR page size limit

        granule_arr = []

        while True:
            
    

            cmr_param = {
                "collection_concept_id": concept_id, 
                "page_size": page_size,
                "page_num": page_num,
                "temporal": temporal_str,
                "bounding_box[]": bound_str
                }
    
            granulesearch = cmrurl + 'granules.json'

            response = requests.get(granulesearch, params=cmr_param)
            response.raise_for_status()
            granules = response.json()['feed']['entry']
    
            if granules:
                for g in granules:
                        
                    granule_url = ''
            
                    granule_size = float(g['granule_size'])

                    for links in g['links']:
                        if 'title' in links and links['title'].startswith('Download') \
                        and links['title'].endswith('.h5'):
                            granule_url = links['href']
                    granule_arr.append([granule_url, granule_size])
               
                page_num += 1
            else:
                break
        l4adf = pd.DataFrame(granule_arr, columns=["granule_url", "granule_size"])
        return l4adf

    def download(self, df,column_name, out_path):
        '''
         Downloads all the GEDI L4A datasets to the specified path

         Args:
            df : A dataframe containing URLs
            column_name : Name of the column in the dataframe which contains URLs
            out_path : Path to download and store the GEDI data

        Returns:
            The GEDI data in the h5 format
        
        '''
        import earthaccess
        earthaccess.login()

        for i in df[column_name]:
            results = i
            downloaded_files = earthaccess.download(results,local_path=out_path,)
        print('Successfully downloaded the data')

class gedi_reader:
    def __init__(self, file_path):
    
        '''
        Reads the BEAM information from the GEDI data

        Args:
            file_path : Path of the downloaded GEDI L4A data
        
        '''
        self.file_path = file_path
        x = h5py.File(file_path, 'r')

        beams = [i for i in x.keys() if i.startswith('BEAM')]

        print(f'The file has {len(beams)} beams, namely {beams}')

    def get_gdf(self):
        '''
        Converts the H5 format of GEDI data to Geodataframe

        Returns:
            A Geodataframe
        
        '''
        import h5py
        import pandas as pd
        import geopandas as gpd
        x = h5py.File(self.file_path, 'r')

        inp_beam = input('Select a beam :')

        data = x[inp_beam]

        df = pd.DataFrame()

        cols = ['agbd',  'degrade_flag', 'delta_time', 'elev_lowestmode', 'l2_quality_flag', 
                 'l4_quality_flag', 'lat_lowestmode', 'lon_lowestmode', 
                 'sensitivity', 'shot_number', 'solar_elevation']
    
        for i in cols:
            df[i] = data[i][:]

        gdf = gpd.GeoDataFrame(data=df, geometry=gpd.points_from_xy(df['lon_lowestmode'], df['lat_lowestmode']), crs = 'EPSG:4326')

        return gdf

    def visualize(self):
        '''
        Visualizes the individual BEAMs of the provided GEDI Data

        Returns:
            Two maps which visualizes GEDI orbits with ESRI Satellite basemap and CartoDark basemap
            
        
        '''
        import folium
        import h5py
        import pandas as pd
        import geopandas as gpd
        import geoviews as gv
        import geoviews.feature as gf
        from geoviews import opts
        gv.extension('bokeh', 'matplotlib')
        
        x = h5py.File(self.file_path, 'r')

        inp_beam = input('Select a beam for visualization:')

        data = x[inp_beam]

        df = pd.DataFrame()

        cols = ['agbd','lat_lowestmode', 'lon_lowestmode']
    
        for i in cols:
            df[i] = data[i][:]

        gdf = gpd.GeoDataFrame(data=df, geometry=gpd.points_from_xy(df['lon_lowestmode'], df['lat_lowestmode']), crs = 'EPSG:4326')

        x = []
        y = []

        for index, row in gdf.iterrows():    
            x.append(row['geometry'].x)
            y.append(row['geometry'].y)

        gdf['x'] = x
        gdf['y'] = y

        gdf.drop(columns = ['lon_lowestmode', 'lat_lowestmode'], inplace = True)

        x = gv.Points(gdf, kdims=['x', 'y'])

        plot_dark = (gv.tile_sources.CartoDark * x).opts(opts.Points(global_extent=False, width=700, height=500, size=8, color='yellow', tools=['hover']))

        plot_esri = (gv.tile_sources.EsriImagery * x).opts(opts.Points(global_extent=False, width=700, height=500, size=8, color='yellow', tools=['hover']))

        
        return plot_dark, plot_esri
        
        
                    

        
