import sys
import ipywidgets as widgets
import shutil

# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
import ipydatetime
from ipywidgets import FileUpload, Button
from IPython.display import FileLink
import html
from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoJSON, Marker, Polyline
from ipywidgets import Layout, HBox, VBox, FloatText
from ipywidgets import *
from ipyfilechooser import FileChooser

import pandas as pd
import numpy as np
from IPython.display import display, clear_output
import zipfile

from emagpy import Problem # import the main Problem class from emagpy
import reda

from datetime import date, datetime

from lib.geometadp.about import _widget_about

import tempfile
import shutil
import os


from lib.geometadp.md_manager import geo_metadata

class project_API(object):
        def __init__(self):

            # this stores the actual values exported to json/xml
            self.metadata = {}
            self.dir_path = []

        def _read_json(self):
            """Read json file containing metadata.

            Returns
            -------
            dict
                A dict of all the metadata.
            """
            print('read json')
            with open(self.dir_path + '/' + 'json_backup_step4.json') as json_file:
                    self.metadata = json.load(json_file)
            pass

        def open_project(self,dir_path):
            """Open the project folder.

            Parameters
            ----------
            dir_path : str type
                Main path where all the project files are located.
            """
            self.dir_path = dir_path
            self._read_json()

            print('open_project')

            pass

        def add_metadata_entry(self,name,value):
            """Add a new metadata entry to the json file.

            Parameters
            ----------
            name : str
                name of the metadata.
            value : type
                value of the metadata.
            """
            new_meta = {name,value}
            # check if name is already existing
            self.metadata[eval(name)]=new_meta[eval(value)]
            print(self.metadata)

            pass
