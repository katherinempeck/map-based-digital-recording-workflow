import os
from datetime import datetime
import sqlite3

import pandas as pd
import fiona
import geopandas as gpd

def get_most_recent_folder(survey_data_folder:str) -> str:
    """Gets the newest survey data folder based on the date code in the folder name

    Parameters
    ----------
    survey_data_folder : str
        Folder path to folder containing survey data subfolders, labelled by date 

    Returns
    -------
    str
        Folder path of most recent folder (i.e, should contain the most recent survey data)
    """

    data_dates = []

    for folder in os.listdir(survey_data_folder):
        m = int(folder[:2])
        d = int(folder[2:4])
        y = int(folder[4:])
        date = datetime(y, m, d)
        data_dates.append(date)

    most_recent = max(data_dates)
    if len(str(most_recent.month)) < 2:
        month = f'0{str(most_recent.month)}'
    else:
        month = str(most_recent.month)

    if len(str(most_recent.day)) < 2:
        day = f'0{str(most_recent.day)}'
    else:
        day = str(most_recent.day)

    final_subfolder = f'{survey_data_folder}/{month}{day}{str(most_recent.year)}'
    return final_subfolder

def organize_data_to_site_folders(survey_data_folder:str, extracted_data_folder:str, output_crs:str):
    if not os.path.isdir(extracted_data_folder):
        os.mkdir(extracted_data_folder)
        print(f'Created {extracted_data_folder} for extracted data')
    data_list = []
    for f in os.listdir(survey_data_folder):
        if f.endswith('.gpkg'):
            data_list.append(f'{survey_data_folder}/{f}')
    gpkg_list = []
    for d in data_list:
        failed_to_open = []
        for layername in fiona.listlayers(d):
            try:
                geopkg = gpd.read_file(d, layer = layername)
            except Exception as e:
                #Certain layers fail to open with geopandas, this makes sure that data is still captured (albeit without spatial reference)
                print(f'{layername} in {d} failed to open as a GDF (Error: {e}) and was opened as a DF. Geometry will not be preserved.')
                sqliteConnection = sqlite3.connect(d)
                geopkg = pd.read_sql(f'SELECT * from [{layername}]', sqliteConnection)
                #TODO: Print this list to the app frame in a readable/easy to comprehend way
                failed_to_open.append([layername, d])
                sqliteConnection.close()
            #This procedure will find all layers included in the original Avenza schema
            #Sometimes, though, users don't add data to these layers
            #We want to skip any of these empty layers as they won't contain any data that we need
            if geopkg.empty:
                pass
            else:
                #Preserve original layer name and filename as a string in this "original_layer_name" column
                geopkg['original_layer_name'] = f'{layername}___{d.split("/")[-1]}'
                gpkg_list.append(geopkg)
    #Now we have a list of all geopackages, opened with GeoPandas as GeoDataFrames
    #Now we want to reorganize all these spatial data by their original site or isolate (photos will be organized in a separate step)
    #First step in that process, create a folder for each unique site name in the data:
    unique_site_names = []
    for g in gpkg_list:
        c = g[g.columns[g.columns.str.contains("Site ID")]]
        if c.empty:
            pass
        else:
            unique_site_names.append(c)
    #For each of those dataframes, get a list of all the values and append each individual value to a new list
    sname = []
    for i in unique_site_names:
        cname = list(i.columns)[0]
        sitenames = list(i[cname])
        for s in sitenames:
            sname.append(s)
        
    #There was a standardization procedure to catch instances where there was non-standard use of capitals etc.
    #However, it didn't fully work and would require manual editing anyway
    #I would recommend a manual check after this stage anyway
    #Get unique values from the list of values created above
    sname = set(sname)

    #Then, make a folder for each site
    for f in sname:
        if os.path.isdir(f'{extracted_data_folder}/{f}'):
            pass
        else:
            os.mkdir(f'{extracted_data_folder}/{f}')
    #This site folder is what everything will be extracted and reorganized into
    #Make an other folder for photos (this will be used later in the procedure)
    os.mkdir(f'{extracted_data_folder}/Other_photos')

    #Now we need to go through the data and find all the shapes associated with each unique site id
    #Export them to the folders with a name that references the original layer name
    query_info = []
    for g in gpkg_list:
        og_name = list(g['original_layer_name'].values)[0]
        og_gpkg = og_name.split(".")[0]
        og_gpkg = og_gpkg.split("___")[1]
        og_layer = og_name.split(".")[0]
        og_layer = og_layer.split("___")[0]
        try:
            info = [og_gpkg, og_layer, str(list(g['avenza_layer_id'].values)[0])]
        except Exception:
            pass
        query_info.append(info)
        #Find all the columns in the dataframe with the string "Site ID"
        c = g[g.columns[g.columns.str.contains("Site ID")]]
        if c.empty:
            pass
        else:
            cname = list(c.columns)[0]
            for s in sname:
                r = g[g[cname].isin([s])]
                if r.empty == False:
                    og_name = list(r['original_layer_name'].values)[0]
                    if isinstance(r, gpd.GeoDataFrame):
                        r = r.to_crs(f'EPSG:{output_crs}')
                        r.to_file(f'{extracted_data_folder}/{s}/{og_name}')
                    else:
                        #One casualty of having to open certain layers as DFs rather than GDFs is that these won't save as spatial data
                        #So we have to make sure they save as CSVs
                        #Anything that isn't a GDF (after failing isinstance(gpd.GeoDataFrame) gets saved as CSV rather than a GPKG)
                        r.to_csv(f'{extracted_data_folder}/{s}/{og_name.split(".")[0]}.csv')
    df = pd.DataFrame(query_info, columns = ['gpkg', 'layer', 'layer id'])
    #This saves info that we need for handling the photo data later
    df.to_csv(f'{extracted_data_folder}/layer_key.csv')
    return failed_to_open

def put_forms_in_subfolders(extracted_data_folder):
    for fo in os.listdir(extracted_data_folder):
        if os.path.isdir(f'{extracted_data_folder}/{fo}'):
            for f in os.listdir(f'{extracted_data_folder}/{fo}'):
                #Find site forms
                if any(n in f.lower() for n in ("form", "update", "shovel", "stp")):
                    #Write gpkg to csv
                    if os.path.isdir(f'{extracted_data_folder}/{fo}/Site_form'):
                        pass
                    else:
                        os.mkdir(f'{extracted_data_folder}/{fo}/Site_form')
                    #Open the site form
                    print(f'{extracted_data_folder}/{fo}/{f}')
                    form = gpd.read_file(f'{extracted_data_folder}/{fo}/{f}')
                    #Write to csv
                    form = pd.DataFrame(form)
                    #Put data in the relevant "site form" folder
                    form.to_csv(f'{extracted_data_folder}/{fo}/Site_form/{f.split(".")[0]}.csv')


def write_to_file(data, filename):
    # Convert binary data to proper format and write
    with open(filename, 'wb') as file:
        file.write(data)

def blob_to_image(database:str, fid:int, outpath:str, image_label = ''):
    """A basic function for extracting a single image from the BLOB column in an Avenza-exported GPKG.
    Can be used on its own to get images out of the GPKG if not running through entire extraction script.

    Parameters
    ----------
    database : str
        File path to GPKG with photos stored as BLOB
    fid : int
        Feature id (row number) of the image to be extracted (in a for loop, iterate through each in the range 0, len(gpkg))
    outpath : str
        Folder in which images will be saved
    image_label : str, optional
        Label to add to the beginning of the image filename, by default ''
    """
    try:
        sqliteConnection = sqlite3.connect(database)
        cursor = sqliteConnection.cursor()
        sql_fetch_blob_query = """SELECT * from avenza_media where fid = ?"""
        cursor.execute(sql_fetch_blob_query, (fid,))
        record = cursor.fetchall()
        for row in record:
            name = row[3]
            photo = row[1]
            if image_label != '':
                photoPath = f'{outpath}/{image_label}-{name}.jpg'
            else:
                photoPath = f'{outpath}/{name}.jpg'
            write_to_file(photo, photoPath)
            print(f'{photoPath} saved')
        cursor.close()
    except sqlite3.Error as error:
        print("Failed to read blob data from sqlite table", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

def extract_photos_and_logs(survey_data_folder, extracted_data_folder):
    bulk_photos = f'{survey_data_folder}/bulk_photos'
    if not os.path.isdir(bulk_photos):
        os.mkdir(bulk_photos)
    for f in os.listdir(survey_data_folder):
        if f.endswith('.gpkg'):
            database = f'{survey_data_folder}/{f}'
            media = gpd.read_file(database, layer = 'avenza_media')
            for i in range(0, len(media)):
                    try:
                        sqliteConnection = sqlite3.connect(database)
                        cursor = sqliteConnection.cursor()
                        sql_fetch_blob_query = """SELECT * from avenza_media where fid = ?"""
                        cursor.execute(sql_fetch_blob_query, (i,))
                        record = cursor.fetchall()
                        for row in record:
                            name = row[3]
                            photo = row[1]
                            layer_id = row[5]
                            feature_id = row[6]
                            orientation = row[12]
                            if len(orientation) > 0:
                                orientation = orientation.split(' ')
                                orientation = orientation[-1]
                            else:
                                orientation = 'NoOrientation'
                            if orientation == None:
                                orientation = 'NoOrientation'
                            photoPath = f'{bulk_photos}/{f.split(".")[0]}-layer{layer_id}-feature{feature_id}-{name}-{orientation}.jpg'
                            write_to_file(photo, photoPath)
                            print(f'{photoPath} saved')
                        cursor.close()
                    except sqlite3.Error as error:
                        print("Failed to read blob data from sqlite table", error)
                    finally:
                        if sqliteConnection:
                            sqliteConnection.close()
    layer_key = pd.read_csv(f'{extracted_data_folder}/layer_key.csv')
    others = ['These photos were not associated with a site and have been saved in "Other_photos":\n']
    for f in os.listdir(bulk_photos):
        if f.endswith('.jpg'):
            flist = f.split('-')
            filename = f'{survey_data_folder}/{flist[0]}.gpkg'
            layer_id = flist[1].replace('layer','')
            feature_id = flist[2].replace('feature','')
            name = flist[3]
            orientation = flist[4].split('.')[0]
            gpkg = layer_key[layer_key['gpkg'] == flist[0]]
            relevant_row = gpkg.loc[gpkg['layer id'] == int(layer_id)]
            geopkg = gpd.read_file(filename, layer = relevant_row['layer'].values[0])
            data_row = geopkg.loc[geopkg['avenza_feature_id'] == int(feature_id)]
            site_col = [s for s in list(data_row.columns) if 'Site ID' in s]
            if len(site_col) > 0:
                site_col = site_col[0]
                subfolder = f'/{data_row[site_col].values[0]}/Photos'
            else:
                subfolder = '/Other_photos'
                #Keep a record of photos saved in the "Other_photos" folder
                #TODO: Find some way of printing this list in a readable way to the app frame
                others.append(f)
            final_file_location = f'{extracted_data_folder}{subfolder}'
            if os.path.isdir(final_file_location):
                pass
            else:
                os.mkdir(final_file_location)
            final_file = f'{final_file_location}/{name.split(".")[0]}-{relevant_row["layer"].values[0]}-{relevant_row["gpkg"].values[0]}-{orientation}-fid{feature_id}.jpg'
            os.rename(f'{bulk_photos}/{f}', final_file)
    for fo in os.listdir(extracted_data_folder):
        if os.path.isdir(f'{extracted_data_folder}/{fo}/Photos'):
            photo_log_data = []
            foldername = fo
            photo_subfolder = f'{extracted_data_folder}/{foldername}/Photos'
            for im in os.listdir(photo_subfolder):
                if im.endswith('.jpg'):
                    att_list = im.split('-')
                    placemark = att_list[0]
                    layer = att_list[1]
                    gpkg = att_list[2]
                    orientation = att_list[3]
                    fid = att_list[-1].split('.')[0]
                    fid = fid.replace('fid','')
                    relevant_gpkg = f'{survey_data_folder}/{gpkg}.gpkg'
                    data = gpd.read_file(relevant_gpkg, layer = layer)
                    relevant_row = data.loc[data['avenza_feature_id'] == int(fid)]
                    desc_col = [s for s in list(relevant_row.columns) if 'escript' in s]
                    if len(desc_col) > 1:
                        desc = relevant_row[desc_col[1]]
                    elif len(desc_col) == 1:
                        desc = relevant_row[desc_col[0]]
                    if len(desc) > 0:
                        desc = desc.values[0]
                    else:
                        desc = 'No description available'
                    photo_log_data.append([placemark, desc, orientation])
            df = pd.DataFrame(photo_log_data, columns = ['Photo name', 'Description', 'Photo Orientation'])
            df.to_csv(f'{extracted_data_folder}/{fo}/Photos/{fo}_Photo_log.csv')
            return others
        
def site_form_to_text(extracted_data_folder, output_crs):
    avenza_categories = ["fid", "avenza_name", "avenza_description", "avenza_datetime", "OGR_STYLE", "avenza_layer_id", "avenza_feature_id", 'geometry', 'original_layer_name','Unnamed: 0']
    for fo in os.listdir(extracted_data_folder):
        if os.path.isdir(f'{extracted_data_folder}/{fo}'):
            form_folder = f'{extracted_data_folder}/{fo}/Site_form'
            for p in os.listdir(f'{extracted_data_folder}/{fo}'):
                if p.endswith('.gpkg'):
                    geopkg = gpd.read_file(f'{extracted_data_folder}/{fo}/{p}')
                    input_crs = geopkg.crs.to_epsg()
                    break
            if os.path.isdir(form_folder):
                forms = os.listdir(form_folder)
                for form in forms:
                    if '.csv' in form:
                        form_open = pd.read_csv(f'{extracted_data_folder}/{fo}/Site_form/{form}')
                    else:
                        pass
                form_type = form_open['original_layer_name'].values[0].split('_')[0]
                c = list(form_open.columns)
                c_final = list(set(c).difference(avenza_categories))
                to_write = []
                df = form_open[c_final]
                c_final.sort()
                for index, row in df.iterrows():
                    for label in c_final:
                        to_write.append(f'{label}: ')
                        to_write.append(f'{row[label]}\n')
                text_file_path = f'{extracted_data_folder}/{fo}/Site_form/{fo}_{form_type}.txt'
                form_open['geometry'] = gpd.GeoSeries.from_wkt(form_open['geometry'])
                form_gdf = gpd.GeoDataFrame(form_open, geometry = 'geometry', crs = input_crs)
                form_gdf = form_gdf.to_crs(f'EPSG:{output_crs}')
                if form_gdf.iloc[0]['geometry'].geom_type != 'Point':
                    x = 'See GPKG'
                    y = 'See GPKG'
                    pass
                else:
                    x = form_gdf.iloc[0]['geometry'].x
                    y = form_gdf.iloc[0]['geometry'].y
                to_write.append('Datum coordinates:')
                to_write.append(f'x = {x}, y = {y}')
                with open(text_file_path, 'a') as textfile:
                    textfile.write('\n'.join(to_write))
            else:
                print(f'No site form found for {fo}')
        else:
            print(f'{extracted_data_folder}/{fo} could not be found')