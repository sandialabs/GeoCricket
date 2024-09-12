"""
Functions to handle the creation of kml

TODO: optional highlight color?
TODO: multi part geometry...

LINTING
import pdb
"""

import os
import geopandas as gpd
import numpy as np
import shapely
import simplekml


def make_kml_pts(
            geo_df,
            element_color=simplekml.Color.yellowgreen,
            highlight_color=None,
            id_field=None,
            groupby_field=None,
            output_name=None,
            output_path=None,
            export_as_kmz=False):
    """
    Generically output kml from geopandas dataframe
    """

    # handle arbitrarty grouping of folders based on column unique value
    folder_list = [output_name]
    use_folders = False
    if groupby_field is not None:
        try:
            folder_list = list(geo_df[groupby_field].unique())
            folder_list.sort()  # for consistent
            use_folders = True
        except KeyError:
            print(f'Groupby Field {groupby_field} not found')

    # NOTE: uses google maps icons, assert internet connection
    default_icon = r"http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"

    norm_styles = {}
    for style_color, folder_name in zip(element_color, folder_list):
        # kml style for points
        norm_style = simplekml.Style()
        norm_style.labelstyle.scale = 0
        norm_style.iconstyle.color = style_color
        norm_style.iconstyle.scale = 1
        norm_style.iconstyle.icon.href = default_icon

        norm_styles[folder_name] = norm_style

    selected_style = simplekml.Style()
    selected_style.labelstyle.scale = 0
    selected_style.iconstyle.color = simplekml.Color.orange
    selected_style.iconstyle.scale = 2
    selected_style.iconstyle.icon.href = default_icon

    # Being Making KML
    kml = simplekml.Kml(open=1)

    # Document top level folder
    doc = kml.newdocument(name=output_name)
    if use_folders:
        doc = doc.newfolder(name=groupby_field)
    else:
        doc = doc.newfolder(name=output_name)

    folders = {folder_name: doc.newfolder(name=folder_name)
               for folder_name in folder_list}

    # write each feature, row by row... (that's how kml do)
    for index, row in geo_df.iterrows():

        if id_field is None:
            kml_id = index
        else:
            kml_id = row[id_field]

        if use_folders:
            folder = row[groupby_field]
        else:
            folder = output_name

        kml_point = folders[folder].newpoint(
            name=f'{kml_id}', coords=row['geometry'].coords)

        kml_point.stylemap.normalstyle = norm_styles[folder]
        kml_point.stylemap.highlightstyle = selected_style

        description_table = """<table>"""

        for attr, value in zip(row.index, row.values):
            if attr == 'geometry':
                continue
            # build string...
            description_table += f"""
            <tr style='background-color:#9DBBE0'> <th>{attr}</th> </tr>
            <tr style='background-color:#ffffff'> <td>{value}</td>
            """
        description_table += """</table>"""

        kml_point.description = description_table

    if export_as_kmz:
        res_file = os.path.join(output_path, f"{output_name}.kmz")
        kml.savekmz(res_file)
    else:
        res_file = os.path.join(output_path, f"{output_name}.kml")
        kml.save(res_file)

    return res_file


def make_kml_lines(
            geo_df,
            element_color=simplekml.Color.yellowgreen,
            highlight_color=None,
            id_field=None,
            groupby_field=None,
            output_name=None,
            output_path=None,
            export_as_kmz=False):
    """
    Generically output kml from geopandas dataframe
    """

    # handle arbitrarty grouping of folders based on column unique value
    folder_list = [output_name]
    use_folders = False
    if groupby_field is not None:
        try:
            folder_list = list(geo_df[groupby_field].unique())
            folder_list.sort()  # for consistent
            use_folders = True
        except KeyError:
            print(f'Groupby Field {groupby_field} not found')

    norm_styles = {}
    for style_color, folder_name in zip(element_color, folder_list):
        # kml style for lines
        norm_style = simplekml.Style()
        norm_style.linestyle.color = style_color
        norm_style.linestyle.width = 2

        norm_styles[folder_name] = norm_style

    sel_style = simplekml.Style()
    sel_style.linestyle.color = simplekml.Color.orange
    sel_style.linestyle.width = 4
    # Being Making KML
    kml = simplekml.Kml(open=1)

    # Document top level folder
    doc = kml.newdocument(name=output_name)
    if use_folders:
        doc = doc.newfolder(name=groupby_field)
    else:
        doc = doc.newfolder(name=output_name)

    folders = {folder_name: doc.newfolder(name=folder_name)
               for folder_name in folder_list}

    # write each feature, row by row... (that's how kml do)
    for index, row in geo_df.iterrows():

        if id_field is None:
            kml_id = index
        else:
            kml_id = row[id_field]

        if use_folders:
            folder = row[groupby_field]
        else:
            folder = output_name

        kml_line = folders[folder].newlinestring(
            name=f'{kml_id}', coords=row['geometry'].coords)
        kml_line.stylemap.normalstyle = norm_styles[folder]
        kml_line.stylemap.highlightstyle = sel_style

        description_table = """<table>"""

        for attr, value in zip(row.index, row.values):
            if attr == 'geometry':
                continue
            # build string...
            description_table += f"""
            <tr style='background-color:#9DBBE0'> <th>{attr}</th> </tr>
            <tr style='background-color:#ffffff'> <td>{value}</td>
            """
        description_table += """</table>"""

        kml_line.description = description_table

    if export_as_kmz:
        res_file = os.path.join(output_path, f"{output_name}.kmz")
        kml.savekmz(res_file)
    else:
        res_file = os.path.join(output_path, f"{output_name}.kml")
        kml.save(res_file)

    return res_file


def make_kml_polygons(
            geo_df,
            element_color=simplekml.Color.yellowgreen,
            highlight_color=None,
            id_field=None,
            groupby_field=None,
            output_name=None,
            output_path=None,
            export_as_kmz=False):
    """
    Generically output kml from geopandas dataframe
    """
    # Polygon alpha definitions
    alpha_non_selected = round(255 * 0.65)
    alpha_selected = round(255 * 0.8)

    # handle arbitrarty grouping of folders based on column unique value
    folder_list = [output_name]
    use_folders = False
    if groupby_field is not None:
        try:
            folder_list = list(geo_df[groupby_field].unique())
            folder_list.sort()  # for consistent
            use_folders = True
        except KeyError:
            print(f'Groupby Field {groupby_field} not found')

    norm_styles = {}
    for style_color, folder_name in zip(element_color, folder_list):
        # kml style for polygons
        norm_style = simplekml.Style()
        norm_style.linestyle.color = style_color
        norm_style.linestyle.width = 2
        norm_style.polystyle.color = simplekml.Color.changealphaint(
            alpha_non_selected, style_color)

        norm_styles[folder_name] = norm_style

    sel_style = simplekml.Style()
    sel_style.linestyle.color = simplekml.Color.orange
    sel_style.linestyle.width = 4
    sel_style.polystyle.color = simplekml.Color.changealphaint(
        alpha_selected, simplekml.Color.orange)

    # Being Making KML
    kml = simplekml.Kml(open=1)

    # Document top level folder
    doc = kml.newdocument(name=output_name)
    if use_folders:
        doc = doc.newfolder(name=groupby_field)
    else:
        doc = doc.newfolder(name=output_name)

    folders = {folder_name: doc.newfolder(name=folder_name)
               for folder_name in folder_list}

    # write each feature, row by row... (that's how kml do)
    for index, row in geo_df.iterrows():

        if id_field is None:
            kml_id = index
        else:
            kml_id = row[id_field]

        if use_folders:
            folder = row[groupby_field]
        else:
            folder = output_name

        kml_poly = folders[folder].newpolygon(name=f'{kml_id}')
        kml_poly.outerboundaryis = row['geometry'].exterior.coords
        kml_poly.stylemap.normalstyle = norm_styles[folder]
        kml_poly.stylemap.highlightstyle = sel_style

        description_table = """<table>"""

        for attr, value in zip(row.index, row.values):
            if attr == 'geometry':
                continue
            # build string...
            description_table += f"""
            <tr style='background-color:#9DBBE0'> <th>{attr}</th> </tr>
            <tr style='background-color:#ffffff'> <td>{value}</td>
            """
        description_table += """</table>"""

        kml_poly.description = description_table

    if export_as_kmz:
        res_file = os.path.join(output_path, f"{output_name}.kmz")
        kml.savekmz(res_file)
    else:
        res_file = os.path.join(output_path, f"{output_name}.kml")
        kml.save(res_file)

    return res_file


def convert_to_kml(
        input_file,
        id_field=None,
        content_fields=None,
        groupby_field=None,
        output_name=None,
        output_path=None,
        element_color=None,
        highlight_color=None,
        max_n_attributes=0,
        export_as_kmz=False,
        geometry_field='geometry',
                   ):
    """
    Convert geopandas readable input_file vector to kml or kmz.
    Assumes a single type of geometry per input_file.
    Returns the path of converted file.

    If output_name is not specified, result will have same name
    and be in same folder as input_file, or current running directory.

    max_n_attributes used to define how much data to include in kml
    description. Set 0 for all. Overwriten if contetn_fields are defined.

    element_color can be chosen for kml style - if None, random color
    will be selected.
    TODO: list of colors can be input for each unique value.

    grouby_field will be used to find unique values for that column, then
    placing

    KML style of hex is #AABBGGRR where AA is the alpha value
    use of simplekml constants like simplekml.Color.red may be useful.

    TODO: handle multilinestring

    """
    # Check for geodataframe input
    if isinstance(input_file, gpd.GeoDataFrame):
        if output_name is None:
            print('Failed. output_name required for GeoDataFrame input_file.')
            return

        geo_df = input_file.copy()
        # handle case of named index being id or content choice
        geo_df.reset_index(inplace=True)
    else:
        # attempt to read dataframe
        try:
            geo_df = gpd.read_file(input_file)
        except TypeError:
            # may require other error type.
            print(f"Error reading {input_file}")
            return

    # convert to google earth crs
    geo_df = geo_df.to_crs(4326)

    # handle multipolygon geometry
    if 'MultiPolygon' in geo_df['geometry'].geom_type.values:
        geo_df = geo_df.explode(index_parts=True).reset_index()

    # handle multi line strings
    if 'MultiLineString' in geo_df['geometry'].geom_type.values:
        geo_df = geo_df.explode(index_parts=True).reset_index()

    # determine type of data
    data_type = type(geo_df.loc[0]['geometry'])
    if data_type == shapely.geometry.polygon.Polygon:
        detected_geo_type = 3
    elif data_type == shapely.geometry.linestring.LineString:
        detected_geo_type = 2
    elif data_type == shapely.geometry.point.Point:
        detected_geo_type = 1
    else:
        print(f"Input type of '{data_type}' - not currently accounted for.")
        # TODO can these multi types be converted to single types in gpd?
        return None

    colors_to_choose = 1
    if groupby_field is not None:
        try:
            group_fields = list(geo_df[groupby_field].unique())
            colors_to_choose = len(group_fields)
        except KeyError:
            print(f'Groupby Field {groupby_field} not found')
            group_fields = None

    # handle creation of arbitrary number of colors
    if element_color is not None:
        element_colors = element_color
        if not isinstance(element_colors, list):
            element_colors = list(element_colors)
    else:
        element_colors = []

    while len(element_colors) != colors_to_choose:
        # select random color for items.
        if element_color is None:
            # dummy value to enter while loop for color selection
            element_color = '__blank'
            while (
                    ('__' in element_color) or
                    ('change' in element_color) or
                    ('hex' in element_color)):
                element_color = np.random.choice(dir(simplekml.Color))

            # eval(f"simplekml.Color.{element_color}")  # replaced below
            element_color = getattr(simplekml.Color, element_color)
            element_colors.append(element_color)
            if len(element_colors) < 50:
                # allow for 50 unique colors
                element_colors = list(set(element_colors))
            element_color = None
        else:
            element_colors.append(element_color)

    element_color = element_colors

    # check if id_field is in columns
    if id_field is not None:
        if id_field not in geo_df.columns:
            print(f'Warning: idField {id_field} not available')
            id_field = None

    # select output fields (if available)
    use_max_n_attributes = True
    if content_fields is not None:
        use_max_n_attributes = False

        n_desired_fields = len(content_fields)
        # check for fields / find intersection
        found_fields = [x for x in content_fields if x in geo_df.columns]
        # notify if differetn / missing
        n_found_fields = len(found_fields)
        if n_desired_fields != n_found_fields:
            print(f'Found {n_found_fields} of {n_desired_fields} Fields')
            print(f'Found: {found_fields}')

        # pre-pend idfield and  'down select'
        if id_field is not None:
            found_fields.insert(0, id_field)
            # avoid possible duplication

        found_fields.append(geometry_field)
        cols2keep = list(set(found_fields))

        geo_df = geo_df[cols2keep]

    # select columns to output based on max attributes
    if (max_n_attributes > 0) and use_max_n_attributes:
        total_cols = len(geo_df.columns)
        if max_n_attributes < total_cols:
            cols = geo_df.columns
            # replaced below
            # cols2keep = [x for x in cols[0:max_n_attributes]]
            cols2keep = list(cols[0:max_n_attributes])
            cols2keep.append(cols[-1])

            # pre-pend idfield.
            if id_field is not None:
                cols2keep.insert(0, id_field)
                # avoid possible duplication
                cols2keep = list(set(cols2keep))

            geo_df = geo_df[cols2keep]

    # Parse Output Name from input path
    if output_name is None:
        file_path = os.path.split(input_file)
        output_name = file_path[-1]
        output_name = output_name.split('.')[0]

    if output_path is None:
        output_path = os.getcwd()

    # make kml from geodataframe.
    if detected_geo_type == 1:
        result_path = make_kml_pts(
            geo_df,
            element_color=element_color,
            highlight_color=highlight_color,
            id_field=id_field,
            groupby_field=groupby_field,
            output_name=output_name,
            output_path=output_path,  # won't be none
            export_as_kmz=export_as_kmz,
            )
    elif detected_geo_type == 2:
        result_path = make_kml_lines(
            geo_df,
            element_color=element_color,
            highlight_color=highlight_color,
            id_field=id_field,
            groupby_field=groupby_field,
            output_name=output_name,
            output_path=output_path,  # won't be none
            export_as_kmz=export_as_kmz,
            )
    elif detected_geo_type == 3:
        result_path = make_kml_polygons(
            geo_df,
            element_color=element_color,
            highlight_color=highlight_color,
            id_field=id_field,
            groupby_field=groupby_field,
            output_name=output_name,
            output_path=output_path,  # won't be none
            export_as_kmz=export_as_kmz,
            )

    return result_path
