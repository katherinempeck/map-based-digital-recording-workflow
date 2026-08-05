# Digital Recording Workflow Part 3: Post-Field Data Management

## Managing outputs without Python
Exported field data can be accessed using any GIS software. Import the layer into your GIS program of choice and use the select by attribute tool to extract data associated with each documented site. Artifact tables can be exported as CSVs and copied into report tables directly.

To access photos, export as a shapefile and unzip the photo folder included in the export. Images can be directly associated with the point at which they were taken using the file path in the “Photos” attribute in the exported shapefile. 

## Managing outputs with Python
We have developed a post-field data extraction script. This script works with the exported GeoPackage to:
* Use the "Site ID" attribute to extract and organize spatial data from the original Avenza output into folders, by site.
* Extract individual forms for each site, convert to CSV, and place them into subfolders.
* Convert the site form CSV to a readable text file for proofreading and entry into a database/PDF form
* Extract images (stored as BLOBs in the exported GeoPackages) from Avenza output, organize photos into folders, and create photo logs for each folder.

### Installing Python and relevant libraries (beginner's guide)
Python is a programming language with many options for geospatial data management (if you are already comfortable using Python, skip to "Required Libraries" below). To run a Python script (```.py``` file) you need to have:

1. A Python interpreter installed on your computer
2. Some way to download and install Python libraries
3. Some way to manage virtual environments
4. An integrated development environment (IDE) software that helps you edit and debug code (alternatively, you can edit these files in programs like Notepad or TextEdit, but IDEs make it easier)

You can download an install a Python interpreter by following the instructions on the [Python Software Foundation webpage](https://www.python.org/about/gettingstarted/). Your computer may also already have its own Python installation and you can follow the instructions on that webpage to check. 

In addition to Python itself you will also need to install additional Python libraries. Python has a standard library (a set of functions that you can use without having to write them yourself) that includes basic math, statistics, and file management functions. Other developers have created libraries of code to do complex work like analyzing geospatial data. To use the scripts in this repository, you will need to install some of these libraries. The best way to do that is with a package manager software. ```pip``` is a common Python package manager that runs through the command line. The Python Software foundation has a page explaining how to use this package manager (see ["Installing Python modules"](https://docs.python.org/3/installing/index.html)). [Anaconda](https://www.anaconda.com/download/success) is another way to manage Python libraries. It comes with a Python distribution and a program to download and install additional libraries with a graphical user interface. 

Once you decide which package manager you want to use, then you should create a new "virtual environment." A virtual environment is essentially a separate set of folders on your computer with its own version of Python and a select number of libraries installed. Sometimes libraries have different requirements (e.g., only work with certain versions of Python) so the easiest way to make sure that your libraries can run correctly is to create a new virtual environment with the required Python version, install libraries in that environment, and run scripts while that environment is active. Python comes wth a built-in environment manager called ```venv``` ([see Python documentation](https://docs.python.org/3/library/venv.html#module-venv)) that runs through the command line. Anaconda also lets you manage environments without using the command line.

Finally, you will need some way to open and run Python files. You can run Python files from the terminal (MacOS/Linux) or command line (Windows) with the command ```python script.py``` replacing ```script.py``` with the file path to your script. However, it is much easier to use an IDE that lets you edit and debug code all within the same text editing program. The program [IDLE](https://docs.python.org/3/library/idle.html) should come with your Python installation if you installed it from the Python Software Foundation. It is a simple IDE that lets you edit, debug, and run Python scripts. [Spyder](https://en.wikipedia.org/wiki/Spyder_(software)) is another IDE that has a few more features than IDLE. If you use other programming languages, [Visual Studio Code](https://en.wikipedia.org/wiki/Visual_Studio_Code) is a great option.

#### Required libraries

Running the scripts in this folder requires several Python data/geospatial data analysis libraries:
* [Pandas](https://pandas.pydata.org/getting_started.html) (2.2.3)
* [GeoPandas](https://geopandas.org/en/stable/getting_started.html) (1.0.1)
* [Fiona](https://fiona.readthedocs.io/en/stable/install.html) (1.10.1, should install as a GeoPandas dependency)
* [Shapely](https://shapely.readthedocs.io/en/stable/) (2.0.6, should install as a GeoPandas dependency)

Follow the instructions on each library's page to install the libraries with your package manager.

### Data structure assumptions

This extractor script  makes some assumptions about the structure of the data:

* All spatial data in the input folder are GeoPackages, and those GeoPackages were exported from Avenza (there are specific database functions and Avenza layers that the script needs to function)
* All data that you want to be extracted and reorganized will have a column called "Site ID" (anything without a Site ID column will not be extracted into the relevant site folder and will have to be manually located after the extractor script finishes)
* The Photo layer has a column with a name like "Description" with data that should go into the photo log (the script searches for a field that contains the string "escript"; if that field isn't located, that photo will have an empty description field in the generated photo log)
* New sites/isolates/site updates were recorded in a layer that included the text "form" or "update" (to find the site form, the extractor script searches within layers with these names)

Other than these assumptions, the extractor scripts should still work even if users have edited other schema attributes.

### Using the script

Activate the environment with the listed libraries installed. Then, open the ```extract_survey_data.py``` file in your IDE (different IDEs have different ways of working with virtual environments, so be sure to read the program's documentation). 

At the top of the script is a section labelled:

```
################
## Parameters ##
################
```

You should only need to make edits to the script below this header. This section lets you assign values to specific [variables](https://en.wikipedia.org/wiki/Variable_(high-level_programming_language)) (a name associated with a value) that the functions (in the source folder) will use to organize your data. In Python, you assign values to variables by typing the name of the variable followed by an equals sign. In this script, for example, the first variable is ```get_recent```. The line ```get_recent = False``` means that every time the variable ```get_recent``` is used in the script the interpreter reads that as the value "False." 

Go through the variables under the Parameters header and update the variables so they match the file paths where your data is stored. If you're not sure what to fill out for a variable, look for the comment (text preceded by ```#```) above the variable. File paths should have forward slashes and be enclosed in apostrophes or quotation marks. The final variable, ```output_crs``` needs to have the [EPSG](https://en.wikipedia.org/wiki/EPSG_Geodetic_Parameter_Dataset) code of coordinate reference system to which you want your final geospatial data projected. You can find these online by searching the name of the coordinate system you want to project into. For instance, searching "NAD 83 UTM zone 12n epsg" tells us that the EPSG code for UTM Zone 12N is 26912. 

Once you have updated all the variables, run the script (look for a play button or a menu labelled "Run" in your IDE). This will run through all the data in the survey data folder and reorganize it (without modifying the original data) into the folder you defined as ```extracted_data_folder```.

### Using the GUI app

Editing Python scripts can be difficult if you do not use them regularly. If you want to use this script with a graphical user interface (like a regular program), you will also need (in addition to the libraries above) a library called [wxPython](https://wxpython.org/index.html). Once this library is installed into your virtual environment, activate the environment and open the script ```extract_survey_data_GUI.py``` in the GUI subfolder. Run the script without changing anything, and an application should open. It may take some time to load, but once it does you can follow the prompts to set the input folder, output folder, and output CRS. To quite the application, click into the terminal of your IDE and hit CTRL + C.

### Compiling the GUI app (optional)

If running the script every time to generate the GUI app is too cumbersome, you can also compile the script into an executable file using the library [PyInstaller](https://pyinstaller.org/en/stable/).

Open the terminal or command prompt and type ```cd``` followed by the file path to the folder where this script is located. This means that any operations you run in the prompt will be done in this folder. Then, run ```pyinstaller --window GUI_app_main.py```. This will create an executable (.exe) on Windows or a .app on MacOS. If you are using a Mac, you can also run ```pyinstaller --window --icon icons.icns GUI_app_main.py``` to use the included icons file as the shortcut icon for your compiled app.

### Modifying for other input data formats

As discussed in the manuscript, we developed this script to work with GeoPackages. GeoPackages offer a number of advantages over shapefiles. GeoPackages are composed of a single file (.gpkg) rather than 3+ (.shp, .shx, .dbf) making them easier to share. They can include multiple different geometry types, photos (as "binary large object" data - "BLOB" format), and even raster data. For digital recording, an especially relevant advantage is that GeoPackages do not limit attribute field name length or field value length. Attributes with long names (e.g., "Projectile Point Type") will not be truncated, nor will long descriptions.

However, depending on project needs, shapefiles or other data formats may be preferred. Modifying the extractor scripts to work with your format of choice will require some previous Python experience. Here are a few areas of the script that should be modified if you want to adapt it to work with different spatial data inputs:

* Throughout the script, functions are written to look for files that end with .gpkg. These should be changed to look for the appropriate file path.
* In the function ```organize_data_to_site_folders()```, as written, the function iterates through each layer in each GeoPackage in the input folder (see line 55). If using shapefiles as the input, this section should be changed to just iterate through each file and find unique site IDs. KMLs also contain layers and so a similar format can likely be used.
* The function ```extract_photos_and_logs``` is designed to read BLOB data attached to rows in the "photos" layer of a GeoPackage exported from Avenza (starting at line 219). This function will not work in the same way for shapefiles or KMLs. For instance, if you export data as shapefiles from Avenza, your export will be a zipped folder. If the exported Avenza layers included attached images, the zipped folder will include both the shapefiles and an image subfolder. Images can be directly associated with the point at which they were taken using the file path in the “Photos” attribute in the exported shapefile. This function can be modified at line 250 onward to iterate through images in the subfolder and find the record in the shapefile that matches the file path. 

