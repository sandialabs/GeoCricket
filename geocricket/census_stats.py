"""
Functions to handle census data query
"""

import geopandas as gpd
import pandas as pd
import requests


def json_to_dataframe(response):
    """
    Convert census request response to dataframe
    """
    return pd.DataFrame(response.json()[1:], columns=response.json()[0])


def generate_geoid(res_df):
    """
    create geoid based on census response.
    return no change dataframe if geometry not a county, tract, or block group
    """
    if 'block group' in res_df.columns:
        res_df['GEOID'] = ''
        cols_to_keep = res_df.columns.to_list()
        cols_to_keep.remove('state')
        cols_to_keep.remove('county')
        cols_to_keep.remove('tract')
        cols_to_keep.remove('block group')

        for index, row in res_df.iterrows():
            res_df.at[index, 'GEOID'] = row['state'] + row['county'] + row['tract'] + row['block group']
        return res_df[cols_to_keep]

    if 'tract' in res_df.columns:
        res_df['GEOID'] = ''
        cols_to_keep = res_df.columns.to_list()
        cols_to_keep.remove('state')
        cols_to_keep.remove('county')
        cols_to_keep.remove('tract')

        for index, row in res_df.iterrows():
            res_df.at[index, 'GEOID'] = row['state'] + row['county'] + row['tract']
        return res_df[cols_to_keep]

    if 'county' in res_df.columns:
        res_df['GEOID'] = ''
        cols_to_keep = res_df.columns.to_list()
        cols_to_keep.remove('state')
        cols_to_keep.remove('county')

        for index, row in res_df.iterrows():
            res_df.at[index, 'GEOID'] = row['state'] + row['county']
        return res_df[cols_to_keep]
    else:
        return res_df


def get_census_stats(
        census_geo,
        api_key,
        census_year='2022',
        ):
    """
    census_geo filepath or geodataframe
    api_key for census
    census_year = optional, year of ACS stats to query

    Examples: https://api.census.gov/data/2022/acs/acs5/examples.html

    """

    # to allow for additional data collections
    census_vars = {
        'total_population': 'B01001_001E',
        'median_household_income': 'B19013_001E'
    }
    var_str = ','.join(census_vars.values())

    census_year = '2022'  # year of data to query

    if isinstance(census_geo, gpd.GeoDataFrame):
        gdf = census_geo.copy()
    else:
        gdf = gpd.read_file(census_geo)

    # collect states and counties to query
    if 'STATE' in gdf.columns:
        state_col = 'STATE'
    else:
        state_col = gdf.columns[gdf.columns.str.lower().str.contains('state')]
        state_col = state_col.unique().tolist()[0]
    states = gdf[state_col].unique().tolist()

    if 'COUNTY' in gdf.columns:
        county_col = 'COUNTY'
    else:
        county_col = gdf.columns[gdf.columns.str.lower().str.contains('county')]
        county_col = county_col.unique().tolist()[0]
    counties = gdf[county_col].unique().tolist()
    counties_str = ','.join(counties)

    # identify geoid
    if 'GEOID' in gdf.columns:
        geoid_col = 'GEOID'
    else:
        geoid_col_mask = gdf.columns.str.lower().str.contains('geoid')
        geoid_col = gdf.columns[geoid_col_mask]

    # find length of geoid from nested data...
    geo_id_len = gdf[geoid_col].str.len().max()

    # based on https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html
    # 11 == census tract (handled)
    # 12 >= block group (handled)
    # 5 = county (handled)
    # TODO: block data? may only have population every 10 years...

    # 10 == county subdivision
    # 7 = place
    # 2 = state

    responses = []

    base_query = fr"https://api.census.gov/data/{census_year}/acs/acs5?get=NAME,{var_str}"

    for state in states:

        # form query based on input geometry level
        if geo_id_len == 11:
            # print('Census Tracts')
            geo_query = fr"&for=tract:*&in=state:{state}%20county:{counties_str}&key={api_key}"

        elif geo_id_len >= 12:
            # print('Census Block groups')
            geo_query = fr"&for=block%20group:*&in=state:{state}&in=county:{counties_str}&in=tract:*&key={api_key}"

        elif geo_id_len == 5:
            # print('Census County')
            geo_query = fr"&for=county:{counties_str}&in=state:{state}&key={api_key}"

        else:
            print('Geometry unknown')

        query = base_query + geo_query
        response = requests.request('GET', query, timeout=10)

        # invalid response
        if len(response.content) == 0:
            continue

        df = json_to_dataframe(response)

        responses.append(df)

    if len(response.content) == 0:
        # no valid resonse
        print('No valid response from census query')
        return gdf

    # combine results from multiple states
    res_df = pd.concat(responses)
    res_df.reset_index(inplace=True, drop=True)

    for var in census_vars.values():
        res_df[var] = pd.to_numeric(res_df[var])  # converte desired columsn to numeric
        res_df[var] = res_df[var].mask(res_df[var] < 0)  # negatives replaced by nan

    # create geoid for results
    res_df = generate_geoid(res_df)

    # merge with gdf
    merged_results = gdf.merge(
        res_df,
        left_on='GEOID',
        right_on='GEOID',
        how='inner',
        suffixes=('_OG', '_QUERY')
    )

    # rename value columns to include ending
    rename_dict = {}
    for name, code in census_vars.items():
        rename_dict[code] = name + '_' + code

    return merged_results.rename(columns=rename_dict)
