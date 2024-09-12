"""
Code to handle collected data into csv format
"""

import os
import pathlib
import pandas as pd
import geopandas as gpd


def prepare_census_data_for_csv(census_fp):
    """
    read in a census generated gis file,
    export csv with latitude and longitude and default stat fields.
    """
    gis_data = gpd.read_file(census_fp)

    # if field name not found, use first column
    if 'rencat_id' not in gis_data.columns:
        gis_data['rencat_id'] = 'rencat_id' + gis_data.index.astype(str)

    # ensure correct lat long
    gis_data = gis_data.to_crs(4326)

    # collect input data type
    input_data_type = gis_data.geometry.type.unique()

    if len(input_data_type) > 1:
        if all(['Polygon' in x for x in input_data_type]):
            input_data_type = 'Polygon'
        else:
            return print('Multiple data types found')

    # account for various input types (multipoing, point, poly, ...)
    if input_data_type == 'MultiPoint':
        # multipoint data uses a representative point...
        location_points = gis_data.representative_point()

    elif input_data_type == 'Point':
        location_points = gis_data.geometry

    elif input_data_type == 'Polygon':
        # if not point, make into centroids...
        original_crs = gis_data.crs.to_epsg()
        # convert to meter crs
        converted_gdf = gis_data.to_crs(3857)
        # replace original geometry with centroids
        converted_gdf['geometry'] = converted_gdf.centroid
        # convert back to original crs
        gis_data = converted_gdf.to_crs(original_crs)
        # collect centroid lat long
        location_points = gis_data.geometry

    columns_to_keep = [
        'rencat_id',
        'longitude',
        'latitude',
        'total_population_B01001_001E',
        'median_household_income_B19013_001E',
        'GEOID',
        ]

    # add desired data to original object
    gis_data['longitude'] = location_points.x
    gis_data['latitude'] = location_points.y

    valid_columns = [x for x in columns_to_keep if x in gis_data.columns ]
    gis_data = gis_data[valid_columns]

    return gis_data


def export_census_geography_to_csv(
        census_fp,
        output_path=None,
        export_csv=True):
    """
    Use data in census_fp to create simplified csv
    """
    census_data = prepare_census_data_for_csv(census_fp)

    if not export_csv:
        return census_data

    if output_path is None:
        output_path = pathlib.Path(os.getcwd())

    pathlib.Path.mkdir(output_path, parents=True, exist_ok=True)

    census_data.to_csv(
        pathlib.Path(output_path) / 'census_geometry_and_stats.csv',
        index=False)

    return output_path


def prepare_facility_data_for_csv(facility_fp, sector_field='Sector'):
    """
    read in a facility gis file, add sector name,
    export csv with latitude and longitude.
    """
    gis_data = gpd.read_file(facility_fp)

    # standardize rencat id
    if 'rencat_id' not in gis_data.columns:
        gis_data['rencat_id'] = 'rencat_id' + gis_data.index.astype(str)

    # ensure correct lat long
    gis_data = gis_data.to_crs(4326)

    # collect input data type
    input_data_type = gis_data.geometry.type.unique()

    if len(input_data_type) > 1:
        return 'Multiple data types found'

    # account for various input types (multipoing, point, poly, ...)
    if input_data_type == 'MultiPoint':
        # multipoint data uses a representative point...
        location_points = gis_data.representative_point()

    elif input_data_type == 'Point':
        location_points = gis_data.geometry

    elif input_data_type == 'Polygon':
        # if not point, make into centroids...
        original_crs = gis_data.crs.to_epsg()
        # convert to meter crs
        converted_gdf = gis_data.to_crs(3857)
        # replace original geometry with centroids
        converted_gdf['geometry'] = converted_gdf.centroid
        # convert back to original crs
        gis_data = converted_gdf.to_crs(original_crs)
        # collect centroid lat long
        location_points = gis_data.geometry

    elif 'Line' in input_data_type:
        return 'Line data not handled.'
    else:
        return f"Data type '{input_data_type}' not handled."

    columns_to_keep = [
        'rencat_id',
        'longitude',
        'latitude',
        'sector']

    # add desired data to original object
    gis_data['longitude'] = location_points.x
    gis_data['latitude'] = location_points.y
    gis_data['sector'] = gis_data[sector_field]

    gis_data = gis_data[columns_to_keep]

    return gis_data


def export_facilities_to_csv(
        facility_fps,
        output_path=None,
        export_csv=True,
        ):
    """
    Collect and export facility data to csv
    """

    facility_data = []
    for facility_fp in facility_fps:
        if isinstance(facility_fp, float):
            # skips nan
            continue
        if facility_fp is None:
            continue

        csv_data = prepare_facility_data_for_csv(facility_fp)

        if isinstance(csv_data, pd.DataFrame):
            facility_data.append(csv_data)
        else:
            # handle non handled types
            print(f"Error on {facility_fp}' : {csv_data}")

    facility_df = pd.concat(facility_data)

    if not export_csv:
        return facility_df

    if output_path is None:
        output_path = pathlib.Path(os.getcwd())

    pathlib.Path.mkdir(output_path, parents=True, exist_ok=True)

    facility_df.to_csv(
        pathlib.Path(output_path) / 'facility_data.csv',
        index=False)

    return output_path
