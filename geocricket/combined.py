"""
Codes to perform full collect of gis data.

Functions have nice docstrings...

"""
import pathlib
from pathlib import Path
import time
import geopandas as gpd
import pandas as pd
import geocricket as gc


def query_census(
        geometry_bound,
        output_paths,
        census_geometry_level=1,
        census_api_key=None,
    ):
    """
    Query census for geometry and optionally statistics.
    Return dataframe of collection results.

    Parameters
    ----------
    geometry_bound : restapi.Geometry
        Converted geometry valid for query.  Should be in crs 3857
    output_paths : dict
        dictionary of output locations for file types to export.
    census_geometry_level : int
        Define level of census geometry to be used. Valid ints range are
        0, 1, and 2, which correspond to block groups, tracts, and county
        level data, respctively. Defaults to 1
    census_api_key : str, optional
        api key used for census statistics query.  If not given, census
        statistics will not be collected. Defaults to None.

    Returns
    -------
    pandas.DataFrame
        A dataframe with query results and final output locations.
    """
    # initialize result dictionary
    ci_result_count = {}

    query_start = time.perf_counter()

    temp_out_path = gc.export_census_geometry(
        geometry_bound,
        out_directory=output_paths['shp'],
        census_level=census_geometry_level,
        )

    # stop query time
    query_end = time.perf_counter()
    ci_result_count['census_geometry'] = {}
    ci_result_count['census_geometry']['query_time'] = query_end - query_start

    # read collected census data
    census_df = gpd.read_file(temp_out_path)

    if census_api_key is not None:
        # get census statistics
        census_df = gc.get_census_stats(census_df, census_api_key)

    ci_result_count['census_geometry']['count'] = len(census_df)

    # add rencat id
    census_df = gc.add_rencat_id(census_df, sector='census_geometry')

    # export shp
    census_df.to_file(temp_out_path)
    ci_result_count['census_geometry']['shp'] = temp_out_path

    # export gpkg
    if 'gpkg' in output_paths:
        temp_out_path = Path(temp_out_path)
        single_gpkg_path = output_paths['gpkg'] / (str(temp_out_path.stem)+'.gpkg')
        census_df.to_file(single_gpkg_path, driver='GPKG')
        ci_result_count['census_geometry']['gpkg'] = single_gpkg_path

    # export kml
    if 'kml' in output_paths:
        try:
            kml = gc.convert_to_kml(
                temp_out_path,
                output_path=output_paths['kml'],
                id_field='GEOID')
            ci_result_count['census_geometry']['kml'] = kml
        except:
            print("KML export failed (multi-part?)")

    return ci_result_count


def query_hifld(
        geometry_bound,
        output_paths,
    ):
    """
    Query HIFLD for information related to infrstructure layers described
    in gis_collect.hifld_dict.
    Return dataframe of collection results.

    Parameters
    ----------
    geometry_bound : restapi.Geometry
        Converted geometry valid for query.  Should be in crs 4326
    output_paths : dict
        dictionary of output locations for file types to export.

    Returns
    -------
    pandas.DataFrame
        A dataframe with query results and final output locations.    
    """
    # collect standard HIFLD query set
    hifld_dict = gc.hifld_dict()

    ci_result_count = {}

    # Step through entries in HIFLD dictionary and collect data...
    for key, _ in hifld_dict.items():
        # init result dictionary
        ci_result_count[key] = {}

        # simplify function input.
        outCRS = hifld_dict[key]['outCRS']

        # start query time
        query_start = time.perf_counter()

        # collect data from server, export shape file
        temp_out_path = gc.export_hifld_data(
            geometry_bound,
            hifld_dict[key]['service'],
            hifld_dict[key]['layer'],
            out_directory=output_paths['shp'],
            out_name=key,
            crs_out=outCRS,
            )

        # stop query time
        query_end = time.perf_counter()
        ci_result_count[key]['query_time'] = query_end - query_start
        ci_result_count[key]['count'] = temp_out_path[1]

        # Handle case where there is no CI in bounds.
        if temp_out_path[0] is None:
            print(f'* No infrastructure located for "{key}"\n')
            continue

        # Add a sector field to collected data
        sector_name = key[6:]  # slice to remove HIFLD_

        # issue is during this write again...
        gc.add_field_to_file(
            Path(temp_out_path[0]),
            'Sector',
            sector_name,
            overwrite_old=True)

        # add rencat id
        temp_out_path = gc.add_rencat_id(temp_out_path[0], sector=sector_name)

        ci_result_count[key]['shp'] = temp_out_path

        # export gpkg
        if 'gpkg' in output_paths:
            gpkg = gc.shp_to_gpkg(
                temp_out_path,
                out_path=output_paths['gpkg'],
                remove_old=False)
            ci_result_count[key]['gpkg'] = Path(gpkg)

        # export kml
        if 'kml' in output_paths:
            # export kml
            try:
                kml = gc.convert_to_kml(
                    gpkg,
                    output_path=output_paths['kml'],
                    id_field=hifld_dict[key]['idField'],
                    element_color=hifld_dict[key]['color'],
                    )
                ci_result_count[key]['kml'] = Path(kml)
            except:
                print("* KML export failed (multi-part?)")
            print(f'Collected {key} resources...\n')

    return ci_result_count


def query_non_hifld(
        geometry_bound,
        output_paths,
        input_dict=gc.non_hifld_dict()
        ):
    """
    Query non-HIFLD sources for information related to infrstructure 
    described in gis_collect.non_hifld_dict.
    Return dataframe of collection results.

    Parameters
    ----------
    geometry_bound : restapi.Geometry
        Converted geometry valid for query.  Should be in crs 4326
    output_paths : dict
        dictionary of output locations for file types to export.

    Returns
    -------
    pandas.DataFrame
        A dataframe with query results and final output locations.
    """
    non_hifld_dict = input_dict
    ci_result_count = {}

    for key, _ in non_hifld_dict.items():
        # initialize result dictionary
        ci_result_count[key] = {}

        # simplify funtion inputs...
        outCRS = non_hifld_dict[key]['outCRS']
        url = non_hifld_dict[key]['url']

        # start query time
        query_start = time.perf_counter()

        # collect data from server, export shape file (default restapi)
        temp_out_path = gc.export_server_URL_data(
            geometry_bound,
            url,
            non_hifld_dict[key]['service'],
            non_hifld_dict[key]['layer'],
            out_directory=output_paths['shp'],
            out_name=key,
            crs_out=outCRS)

        # finish time query
        query_end = time.perf_counter()
        ci_result_count[key]['query_time'] = query_end - query_start
        ci_result_count[key]['count'] = temp_out_path[1]

        # Handle case where there is no CI in bounds.
        if temp_out_path[0] is None:
            print(f'No infrastructure located for "{key}"\n')
            continue

        # Add a sector field to collected data
        sector_name = key
        gc.add_field_to_file(
            temp_out_path[0],
            'Sector',
            sector_name,
            overwrite_old=True)

        temp_out_path = gc.add_rencat_id(temp_out_path[0], sector=sector_name)
        ci_result_count[key]['shp'] = temp_out_path

        # export gpkg
        if 'gpkg' in output_paths:
            gpkg = gc.shp_to_gpkg(
                temp_out_path,
                out_path=output_paths['gpkg'],
                remove_old=False)
            ci_result_count[key]['gpkg'] = Path(gpkg)

        # export kml
        if 'kml' in output_paths:
            # export kml
            try:
                kml = gc.convert_to_kml(
                    gpkg,
                    output_path=output_paths['kml'],
                    id_field=non_hifld_dict[key]['idField'],
                    element_color=non_hifld_dict[key]['color'],
                    )
                ci_result_count[key]['kml'] = Path(kml)
            except:
                print("* KML export failed (multi-part?)")
            print(f'Collected {key} resources...\n')

    return ci_result_count


def collect(
        query_geometry,
        output_dir,
        census_geometry_level=1,
        census_api_key=None,
        update_census_geo=True,
        output_kml=True,
        output_gpkg=True,
        output_csv=True
        ):
    """
    Perform full gis collect of given query_geometry. This includes:
    Census geomety
    Return dataframe of collection results.

    Parameters
    ----------
    query_geometry : path or geodataframe
        Path location, or dataframe that describes the area that gis
        data should be collected from.
    output_dir : path or str
        location for results to be saved.
    census_geometry_level : int
        Define level of census geometry to be used. Valid ints range are
        0, 1, and 2, which correspond to block groups, tracts, and county
        level data, respctively. Defaults to 1
    census_api_key : str, optional
        api key used for census statistics query.  If not given, census
        statistics will not be collected. Defaults to None.
    update_census_geo : bool
        If true, query bounds will be updated with a dissolved census
        geometry bound. Defaults to True.
    output_kml : bool
        If true, kml file is attempted to be crated in output_dir.
        Defaults to True
    output_gpkg : bool
        If true, gpkg files are created from initial shp files.
        Defaults to True
    output_csv : bool
        If true, output ReNCAT compatible csv files for geometry and
        infrastructure.

    Returns
    -------
    pandas.DataFrame
        A dataframe with query results and final output locations.

    """

    # handle output folders
    if not isinstance(output_dir, pathlib.Path):
        output_dir = pathlib.Path(output_dir)

    output_paths = {
        'base': output_dir,
        'shp': output_dir / 'shp'
    }

    if output_gpkg:
        output_paths['gpkg'] = output_dir / 'gpkg'
    if output_kml:
        output_paths['kml'] = output_dir / 'kml'
    if output_csv:
        output_paths['csv'] = output_dir / 'csv'

    for folder in output_paths.values():
        folder.mkdir(parents=True, exist_ok=True)

    # convert original input geometry to valid search geometry
    b_geo_3857 = gc.convert_geometry_bound(query_geometry, epsg=3857)
    b_geo_4326 = gc.convert_geometry_bound(query_geometry, epsg=4326)

    # query census
    census_result = query_census(
        b_geo_3857,
        output_paths,
        census_geometry_level=census_geometry_level,
        census_api_key=census_api_key,
    )

    # update query bounds.
    if update_census_geo:
        new_geometry_fp = census_result['census_geometry']['shp']
        b_geo_3857 = gc.convert_geometry_bound(new_geometry_fp, epsg=3857)
        b_geo_4326 = gc.convert_geometry_bound(new_geometry_fp, epsg=4326)

    # query HIFLD
    hifld_result = query_hifld(
        b_geo_4326,
        output_paths
    )

    # query usgs - note different geo...
    usgs_result = query_non_hifld(
        b_geo_3857,
        output_paths,
        input_dict=gc.usgs_dict()
    )

    # query non-HIFLD
    non_hifld_result = query_non_hifld(
        b_geo_4326,
        output_paths
    )

    # combine results
    census_result.update(hifld_result)
    census_result.update(usgs_result)
    census_result.update(non_hifld_result)

    ci_result_df = pd.DataFrame.from_dict(census_result, orient='index')
    ci_result_df.index.rename('query', inplace=True)

    ci_result_df.to_csv(output_paths['base'] / 'query_result.csv')

    # handle csv ouput
    if output_csv:
        census_fp = ci_result_df.iloc[0]['shp']
        gc.export_census_geography_to_csv(
            census_fp,
            output_path=output_paths['csv'])

        facility_fps = ci_result_df.iloc[1:]['shp']
        gc.export_facilities_to_csv(
            facility_fps,
            output_path=output_paths['csv'])

    return ci_result_df
