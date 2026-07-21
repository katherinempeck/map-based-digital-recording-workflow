from source.source_functions import *

################
## Parameters ##
################

#Do you want to find the most recent dated folder in the parent folder automatically (based on the folder name date code)?
#This is useful if you have multiple daily backup folders organized by date
get_recent = False
#If True, provide the folder path to the parent folder containing the folders to search:
survey_data_parent_folder = ''
#If False, provide a desired subfolder to use for extraction:
survey_data_folder = "/replace/with/folderpath"
#Provide a folder path to the folder in which you want to save all the extracted data:
extracted_data_folder = "/replace/with/folderpath"
#What is the final projected coordinate system for these data? Provide the EPSG code (e.g., https://epsg.io/26910)
output_crs = '26910'

#########
## Run ##
#########

#Organize site data into folders
if get_recent == True:
    survey_data_folder = get_most_recent_folder(survey_data_parent_folder)
else:
    pass

organize_data_to_site_folders(survey_data_folder, extracted_data_folder, output_crs)
print('Created site folders and organized files')

#Organize forms into subfolders
put_forms_in_subfolders(extracted_data_folder)
print('Forms now in subfolders')

#Extract photos and create photo log
extract_photos_and_logs(survey_data_folder, extracted_data_folder)
print('Photo extraction complete')

#Convert site form CSVs to text
site_form_to_text(extracted_data_folder, output_crs)
print('Text forms created')