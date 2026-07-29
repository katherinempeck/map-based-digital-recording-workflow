# A map-based and task-oriented digital recording workflow for archaeological survey

## Overview
This repository contains Avenza schemas, Python scripts, and a detailed manual for the digital recording workflow described in the paper:

Peck, Katherine and Grant Snitker. 2026. "Evaluating a task and map-based digital recording workflow for pedestrian archaeological survey." Submitted to *American Antiquity* (report).

The contents of each folder is summarized below. 

### Pre-field Setup
The **Pre-field Setup** folder contains a manual (```Avenza Setup.md```) with screenshots showing how to import Avenza schemas and provides a review of the tasks associated with each layer. This folder also includes schemas and optional symbology files for import. We provide two example schemas:
* Digital_Schema_WA.kmz - the schema we used for our case study (in Washington state)
* Digital_Schema_Minimal.kmz - a stripped-down example that can be customized for use in any project. 

Both schemas contain three sublayers (Feature and Artifact Inventory, Photos and Site Boundaries, and Site and Isolate Form) which are meant to match the tasks described in the "Field" folder. Each task layer has additional sublayers. The WA schema contains several artifact sublayers and a site form layer with fields meant to streamline data entry into the Washington SHPO database (WISAARD). The minimal schema has a single artifact sublayer provided as an example (a debitage layer) and a minimal "site form" layer (with just a Site ID and Narrative field). Users should customize these as necessary to create the ideal data entry form.

Although these schemas and the symbology layer are in a spatial data format, they do not actually contain any spatial data. To view or edit the schemas, follow the steps in the setup manual to import.

### Field Recording
The **Field Recording** folder contains a manual (```Recording Manual.md```) with screenshots that summarizes each field recording task and has instructions for completing that task in Avenza.

### Post-Field Data Management
The **Post-Field Data Management** folder contains Python scripts to run the data extraction and organization procedure described in the manuscript. The script ```extract_survey_data.py``` is a Python script. To use, edit the script's parameters and run. The script ```extract_survey_data_GUI.py```, on the other hand, once run, creates a simple application that lets you load the data with a graphical user interface. This application can also be compiled to an executable. This subfolder has detailed documentation (```Using Python Scripts to Manage Field Data.md```) describing how to run and use each of these extractors.