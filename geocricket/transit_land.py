"""
Functions to query, collect, and export transit land data.

This is typically public transportation route and stop information
(bus, train, etc.)

Transit land website: https://www.transit.land/
API documentation: https://www.transit.land/documentation
"""
import datetime  # to generate output names with timestamp
import os
import time  # to handle transit land max query
import requests

import pandas as pd
import geopandas as gpd
import numpy as np

from shapely.geometry import shape
from shapely.geometry import Point


def transit_land_radius_query(api_key, lat, long, radius=1000):
    """
    Query transit land routes and stops using supplied api key and
    lat and long.
    Radius is in meters with a possible range of 0-10k.
    """
    # create routes query
    geojson_query = f"https://transit.land/api/v2/rest/routes?api_key={api_key}&lat={lat}&lon={long}&radius={radius}&format=geojson"

    # get response
    geojson_response = requests.request("GET", geojson_query, timeout=20)

    # check response
    if geojson_response.status_code != 200:
        print(geojson_query)
        print('Response not 200')
        return None

    # response is okay - convert response to gpd
    res = geojson_response.json()

    return res


def get_routes_from_transit_land_res(res):
    """
    Accepts a transit land response and returns a geopandas dataframe
    with routes in epsg 4326
    """
    # collect route multistring column data via list comprehension
    route_onestop_id = [
        route['properties']['onestop_id'] for route in res['features']]
    route_name = [
        route['properties']['route_long_name'] for route in res['features']]
    route_type = [
        route['properties']['route_type'] for route in res['features']]
    route_n_stops = [
        len(route['properties']['route_stops']) for route in res['features']]
    agency_name = [
        route['properties']['agency']['agency_name']
        for route in res['features']]
    agency_onestop_id = [
        route['properties']['agency']['onestop_id']
        for route in res['features']]
    route_geometry = [shape(route['geometry']) for route in res['features']]

    # combine lists into dictionary
    route_dict = {
        'route_onestop_id': route_onestop_id,
        'route_name': route_name,
        'route_type': route_type,
        'route_n_stops': route_n_stops,
        'agency_name': agency_name,
        'agency_onestop_id': agency_onestop_id,
        'geometry': route_geometry
    }

    # convert dictionary to geodataframe
    route_df = gpd.GeoDataFrame(route_dict)

    route_df.set_crs(epsg="4326", inplace=True)

    return route_df


def get_stops_from_transit_land_res(res):
    """
    Accepts a transit land response and returns a geopandas dataframe
    with route stops in epsg 4326
    """
    # handle data from stops
    full_stop_route_onestop_id = []
    full_stop_route_name = []
    full_stop_route_type = []
    full_stop_agency = []
    full_stop_agency_onestop_id = []

    full_stop_id = []
    full_stop_names = []
    full_stop_geometry = []

    # Handle individual stops
    for route in res['features']:

        n_stops = len(route['properties']['route_stops'])
        # collect information common to each stop
        route_onestop_id = [route['properties']['onestop_id']] * n_stops
        route_name = [route['properties']['route_long_name']] * n_stops
        route_type = [route['properties']['route_type']] * n_stops

        stop_agency = [route['properties']['agency']['agency_name']] * n_stops
        stop_agency_onestop_id = [route['properties']['agency']['onestop_id']] * n_stops

        # list comprehend each stop in current route
        stops = route['properties']['route_stops']

        stop_geometry = [shape(stop['stop']['geometry']) for stop in stops]
        stop_names = [stop['stop']['stop_name'] for stop in stops]
        stop_id = [stop['stop']['id'] for stop in stops]

        # combine stops from route into one list
        full_stop_id.extend(stop_id)
        full_stop_names.extend(stop_names)
        full_stop_geometry.extend(stop_geometry)

        full_stop_route_onestop_id.extend(route_onestop_id)
        full_stop_route_name.extend(route_name)
        full_stop_route_type.extend(route_type)

        # unsure if this really makes sense...
        full_stop_agency.extend(stop_agency)
        full_stop_agency_onestop_id.extend(stop_agency_onestop_id)

    # collect stops into dictionary
    stop_dict = {
        'id': full_stop_id,
        'name': full_stop_names,
        'route_onestop_id': full_stop_route_onestop_id,
        'route_name': full_stop_route_name,
        'route_type': full_stop_route_type,
        'agency': full_stop_agency,
        'agency_onestop_id': full_stop_agency_onestop_id,
        'geometry': full_stop_geometry
    }

    # convert dictionary to geodatafram
    stop_df = gpd.GeoDataFrame(stop_dict)

    stop_df.set_crs(epsg="4326", inplace=True)

    return stop_df


def export_transit_land_point_radius_query(
        api_key,
        lat,
        long,
        radius=1000,
        out_name=None,
        out_dir=None):
    """
    Collect and export transit land routes and stops given an api_key
    and a lat and long coordinates

    Return list of exported geopackages.

    """

    res = transit_land_radius_query(api_key, lat, long, radius)

    if res is None:
        print('Error with API response')
        return None

    route_df = get_routes_from_transit_land_res(res)
    stop_df = get_stops_from_transit_land_res(res)

    # handle no name
    if out_name is None:
        # present as longitude_latitude_radius
        out_name = f"result_{long:6.6f}_{lat:6.6f}_{radius}"

    # handle dir export
    if out_dir is None:
        out_dir = os.getcwd()

    # create file paths for export
    route_fp_out = os.path.join(out_dir, f'{out_name}_routes.gpkg')
    stops_fp_out = os.path.join(out_dir, f'{out_name}_stops.gpkg')

    # export geopackages
    route_df.to_file(route_fp_out, driver="GPKG")
    stop_df.to_file(stops_fp_out, driver="GPKG")

    return [route_fp_out, stops_fp_out]


def export_transit_land_geometry_bound_query(
        api_key,
        boundary_fp,
        out_name=None,
        out_dir=None,
        ):
    """
    Export collected routes and stops found inside boundary defined by
    geopandas readable file located at the boundary_fp path location.

    Returns locations of exported full stops and routes geopackages

    NOTE: Includes a 1 second sleep between each api call to prevent
    over query (assumes free api license)
    """

    # read bounding geometry
    boundary_df = gpd.read_file(boundary_fp)
    # estimate utm crs - for meter math
    utm_crs = boundary_df.estimate_utm_crs()
    # convert boundary to utm
    utm_df = boundary_df.to_crs(utm_crs)
    # collect bounds
    all_bounds = utm_df.total_bounds

    # seperate bounds into human readalbe variables
    min_x = int(np.floor(all_bounds[0]))
    min_y = int(np.floor(all_bounds[1]))
    max_x = int(np.ceil(all_bounds[2]))
    max_y = int(np.ceil(all_bounds[3]))

    search_radius = 10000  # use 10km range

    # define interval of radius search
    # e.g. largest square to fit inside radius
    point_radius = int(np.floor(2 * search_radius / np.sqrt(2)))

    # create ranges
    x_range = list(range(min_x, max_x, point_radius))
    y_range = list(range(min_y, max_y, point_radius))

    # make lists of points for query dataframe
    n = 1
    pts = []
    ndx = []
    for x in x_range:
        for y in y_range:
            pts.append(Point([x, y]))
            ndx.append(str(n))
            n += 1

    # create utm dataframe from grid of search coordinates
    gdf = gpd.GeoDataFrame(ndx, geometry=pts, columns=['num'])
    gdf.set_crs(utm_crs, inplace=True)

    # convert search coordinates back to lat long for api
    gdf2 = gdf.to_crs(epsg="4326")

    # initialize dictionary for api query results
    res_dict = {}

    for index, row in gdf2.iterrows():
        # collect require information for query
        long = row.geometry.x
        lat = row.geometry.y

        res_dict[index] = {}
        res_dict[index]['lat'] = lat
        res_dict[index]['long'] = long

        res = transit_land_radius_query(
            api_key,
            lat,
            long,
            radius=search_radius)

        if res is None:
            res_dict[index]['routes'] = None
            res_dict[index]['stops'] = None
        else:
            res_dict[index]['routes'] = get_routes_from_transit_land_res(res)
            res_dict[index]['stops'] = get_stops_from_transit_land_res(res)

        time.sleep(1)  # to prevent over query of 'free' transit land api key

    # handle result dictionary
    stops_init = False
    routes_init = False

    for d in res_dict.values():
        if not d['stops'].empty:
            # stops in result
            if not stops_init:
                # df not created yet, init full stops df
                full_stops = d['stops']
                stops_init = True
            else:
                # stops df already created, simple concat
                full_stops = pd.concat([full_stops, d['stops']])

        if not d['routes'].empty:
            # routes in result
            if not routes_init:
                # routes df not created yet, init full routes df
                full_routes = d['routes']
                routes_init = True
            else:
                # routes df already created, simple concat
                full_routes = pd.concat([full_routes, d['routes']])

    # clean up full collections of routes and stops
    full_routes.drop_duplicates(inplace=True)
    full_routes.reset_index(drop=True, inplace=True)

    full_stops.drop_duplicates(inplace=True)
    full_stops.reset_index(drop=True, inplace=True)

    # handle no name
    if out_name is None:
        # add time string
        t_str = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        out_name = f"result_bounds_{t_str}"

    # handle dir export
    if out_dir is None:
        out_dir = os.getcwd()

    # create file paths for export
    route_fp_out = os.path.join(out_dir, f'{out_name}_routes.gpkg')
    stops_fp_out = os.path.join(out_dir, f'{out_name}_stops.gpkg')

    # export geopackages
    full_routes.to_file(route_fp_out, driver="GPKG")
    full_stops.to_file(stops_fp_out, driver="GPKG")

    return [route_fp_out, stops_fp_out]
