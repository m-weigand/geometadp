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


import tempfile
import shutil
import os

#import exdir

from lib.geometadp.EM import EM_widgets
from lib.geometadp.about import _widget_about

#from about import _widget_about
#from file_import_qt5 as fileImportQt5

"""
Each widget object is associated with one metadata entry


Requirements for widget objects
1) .is_visible() <- this function evaluates if a widget is to be shown,
   i.e., based on the current value of another metadata-set

   This also implies marking itself for non-output.
   For example, if the data type is switched from lab to field,
   widget values should be retained, but not exported

2) we need a global refresh function
"""


import asyncio

# some css
style = {'description_width': '300px'}
layout = {'width': 'auto'}

# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#Debouncing
from IPython.display import display_html

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        self._callback()

    def cancel(self):
        self._task.cancel()


def debounce(wait):
    """ Decorator that will postpone a function's
        execution until after `wait` seconds
        have elapsed since the last time it was invoked. """
    def decorator(fn):
        timer = None

        def debounced(*args, **kwargs):
            nonlocal timer

            def call_it():
                fn(*args, **kwargs)
            if timer is not None:
                timer.cancel()
            timer = Timer(wait, call_it)
        return debounced
    return decorator


class geo_metadata(EM_widgets):
    def __init__(self,*args, **kwargs):

        super().__init__(*args, **kwargs)
        EM_widgets.__init__(self)

        # self.app = QApplication(sys.argv)

        # this stores the actual values exported to json/xml
        self.metadata = {}
        self.warnings = [] # report all the warnings

        # stores the various widget objects. They are shown in this order
        self.widget_guidelines = []
        self.widget_guidelines_footer = []

        self.widget_ownership = []
        self.widget_survey = []
        self.widget_survey_map = []

        self.widget_ERT = [] # min required ERT metadata
        self.widget_ERT_upload = []
        self.widget_ERT_files = []

        #self.widget_EM = [] # min required EM metadata
        #self.widget_EM_upload = []
        #self.widget_EM_files = []

        self.widget_timelapse = [] # Assist in Time Lapse nested tabs creation

        self.widget_quality = []
        self.widget_sampling = []
        self.widget_data_structure = []

        self.widget_import = [] # Json pre-existing file importer
        self.widget_export = [] # Export Json
        self.widget_files_tree = [] # display file structure
        self.widget_export_HDF5 = []

        self.widget_logger = []

        self.widget_about = []

        self._prepare_widgets()


    def _prepare_widgets(self):

        self.widget_guidelines.append(self._widget_header())
        self.widget_guidelines.append(self._restart_project())

        #%% REPORT: title/authors
        self.widget_ownership.append(self._widget_report_title())
        self.widget_ownership.append(self._widget_report_authors())
        self.widget_ownership.append(self._widget_owner())
        self.widget_ownership.append(self._widget_email())
        self.widget_ownership.append(self._widget_dataset_DOI())

        self.widget_guidelines_footer.append(self._widget_footer())


        # SURVEY: method/type/instrument
        self.widget_survey.append(self._widgets_survey_doc())
        # self.widget_survey.append(self._widget_upload_CAGS()) # not yet implemented

        self.widget_survey.append(self._widget_method())
        self.widget_survey.append(self._widget_measurement_type())
        #self.widget_survey.append(self._widget_variables())
        # self.widget_survey.append(self._widget_location_bounds()) # deprecated (use leaflet instead)

        # SURVEY: map
        self.widget_survey_map.append(self._widget_leaflet())

        # widgets common to every methods
        # Reasons for choice of survey technique
        # Time lapse data flag
            # nb of files
            # date/time flag
        #self.widget_timelapse.append(self._timelapse_option())
        #self.widget_timelapse.append(self._nb_of_files())
        #self.widget_timelapse.append(self._time_schedule())


        #%% ERT metadata: Date_measure/ Time_measure/ Elec_conf/ Elec_spacing
        #self.widget_ERT.append(self._widgets_ERT_doc())
        self.widget_ERT.append(self._widget_instrument_ERT())
        self.widget_ERT.append(self._widget_datetime_ERT())
        # self.widget_objects.append(self._widget_time())
        self.widget_ERT.append(self._widget_elec_config())
        self.widget_ERT.append(self._widget_elec_seq())
        self.widget_ERT.append(self._widget_elec_spacing())
        self.widget_ERT.append(self._widget_description_ERT())
        #self.widget_ERT.append(self._widget_ERT_more())
        self.widget_ERT.append(self._timelapse_option())
        #self.widget_ERT.append(self._timelapse_slider())



        self.widget_ERT_upload.append(self._widget_upload_ERT_button())
        self.widget_ERT_upload.append(self._display_head_table())
        self.widget_ERT_files.append(self._widget_upload_suppdata_buttons(self.metadata['method']))


        #%% EM metadata
        #self.widget_EM.append(self._widgets_EM_doc())
        #self.widget_EM.append(self._widget_instrument_EM())
        #self.widget_EM.append(self._widget_datetime_EM())
        #self.widget_EM.append(self._widget_coil_config())
        #self.widget_EM.append(self._widget_coil_height())
        #self.widget_EM.append(self._widget_coil_spacing())
        #self.widget_EM.append(self._widget_description_EM())
        #self.widget_EM.append(self._timelapse_option())

        #self.widget_EM_upload.append(self._widget_upload_EM_button())  # upload EM data from emagpy
        #self.widget_EM_files.append(self._widgets_EM_add_file())


        #%% DATA QUALITY ASSESSEMENT metadata
        self.widget_quality.append(self._widgets_quality_doc())
        self.widget_quality.append(self._widget_peer_reviewed())
        self.widget_quality.append(self._widget_peer_reviewer_contact())
        self.widget_quality.append(self._widget_replicate_datasets())
        self.widget_quality.append(self._widget_comparison_ref_data())
        self.widget_quality.append(self._widget_ref_data())
        self.widget_quality.append(self._widget_free_quality())

        #%% SAMPLING
        self.widget_sampling.append(self._widgets_sampling_doc())
        self.widget_sampling.append(self._widget_free_sampling())

        #%% DATA structure
        #self.widget_data_structure.append(self._widgets_dataset_structure_doc())
        #self.widget_data_structure.append(self._widget_upload_img_button())
        #self.widget_data_structure.append(self._widget_external_ressource_more(my_columns))
        #self.widget_data_structure.append(self._widgets_dataset_structure())
        #self.widget_data_structure.append(self._widgets_related_external_resources_doc())


        #%% ancillary DATA
        # self.widget_ancillary.data.append(self._widgets_figures())

        #%% Upload
        self.widget_export.append(self._widget_export())
        self.widget_export.append(self._widget_download_buttons())
        #self.widget_export.append(self._display_Zip())
        #self.widget_export.append(self._update_display_Zip())

        #self.widget_files_tree.append(self._display_Zip())
        self.widget_files_tree.append(self._display_dir_tree_old())
        #self.widget_files_tree.append(self._display_dir_tree())


        self.widget_export_HDF5.append(self._widgets_HDF5_doc())


        #%% Import
        self.widget_import.append(self._widget_upload_json())
        self.widget_import.append(self._widget_upload_button())
        #self.widget_import.append(self._widget_upload_from_db())

        #%% Logger
        self.widget_logger.append(self._widget_log())

        #%% About
        self.widget_about.append(_widget_about())


    def _restart_project(self):
        '''
        Close all widgets - closes all widgets currently in the widget manager (which also closes them in the kernel)
        and restart the class
        '''

        button_restart = widgets.Button(description="restart",button_style='warning')

        self.button_restart_box = widgets.HBox([button_restart])
        def _on_button_restart_click(change):
            #display_html("<script>Jupyter.notebook.kernel.restart()</script>",raw=True)
            widgets.Widget.close_all()
            obj = geo_metadata()
            obj.manage()

        button_restart.on_click(_on_button_restart_click)

        text = widgets.HTML('''
            <hr style="height:5px;border-width:0;color:black;background-color:gray">
            ''')

        vbox = widgets.VBox([button_restart, text])
        #Close all widgets - closes all widgets currently in the widget manager (which also closes them in the kernel)

        return vbox


    def _widget_header(self):
        """Show the header of the data mangement gui that explains the basic concepts
        """

        file = open("img/logo.png", "rb")
        image = file.read()
        logo = widgets.Image(
            value=image,
            format='png',
            width=30,
            height=30,
        )

        title = widgets.HTML(
            '<h2>Data Manager and Metadata Collector for CAGS</h2>'
            '<h5>&beta; version</h5>')
        vbox = widgets.VBox([logo, title])

        return vbox

    def _widget_footer(self):
        """Show the footer of the data mangement gui that explains the basic concepts
        """
        text = widgets.HTML('''
            <h4> Introduction  </h4>
            <p> This gui is designed to help with the initial preparation of one
            geophysical dataset metadata. Simple metadata descriptors must be filled in order to:
                <ol>
                  <li> Make your survey datasets reusable for you</li>
                  <li> And for the community. Descriptors with * are minimum required metadata identified for your research to be considered FAIR</li>
                </ol>

            <h4> Tips  </h4>
                <ol>
                  <li> Use data importers for automatic metadata extraction </li>
                  <li> Use it locally for a maximum flexibility</li>
                </ol>

            <h4> Recommandations </h4>
                <ol>
                  <li> Fill out the maximum number of metadata fields </li>
                  <li> Check the logger for possible errors</li>
                </ol>

            <h4> More on github </h4>
                See About tab and github page for <a href="https://github.com/agrogeophy/geometadp" target="_blank">more informations.</a></p>

            <hr style="height:5px;border-width:0;color:black;background-color:gray">

            ''')

        vbox = widgets.VBox([text])

        return vbox

#%% REPORT: title/authors

    # def validate(change):
    #     # Put your validation condition here
    #     if change['new'] > 50:
    #         self.widget_report_title.value = change['old']

    # text.observe(validate, 'value')


    def _widget_report_title(self):
        self.widget_report_title = widgets.Text(
            description='Short title description of the dataset',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_report_title(change):
            self.metadata['report_title'] = self.widget_report_title.value
            self._update_widget_export()

        self.widget_report_title.observe(_observe_report_title)
        self.widget_report_title.add_class("box_style")

        return self.widget_report_title

    def _widget_report_authors(self):
        self.widget_report_authors = widgets.Text(
            description='Reporting authors names',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_report_authors(change):
            self.metadata['report_authors'] = self.widget_report_authors.value
            self._update_widget_export()

        self.widget_report_authors.observe(_observe_report_authors)
        return self.widget_report_authors

    def _widget_owner(self):
        self.widget_owner = widgets.Text(
            description='Owner:',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_owner(change):
            self.metadata['owner'] = self.widget_owner.value
            self._update_widget_export()

        self.widget_owner.observe(_observe_owner)
        return self.widget_owner

    def _widget_email(self):
        self.widget_email = widgets.Text(
            description='Email:',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_email(change):
            self.metadata['email'] = self.widget_email.value
            self._update_widget_export()

        self.widget_email.observe(_observe_email)
        return self.widget_email

    def _widget_dataset_DOI(self):
        self.widget_dataset_DOI = widgets.Text(
            description='Dataset DOI:',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_dataset_DOI(change):
            self.metadata['dataset_DOI'] = self.widget_dataset_DOI.value
            self._update_widget_export()

        self.widget_dataset_DOI.observe(_observe_dataset_DOI)
        return self.widget_dataset_DOI

    def _widget_variables(self):
        self.widget_variables = widgets.Text(
            description='Physical property investigated:',
            style=style,
            layout=layout)


        @debounce(0.2)
        def _observe_variables(change):
            self.metadata['variables'] = self.widget_variables.value
            self._update_widget_export()

        self.widget_variables.observe(_observe_variables)
        return self.widget_variables

    # def _widget_location_bounds(self):
    #     self.widget_location_bounds = widgets.Text(
    #         description='North, West, East, and South Bounding Latitudes:',
    #         style={'description_width': 'initial'}
    #         )

    #     @debounce(0.2)
    #     def _observe_location_bounds(change):
    #         self.metadata['location_bounds'] = self.widget_location_bounds.value
    #         self._update_widget_export()

    #     self.widget_location_bounds.observe(_observe_location_bounds)
    #     return self.widget_location_bounds

    def _widget_upload_XY_button(self):
       """Import XY file describing a 2d line prospection and plot it in the map"""

       #self.widget_xy_coords_file
       self.widget_xy_coords_file = FileChooser(use_dir_icons=True)
       self.widget_xy_coords_file.filter_pattern = '*.csv'
       self.widget_xy_coords_file.title = '<b>xy_coords</b>'

       vbox = widgets.VBox([self.widget_xy_coords_file])

       def _on_upload_xy_change():
            #for name, file_info in self.widget_xy_coords_file.value.items():

            name = self.widget_xy_coords_file.selected # absolute path
            path_abs , file = os.path.split(name)
            level_dir = 'Site_metadata'
            dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file


            #self._add_to_Zip(name, target_dir=self.metadata['method'], level_dir='spatial')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='spatial')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)
            self._update_widget_log('xy_file copied into zip')

            with open(name, newline='') as csvfile:
                self.xy_data = pd.read_csv(csvfile,sep=';')

            poly_line = Polyline(locations=self.xy_data.values.tolist(), color="red" , fill=False)
            self.m_top.add_layer(poly_line)

            #for name, file_info in self.widget_xy_coords_file.value.items():
            name = self.widget_xy_coords_file.selected
            self.metadata['xy_coords_file'] = dest_project_path
            self._update_widget_export()

       # self.widget_xy_coords_file.register_callback(_observe_xy_coords) # add to metadata export
       # self.self.m_top.observe(_observe_geojson) # add to metadata export
       self.widget_xy_coords_file.register_callback(_on_upload_xy_change) # plot into leaflet

       return vbox

    def _widget_leaflet(self):
        '''
        Create a leaflet map
        '''

        header = HTML("Import tools for 1d souding, 2d line and 2d map", layout=Layout(height='auto'))
        header.style.text_align='center'
        details = HTML("For geophysical maps and 2d lines, import directly the respective file", layout=Layout(height='auto'))


        center = [0, 0]

        self.m_top = Map(
            zoom=-10,
            basemap=basemaps.Esri.WorldTopoMap,
            attribution_control=False,
            zoom_control=True,
            width='100%',
            fullscreenControl=True,
            # layout=Layout(height='800px'),
            flex=1
        )

        # case of a sounding data
        # Create the two text boxes
        self.widget_latitude = widgets.Text(
            value=str(center[0]),
            description='Lat:'
        )

        self.widget_longitude = widgets.Text(
            value= str(center[1]),
            description='Lng:'
        )

        # case of a 2d line data
        box_2dline = self._widget_upload_XY_button()

        # case of a 2d map data
        box_map = self._widget_upload_GeoJSON_button()



        def _observe_location_bounds(change):
            self.metadata['latitude'] = self.widget_latitude.value
            self.metadata['longitude'] = self.widget_longitude.value
            self._update_widget_export()

            # Create a callback for when the center of the map has changed
            def on_coord_change(change):
                marker = Marker(location=[self.widget_latitude.value,  self.widget_longitude.value], draggable=False)
                self.m_top.add_layer(marker);

            self.m_top.observe(on_coord_change, names='center')


        self.widget_latitude.observe(_observe_location_bounds)
        self.widget_longitude.observe(_observe_location_bounds)


        # show on map
        bmap = widgets.Button(
            description='Show on map',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        out = widgets.Output()

        def on_button_clicked(bmap):
            with out:
                clear_output()
                display(self.m_top)

        bmap.on_click(on_button_clicked)
        box_1d = widgets.HBox([self.widget_latitude, self.widget_longitude])

        # Create the horizontal container containing the two textboxes
        hbox = widgets.VBox([box_1d,details,box_2dline,box_map])

        # Create the horizontal container containing the map and the horizontal container
        vbox = widgets.VBox([header, hbox, bmap, out])
        # vbox = widgets.VBox([header, hbox, self.m_top])
        # vbox = widgets.VBox([self.m_top])

        # And display it
        return vbox


    def _widget_upload_GeoJSON_button(self):
       """Import GeoJSON file"""

       #self.geojson_upload = widgets.FileUpload(
       #        description = 'geo.json',
       #        accept='.json',  # Accepted file extension
       #        multiple=False,  # True to accept multiple files upload else False
       #        style=style,
       #        layout=layout)
       self.geojson_upload = FileChooser(use_dir_icons=True)
       self.geojson_upload.title = '<b>GeoJSON</b>'

       #print(self.geojson_upload.selected)
       vbox = widgets.VBox([self.geojson_upload])

       def _on_upload_change():


            name = self.widget_xy_coords_file.selected # absolute path
            path_abs , file = os.path.split(name)
            level_dir = 'Site_metadata'
            dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file

            #for name, file_info in self.geojson_upload.value.items():
            #self._add_to_Zip(name, target_dir=self.metadata['method'] , level_dir='spatial')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='spatial')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)
            self._update_widget_log('geojson_file copied into zip')
            with open(name, 'r') as f:
                self.geojson_data = json.load(f)
            self.geo_json = GeoJSON( data=self.geojson_data,
                                style={'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 1},
                                hover_style={'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5},
                            )
            self.m_top.add_layer(self.geo_json)

            name = self.geojson_upload.selected
            # print('print to metadata')
            #for name, file_info in self.geojson_upload.value.items():
                # print(name)
            self.metadata['geojson_file'] = dest_project_path
            self._update_widget_export()


       self.geojson_upload.register_callback(_on_upload_change) # plot into leaflet
       # self.self.m_top.observe(_observe_geojson) # add to metadata export

       return vbox


    # def _overlay_layer():
    #     for feature in self.geojson_data['features']:
    #         feature['properties']['style'] = {
    #             'color': 'grey',
    #             'weight': 1,
    #             'fillColor': 'grey',
    #             'fillOpacity': 0.5
    #         }
    #     geo = GeoJSON(data=self.geojson_data, hover_style={'fillColor': 'red'}, name='Countries')

    #     return geo




    #%% SURVEY: method/type/instrument

    def _widgets_survey_doc(self):
        title = widgets.HTML('''
            <h3> Survey metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             For the choice of the method please report to <a href="https://agrogeophy.github.io/datasets/glossary.html" "target"="_blank">the online documentation glossary</a>
             ''')
        vbox = widgets.VBox([title])
        return vbox


    def _widget_method(self):
        self.widget_method = widgets.SelectMultiple(
            options=[
                'Geoelectrical - ERT',
                #'Geoelectrical - TDIP',
                #'Geoelectrical - sEIT',
                #'Geoelectrical - SIP/EIS',
                #'GPR',
                'EM',
                #'Seismic',
            ],
            default='Geoelectrical - ERT',
            description='Method(s):',
            disabled=False,
            style=style,
            layout=layout)


        # set initial metadata
        self.metadata['method'] = ''


        return self.widget_method

#%% TIME LAPSE MANAGEMENT



    def _timelapse_option(self, reloadJSON=False):
        '''
        A selection yes/no button (just for flag record in the metadata)
        A nb_of_file input text widget whi triggered the creation of new tabs
        A _time_interval_TL input widget (not used)
        '''

        #text = widgets.HTML('''
        #    <hr style="height:5px;border-width:0;color:black;background-color:gray">
        #    ''')

        #vbox_TL = widgets.VBox([text])
        vbox_TL = widgets.VBox()

        if reloadJSON==False:


            self.widget_TL_choice = widgets.RadioButtons(
            options=['No', 'Yes'],
            default='No',
            #value=None,
            description='Add time lapse metadata',
            disabled=False,
            style=style,
            layout=layout)

            #print('test False')
            button_True = widgets.Button(description="Time Lapse True")
            button_False = widgets.Button(description="False")

            #self.widget_time_lapse = widgets.HBox([button_True,button_False])
            self.widget_time_lapse = widgets.HBox([self.widget_TL_choice])
            # set initial metadata
            # self.metadata['time_lapse'] = 'False'

            # Where we will put all our time lapse widgets
            #print(self.widget_TL_choice.value)
            if self.widget_TL_choice.value == 'No':

            #def _on_button_True_click(change):
                #print('change')
                self.metadata['time_lapse'] = 'True'
                vbox_nb_of_files = self._nb_of_files_TL()
                vbox_time_interval = self._time_interval_TL()
                #vbox_create_TL_tabs = self._create_TL_tabs()
                vbox_TL.children = (*vbox_TL.children, vbox_nb_of_files)
                vbox_TL.children = (*vbox_TL.children, vbox_time_interval)
                #vbox_TL.children = (*vbox_TL.children, vbox_create_TL_tabs)
                #self._update_widget_export()


            else:
            #def _on_button_False_click(change):
                self.metadata['time_lapse'] = 'False'
                #vbox_TL = widgets.VBox()
                #vbox_TL.children = ()
                #with self.widget_nb_files_TL:
                #    clear_output()
                #self.widget_nb_files_TL.clear_output()
                self._update_widget_export()

            #button_True.on_click(_on_button_True_click)
            #button_False.on_click(_on_button_False_click)

        else:
            self.metadata['time_lapse'] = 'True'
            vbox_nb_of_files = self._nb_of_files_TL()
            vbox_time_interval = self._time_interval_TL()
            vbox_TL.children = (*vbox_TL.children, vbox_nb_of_files)
            vbox_TL.children = (*vbox_TL.children, vbox_time_interval)
            self._update_widget_export()


        # Put Dropdown and button together
        vbox = widgets.VBox([self.widget_time_lapse, vbox_TL])

        return vbox



        # Put Dropdown and button together
        #vbox = widgets.VBox([self.widget_time_lapse, self.vbox_TL])
        #display(vbox)




    def _nb_of_files_TL(self):
        self.widget_nb_files_TL = widgets.IntText(
            description='Nb of steps',
            style=style,
            layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%')
            )

        def delete_btn_clicked(b):
            b.parent.layout.display = 'none'

        delete = widgets.Button(icon="trash")
        delete.on_click(delete_btn_clicked)
        container = widgets.HBox([self.widget_nb_files_TL,delete])
        delete.parent = container
        #self.widget_nb_files_TL.parent = container

        #children = self.widget_nb_files_TL + delete
        #container.children = children

        def _observe_nb_of_files_TL(change):
            print('_observe_nb_of_files_TL')
            self.metadata['nb_of_files_TL'] = change.new
            #self.widget_TL_slider.max = change.new
            self._update_widget_export()
            self._add_children_TL()

        self.widget_nb_files_TL.observe(_observe_nb_of_files_TL,'value')

        #return self.widget_nb_files_TL
        return container

    def _time_interval_TL(self):
        self.widget_time_interval_TL = widgets.Text(
            description='Time interval reading',
            style=style,
            layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%')
            )

        def delete_btn_clicked(b):
            b.parent.layout.display = 'none'

        delete = widgets.Button(icon="trash")
        delete.on_click(delete_btn_clicked)
        container = widgets.HBox([self.widget_time_interval_TL,delete])
        delete.parent = container

        def _observe_time_interval_TL(change):
            self.metadata['time_interval_TL'] = self.widget_time_interval_TL.value
            self._update_widget_export()

        self.widget_time_interval_TL.observe(_observe_time_interval_TL)

        return container



    def _timelapse_slider(self):
        '''
            Not implemented for the moment;
            might be useful to add to header for selecting more quickly a TL tab
        '''

        self.widget_TL_slider = widgets.IntSlider(
                                            value=1,
                                            min=1,
                                            max=1,
                                            step=1,
                                            description='Choose the time step to display:',
                                            disabled=False,
                                            continuous_update=False,
                                            orientation='horizontal',
                                            readout=True,
                                            readout_format='d'
                                        )
        vbox_TL_slider = widgets.VBox([self.widget_TL_slider])

        return vbox_TL_slider

    def create_TL_widgets(child_to_create, step):
        '''
            call by _add_children_TL
            Make a copy with a new name of the main tab root widget
            The new widget as a new description based on root description + step nb
            Value of root widget are automatically propagated into new one
        '''

        print('*****_create_TL_widgets*****')
        #print(child_to_create)
        print(child_to_create._view_name)
        #print(child_to_create._view_name)

        if child_to_create._view_name == 'TextView':
            new_widgets_TL = widgets.Text(value=child_to_create.value,
                                        description=child_to_create.description + str(step[1]),
                                        style=style,layout=layout)

        if child_to_create._view_name == 'RadioButtonsView':
            new_widgets_TL = widgets.RadioButtons(options=child_to_create.options,
                                               value=child_to_create.value,
                                               description=child_to_create.description + str(step[1]),
                                               disabled=False,style=style,layout=layout)

        if child_to_create._view_name == 'HTMLView':
            new_widgets_TL = widgets.HTML(description=child_to_create.description + str(step[1]),value=child_to_create.value,style=style,layout=layout)
            print(child_to_create)

        if child_to_create._view_name == 'DropdownView':
            new_widgets_TL = widgets.Dropdown(layout=Layout(width='10%'), options=child_to_create.options, value=child_to_create.value,style=style)

        if child_to_create._view_name == 'ButtonView':
            #new_widgets_TL = widgets.Button(description=child_to_create.description + str(step[1]),
            #                                layout=child_to_create.layout,
            #                                style=child_to_create.style, icon=child_to_create.icon, button_style=child_to_create.button_style)
            new_widgets_TL = child_to_create # copy to keep button callback

            #print('copppppy button')
            #print(child_to_create.description)

        if child_to_create._view_name == 'HBoxView':
            child_to_create_children = []
            for childs in child_to_create.children:
                child_to_create_children.append(childs)

            new_widgets_TL = widgets.HBox(children=(child_to_create_children),style=style,layout=layout)

        if child_to_create._view_name == 'VBoxView':
            new_widgets_TL = widgets.VBox()

        if child_to_create._view_name == 'IntSliderView':
            new_widgets_TL = widgets.IntSlider(value=child_to_create.value,
                                                continuous_update=False, description='Choose the time step to display', max=3, min=1,style=style,layout=layout)

        if child_to_create._view_name == 'OutputView':
            new_widgets_TL = widgets.Output(layout=Layout(border='1px solid black'),style=style)

        if child_to_create._view_name == 'DatePickerView':
            new_widgets_TL = widgets.DatePicker(value=child_to_create.value, description='Datetime of measurement' + str(step[1]),
                layout=Layout(width='auto'), disabled=False, style=style)

        if child_to_create._view_name == 'SelectView':
            new_widgets_TL = FileChooser(use_dir_icons=True)

        if child_to_create._view_name == 'TextareaView':
            new_widgets_TL = Textarea(value=child_to_create.value, description='Short description of the dataset' + str(step[1]),
                            layout=Layout(display='flex', flex_flow='row',
                            justify_content='space-between', width='80%'),
                            style=style)
        if child_to_create._view_name == 'AccordionView':
            new_widgets_TL = None
            #self.TL_upload.append(FileChooser(use_dir_icons=True, title=child_to_create.title + str(step[0])))

        if child_to_create._view_name == 'IntTextView':
            new_widgets_TL = IntText(value=child_to_create.value, description=child_to_create.description + str(step[1]),
                            layout=Layout(display='flex', flex_flow='row', justify_content='space-between', width='80%'),
                            style=style)

        if child_to_create._view_name == 'FileUploadView':
            new_widgets_TL = FileUpload(description=child_to_create.description + str(step[1]),
                            multiple=True, layout=Layout(display='flex', flex_flow='row', justify_content='space-between', width='80%'),
                            style=style)

                                        #self.TL_upload.append(FileChooser(use_dir_icons=True, title=child_to_create.title + str(step[0])))
        #if child_to_create._view_name == 'GridBoxView':
            #print(child_to_create)

        return new_widgets_TL

    def create_TL_widgets_upload(self, child_to_create, step):
        newFileChooser = FileChooser(use_dir_icons=True, title=child_to_create.title + str(step[1]))
        #print('title upload')
        #print(child_to_create.title)

        return newFileChooser
        #elif '<b>Upload raw data</b>' in child_to_create.title:
            #tmpFileChooser.register_callback(REDA_explore_meta)
        #elif '<b>Upload figs</b>' in child_to_create.title:
            #tmpFileChooser.register_callback(self.REDA_explore_meta())


    def _add_TL_header_control(self):

        def rmv_children_all(change): # add children tabs to existing root tab
            print('rmv')
            self.TL_tab.close
            #self.TL_tab.close
            self.TL_tab =  widgets.VBox([self.accordion_tab_ERT])
            #self._create_TL_tabs()
            self.deleteAll.layout.display = 'none'
            self.vbox_tab_ERT.children = [self.TL_tab]


        #widget_add_tab = widgets.IntText(description='Add new tab')
        self.deleteAll = widgets.Button(icon="trash", description='Remove all TL tabs',button_style='danger')
        #deleteOne = widgets.Button(icon="trash", description='Remove selected TL tab')
        self.deleteAll.on_click(rmv_children_all)
        #deleteOne.on_click(rmv_children_tab)

        #self._nb_of_files_TL()
        self.widget_nb_files_TL.value = self.metadata['nb_of_files_TL']

        return  widgets.HBox([self.widget_nb_files_TL, self.deleteAll])


    def _add_children_TL(self): # add children tabs to existing root tab
        '''Loop over all the childrens and find all widgets to recreate them with a new index corresponding to the time step'''
        print('add children')
        vboxTL_min_req = [] # minimum required metadata (1st accordion)
        vboxTL_upload = [] # upload dataset  (2nd accordion)
        vboxTL_upload_supp = [] # upload supplementary files (3rd accordion)

        try:
            print('Existing TL tabs: ' + str(len(self.accordionTL)))
            print('self.vbox_tab_ERT.children')
            #print(self.vbox_tab_ERT.children.children)
            for i, child in enumerate(self.vbox_tab_ERT.children):
                for j, child in enumerate(child.children):
                    if j==0:
                        #print('child TEST')
                        #print(child.children)
                        child_min_req = child.children[0]
                        child_upload = child.children[1]
                        child_upload_supp = child.children[2]

        except:
            print('no time lapse tabs detected')
            #self.accordionTL = [] # merge all accordion
            self.accordionTL = [self.accordion_tab_ERT] # keep the background time
            self.TL_names = ['Background Time'] # names for tabs
            self.TL_tab = widgets.Tab() # create TL tabs
            for i, child in enumerate(self.vbox_tab_ERT.children):
                child_min_req = child.children[0]
                child_upload = child.children[1]
                child_upload_supp = child.children[2]


        def test_create(vec_append,child,step):
            """Short summary.

            Parameters
            ----------
            vec_append : type
                Description of parameter `vec_append`.
            child : type
                Description of parameter `child`.
            step : type
                Description of parameter `step`.

            Returns
            -------
            type
                Description of returned object.

            """
            print('-------')
            print(child)
            if hasattr(child,'selected'): # this is a upload widget
                tmpFileChooser = self.create_TL_widgets_upload(child,step)
                vec_append.append(tmpFileChooser)
            elif hasattr(child,'description'): # this is other type widgets
                new_widgets_TL = geo_metadata.create_TL_widgets(child,step)
                vec_append.append(new_widgets_TL)

            return vec_append

        for step in enumerate(np.arange(len(self.accordionTL),self.metadata['nb_of_files_TL'])): # tab nest = time lapse
            #print('stepnb: ' + str(step[1]))
            self.TL_names.append('step'+ str(step[1]))

            TL_min_req = []
            TL_upload = []
            TL_upload_supp = []

            # Loop over widgets of min req
            for i, child in enumerate(child_min_req.children):
                if hasattr(child,'selected'):
                    tmpFileChooser = self.create_TL_widgets_upload(child,step)
                    TL_min_req.append(tmpFileChooser)
                elif hasattr(child,'description'):
                    new_widgets_TL = geo_metadata.create_TL_widgets(child,step)
                    TL_min_req.append(new_widgets_TL)

            # Loop over widgets of upload
            for i, child in enumerate(child_upload.children):
                test_create(TL_upload,child,step)
                if hasattr(child,'children'):
                    for child2 in child.children:
                        test_create(TL_upload,child2,step)
                        if hasattr(child2,'children'):
                            for child3 in child2.children:
                                test_create(TL_upload,child3,step)

            # Loop over widgets of upload_supp
            for i, child in enumerate(child_upload_supp.children):
                test_create(TL_upload_supp,child,step)
                if hasattr(child,'children'):
                    for child2 in child.children:
                        test_create(TL_upload_supp,child2,step)
                        if hasattr(child2,'children'):
                            for child3 in child2.children:
                                test_create(TL_upload_supp,child3,step)
                                if hasattr(child3,'children'):
                                    for child4 in child3.children:
                                        test_create(TL_upload_supp,child4,step)


            vboxTL_min_req.append(widgets.VBox(TL_min_req))
            vboxTL_upload.append(widgets.VBox(TL_upload))
            vboxTL_upload_supp.append(widgets.VBox(TL_upload_supp))




            self.accordionTL.append(widgets.Accordion(children=[vboxTL_min_req[step[0]],
                                                                vboxTL_upload[step[0]],
                                                                vboxTL_upload_supp[step[0]]],
                                                            titles=('Min meta', 'Upload dataset', 'Supplementary material')))
            self.accordionTL[step[1]].set_title(index=0, title='Min meta')
            self.accordionTL[step[1]].set_title(index=1, title='Upload')
            self.accordionTL[step[1]].set_title(index=2, title='Related data ressources')

        #self.TL_head_control = self._add_TL_header_control() # To implement, header control for very large time lapse dataset (including a slider to select quickly)
        #intro_tl_resume = widgets.HTML('''
        #        not yet implemented; resume tab with map + interactive table showing imported data
        #     ''')

        #self.TL_head_control = self._add_TL_header_control() # To implement, header control for very large time lapse dataset (including a slider to select quickly)


        #self.vboxTL_resume = widgets.VBox([intro_tl_resume])
        #self.resume_tab.children = self.vboxTL_resume
        #[self.resume_tab.set_title(num,name) for num, name in enumerate(['resume'])]
        #self.TL_tab  = widgets.Tab(children = [self.accordionTL,
        #                               self.resume_tab])


        #self.TL_tab.children = [self.accordionTL,self.resume_tab]
        self.TL_tab.children = self.accordionTL
        [self.TL_tab.set_title(num,name) for num, name in enumerate(self.TL_names)]
        self._create_TL_tabs()

        #self.vbox_tab_ERT.children = [self.TL_tab,self.resume_tab]


        for step in enumerate(np.arange(len(self.accordionTL),self.metadata['nb_of_files_TL'])):
            print(step)
            print('step')
            self._observe_TL_tab_widgets(step)
            self._update_widget_export()


        def _observe_TL(change):
            print('obs TL --> switch to new TL tab observed')
            step_tab = change['new']
            self._observe_TL_tab_widgets(step_tab)
            self._update_widget_export()


        self.TL_tab.observe(_observe_TL,'selected_index')

        #for child in self.TL_tab.children:
        #    print(child)
        #    print('***')
        #    child.observe(_observe_TL,'selected_index')

        return self.vbox_tab_ERT.children



    def _remove_children_TL(self): # add children tabs to existing root tab
        print('remove children')
        #vboxTL_min_req = []
        #TL_upload = []
        #accordionTL = []
        #self.TL_tab = widgets.Tab()
        #TL_names = []



    def _widget_measurement_type(self):
        self.widget_measurement_type = widgets.RadioButtons(
            options=['Laboratory', 'Field'],
            #default='Field',
            value=None,
            description='Measurement type:',
            disabled=False,
            style=style,
            layout=layout)

        # set initial metadata
        # self.metadata['measurement_type'] = 'Field'

        def _observe_measurement_type(change):
            self.metadata['measurement_type'] = self.widget_measurement_type.value
            self._update_widget_export()

        self.widget_measurement_type.observe(_observe_measurement_type)
        return self.widget_measurement_type

    #%% ERT metadata: Time_measure/ Elec_conf/ Elec_spacing
    def _widgets_ERT_doc(self):
        title = widgets.HTML('''
                <h3> ERT metadata </h3>
                <hr style="height:1px;border-width:0;color:black;background-color:gray">
                <b> Minimum required metadata. </b>
                Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-ert-metadata">online ERT metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox

    def _widget_instrument_ERT(self):
        self.widget_instru_ERT = widgets.Text(
            description='Instrument ERT',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_instrument(change):
            self.metadata['instrument ERT'] = self.widget_instru_ERT.value
            self._update_widget_export()

        self.widget_instru_ERT.observe(_observe_instrument)
        return self.widget_instru_ERT


    def _widget_datetime_ERT(self):
        self.widget_date_ERT = widgets.DatePicker(
            description='Datetime of measurement ERT',
            disabled=False,
            style=style,
            layout=layout)

        def _observe_dt(change):
            date = self.widget_date_ERT.value
            if date is not None:
                self.metadata['date ERT'] = date.isoformat()
                self._update_widget_export()

        self.widget_date_ERT.observe(_observe_dt)
        return self.widget_date_ERT



    def _widget_time(self):
        widget_t = ipydatetime.TimePicker(
            description='Time of measurement',
            disabled=False
        )

        def _observe_t(change):
            time = widget_t.value
            if time is not None:
                self.metadata['time'] = time
                self._update_widget_export()

        widget_t.observe(_observe_t)
        return widget_t

    def _widget_elec_config(self):
        self.widget_elec_config = widgets.RadioButtons(
            options=['1D', '2D','3D'],
            #default='1D',
            value=None,
            description='Electrode configuration',
            disabled=False,
            style=style,
            layout=layout)


        #self.widget_elec_config.layout.display   = 'none'
        #if  self.metadata['method'] == 'Geoelectrical - ERT':
        #    elec_config.layout.display   = 'block'

        # set initial metadata
        # self.metadata['elec_config'] = '1D'

        def _observe_elec_config(change):
            self.metadata['elec_config'] = self.widget_elec_config.value
            self._update_widget_export()

        self.widget_elec_config.observe(_observe_elec_config)
        return self.widget_elec_config


    def _widget_ERT_more(self):

        # Data examples
        my_columns = list(['elecs_geom (upload .xyz ascii file'])
        df = pd.DataFrame(np.random.randint(0,100,size=(100, np.shape(my_columns)[0])), columns=my_columns)

        # Our filter generator
        def generate_filter(button):
            # Check if exist before creating
            new_widget = widgets.Text(description=select_definition.value,
            style=style,
            layout=layout)
            # Append created filter
            filters.children=tuple(list(filters.children) + [new_widget])
            choose_filter = widgets.HBox([select_definition, button, filters])

            @debounce(0.2)
            def _observe_filter(change):
                self.metadata[select_definition.value] = new_widget.value
                self._update_widget_export()

            new_widget.observe(_observe_filter)


        # Define Dropdown
        select_definition = widgets.Dropdown(options=my_columns, layout=Layout(width='10%'))

        button = widgets.Button(description="Add",
            style=style,
            layout=layout)
        # Define button and event
        button.on_click(generate_filter)

        # Where we will put all our filters
        filters = widgets.VBox()
        # Put Dropdown and button together
        add_filter = widgets.HBox([select_definition, button])
        choose_filter = widgets.VBox([add_filter, filters])

        return choose_filter


    def _widget_elec_seq(self):
        self.widget_elec_seq = widgets.RadioButtons(
            options=['Wenner', 'WS','user defined'],
            #default='WS',
            value=None,
            description='Electrode sequence',
            disabled=False,
            style=style,
            layout=layout)

        # set initial metadata
        # self.metadata['elec_seq'] = 'WS'

        def _observe_elec_seq(change):
            self.metadata['elec_seq'] = self.widget_elec_seq.value
            self._update_widget_export()

        self.widget_elec_seq.observe(_observe_elec_seq)
        return self.widget_elec_seq

    def _widget_elec_spacing(self):
        self.widget_elec_spacing = widgets.Text(
            description='Electrode spacing',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_widget_elec_spacing(change):
            self.metadata['elec_spacing'] = self.widget_elec_spacing.value
            self._update_widget_export()

        self.widget_elec_spacing.observe(_observe_widget_elec_spacing)
        return self.widget_elec_spacing

    def _widget_description_ERT(self):
        self.widget_description_ERT = widgets.Textarea(
            description='Short description of the dataset',
            style=style,
            layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%')
            )

        @debounce(0.2)
        def _observe_description_ERT(change):
            self.metadata['description_ERT'] = self.widget_description_ERT.value
            self._update_widget_export()

        self.widget_description_ERT.observe(_observe_description_ERT,'value')
        return self.widget_description_ERT

    def _widget_upload_ERT_doc(self):
        """upload ERT file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>REDA importer<h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''',
        layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%'))
        text = widgets.HTML('''
        Infer all the ERT metadata from the ERT dataset uploaded. Please refer to the <a href="https://github.com/geophysics-ubonn/reda"> REDA online doc</a>
        ''',
        layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%'))
        vbox = widgets.VBox([title, text],
                            layout=Layout(display='flex',flex_flow='row',justify_content='space-between',width='80%'))
        return vbox


    def REDA_explore_meta(self,name,step_tab):

        print('REDA harvester')

        #step_tab:
        #    name = self.ERT_upload.selected
        #else:
        #    name =
        path_abs , file = os.path.split(name)
        level_dir = 'Data'
        dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file


        #for name, file_info in self.fig_upload.value.items():
        #self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir=level_dir)
        #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Figures')
        if len(self.metadata['method'])<1:
            self._update_widget_log('<p style="color:red;">No method defined; impossible to copy file in the prjectdir hierarchical tree</p>')
        else:
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)
            self._update_widget_log(name + ' ERT file imported with REDA;')
            self._update_widget_log(name + 'file copied into: ' + self.metadata['method'] + '/' + level_dir)

        #self._add_to_Zip(self.ERT_upload.selected, target_dir='', level_dir='')
        #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Data')
        #self._add_to_dir(name, target_dir=self.metadata['method'], level_dir='Data')
        self.metadata['ERT_filename' + str(step_tab)] = dest_project_path

        self.ert = reda.ERT()

        if 'bin' in file:
            self.ert.import_syscal_bin(name)
        elif 'dat' in file:
            self.ert.import_pygimli(name)
        #self.metadata['print_log_REDA'] =   ert.print_log()
        self.metadata['nb_abmn'] =   str(len(self.ert.data))
        #print(str(len(self.ert.data)))
        if hasattr(self.ert.data, 'chargeability'):
            self.metadata['chargeability'+ str(step_tab)] =   True
        else:
            self.metadata['chargeability'+ str(step_tab)] =   False

        if len(self.ert.electrode_positions)>0:
            #print(self.ert.electrode_positions)
            self._update_widget_log('electrode positions detected from file upload')

        self._update_widget_export()

        #self._parse_json() # parse to metadata for export
        #self._update_fields_values(['print_log_REDA']) # parse to widgets to replace initial value
        self._update_fields_values(['nb_abmn'+ str(step_tab)]) # parse to widgets to replace initial value
        self._update_fields_values(['chargeability'+ str(step_tab)]) # parse to widgets to replace initial value


    def _widget_upload_ERT_button(self):
       """Import ERT dataset """

       vbox_doc = self._widget_upload_ERT_doc()

       #self.ERT_upload = widgets.FileUpload(
       #        accept='.bin',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #    )

       self.ERT_upload  = FileChooser(use_dir_icons=True)
       self.ERT_upload.title  = 'ERT Upload with REDA'
       vbox = widgets.VBox([vbox_doc,self.ERT_upload])

       def on_upload_ERT_change():
            self.REDA_explore_meta(self.ERT_upload.selected,'_background')

            #vbox.children = (*vbox.children, self._print_log_REDA())
            vbox.children = (*vbox.children, self._nb_of_ambn())
            vbox.children = (*vbox.children, self._ERT_chargeability())
            #vbox.children = (*vbox.children, self.button_display_table_box)
            #vbox.children = (*vbox.children, self._display_head_table())
            self._update_fields_values(['nb_abmn']) # parse to widgets to replace initial value
            self._update_fields_values(['chargeability']) # parse to widgets to replace initial value



       #self.ERT_upload.register_callback(on_upload_ERT_change)
       self.ERT_upload.register_callback(on_upload_ERT_change)


       return vbox

    def _display_head_table(self):

        button_display_table = widgets.Button(description="Show data table",button_style='info')
        delete = widgets.Button(icon="trash")
        out = widgets.Output(layout={'border': '1px solid black'})
        delete.parent = out
        self.button_display_table_box = widgets.HBox([button_display_table,delete])

        def display_df(button):

            with out:
                display(self.ert.data)

        display_head_table_box = widgets.VBox([self.button_display_table_box,out])
        button_display_table.on_click(display_df)

        def delete_btn_clicked(b):
            b.parent.layout.display = 'none'

        delete.on_click(delete_btn_clicked)


        return display_head_table_box


    def _print_log_REDA(self):
        self.widget_print_log_REDA = widgets.Text(
            description='Import processing Log REDA',
            style=style,
            layout=layout)
        def _observe_print_log_REDA(change):
            self.metadata['print_log_REDA'] = self.widget_print_log_REDA.value
            #self._update_widget_export()

        self.widget_print_log_REDA.observe(_observe_print_log_REDA)

        return self.widget_print_log_REDA


    def _nb_of_ambn(self):
        self.widget_nb_abmn = widgets.Text(
            description='Nb of abmn',
            style=style,
            layout=layout)

        def _observe_nb_of_abmn(change):
            self.metadata['nb_abmn'] = self.widget_nb_abmn.value
            #self._update_widget_export()

        self.widget_nb_abmn.observe(_observe_nb_of_abmn)

        return self.widget_nb_abmn

    def _ERT_chargeability(self):

        self.widget_ERT_chargeability = widgets.Select(
                            value='False',
                            description='Contains chargeability',
                            disabled=False,
                            options=['True','False'],
                            style=style,
                            layout=layout)

        def _observe_ERT_chargeability(change):
            self.metadata['ERT_chargeability'] = self.widget_ERT_chargeability.value
            #self._update_widget_export()

        self.widget_ERT_chargeability.observe(_observe_ERT_chargeability)

        return self.widget_ERT_chargeability

    def _widgets_ERT_add_file(self):


        #columns = list(['raw file','processed file'])
        #vbox_ERT_add_files = self._widget_add_external_ressource(columns,self.metadata['method'])
        vbox_ERT_add_files = self._widgets_related_external_resources_raw_doc('Geoelectrical - ERT')
        vbox_files = self._widgets_related_external_resources_files_doc('Geoelectrical - ERT')
        vbox_figs = self._widgets_related_external_resources_fig_doc('Geoelectrical - ERT')
        vbox_codes = self._widgets_related_external_resources_codes_doc('Geoelectrical - ERT')

        vbox = widgets.VBox([vbox_files,vbox_ERT_add_files,vbox_figs,vbox_codes])

        return vbox


    #%% EM metadata
    def _widgets_EM_doc(self):
        title = widgets.HTML('''
            <h3> EM metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            <b> Minimum required metadata. </b>
            Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-em-metadata">online EM metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox


    # Date_measure

    def _widget_instrument_EM(self):
        self.widget_instru_EM = widgets.Text(
            description='Instrument EM',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_instrument(change):
            self.metadata['instrument EM'] = self.widget_instru_EM.value
            self._update_widget_export()

        self.widget_instru_EM.observe(_observe_instrument)
        return self.widget_instru_EM


    def _widget_datetime_EM(self):
        self.widget_date_EM = widgets.DatePicker(
            description='Datetime of measurement EM',
            disabled=False,
            style=style,
            layout=layout)

        def _observe_dt(change):
            date = self.widget_date_EM.value
            if date is not None:
                self.metadata['date EM'] = date.isoformat()
                self._update_widget_export()

        self.widget_date_EM.observe(_observe_dt)
        return self.widget_date_EM


    def _widget_coil_config(self):
        self.widget_coil_config = widgets.SelectMultiple(
            options=['VCP', 'VMD','PRP', 'HCP', 'HMD'],
            default='VCP',
            description='Coil orientation',
            disabled=False,
            style=style,
            layout=layout)

        # set initial metadata
        # self.metadata['coil_spacing'] = 'VCP'

        def _observe_coil_config(change):
            self.metadata['coil_config'] = self.widget_coil_config.value
            self._update_widget_export()

        self.widget_coil_config.observe(_observe_coil_config)
        return self.widget_coil_config


    def _widget_coil_height(self):
        self.widget_coil_height = widgets.Text(
            description='Height of the instrument above the ground [m]',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_coil_height(change):
            self.metadata['coil_height'] = self.widget_coil_height.value
            self._update_widget_export()

        self.widget_coil_height.observe(_observe_coil_height)
        return self.widget_coil_height

    def _widget_coil_spacing(self):
        self.widget_coil_spacing = widgets.Text(
            options=['0.2', '1','3'],
            description='Coil spacing',
            disabled=False,
            style=style,
            layout=layout)

        # set initial metadata
        # self.metadata['coil_spacing'] = 'VCP'

        def _observe_coil_spacing(change):
            self.metadata['coil_spacing'] = self.widget_coil_spacing.value
            self._update_widget_export()

        self.widget_coil_spacing.observe(_observe_coil_spacing)
        return self.widget_coil_spacing

    def _widget_description_EM(self):
        self.widget_description_EM = widgets.Textarea(
            description='Short description of the dataset',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_description_EM(change):
            self.metadata['description_EM'] = self.widget_description_EM.value
            self._update_widget_export()

        self.widget_description_EM.observe(_observe_description_EM)
        return self.widget_description_EM

    def _widget_upload_EM_doc(self):
        """upload EM file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>Emagpy importer<h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
        text = widgets.HTML('''
        Infer all the EM metadata from the EM uploaded. Please refer to the <a href="https://gitlab.com/hkex/emagpy"> Emagpy online doc</a>
        ''')

        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_EM_button(self):
       """Import EM dataset """

       vbox_doc = self._widget_upload_EM_doc()

       #self.EM_upload = widgets.FileUpload(
       #        accept='.csv',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #   )

       self.widget_em_file = FileChooser(use_dir_icons=True)
       self.widget_em_file.filter_pattern = '*.csv'
       self.widget_em_file.title = '<b>EM_upload</b>'
       #        accept='.csv',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #    )



       vbox = widgets.VBox([vbox_doc,self.widget_em_file])


       def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.widget_em_file.selected
            path_abs , file = os.path.split(name)
            level_dir = 'Data'
            dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file


            #self.widget_em_file = self.EM_upload.selected
            #self._add_to_Zip(name, target_dir= self.metadata['method'], level_dir='Emagpy_import')
            self._add_to_Zip(self.widget_em_file.selected, target_dir= self.metadata['method'], level_dir='Emagpy_import')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Data')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)

            self._update_widget_log('EM file imported for automatic metadata extraction')
            self.metadata['em_file'] = dest_project_path

            k = Problem() # this create the main object
            k.createSurvey(name) # this import the data
            k.invert(forwardModel='CS') # specify the forward model (here the Cumulative Sensitivty of McNeil1980)
            k.showResults() # display the section

            k.coils
            k.freqs
            k.hx
            k.cspacing
            self.metadata['coil_spacing'] =   ';'.join(map(str, k.cspacing))

            self._update_widget_export()
            #self._parse_json() # parse to metadata for export
            self._update_fields_values(['coil_spacing']) # parse to widgets to replace initial value

       #self.EM_upload.observe(on_upload_change, names='_counter')
       self.widget_em_file.register_callback(on_upload_change)


       return vbox

#    def _widgets_EM_add_file(self):


#        columns = list(['raw file','processed file'])
#        vbox_EM_add_files = self._widget_add_external_ressource(columns,self.metadata['method'])
#
#        vbox_files = self._widgets_related_external_resources_files_doc()
#        vbox_figs = self._widgets_related_external_resources_fig_doc()
#        vbox_codes = self._widgets_related_external_resources_codes_doc()

#        vbox = widgets.VBox([vbox_files,vbox_EM_add_files,vbox_figs,vbox_codes])

#        return vbox


    #%% DATA QUALITY ASSESSEMENT metadata
    def _widgets_quality_doc(self):
        title = widgets.HTML('''
            <h3> Quality metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-data-quality-assessment-metadata">online quality metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox


    def _widget_peer_reviewed(self):
        self.widget_peer_reviewed = widgets.Text(
            description='Peer reviewed',
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_peer_reviewed(change):
            self.metadata['peer_reviewed'] = self.widget_peer_reviewed.value
            self._update_widget_export()

        self.widget_peer_reviewed.observe(_observe_peer_reviewed)
        return self.widget_peer_reviewed


    def _widget_peer_reviewer_contact(self):
        self.widget_peer_reviewer_contact = widgets.Text(
            description='Peer reviewer contact',
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_peer_reviewer_contact(change):
            self.metadata['peer_reviewer_contact'] = self.widget_peer_reviewer_contact.value
            self._update_widget_export()

        self.widget_peer_reviewer_contact.observe(_observe_peer_reviewer_contact)
        return self.widget_peer_reviewer_contact


    def _widget_replicate_datasets(self):
        self.widget_replicate_datasets = widgets.Text(
            description='Replicate datasets',
            style={'description_width': 'initial'}
        )


        @debounce(0.2)
        def _observe_replicate_datasets(change):
            self.metadata['replicate_datasets'] = self.widget_replicate_datasets.value
            self._update_widget_export()

        self.widget_replicate_datasets.observe(_observe_replicate_datasets)
        return self.widget_replicate_datasets


    def _widget_comparison_ref_data(self):
        self.widget_comparison_ref_data = widgets.Text(
            description='Comparison ref data',
            style={'description_width': 'initial'}
        )


        @debounce(0.2)
        def _observe_comparison_ref_data(change):
            self.metadata['comparison_ref_data'] = self.widget_comparison_ref_data.value
            self._update_widget_export()

        self.widget_comparison_ref_data.observe(_observe_comparison_ref_data)
        return self.widget_comparison_ref_data


    def _widget_ref_data(self):
        self.widget_ref_data = widgets.Text(
            description='ref data',
            style={'description_width': 'initial'}
        )


        @debounce(0.2)
        def _observe_ref_data(change):
            self.metadata['ref_data'] = self.widget_ref_data.value
            self._update_widget_export()

        self.widget_ref_data.observe(_observe_ref_data)
        return self.widget_ref_data

    def _widget_free_quality(self):
        self.widget_free_quality = widgets.Text(
            description='Free quality metadata to add',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_free_quality(change):
            self.metadata['free_quality'] = self.widget_free_quality.value
            self._update_widget_export()

        self.widget_free_quality.observe(_observe_free_quality)
        return self.widget_free_quality


    #%% SAMPLING
    def _widgets_sampling_doc(self):
        title = widgets.HTML('''
            <h3> Sampling metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-sampling">online sampling metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox

    def _widget_free_sampling(self):
        self.widget_free_sampling = widgets.Text(
            description='Free sampling metadata to add',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_free_sampling(change):
            self.metadata['free_sampling'] = self.widget_free_sampling.value
            self._update_widget_export()

        self.widget_free_sampling.observe(_observe_free_sampling)
        return self.widget_free_sampling


    #%% Dataset structure
    def _widgets_dataset_structure_doc(self):
        title = widgets.HTML('''
            <h3> Dataset structure </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            Please refer to the <a href="https://agrogeophy.github.io/datasets/data-management.html#workflow-for-preparing-dataset">online guidelines to structure a dataset </a>
             ''')
        vbox = widgets.VBox([title])

        return vbox

    def _widgets_related_external_resources_files_doc(self):
        title = widgets.HTML('''
            <h4> Files </h4>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')
        vbox = widgets.VBox([title])
        return vbox


    def _widgets_related_external_resources_raw_doc(self):
        title = widgets.HTML('''
            <h4> Raw data </h4>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        vbox_rawdata = self._widget_upload_rawdata_button(self.metadata['method'])

        vbox = widgets.VBox([title,vbox_rawdata])
        return vbox

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

    def _widget_upload_suppdata_buttons(self,method_str):
        """Import raw dataset file """


        self.raw_upload = widgets.FileUpload(
               accept='',  # Accepted file extension
               multiple=True  # True to accept multiple files upload else False
           )

        self.prepro_upload = widgets.FileUpload(
               accept='',  # Accepted file extension
               multiple=True  # True to accept multiple files upload else False
           )

        self.models_upload = widgets.FileUpload(
               accept='',  # Accepted file extension
               multiple=True  # True to accept multiple files upload else False
           )

        self.postpro_upload = widgets.FileUpload(
               accept='',  # Accepted file extension
               multiple=True  # True to accept multiple files upload else False
           )

        box_supp_data = widgets.HBox([self.raw_upload,self.prepro_upload,self.models_upload,self.postpro_upload])

        return box_supp_data

    def _widget_upload_rawdata_button(self,method_str):
       """Import raw dataset file """


       #self.fig_upload = widgets.FileUpload(
       #        accept='',  # Accepted file extension
       #        multiple=True  # True to accept multiple files upload else False
       #    )
       self.rawdata_upload = FileChooser(use_dir_icons=True)
       self.rawdata_upload.title = '<b>Upload raw data</b>'

       vbox = widgets.VBox([self.rawdata_upload])


       def on_upload_change():
            name =  self.rawdata_upload.selected
            #for name, file_info in self.fig_upload.value.items():
            self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir='RAW')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Figures')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir='RAW')
            self._update_widget_log(name + 'file copied into: ' + method_str + '/' + 'RAW zip folder')
            self.metadata['external_ressource_' + method_str + '_RAW'] = name
            self._update_widget_export()

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

       #self.fig_upload.observe(on_upload_change, names='_counter')
       self.rawdata_upload.register_callback(on_upload_change)

       return vbox


    def actions_upload_supp_data(self,name,step_tab,level_dir):

        print('actions_upload_supp_data')

        path_abs , file = os.path.split(name)
        dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file


        #for name, file_info in self.fig_upload.value.items():
        #self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir=level_dir)
        #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Figures')
        if len(self.metadata['method'])<1:
            self._update_widget_log('<p style="color:red;">No method defined; impossible to copy file in the prjectdir hierarchical tree</p>')
        else:
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)
            self._update_widget_log(name + str(step_tab) + ' file uploaded;')
            self._update_widget_log(name + str(step_tab) + 'file copied into: ' + self.metadata['method'] + '/' + level_dir)

        #self._add_to_Zip(self.ERT_upload.selected, target_dir='', level_dir='')
        #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Data')
        #self._add_to_dir(name, target_dir=self.metadata['method'], level_dir='Data')
        self.metadata[level_dir + '_filename' + str(step_tab)] = dest_project_path
        self._update_widget_export()


    def _widget_add_external_ressource(self, my_columns, method_str):

        # Data examples
        # my_columns = list(['field picture', 'post processing figure', 'rawdata'])
        df = pd.DataFrame(np.random.randint(0,100,size=(100, np.shape(my_columns)[0])), columns=my_columns)

        # Our filter generator
        def generate_filter(button):
            # Check if exist before creating
            widget_name = method_str + select_definition.value
            new_widget = widgets.Text(description=select_definition.value) # Value from the user

            new_upload = widgets.FileUpload(
                   accept='.png',  # Accepted file extension
                   multiple=True  # True to accept multiple files upload else False
               )

            vbox = widgets.HBox([new_upload])
            # Append created filter
            filters.children=tuple(list(filters.children) + [new_widget] + [new_upload])
            choose_filter = widgets.HBox([select_definition, button, filters])

            @debounce(0.2)
            def _observe_filter(change):
                self.metadata[select_definition.value] = new_widget.value
                self._update_widget_export()

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

            new_widget.observe(_observe_filter)

            def on_upload_change(change):
                for name, file_info in new_upload.value.items():
                    self._add_to_Zip(name,target_dir=method_str,level_dir=select_definition.value)
                    self._update_widget_log(name + 'file copied into: ' + method_str + '/' + select_definition.value + ' zip folder')
                    self.metadata['external_ressource ' + new_widget.value] = name
                    self._update_widget_export()

                # self._parse_json() # parse to metadata for export
                # self._update_fields_values() # parse to widgets to replace initial valus

            new_upload.observe(on_upload_change, names='_counter')



        # Define Dropdown
        select_definition = widgets.Dropdown(options=my_columns, layout=Layout(width='10%'))

        button = widgets.Button(description="Add")

        # Define button and event
        button.on_click(generate_filter)

        # Where we will put all our filters
        filters = widgets.VBox()
        # Put Dropdown and button together
        add_filter = widgets.HBox([select_definition, button])
        choose_filter = widgets.VBox([add_filter, filters])

        return choose_filter


    def _widgets_related_external_resources_fig_doc(self):
        title = widgets.HTML('''
            <h4> Figures </h4>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        #vbox_figs = self._widget_upload_fig_button(self.metadata['method'])
        vbox_figs = self._widget_upload_fig_button('')

        vbox = widgets.VBox([title,vbox_figs])
        return vbox

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

    def _widget_upload_fig_button(self,method_str):
       """Import EM dataset """


       #self.fig_upload = widgets.FileUpload(
       #        accept='',  # Accepted file extension
       #        multiple=True  # True to accept multiple files upload else False
       #    )
       self.fig_upload = FileChooser(use_dir_icons=True)
       self.fig_upload.filter_pattern = '*.png'
       self.fig_upload.title = 'Upload figs'


       vbox = widgets.VBox([self.fig_upload])


       def on_upload_change():


            name = self.fig_upload.selected
            path_abs , file = os.path.split(name)
            level_dir = 'Postprocessed'
            dest_project_path = 'projectdir' + '\\' + self.metadata['method'] + '\\' + level_dir + '\\' +  file


            #for name, file_info in self.fig_upload.value.items():
            #self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir=level_dir)
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Figures')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir=level_dir)
            self._update_widget_log(name + 'file copied into: ' + method_str + '/' + 'Postprocessed folder')
            self.metadata['external_ressource_' + method_str + '_fig'] = dest_project_path
            self._update_widget_export()

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

       #self.fig_upload.observe(on_upload_change, names='_counter')
       self.fig_upload.register_callback(on_upload_change)


       return vbox


    def _widgets_related_external_resources_codes_doc(self):
        title = widgets.HTML('''
            <h4> Code scripts </h4>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        #vbox_codes = self._widget_upload_codes_button(self.metadata['method'])
        vbox_codes = self._widget_upload_codes_button('')

        vbox = widgets.VBox([title,vbox_codes])
        return vbox

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

    def _widget_upload_codes_button(self,method_str):
       """Import codes files """

       self.codes_upload = FileChooser(use_dir_icons=True)

       #self.codes_upload = widgets.FileUpload(
       #        accept='',  # Accepted file extension
       #        multiple=True  # True to accept multiple files upload else False
       #    )

       vbox = widgets.VBox([self.codes_upload])


       def on_upload_codes_change(change):

            #for name, file_info in self.codes_upload.value.items():
            name = self.codes_upload.selected
            self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir='scripts')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Scripts')
            self._add_to_dir(name, target_dir=self.metadata['method'], level_dir='Scripts')
            self._update_widget_log(name + 'file copied into: ' + method_str + '/' + 'scripts zip folder')
            self.metadata['external_ressource_' + method_str + '_codes'] = name
            self._update_widget_export()

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

       #self.codes_upload.register_callback(on_upload_change, names='_counter')
       self.codes_upload.register_callback(on_upload_codes_change)


       return vbox


    def _observe_TL_tab_widgets(self,step_tab=[]):
        ''' apply observe/onclick/callback to TL widgets'''

        def on_upload_TL_change(chooser):
            ''' Apply callback to the chooser '''
            print('Apply callback to the chooser')
            #self._add_to_Zip(self.tmp_name_upload,target_dir=self.metadata['method'],level_dir='scripts')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Scripts')
            name =  chooser.selected
            #self._add_to_dir(name, target_dir=self.metadata['method'], level_dir='Scripts')
            #self._update_widget_log(name + 'file copied into: ' + self.metadata['method'] + '/' + str(chooser.title))
            #self.metadata[chooser.title] = name
            #self._update_widget_export()
            print(chooser)
            if 'Upload raw data' in chooser.title:
                #print('ERT Upload with REDA child_to_create')
                level_dir= 'RAW'
                self.actions_upload_supp_data(name,step_tab,level_dir)

            if 'ERT Upload with REDA' in chooser.title:
                print('ERT Upload with REDA child_to_create')
                self.REDA_explore_meta(name,step_tab)
            return



        def on_click_TL_change(change):
            ''' Apply on_click to the button'''
            print('Apply on_click to the button')
            #self._add_to_Zip(self.tmp_name_upload,target_dir=self.metadata['method'],level_dir='scripts')
            #self._add_to_Exdir(name, target_dir=self.metadata['method'], level_dir='Scripts')
            #print(change)
            if 'Show on map lapse' in change.description:
                print('Show on map lapse callback')
                out = widgets.Output(description='out space map')
                #clear_output()
                display(self.m_top)
            if 'Show data table' in change['owner'].description:
                print('show data table')
            return



        def on_TL_tab_change(change):
            ''' Apply observe to the widget'''
            print('Apply observe to the widget')
            try:
                print(change['owner'].description)
                print('+++++')
            except:
                pass
            try:
                print(change['owner'].description)
                print('-------')
                if 'Date' in change['owner'].description:
                    print('change to date format')
                    self.metadata[change['owner'].description] = change['owner'].value.isoformat()
                else:
                    self.metadata[change['owner'].description] = change['owner'].value
                    print(self.metadata[change['owner'].description])
                    self._update_widget_export()
            except:
                print('no sucess')
                pass


        # loop over all the children
        for child in self.TL_tab.children:
            child.observe(on_TL_tab_change,'selected_index')

            if hasattr(child,'children'):
                for child_2 in child.children: # 1st/second accordion
                    #print('+++++')
                    #print(child_2)
                    if hasattr(child_2, 'title'):
                        child_2.register_callback(on_upload_TL_change)
                    elif hasattr(child_2, 'button_style'):
                        child_2.on_click(on_click_TL_change)
                    else:
                        child_2.observe(on_TL_tab_change,'value')

                    if hasattr(child_2,'children'):
                        for child_3 in child_2.children: # 1st/second accordion
                            #print('------')
                            #print(child_3)
                            if hasattr(child_3, 'title'):
                                #print(child_3)
                                child_3.register_callback(on_upload_TL_change)
                            elif hasattr(child_3, 'button_style'):
                                child_3.on_click(on_click_TL_change)
                            else:
                                child_3.observe(on_TL_tab_change,'value')

                        if hasattr(child_3,'children'):
                            for child_4 in child_3.children: # 1st/second accordion
                                #print('......')
                                #print(child_4)
                                if hasattr(child_4, 'title'):
                                    child_4.register_callback(on_upload_TL_change)
                                elif hasattr(child_4, 'button_style'):
                                    child_4.on_click(on_click_TL_change)
                                else:
                                    child_4.observe(on_TL_tab_change,'value')

                            if hasattr(child_4,'children'):
                                for child_5 in child_4.children: # 1st/second accordion
                                    #print('iiiiii')
                                    #print(child_5)
                                    if hasattr(child_5, 'title'):
                                        child_5.register_callback(on_upload_TL_change)
                                    elif hasattr(child_5, 'button_style'):
                                        child_5.on_click(on_click_TL_change)
                                    else:
                                        child_5.observe(on_TL_tab_change,'value')

            else:
                if hasattr(child, 'title'):
                    child.register_callback(on_upload_TL_change)
                if hasattr(child, 'button_style'):
                    child.on_click(on_click_TL_change)
                else:
                    child.observe(on_TL_tab_change,'value')



    def _create_TL_tabs(self):
        print('_create_TL_tabs')

        # need here to select the right tab ERT/EM

        # if ERT tab
        #self.vbox_tab_ERT.children = [self.TL_head_control,self.TL_tab]
        #self.resume_tab = widgets.Tab() # create TL tabs
        self.vbox_tab_ERT.children = [self.TL_tab]

        # if EM tab
        #self.vbox_tab_EM.children = [self.TL_head_control,self.TL_tab]


        return self.vbox_tab_ERT

    def _widget_export(self):
        """Preview of metadata export"""

        self.export = widgets.HTML()
        self.export_type = widgets.RadioButtons(
            options=['JSON', 'XML'],
            default='JSON',
            description='Export type:'
        )


        vbox = widgets.VBox(
            [
                widgets.HTML('''
                    <h4>Preview of metadata export:</h4>
                    <hr style="height:1px;border-width:0;color:black;background-color:gray">
                    '''),
                self.export_type,
                self.export
            ]
        )


        def _observe_export_type(change):
            self._update_widget_export()

        self.export_type.observe(_observe_export_type)
        #print(self.export)
        return vbox



    def export_metadata_to_json_str(self):
        """Generate a string representation of the metadata"""
        #print('dkjdijdi')
        #print(self.metadata)
        metadata_json_raw = json.dumps(self.metadata, indent=4)
        return metadata_json_raw

    def export_metadata_to_xml_str(self):
        xml = dicttoxml.dicttoxml(self.metadata)
        dom = dicttoxml.parseString(xml)
        metadata_xml = dom.toprettyxml()
        return metadata_xml

    def _update_widget_export(self):
        #print('update project export')
        if self.export_type.value == 'JSON':
            metadata_str = self.export_metadata_to_json_str()
        else:
            metadata_str = self.export_metadata_to_xml_str()
        # self.widget_export.value = metadata_str
        self.export.value = "<pre>{}</pre>".format(
            html.escape(metadata_str))



    def _widgets_HDF5_doc(self):
        title = widgets.HTML('''
            <h4> HDF5 data container (Not yet implemented) </h4>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        vbox = widgets.VBox([title])
        return vbox


    def _widget_upload_json(self):
        """upload json file and parse values
        """


        title = widgets.HTML(
            '''<h3>Upload pre-existing metadata json file<h3/>
               <hr style="height:1px;border-width:0;color:black;background-color:gray">
                <h4> Tips </h4>
                <p> Keep track of your datasets structure/metadata during every stages i.e. acquisition/processing/publication:
                Use the import/export tabs respectively to import a pre-existing JSON file and save your work <p>
                <h4> Metadata templates </h4>
                <p> Metadata templates for generic survey to upload are available on the github page.
                If you require additionnal metadata, please let us know by opening an issue <a href="https://github.com/agrogeophy/geometadp" target="_blank">on github</a>.
                </p>

            ''')
        text = widgets.HTML('''
        <b> Action of importing </b>: replace all the field by the uploaded json fields; if a metadata name is not matching it is indicated in the logger.
        ''')
        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_from_db(self):
        """upload csv file from github db
        """
        title = widgets.HTML(
            '''<h3>Upload json file<h3/>
               <hr style="height:1px;border-width:0;color:black;background-color:gray">


                <h4> Metadata templates </h4>
                <p> Metadata templates for generic survey to upload are available on the github page.
                If you require additionnal metadata, please let us know by opening an issue <a href="https://github.com/agrogeophy/geometadp" target="_blank">on github</a>.
                </p>

            ''')

        df = pd.read_csv(
            'https://raw.githubusercontent.com/agrogeophy/catalog/master/db.csv')
        #df = df.drop(df.columns[[0]], axis=1)

        df['contribution_type'].unique().tolist()

        textbox = widgets.Dropdown(
            description='instrument:   ',
            options=df['contribution_type'].unique().tolist(),
            disabled=False
        )

        out = widgets.Output(layout={'border': '1px solid black'})
        delete.parent = out
        self.button_display_table_box = widgets.HBox([button_display_table,delete])

        #display_head_table_box = widgets.VBox([self.button_display_table_box,container_head_table])
        #display_head_table_box = widgets.VBox([self.button_display_table_box,container_head_table])

        def display_df(button):

            with out:
                display(self.ert.data)

        #output_db =
        #display(df)
        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_button(self):
       """Import pre-existing JSON file"""

       #self.json_upload = widgets.FileUpload(
       #        accept='',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #    )

       #vbox = widgets.VBox([self.json_upload])

       self.json_upload = FileChooser(use_dir_icons=True)
       self.json_upload.title = '<b>Import template/backup JSON</b>'

       vbox = widgets.VBox([self.json_upload])


       def on_upload_change(change):
            #for name, file_info in self.json_upload.value.items():
            name = self.json_upload.selected
            with open(name) as json_file:
                    self.data_uploaded = json.load(json_file)

            self._update_fields_values_JSON()

       self.json_upload.register_callback(on_upload_change)


       return vbox

    def _update_fields_values(self,metadata_key):
        """Update all fields after data metadata harvester call (REDA/Emagpy)"""
        for i in enumerate(metadata_key):
            if hasattr(self, 'widget_' + i[1]):
               widget2fill = eval('self.widget_' + i[1])
               if "date" in i[1]:
                    date_time_obj = datetime.strptime(self.metadata[i[1]],  "%Y-%m-%d")
                    widget2fill.value = date_time_obj
               else:
                    try:
                        widget2fill.value = self.metadata[i[1]]
                    except:
                        pass

                    try:
                        metadata_tuple = tuple(map(int, i[1].split('; ')))
                        #print(metadata_tuple)
                        widget2fill.value = metadata_tuple
                    except:
                        pass



    def _update_fields_values_JSON(self):
        """Update all fields after uploading JSON file"""
        json_tmp = json.dumps(self.data_uploaded, indent=0)
        print(json_tmp)
        #print('self.metadata')
        #print(self.metadata)
        mylist = json.loads(json_tmp)
        for i in enumerate(mylist):
            print(i)
            if hasattr(self, 'widget_' + i[1]): # existing widget
               widget2fill = eval('self.widget_' + i[1])
               if "date" in i[1]:
                    date_time_obj = datetime.strptime(self.data_uploaded[i[1]],  "%Y-%m-%d")
                    widget2fill.value = date_time_obj
               elif "file" in i[1]:
                    path , file = os.path.split(self.data_uploaded[i[1]])
                    widget2fill.reset(path=path, filename=file)
               else:
                    try:
                        widget2fill.value = self.data_uploaded[i[1]]
                    except:
                        pass

                    try: # for multiple selection (such as coil orientation)
                        metadata_tuple = tuple(map(int, i[1].split('; ')))
                        widget2fill.value = metadata_tuple
                    except:
                        pass
            else: # fill optionnal/timelapse metadata; create them first
                if "nb_of_files_TL" in i[1]:
                    print(i)
                    self.metadata['nb_of_files_TL']= int(mylist['nb_of_files_TL'])
                    #print(self.metadata['nb_of_files_TL'])
                    #print(mylist['nb_of_files_TL'])
                     #print(i[0])
                     #print(i[1])
                     #print('***')
                    #self._update_widget_export() # ???
                    #self._prepare_widgets()
                    self._add_children_TL()
                    self._observe_TL_tab_widgets() # before
                    self._update_fields_values_TL()
                    self._observe_TL_tab_widgets() # after
                    #self.widget_EM.append(self._timelapse_option())
                    #self._update_widget_export() # ???
                    self._update_widget_export() # ???
                    #self._timelapse_option(reloadJSON=True)
                #print('eval')
                #print('self._' + i[1] + '()')
                #eval('self._' + i[1] + '()')



    def _update_fields_values_TL(self):
        """Update all fields from TL"""

        json_tmp = json.dumps(self.data_uploaded, indent=0)
        mylist = json.loads(json_tmp)
        for i in enumerate(mylist):

            for child in self.TL_tab.children:
                if hasattr(child,'children'):
                    for child_2 in child.children: # 1st/second accordion
                        #print('+++++')
                        #print(child_2)
                        if hasattr(child_2,'description'):
                            if i[1] in child_2.description:
                                #print('!.....!')
                                #print(i[1],child_2nd.description)
                                child_2.value = mylist[child_2.description]
                            break

                        if hasattr(child_2,'children'):
                            for child_3 in child_2.children: # 1st/second accordion
                                #print('------')
                                #print(child_3)
                                if hasattr(child_3,'description'):
                                    if i[1] in child_3.description:
                                        #print('!.....!')
                                        #print(i[1],child_3.description)
                                        child_3.value = mylist[child_3.description]
                                    break

                            if hasattr(child_3,'children'):
                                for child_4 in child_3.children: # 1st/second accordion
                                    if hasattr(child_4,'description'):
                                        if i[1] in child_4.description:
                                            #print('!.....!')
                                            #print(i[1],child_4.description)
                                            child_4.value = mylist[child_4.description]
                                        break

                                if hasattr(child_4,'children'):
                                    for child_5 in child_4.children: # 1st/second accordion
                                        if hasattr(child_5,'description'):
                                            if i[1] in child_5.description:
                                                #print('!.....!')
                                                #print(i[1],child_5.description)
                                                child_5.value = mylist[child_5.description]
                                            break

                                    if hasattr(child_5,'children'):
                                        for child_6 in child_5.children: # 1st/second accordion
                                            if hasattr(child_6,'description'):
                                                if i[1] in child_6.description:
                                                    #print('!.....!')
                                                    #print(i[1],child_6.description)
                                                    child_6.value = mylist[child_6.description]
                                                break

                else:
                    if hasattr(child,'description'):
                        if i[1] in child.description:
                            #print('!.....!')
                            #print(i[1],child.description)
                            child.value = mylist[child.description]
                        break




    def _parse_json_old(self):
        """Fill out metadata container (for export)"""
        for i in enumerate(self.data_uploaded):
            if hasattr(self, 'widget_' + i[1]):
                self.metadata[i[1]] = self.data_uploaded[i[1]]
            else:
                warning = '<p style="color:red;">metadata not matching: + str(i[1])</p>'
                self._update_widget_log(warning)

    #def _parse_json(self,metadata_key):
    #    """Fill out metadata container (for export)"""
    #        self.metadata[metadata_key] =
            #warning = '<p style="color:red;">metadata not matching: + str(i[1])</p>'
            #self._update_widget_log(warning)


    def _widget_download_buttons(self):
        """Download JSON file"""

        self.download = widgets.Button(
                value=False,
                description='Save',
                disabled=False,
                button_style='danger', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='This action will overwrite the json file if already existing',
                icon='save' # (FontAwesome names without the `fa-` prefix)
            )

        metadata_json_raw = json.dumps(self.metadata, indent=4)
        # write tmp json file


        vbox_button = widgets.VBox([self.download])
        json_backup_file = widgets.Text(description='backup name',
                                        value= 'backup' +
                                                datetime.now().strftime("%d%m%Y_%H%M%S")
                                                + '.json') # Value from the user
        vbox = widgets.HBox([vbox_button,json_backup_file])


        def on_download_change(change): # read an display
            #with open(vbox_file_save_name.value, 'w') as outfile:
            #    json.dump(self.metadata, outfile)
            # link2file = FileLink(r'json_backup.json')
            # linkwidget = widgets.HTML(
            #            value="<a href={code}>link2file to click</a>".format(code=link2file),
            #            description='Some HTML',
            # )
            with open(json_backup_file.value, 'w') as outfile:
                json.dump(self.metadata, outfile, indent=4)
            if not os.path.exists(self.projectdir_path + '\projectdir'):
                os.makedirs(self.projectdir_path + '\projectdir')

            #shutil.move(vbox_file_save_name.value,'projectdir')
            shutil.move(os.path.join(self.projectdir_path, json_backup_file.value),
            os.path.join(self.projectdir_path + '\projectdir', json_backup_file.value))

            self._update_widget_log(json_backup_file.value + ' file copied into projectdir folder')
            self._display_dir_tree()
            #self._add_to_Zip(vbox_file_save_name.value,'','')
            #self._add_to_Exdir(vbox_file_save_name.value,'','')
            #self._add_to_dir(vbox_file_save_name.value,'','')


             #vbox_link = widgets.HBox([vbox,linkwidget])

        self.download.on_click(on_download_change)

        return vbox


    def _add_to_dir(self,src_fpath,target_dir,level_dir):
        """_add_to_dir
        """
        if not os.path.exists('projectdir'):
            os.makedirs('projectdir')

        dest_fpath = 'projectdir' + '\\' + target_dir + '\\' + level_dir + '\\' +  os.path.basename(src_fpath)

        os.makedirs(os.path.dirname(dest_fpath), exist_ok=True)
        shutil.copy(src_fpath, dest_fpath)

        self._display_dir_tree()


    def _add_to_Exdir(self,name,target_dir,level_dir):
        """_add_to_Exdir
        """
        experiment = exdir.File("project.exdir")
        group = experiment.require_group(level_dir)
        #print(group.path)
        #data = np.arange(10)
        #dataset = group.require_dataset(target_dir, data=data)
        #group.attrs["room_number"] = 1234
        #dataset.attrs["recoring_date"] = "2018-02-04"


    def _add_to_Zip(self,filename, target_dir, level_dir):

        try:
            z = zipfile.ZipFile("project.zip", 'r')
        except:
            z = zipfile.ZipFile("project.zip", 'w')
            z.close()

        path = target_dir + '\\' + level_dir + '\\' +  os.path.basename(filename)
        #print(path)


        def remove_from_zip(zipfname, *filenames):
            tempdir = tempfile.mkdtemp()
            try:
                tempname = os.path.join(tempdir, 'new.zip')
                with zipfile.ZipFile(zipfname, 'r') as zipread:
                    with zipfile.ZipFile(tempname, 'w') as zipwrite:
                        for item in zipread.infolist():
                            if item.filename not in filenames:
                                data = zipread.read(item.filename)
                                zipwrite.writestr(item, data)
                shutil.move(tempname, zipfname)
            finally:
                shutil.rmtree(tempdir)

        remove_from_zip('project.zip', path)
        with zipfile.ZipFile('project.zip', 'a') as z:
            z.write(filename,path)
            z.close()

             #vbox_link = widgets.HBox([vbox,linkwidget])

        self._display_Zip()


    def ulify_tree(self,elements):
        #    indent = " " * 4

        def count_level(test_str):
            count = 0
            for i in test_str:
                if i == '/':
                    count = count + 1
            return count

        string = "<ul>\n"
        for s in elements:
            c_level = count_level(s)
            if c_level == 0:
                string += "\n".join(["<li>" + str(s) + "</li>"])
            elif c_level ==1:
                string += "\n".join(["<li>"  + '...' + str(s) + "</li>"])
            elif c_level ==2:
                string += "\n".join(["<li>" + '......' + str(s) + "</li>"])
        #string += "\n".join(["<li>" + str(s) + "</li>" for s in elements])
        string += "\n</ul>"

        return string

    def _display_dir_tree_old(self):

        from directory_tree import display_tree
        out = widgets.Output()
        import os
        self.projectdir_path =  os.getcwd()

        if not os.path.exists('projectdir'):
            os.makedirs(self.projectdir_path + 'projectdir')
        with out:
            display_tree(self.projectdir_path + '/projectdir/')

        return out


    def _display_dir_tree(self):

        from fnmatch import fnmatch
        from pathlib import PurePath

        EXCLUDES = {
            ".git",
            ".github",
            ".vscode",
            "build",
            "dist",
            "lib",
            "node_modules",
            "__pycache__",
            ".ipynb_checkpoints"
        }

        def collect_files(root_path='..'):
            files = []
            for dirpath, dirnames, filenames in os.walk(root_path, followlinks=True):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDES]
                for f in filenames:
                    fullpath = PurePath(dirpath).relative_to(root_path).joinpath(f)

                    if fullpath.parts not in files:
                        files.append(fullpath.parts)
            files.sort()
            return files

        self.projectdir_path =  os.getcwd()

        if not os.path.exists(self.projectdir_path + '\projectdir'):
            os.makedirs(self.projectdir_path + '\projectdir')

        files = collect_files(self.projectdir_path + '\projectdir')
        #print(directory_path + '\projectdir')
        #print(files)

        tree = {}
        for f in files:
            node = tree
            for part in f:
                if part not in node:
                    node[part] = {}
                node = node[part]



        from ipytree import Node, Tree
        from traitlets import Unicode

        class TreeNode(Node):
            fullpath = Unicode("").tag(sync=True)


        def create_tree_widget(root, path, depth=0):
            node = Tree() if depth == 0 else TreeNode()
            for name, children in root.items():
                fullpath = path + [name]
                if len(children) == 0:
                    leaf = TreeNode(name)
                    leaf.fullpath = os.path.join(*fullpath)
                    leaf.icon = 'file'
                    leaf.icon_style = 'warning'
                    node.add_node(leaf)
                else:
                    subtree = create_tree_widget(children, fullpath, depth + 1)
                    subtree.icon = 'folder'
                    subtree.icon_style = 'info'
                    subtree.name = name
                    node.add_node(subtree)
            return node

        file_tree = create_tree_widget(tree, [])


        self.filetreeBox = widgets.VBox([file_tree])
        #print(filetreeBox)
        #out = widgets.Output()
        #with out:
        #    create_tree_widget(tree, [])
        # display(filetreeBox)

        return self.filetreeBox




    def _display_Zip(self):

        z = zipfile.ZipFile("project.zip", 'a')

        header= widgets.HTML('''
                <h4>Preview of files structure</h4>
                <hr style="height:1px;border-width:0;color:black;background-color:gray">
                ''')
        vbox_zip = widgets.VBox([header])

        self.struct_str = self.ulify_tree(z.namelist())

        self.zipstruct = widgets.HTML(
                    value=self.struct_str,
                    description='project.zip')
        #self.zipstruct = widgets.Textarea(
        #            value=self.ulify(z.namelist()),
        #            description='project.zip')


        vbox_zip = widgets.VBox([header,self.zipstruct])
        z.close()

        #self.update_display_Zip()


        return vbox_zip


    def _update_display_Zip(self):

        self.update = widgets.Button(
                value=False,
                description='Update',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Update',
                icon='update' # (FontAwesome names without the `fa-` prefix)
            )

        vbox = widgets.VBox([self.update])

        def on_update_change(change): # read an display
            #print('call update')
            self._display_Zip()

        self.update.on_click(on_update_change)

        return vbox


    def _widget_log(self):
        """Report errors
        """

        header= widgets.HTML(
                    '<h2>Logger<h2/>')
        text = widgets.HTML('''
                    <hr style="height:1px;border-width:0;color:black;background-color:gray">
                    Before downloading your metadata pay attention to the following warnings:
                    ''')
        self.log = widgets.HTML('')

        hbox = widgets.VBox([header,text,self.log])

        return hbox


    def ulify(self,elements):
        string = "<ul>\n"
        string += "\n".join(["<li>" + str(s) + "</li>" for s in elements])
        string += "\n</ul>"
        return string

    def list_files(startpath):
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            print('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                print('{}{}'.format(subindent, f))


    def _update_widget_log(self,warning):
        """Report errors
        """
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        self.warnings.append(dt_string + ': ' + warning)

        self.string = self.ulify(self.warnings)
        self.log.value  = self.string




    def manage(self):
        ''' Create vbox for each sections and display them in separate tabs'''

        self.vbox_guidelines = widgets.VBox(self.widget_guidelines)

        self.vbox_ownership = widgets.VBox(self.widget_ownership)
        self.vbox_guidelines_footer = widgets.VBox(self.widget_guidelines_footer)

        self.vbox_survey = widgets.VBox(self.widget_survey)
        self.vbox_survey_map = widgets.VBox(self.widget_survey_map)

        self.vbox_ERT = widgets.VBox(self.widget_ERT)
        self.vbox_upload_ERT_data = widgets.VBox(self.widget_ERT_upload)
        self.vbox_upload_ERT_files = widgets.VBox(self.widget_ERT_files)

        #self.vbox_EM = widgets.VBox(self.widget_EM)
        #self.vbox_upload_EM_data = widgets.VBox(self.widget_EM_upload)
        #self.vbox_upload_EM_files = widgets.VBox(self.widget_EM_files)


        self.vbox_quality = widgets.VBox(self.widget_quality)
        self.vbox_sampling = widgets.VBox(self.widget_sampling)
        self.vbox_import = widgets.VBox(self.widget_import)


        self.vbox_export = widgets.VBox(self.widget_export)

        self.vbox_tree = widgets.VBox(self.widget_files_tree)
        self.vbox_HDF5 = widgets.VBox(self.widget_export_HDF5)


        self.vbox_logger = widgets.VBox(self.widget_logger)
        #self.vbox_data_structure = widgets.VBox(self.widget_data_structure)

        self.vbox_data_structure = widgets.VBox(self.widget_data_structure)

        self.vbox_about = widgets.VBox(self.widget_about)


        accordion_tab0 = widgets.Accordion(children=[self.vbox_ownership, self.vbox_survey, self.vbox_survey_map],
                                                       selected_index = None)
        accordion_tab0.set_title(0, 'Owner*')
        accordion_tab0.set_title(1, 'General Survey description*')
        accordion_tab0.set_title(2, 'Geolocalisation*')



        self.accordion_tab_ERT = widgets.Accordion(children=[
                                                       self.vbox_ERT,
                                                       self.vbox_upload_ERT_data,
                                                       self.vbox_upload_ERT_files],
                                                       selected_index = 0)

        self.accordion_tab_ERT.set_title(0, 'Minimum required metadata')
        self.accordion_tab_ERT.set_title(1, 'Upload ERT file')
        self.accordion_tab_ERT.set_title(2, 'Related data ressources')


        #accordion_tab_EM = widgets.Accordion(children=[self.vbox_upload_EM_data,
        #                                               self.vbox_upload_EM_files],
        #                                               selected_index = None)
        #accordion_tab_EM.set_title(0, 'Upload EM file')
        #accordion_tab_EM.set_title(1, 'Related data ressources')


        accordion_tab_export = widgets.Accordion(children=[self.vbox_tree,self.vbox_HDF5],
                                                       selected_index = None)
        accordion_tab_export.set_title(0, 'Files structure')
        accordion_tab_export.set_title(1, 'Data container')


        vbox_home = widgets.VBox([self.vbox_guidelines,accordion_tab0,self.vbox_guidelines_footer])
        #self.vbox_tab_ERT = widgets.VBox([self.vbox_ERT,self.accordion_tab_ERT])
        self.vbox_tab_ERT = widgets.VBox([self.accordion_tab_ERT])
        #self.vbox_tab_EM = widgets.VBox([self.vbox_EM,accordion_tab_EM])
        vbox_tab_export = widgets.VBox([self.vbox_export,accordion_tab_export])

        title_resume = widgets.HTML('''
                <h3> Resume </h3>
             ''')
        #self.vbox_tab_plot = widgets.VBox([title_resume])
        #self.vbox_tab_plot = widgets.VBox(self.resume_tab)

        self._update_widget_export()
        #self._update_tab()

        self.tab  = widgets.Tab(children = [vbox_home,
                                       self.vbox_import,
                                       #self.vbox_tab_plot,
                                       self.vbox_tab_ERT,
                                       #self.vbox_tab_EM,
                                       self.vbox_quality,
                                       #self.vbox_sampling,
                                       #self.vbox_data_structure,
                                       vbox_tab_export,
                                       self.vbox_logger,
                                       self.vbox_about
                                      ])

        self.tab_root = widgets.Tab(children = [vbox_home,
                                       self.vbox_import,
                                       #self.vbox_tab_plot,
                                       #vbox_tab_EM,
                                       self.vbox_quality,
                                       #self.vbox_sampling,
                                       #self.vbox_data_structure,
                                       vbox_tab_export,
                                       self.vbox_logger,
                                       self.vbox_about
                                      ])


        tabnames = ['Home','Import','ERT','Quality','Export','Logger','About']
        self.tabnames_root = ['Home','Import','Quality','Export','Logger','About']
        #tabnames = ['Home','Import','Quality','Export','Logger','About']
        for it,name in enumerate(tabnames):
            self.tab.set_title(it,name)

        outtab = widgets.Output()
        with outtab:
            print('outtab')
            display(self.tab)

        def _observe_method(change):
            print(change.new)
            print('tessst')
            with outtab:
                clear_output()
                self.tab = self._update_tabs(change.new)
                display(self.tab)


            self.metadata['method'] = self.widget_method.value
            self._update_widget_export()
            #print(change.new)
            #self.tab.selected_index = 0
            #self.tab = "hidden""hidden"
            #self.tab.layout.visibility = "hidden"
            #self.tab.layout.display = "none"

            #self.tab.layout.visibility = "visible"
            #self.tab.layout.display = "block"
            #display(self.tab)

        self.widget_method.observe(_observe_method,'value')


        #self.tab.set_title(0, 'Home')
        #self.tab.set_title(1, 'Import')
        #self.tab.set_title(2, 'ERT')
        #self.tab.set_title(3, 'EM')
        #self.tab.set_title(4, 'Quality')
        #tab.set_title(4, 'Sampling')
        #self.tab.set_title(5, 'Export')
        #tab.set_title(5, 'Data structure')
        #self.tab.set_title(6, 'Logger')
        #self.tab.set_title(7, 'About')

        #All_tabs = widgets.VBox[outtab]
        #display(All_tabs)
        #def showtabsnew(change):
        #    print('showtabsnew')
        #    display(self.tab)


        #self.tab.observe(showtabsnew, 'value')

        #display(self.tab)
        display(outtab)



    def _update_tabs(self,tabs2insert):
        ls = list(self.tab_root.children)
        ls_name = list(self.tabnames_root)
        for tt in enumerate(tabs2insert):
            if 'ERT' in tt[1]:
                ls.insert(tt[0]+2,self.vbox_tab_ERT)
                ls_name.insert(tt[0]+1,'ERT')
            if 'EM' in tt[1]:
                ls.insert(tt[0]+2,self.vbox_tab_EM)
                ls_name.insert(tt[0]+1,'EM')
            if 'IP' in tt[1]:
                ls.insert(tt[0]+2,self.vbox_tab_EM)
                ls_name.insert(tt[0]+1,'EM')
            #if 'ER_WC' in tt[1]: # relationship between ER and WC
            #    ls.insert(tt[0]+2,self.vbox_tab_ER_WC)
            #    ls_name.insert(tt[0]+1,'EM')



        new_tabs = tuple(ls)
        self.tab  = widgets.Tab(new_tabs)
        #tabnames = ['Home','Import','EM','ERT','Quality','Export','Logger','About']
        tabnames = ls_name
        for it,name in enumerate(tabnames):
            self.tab.set_title(it,name)


        return self.tab
