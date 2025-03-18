"""
File to collect restful infromation for easier update.

It is expected (and already observed), that remote servers will change
how they offer data and these definitions may require continous
updates and attention for full functionality.
"""


def hifld_dict():
    """
    Return dictionary with HIFLD data definitions.

    The dictionary key is realtead to the output file name.
    Each key is a dictionary with:
    service:  name of data on the server
    layer:  corresponds to data layer on server
    outCRS: defined CRS for output - usually 3857, though sometimes 4326
    color: optional, not utilized
    idField: optional, not fully utilized.
    """

    return {
        'HIFLD_Transmission': {
            'service': 'Transmission_Lines',
            'layer': 0,
            'idField': 'ID',
            'color': None,
            'outCRS': 3857},
        'HIFLD_Cellular_Towers': {
            'service': 'Cellular_Towers_New',  # updated 20240727
            'layer': 0,  # updated 20250311
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_Banks_FDIC': {
            'service': 'FDIC_InsuredBanks',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_Hospitals': {
            'service': 'Hospitals_gdb',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},  # updated 20240919
        'HIFLD_Public_Schools': {
            'service': 'Public_Schools',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 4326},  # updated from 3857 20240427
        'HIFLD_Colleges_and_Universities_Campuses': {
            'service': 'Colleges_and_Universities_Campuses',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Local_Emergency_Operations_Centers_EOC': {
            'service': 'Local_Emergency_Operations_Centers_EOC',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Child_Care_Centers': {
            'service': 'ChildCareCenter1',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Veterans_Health_Administration_Medical_Facilities': {
            'service': 'Veterans_Health_Administration_Medical_Facilities',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Mobile_Home_Parks': {
            'service': 'Mobile_Home_Parks',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Local_Law_Enforcement_Locations': {
            'service': 'Local_Law_Enforcement_Locations',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Private_Schools': {
            'service': 'Private_Schools',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_Power_Plants': {
            'service': 'Plants_gdb',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Nursing_Homes': {
            'service': 'NursingHomes',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_Microwave_Service_Towers': {
            'service': 'Microwave_Service_Towers_New',
            'layer': 0, # updated 20250311
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_BRS_EBS': {
            'service': 'brs_ebs',
            'layer': 0, # updated 20250311
            'idField': None,
            'color': None,
            'outCRS': 4326},
        'HIFLD_Federal_Organizations': {
            'service': 'organizationsfederal',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
    }


"""
No longer provided by HIFLD to public:
        'HIFLD_State_Capitol_Buildings ': {
            'service': 'StateCapitolBuildings',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Urgent_Care_Facilities': {
            'service': 'Urgent_Care_Facilities',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Major_State_Government_Buildings': {
            'service': 'Major_State_Government_Buildings',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Pharmacies': {
            'service': 'Pharmacies',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Major_Sport_Venues': {
            'service': 'MajorSportVenues',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_FedEx_Facilities': {
            'service': 'FedEx_Facilities',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Places_of_Worship': {
            'service': 'AllPlacesOfWorship',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Public_Health_Departments': {
            'service': 'Public_Health_Departments',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Runways': {
            'service': 'Runways',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_EMS': {
            'service': 'Emergency_Medical_Service_(EMS)_Stations_gdb',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Solid_Waste_Landfill_Facilities': {
            'service': 'Solid_Waste_Landfill_Facilities',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Fire_Stations': {
            'service': 'Fire_Station',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Substations': {  # removed from general HIFLD dataset
            'service': 'Electric_Substations_1',
            'layer': 0,
            'idField': 'NAME',
            'color': '#ff0000ff',
            'outCRS': 3857},  # Likely gone forever 20230301
        'HIFLD_TV_Digital_Station_Transmitters': {
            'service': 'TV_Digital_Station_Transmitters',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_TV_Analog_Station_Transmitters': {
            'service': 'TV_Analog_Station_Transmitters',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_National_Transit_Map_Routes': {
            'service': 'National_Transit_Map_Routes',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_National_Transit_Map_Stops': {
            'service': 'National_Transit_Map_Stops',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_FM_Transmission_Towers': {
            'service': 'FM_Transmission_Towers',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_Aviation_Facilities': {
            'service': 'Aviation_Facilities',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'HIFLD_AM_Transmission_Tower': {
            'service': 'AM_Transmission_Tower',
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},  
"""


def non_hifld_dict():
    """
    Data collected from servers that are not the HIFLD.
    """
    return {
        'SNAP_Accepting_Loctions': {
            'url': r"https://services1.arcgis.com/RLQu0rK7h4kbsBq5/ArcGIS/rest/services",
            'service': "snap_retailer_location_data",  # updated 20240208
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'Dialysis_Locations': {
            'url': r"https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services",
            'service': "Dialysis_Facilities_in_the_United_States",
            'layer': 0,
            'idField': None,
            'color': None,
            'outCRS': 3857},
    }


def usgs_dict():
    """
    Data collected from usgs server.
    """
    return {
        'USGS_Fire_stations_EMS_stations': {
            'url': r"https://carto.nationalmap.gov/arcgis/rest/services",
            'service': "structures",
            'layer': 16,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'USGS_Police_stations': {
            'url': r"https://carto.nationalmap.gov/arcgis/rest/services",
            'service': "structures",
            'layer': 18,
            'idField': None,
            'color': None,
            'outCRS': 3857},
        'USGS_Hospitals_Medical_Centers': {
            'url': r"https://carto.nationalmap.gov/arcgis/rest/services",
            'service': "structures",
            'layer': 14,
            'idField': None,
            'color': None,
            'outCRS': 3857},
    }
