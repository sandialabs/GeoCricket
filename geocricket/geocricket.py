"""
Functions that aid in querying REST servers and
formatting resulting GIS information typically
used in research.

Further details in README.md

"""
import os
import pathlib
import restapi
import requests
import shapely

import geopandas as gpd
from pathlib import Path


# Rest API link definitions:
CENSUS_URL = 'https://tigerweb.geo.census.gov/arcgis/rest/services/'
HIFLD_URL = 'https://services1.arcgis.com/Hp6G80Pky0om7QvQ/ArcGIS/rest/services/'

# For restapi to not use arcpy things
os.environ['RESTAPI_USE_ARCPY'] = 'FALSE'

def check_connection():
    """
    Check python connection to sample server
    """
    try:
        restapi.ArcServer(CENSUS_URL)
        return True
    except:
        return False


def ensure_crs(gdf, epsg=4326):
    converted_gdf = gdf.to_crs(epsg=epsg)
    return converted_gdf


def ensure_gdf(file_path):
    if isinstance(file_path, gpd.GeoDataFrame):
        return file_path.copy()
    else:
        return gpd.read_file(file_path)


def get_single_geometry(gdf, geo_index):
    return gdf.geometry[geo_index]


def get_dissolved_geometry(gdf):
    dissolved_gdf = gdf.dissolve()
    return dissolved_gdf.geometry[0]


def convert_geometry_bound(
        file_path,
        epsg=4326,
        poly_feat_ndx=None,
        ):
    """
    Read geospatial polygon file path and return shapely object
    for feature selection by location.

    Will disolve multiple polygons into one if poly_feat_ndx is not
    defined.

    an optional epsg can be selected for resulting geometry, else
    default is EPSG:4326

    returns geomtery compatible with restapi select_by_location function
    """

    gdf = ensure_gdf(file_path)
    gdf_at_crs = ensure_crs(gdf, epsg)

    if poly_feat_ndx is None:
        gdf_geo = get_dissolved_geometry(gdf_at_crs)
    else:
        gdf_geo = get_single_geometry(gdf_at_crs, poly_feat_ndx)

    return restapi.Geometry(shapely.geometry.mapping(gdf_geo))


def get_census_geo_layer_dict():
    # collect 500k of each
    return {
        0: {
            'name': 'Block_Groups',
            'sub_service': '/Tracts*',
            'layer': 4},
        1: {
            'name': 'Tracts',
            'sub_service': '/Tracts*',
            'layer': 4},  # this had changed remotely
        2: {
            'name': 'Counties',
            'sub_service': '/State*',
            'layer': 11},
        3: {
            'name': 'Tribal_Tracts',
            'sub_service': '/Tribal*',
            'layer': 3},
        4: {
            'name': 'Tribal_Block_Groups',
            'sub_service': '/Tribal*',
            'layer': 4}
        }

def export_census_geometry(
        boundary_geo,
        out_directory=None,
        out_name='Census_',
        crs=3857,
        service='*ACS2022',
        census_level=1,
        ):
    """
    Query TigerWEB and return desired census level data that overlaps
    boundary geometry

    Defaults:
    Use ACS2022 data to return census tracts.

    Other census levels:
    0: Block Groups
    1: Tracts
    2: County
    3: Tribal Tracts
    4: Tribal Block Groups

    return of output file location
    # TODO handle block geometry using last 10 year census...
    https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/Tracts_Blocks/MapServer
    """
    layer_dict = get_census_geo_layer_dict()

    sub_service = layer_dict[census_level]['sub_service']

    arc_gis_server = restapi.ArcServer(CENSUS_URL)
    service_connection = arc_gis_server.getService(service+sub_service)
    layer = service_connection.layer(layer_dict[census_level]['layer'])
    query_result = layer.select_by_location(
        boundary_geo,
        inSR=crs,
        outSR=crs)

    file_out_name = out_name + layer_dict[census_level]['name']

    # handle no given output directory
    if out_directory is None:
        out_directory = os.getcwd()
    else:
        pathlib.Path.mkdir(out_directory, parents=True, exist_ok=True)

    final_out_path = os.path.join(out_directory, f'{file_out_name}.shp')

    restapi.exportFeatureSet(query_result, final_out_path)

    return final_out_path


def export_census_transportation(
        boundary_geo,
        out_directory=None,
        out_name='Census_',
        crs=3857,
        road_layer=0,
        ):
    """
    Query TigerWEB and return desired transportation data from the 2020 Census

    Road Layer Key:
    0: Primary Roads (Interstates)
    1: Secondary (Highways)
    2: Local
    3: Rail

    return of output file location

    """

    layers = [2, 6, 7, 9]  # corresponds to service connection layer
    layer_names = ['Primary_Roads',
                   'Secondary_Roads',
                   'Local_Roads',
                   'Railroads']

    arc_gis_server = restapi.ArcServer(CENSUS_URL)
    service_connection = arc_gis_server.getService('Census2020/Transportation')
    layer = service_connection.layer(layers[road_layer])

    query_result = layer.select_by_location(boundary_geo, inSR=crs, outSR=crs)

    file_out_name = out_name+layer_names[road_layer]

    # handle no given output directory
    if out_directory is None:
        out_directory = os.getcwd()

    final_out_path = os.path.join(out_directory, f'{file_out_name}.shp')

    restapi.exportFeatureSet(query_result, final_out_path)

    return (final_out_path, query_result.count)


def export_hifld_data(
        boundary_geo,
        service,
        layer,
        out_directory=None,
        out_name='HIFLD_data',
        crs_in=4326,
        crs_out=3857,
        ):
    """
    Query Homeland Infrastrucutre Foundataion-Level Data (HIFLD)
    and return desired data from service layer that overlaps boundary geometry

    Server typically requires multiple queries before responding correctly.
    Accounted for 5 attempts before returning None.

    # NOTE: Seems to work best when input crs is 4326,
    output default of 3857 for Census crs match

    Returns tuple of out file path and count
    will return (None, 0) if error or no results found
    """

    arc_gis_server = restapi.ArcServer(HIFLD_URL)

    attempt = 0
    attempt_limit = 5

    while attempt < attempt_limit:
        try:
            service_connection = arc_gis_server.getService(service)
            layer = service_connection.layer(layer)
            attempt = 100  # to break out of while
            query_result = layer.select_by_location(boundary_geo,
                                                    inSR=crs_in, outSR=crs_out)

            # Handle case of no results
            if query_result.count == 0:
                return (None, 0)

            # handle no given output directory
            if out_directory is None:
                out_directory = os.getcwd()
            out_path = os.path.join(out_directory, f'{out_name}.shp')

            restapi.exportFeatureSet(query_result, out_path)

            return (out_path, query_result.count)

        except:
            attempt += 1

    return (None, 'error')


def export_server_URL_data(
        boundary_geo,
        server_url,
        service,
        layer,
        out_directory=None,
        out_name='REST_data',
        crs_in=4326, crs_out=3857):
    """
    Query an ArcGIS server specified by server_url
    and return desired data from layer that overlaps boundary geometry

    Accounts for 5 server attempts before returning None.

    Returns tuple of out file path and count
    will retrun (None, None) if error or no results found

    """
    arc_gis_server = restapi.ArcServer(server_url)

    attempt = 0
    attempt_limit = 5

    while attempt < attempt_limit:
        try:
            service_connection = arc_gis_server.getService(service)
            layer = service_connection.layer(layer)
            attempt = 100  # to break out of while
            query_result = layer.select_by_location(boundary_geo,
                                                    inSR=crs_in, outSR=crs_out)

            # Handle case of no results
            if query_result.count == 0:
                return (None, 0)

            # handle no given output directory
            if out_directory is None:
                out_directory = os.getcwd()
            final_out_path = os.path.join(out_directory, f'{out_name}.shp')

            restapi.exportFeatureSet(query_result, final_out_path)

            return (final_out_path, query_result.count)

        except:
            attempt += 1

    return (None, 'error')

def ensure_path(file_path):
    if not isinstance(file_path, Path):
        return Path(file_path)

def shp_to_gpkg(
        file_path,
        out_path=None,
        remove_old=False,
        ):
    """
    Convert shape file to a geopackage and optionally delete shape files

    return of output file location
    """
    # get file name from path
    file_path = ensure_path(file_path)

    file_path_splits = os.path.split(file_path)
    file_directory = file_path_splits[0]
    file_name = file_path_splits[-1]
    file_name = file_name.split('.')
    file_name = file_name[0]

    shp_file_df = gpd.read_file(file_path)

    if out_path is None:
        # export in same directory
        gpkg_out_path = os.path.join(file_directory, f"{file_name}.gpkg")
    else:
        # export to new directory
        gpkg_out_path = os.path.join(out_path, f"{file_name}.gpkg")

    shp_file_df.to_file(gpkg_out_path, driver="GPKG")

    if remove_old:
        # read directory, collect files related to shape
        file_directory_list = os.listdir(file_directory)
        associated_endings = ['.shp', '.shx', '.dbf', '.sbn', '.sbx', '.fbn',
                              '.fbx', '.ain', '.aih', '.stx', '.ixs', '.msx',
                              '.prj', '.xml', '.cpg']

        removed_files = []

        for file_ending in associated_endings:
            file_to_delete = file_name + file_ending
            if file_to_delete in file_directory_list:
                removed_files.append(file_to_delete)  # keep track of deletions
                os.remove(os.path.join(file_path_splits[0], file_to_delete))

    return gpkg_out_path


def add_field_to_file(
        file_path,
        field_name,
        field_value,
        overwrite_old=True,
        ):
    """
    Load geopandas readable file at filepath,
    add a column named field_name consisting of field_value,
    and save file.
    Overwrite file if overwrite_old is set to True,
    else append an interger to end.

    Accounts for duplicate field names
    """
    # attempt to load file
    try:
        geo_df = gpd.read_file(file_path)
    except:
        print(f"Error reading: {file_path}")
        return None

    # check if column exists and rename if applicable
    field_n = 0
    field_name_og = field_name

    while field_name in geo_df.columns:
        field_n += 1
        field_name = f"{field_name_og}_{field_n}"

    # write column data
    geo_df[field_name] = field_value

    # discover input (and output) file type
    file_path_splits = os.path.split(file_path)
    file_name_full = file_path_splits[-1]
    file_type = file_name_full.split('.')[-1]
    file_name = file_name_full.replace(f'.{file_type}', '')

    # define unique file output path which can iterate
    path_out = file_path

    if not overwrite_old:
        # create new file name
        file_n = 0
        while os.path.exists(path_out):
            file_n += 1
            path_out = os.path.join(file_path_splits[0],
                                    file_name + f'_{file_n}.{file_type}')

    # handle geopackage output
    try:
        if file_type.lower() == 'gpkg':
            geo_df.to_file(path_out, driver='GPKG')
        else:
            geo_df.to_file(path_out)
    except:
        print(f"Error writing to: {path_out}")
        return None

    return path_out


def add_rencat_id(
        file_path,
        sector,
        overwrite_old=True,
        ):
    """
    Load geopandas readable file at filepath,
    add a column named rencat_id with unique id,
    and save file.
    Overwrite file if overwrite_old is set to True,
    else append an interger to end.

    """
    is_gdf = False
    # check for geodataframe input
    if isinstance(file_path, gpd.GeoDataFrame):
        is_gdf = True

    if not is_gdf:
        # attempt to load file
        try:
            geo_df = gpd.read_file(file_path)
        except:
            print(f"Error reading: {file_path}")
            return None
    else:
        geo_df = file_path.copy()

    geo_df['rencat_id'] = sector.lower().replace(' ', '_')
    geo_df['rencat_id'] += '_' + geo_df.index.astype(str)

    if is_gdf:
        return geo_df

    # define unique file output path which can iterate
    path_out = file_path
    file_path_splits = os.path.split(file_path)
    file_name_full = file_path_splits[-1]
    file_type = file_name_full.split('.')[-1]
    file_name = file_name_full.replace(f'.{file_type}', '')

    if not overwrite_old:
        # create new file name
        file_n = 0
        while os.path.exists(path_out):
            file_n += 1
            path_out = os.path.join(
                file_path_splits[0],
                file_name + f'_{file_n}.{file_type}')

    # handle geopackage output
    try:
        if file_type.lower() == 'gpkg':
            geo_df.to_file(path_out, driver='GPKG')
        else:
            geo_df.to_file(path_out)
    except:
        print(f"Error writing to: {path_out}")
        return None

    return path_out
