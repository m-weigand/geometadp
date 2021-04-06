import sys
import ipywidgets as widgets
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
from IPython.core.display import display
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
#from lib.geometadp.EM import *

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


class geo_metadata(object):
    def __init__(self):
        # self.app = QApplication(sys.argv)

        # this stores the actual values exported to json/xml
        self.metadata = {}
        self.warnings = [] # report all the warnings

        # stores the various widget objects. They are shown in this order
        self.widget_guidelines = []
        self.widget_ownership = []
        self.widget_survey = []
        self.widget_survey_map = []

        self.widget_ERT = []
        self.widget_ERT_upload = []
        self.widget_ERT_files = []

        self.widget_EM = []
        self.widget_EM_upload = []
        self.widget_EM_files = []

        self.widget_timelapse = []

        self.widget_quality = []
        self.widget_sampling = []
        self.widget_data_structure = []

        self.widget_import = []
        self.widget_export = []
        self.widget_logger = []

        self.widget_about = []

        self._prepare_widgets()

    def _prepare_widgets(self):
        self.widget_guidelines.append(self._widget_header())
        self.widget_guidelines.append(self._restart_project())


        # DOI

        #%% REPORT: title/authors
        self.widget_ownership.append(self._widget_report_title())
        self.widget_ownership.append(self._widget_report_authors())
        self.widget_ownership.append(self._widget_owner())
        self.widget_ownership.append(self._widget_email())
        self.widget_ownership.append(self._widget_dataset_DOI())


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
        self.widget_timelapse.append(self._timelapse_option())
        #self.widget_timelapse.append(self._nb_of_files())
        #self.widget_timelapse.append(self._time_schedule())


        #%% ERT metadata: Date_measure/ Time_measure/ Elec_conf/ Elec_spacing
        self.widget_ERT.append(self._widgets_ERT_doc())
        self.widget_ERT.append(self._widget_instrument())
        self.widget_ERT.append(self._widget_datetime())
        # self.widget_objects.append(self._widget_time())
        self.widget_ERT.append(self._widget_elec_config())
        self.widget_ERT.append(self._widget_elec_seq())
        self.widget_ERT.append(self._widget_elec_spacing())
        self.widget_ERT.append(self._widget_description_ERT())
        self.widget_ERT.append(self._widget_ERT_more())

        self.widget_ERT_upload.append(self._widget_upload_ERT_button()) 
        self.widget_ERT_files.append(self._widgets_ERT_add_file())


        #%% EM metadata
        self.widget_EM.append(self._widgets_EM_doc())
        self.widget_EM.append(self._widget_instrument())
        self.widget_EM.append(self._widget_datetime())
        self.widget_EM.append(self._widget_coil_config())
        self.widget_EM.append(self._widget_coil_height())
        self.widget_EM.append(self._widget_coil_spacing())
        self.widget_EM.append(self._widget_description_EM())
        self.widget_EM.append(self._timelapse_option())

        self.widget_EM_upload.append(self._widget_upload_EM_button())  # upload EM data from emagpy
        self.widget_EM_files.append(self._widgets_EM_add_file())


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
        self.widget_data_structure.append(self._widgets_dataset_structure_doc())
        #self.widget_data_structure.append(self._widget_upload_img_button())
        #self.widget_data_structure.append(self._widget_external_ressource_more(my_columns))
        #self.widget_data_structure.append(self._widgets_dataset_structure())
        #self.widget_data_structure.append(self._widgets_related_external_resources_doc())


        #%% ancillary DATA 
        # self.widget_ancillary.data.append(self._widgets_figures())

        #%% Upload 
        self.widget_export.append(self._widget_export())
        self.widget_export.append(self._widget_download_buttons())
        self.widget_export.append(self._display_Zip())


        #%% Import 
        self.widget_import.append(self._widget_upload_button())
        self.widget_import.append(self._widget_upload_json())

        #%% Logger
        self.widget_logger.append(self._widget_log())

        #%% About
        self.widget_about.append(_widget_about())

   
    def _restart_project(self):

        button_restart = widgets.Button(description="restart")  

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
        #Save widget state to notebook - Saves the current widget manager state to the notebook, overwriting any existing widget manager state.
        #Clear widget state in notebook - Could be done by close all widgets, then saving widget state, but is more convenient

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
                  <li> Keep track of your datasets structure/metadata during every stages: acquisition/processing/publication: 
                    Use the import/export tabs respectively to import a pre-existing JSON file and save your work </li>
                    <ul>
                      <li> a zip file containing the files structure </li>
                      <li> a Json formatted file in which metadata are saved</li>
                    </ul>                
                </ol>

            <h4> Recommandations </h4>
                <ol>
                  <li> Fill out the maximum number of metadata fields </li>
                  <li> Check if a metadata descriptor exist before creating a new one</li>
                  <li> Check the logger for possible errors</li>
                </ol>

            <h4> More on github </h4>
                See About tab and github page for <a href="https://github.com/agrogeophy/geometadp" target="_blank">more informations.</a></p>
            
            <hr style="height:5px;border-width:0;color:black;background-color:gray">

            ''')

        vbox = widgets.VBox([logo, title, text])
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
       """Import GeoJSON file"""

       self.xy_upload = FileChooser(use_dir_icons=True)
       self.xy_upload.filter_pattern = '*.csv'
       self.xy_upload.title = '<b>xy_coords</b>'

       vbox = widgets.VBox([self.xy_upload])

       def _on_upload_xy_change():
            #for name, file_info in self.xy_upload.value.items():
            name = self.xy_upload.selected
            self._add_to_Zip(name, target_dir=self.metadata['method'], level_dir='spatial')
            self._update_widget_log('xy_file copied into zip')

            with open(name, newline='') as csvfile:
                self.xy_data = pd.read_csv(csvfile,sep=';') 

            poly_line = Polyline(locations=self.xy_data.values.tolist(), color="red" , fill=False)
            self.m_top.add_layer(poly_line)

            #for name, file_info in self.xy_upload.value.items():
            name = self.xy_upload.selected
            self.metadata['xy_coords_file'] = name
            self._update_widget_export()

       # self.xy_upload.register_callback(_observe_xy_coords) # add to metadata export
       # self.self.m_top.observe(_observe_geojson) # add to metadata export
       self.xy_upload.register_callback(_on_upload_xy_change) # plot into leaflet

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

       print(self.geojson_upload.selected)
       vbox = widgets.VBox([self.geojson_upload])

       def _on_upload_change():

            name = self.geojson_upload.selected
            #for name, file_info in self.geojson_upload.value.items():
            self._add_to_Zip(name, target_dir=self.metadata['method'] , level_dir='spatial')
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
            self.metadata['geojson_file'] = name
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


    def _widget_leaflet(self):

        header = HTML("Import tools for 1d souding, 2d line and 2d maps", layout=Layout(height='auto'))
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

        # case of a souding data
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
        self.widget_method = widgets.RadioButtons(
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
            description='Method:',
            disabled=False,
            style=style,
            layout=layout)
        

        # set initial metadata
        self.metadata['method'] = ''

        def _observe_method(change):
            self.metadata['method'] = self.widget_method.value
            self._update_widget_export()

        self.widget_method.observe(_observe_method)
        return self.widget_method

    def _timelapse_option(self):

        button_True = widgets.Button(description="Time Lapse True")  
        button_False = widgets.Button(description="False")  

        self.widget_time_lapse = widgets.HBox([button_True,button_False])
        # set initial metadata
        # self.metadata['time_lapse'] = 'False'

        # Where we will put all our time lapse widgets
        vbox_TL = widgets.VBox()

        def _on_button_True_click(change):
            self.metadata['time_lapse'] = 'True'
            vbox_nb_of_files = self._nb_of_files_TL()
            vbox_time_interval = self._time_interval_TL()
            vbox_TL.children = (*vbox_TL.children, vbox_nb_of_files)
            vbox_TL.children = (*vbox_TL.children, vbox_time_interval)
            self._update_widget_export()

        def _on_button_False_click(change):
            self.metadata['time_lapse'] = 'False'
            vbox_TL = widgets.VBox()
            vbox_TL.children = ()
            self._update_widget_export()


        button_True.on_click(_on_button_True_click)
        button_False.on_click(_on_button_False_click)

        # Put Dropdown and button together
        vbox = widgets.VBox([self.widget_time_lapse, vbox_TL])

        return vbox

    def _nb_of_files_TL(self):
        self.widget_nb_files_TL = widgets.Text(
            description='Nb of files',
        )
        def _observe_nb_of_files_TL(change):
            self.metadata['nb_of_files_TL'] = self.widget_nb_files_TL.value
            #self._update_widget_export()

        self.widget_nb_files_TL.observe(_observe_nb_of_files_TL)

        return self.widget_nb_files_TL

    def _time_interval_TL(self):
        self.widget_time_interval_TL = widgets.Text(
            description='Time interval reading',
        )
        def _observe_time_interval_TL(change):
            self.metadata['time_interval_TL'] = self.widget_time_interval_TL.value
            #self._update_widget_export()

        self.widget_time_interval_TL.observe(_observe_time_interval_TL)

        return self.widget_time_interval_TL


    def _widget_measurement_type(self):
        self.widget_measurement_type = widgets.RadioButtons(
            options=['Laboratory', 'Field'],
            default='Field',
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

    def _widget_instrument(self):
        self.widget_instrument = widgets.Text(
            description='Instrument',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_instrument(change):
            self.metadata['instrument'] = self.widget_instrument.value
            self._update_widget_export()

        self.widget_instrument.observe(_observe_instrument)
        return self.widget_instrument


    def _widget_datetime(self):
        self.widget_date = widgets.DatePicker(
            description='Datetime of measurement',
            disabled=False,
            style=style,
            layout=layout)

        def _observe_dt(change):
            date = self.widget_date.value
            if date is not None:
                self.metadata['date'] = date.isoformat()
                self._update_widget_export()

        self.widget_date.observe(_observe_dt)
        return self.widget_date

 
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
            default='1D',
            description='Electrode configuration:',
            disabled=False,
            style=style,
            layout=layout)
        

        self.widget_elec_config.layout.display   = 'none'
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
            default='WS',
            description='Electrode sequence:',
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
            description='Electrode spacing:',
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

        self.widget_description_ERT.observe(_observe_description_ERT)
        return self.widget_description_ERT

    def _widget_upload_ERT_doc(self):
        """upload ERT file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>REDA importer<h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
        text = widgets.HTML('''
        Infer all the ERT metadata from the ERT dataset uploaded. Please refer to the <a href="https://github.com/geophysics-ubonn/reda"> REDA online doc</a>
        ''')
        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_ERT_button(self):
       """Import EM dataset """

       vbox_doc = self._widget_upload_ERT_doc()

       #self.ERT_upload = widgets.FileUpload(
       #        accept='.bin',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #    )

       self.ERT_upload  = FileChooser(use_dir_icons=True)

       vbox = widgets.VBox([vbox_doc,self.ERT_upload])


       def on_upload_change(change):
            #for name in self.ERT_upload.selected:
            name = self.ERT_upload.selected

            self._add_to_Zip(self.ERT_upload.selected_filename, target_dir='', level_dir='')
            self._update_widget_log('ERT file imported with REDA')
            self.metadata['ERT_filename_metadata'] = name
            ert = reda.ERT()
            ert.import_syscal_bin(name)

            #ert.electrode_positions
            #ert.has_multiple_timesteps
            #ert.log_list
            #ert.print_log()

            vbox.children = (*vbox.children, self._print_log_REDA())
            vbox.children = (*vbox.children, self._nb_of_ambn())
            vbox.children = (*vbox.children, self._ERT_chargeability())


            #self.metadata['print_log_REDA'] =   ert.print_log()
            self.metadata['nb_abmn'] =   str(len(ert.data))
            if ert.data['chargeability'][0] != 0:
                self.metadata['chargeability'] =   True
            else:
                self.metadata['chargeability'] =   False

            self._update_widget_export()
            #self._parse_json() # parse to metadata for export
            #self._update_fields_values(['print_log_REDA']) # parse to widgets to replace initial valus
            self._update_fields_values(['nb_abmn']) # parse to widgets to replace initial valus
            self._update_fields_values(['chargeability']) # parse to widgets to replace initial valus

       self.ERT_upload.register_callback(on_upload_change)


       return vbox

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


        columns = list(['raw file','processed file'])
        vbox_ERT_add_files = self._widget_add_external_ressource(columns,self.metadata['method'])

        vbox_files = self._widgets_related_external_resources_files_doc()
        vbox_figs = self._widgets_related_external_resources_fig_doc()
        vbox_codes = self._widgets_related_external_resources_codes_doc()

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

    def _widget_coil_config(self):
        coil_config = widgets.SelectMultiple(
            options=['VCP', 'VMD','PRP', 'HCP', 'HMD'],
            default='VCP',
            description='Coil orientation:',
            disabled=False,
            style=style,
            layout=layout)

        # set initial metadata
        # self.metadata['coil_spacing'] = 'VCP'

        def _observe_coil_config(change):
            self.metadata['coil_config'] = coil_config.value
            self._update_widget_export()

        coil_config.observe(_observe_coil_config)
        return coil_config


    def _widget_coil_height(self):
        self.widget_coil_height = widgets.Text(
            description='Height of the instrument above the ground [m]:',
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
            description='Coil spacing:',
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

       self.EM_upload = FileChooser(use_dir_icons=True)
       self.EM_upload.filter_pattern = '*.csv'
       self.EM_upload.title = '<b>EM_upload</b>'
       #        accept='.csv',  # Accepted file extension
       #        multiple=False  # True to accept multiple files upload else False
       #    )



       vbox = widgets.VBox([vbox_doc,self.EM_upload])


       def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.EM_upload.selected
            self._add_to_Zip(name, target_dir= self.metadata['method'], level_dir='Emagpy_import')
            self._update_widget_log('EM file imported for automatic metadata extraction')
            self.metadata['em_filename_metadata'] = name

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
            self._update_fields_values(['coil_spacing']) # parse to widgets to replace initial valus

       #self.EM_upload.observe(on_upload_change, names='_counter')
       self.EM_upload.register_callback(on_upload_change)


       return vbox

    def _widgets_EM_add_file(self):


        columns = list(['raw file','processed file'])
        vbox_EM_add_files = self._widget_add_external_ressource(columns,self.metadata['method'])

        vbox_files = self._widgets_related_external_resources_files_doc()
        vbox_figs = self._widgets_related_external_resources_fig_doc()
        vbox_codes = self._widgets_related_external_resources_codes_doc()

        vbox = widgets.VBox([vbox_files,vbox_EM_add_files,vbox_figs,vbox_codes])

        return vbox


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
            description='Peer reviewed:',
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
            description='Peer reviewer contact:',
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
            description='Replicate datasets:',
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
            description='Comparison ref data:',
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
            description='ref data:',
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

    def _widget_add_external_ressource(self, my_columns, method_str):

        # Data examples
        # my_columns = list(['field picture', 'post processing figure', 'rawdata'])
        df = pd.DataFrame(np.random.randint(0,100,size=(100, np.shape(my_columns)[0])), columns=my_columns)

        # Our filter generator
        def generate_filter(button):
            # Check if exist before creating
            widget_name = method_str + select_definition.value
            print(select_definition.value)
            print(widget_name)
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

        vbox_figs = self._widget_upload_fig_button(self.metadata['method'])

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
       self.fig_upload.title = '<b>Upload figs</b>'

       vbox = widgets.VBox([self.fig_upload])


       def on_upload_change():
            name =  self.fig_upload.selected
            #for name, file_info in self.fig_upload.value.items():
            self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir='figures')
            self._update_widget_log(name + 'file copied into: ' + method_str + '/' + 'figures zip folder')
            self.metadata['external_ressource_' + method_str + '_fig'] = name
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

        vbox_codes = self._widget_upload_codes_button(self.metadata['method'])

        vbox = widgets.VBox([title,vbox_codes])
        return vbox

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

    def _widget_upload_codes_button(self,method_str):
       """Import EM dataset """

       self.codes_upload = FileChooser(use_dir_icons=True)

       #self.codes_upload = widgets.FileUpload(
       #        accept='',  # Accepted file extension
       #        multiple=True  # True to accept multiple files upload else False
       #    )

       vbox = widgets.VBox([self.codes_upload])


       def on_upload_change(change):

            #for name, file_info in self.codes_upload.value.items():
            name = self.codes_upload.selected
            self._add_to_Zip(name,target_dir=self.metadata['method'],level_dir='scripts')
            self._update_widget_log(name + 'file copied into: ' + method_str + '/' + 'scripts zip folder')
            self.metadata['external_ressource_' + method_str + '_codes'] = name
            self._update_widget_export()

            # self._parse_json() # parse to metadata for export
            # self._update_fields_values() # parse to widgets to replace initial valus

       #self.codes_upload.register_callback(on_upload_change, names='_counter')
       self.codes_upload.register_callback(on_upload_change)


       return vbox


    #def _widget_data_directory(self):
    #    data_directory = _widget_select_directory(
    #        self.metadata, 'data_dir', 'Data input directory',
    #        callback=self._update_widget_export
    #    )
    #    data_widget = data_directory.get_widget()
    #
    #   return data_widget

    #def _widget_output_directory(self):
    #    output_directory = _widget_select_directory(
    #        self.metadata, 'output_dir', 'Output directory',
    #        callback=self._update_widget_export
    #    )
    #    output_widget = output_directory.get_widget()
    #    return output_widget
         
        
    #def _widget_import_export_buttons(self):
    #    """Import/exports buttons pre-existing JSON file"""
    #    
    #    upload_btn = widgets.FileUpload(
    #            accept='.json,.xml',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
    #            multiple=False  # True to accept multiple files upload else False
    #        )
    #    words = ['Export']
    #    items = [Button(description=w) for w in words]
                

    #    vbox = widgets.VBox(
    #        [
    #            upload_btn, 
    #            items[0]

    #        ]
    #   )
    #    return vbox

        
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
                widgets.HTML(
                    '<hr style="height:5px;border-width:0;color:black;' +
                    'background-color:gray"><hr />' +
                    '<h3>Preview of metadata export:<h3 />'),
                self.export_type,
                self.export
            ]
        )


        def _observe_export_type(change):
            self._update_widget_export()

        self.export_type.observe(_observe_export_type)
        return vbox



    def export_metadata_to_json_str(self):
        """Generate a string representation of the metadata"""
        metadata_json_raw = json.dumps(self.metadata, indent=4)
        return metadata_json_raw

    def export_metadata_to_xml_str(self):
        xml = dicttoxml.dicttoxml(self.metadata)
        dom = dicttoxml.parseString(xml)
        metadata_xml = dom.toprettyxml()
        return metadata_xml

    def _update_widget_export(self):
        if self.export_type.value == 'JSON':
            metadata_str = self.export_metadata_to_json_str()
        else:
            metadata_str = self.export_metadata_to_xml_str()
        # self.widget_export.value = metadata_str
        self.export.value = "<pre>{}</pre>".format(
            html.escape(metadata_str))


    def _widget_upload_json(self):
        """upload json file and parse values
        """
        title = widgets.HTML(
            '''<h3>Upload json file<h3/>
               <hr style="height:1px;border-width:0;color:black;background-color:gray">


                <h4> Metadata templates </h4>
                <p> Metadata templates for generic survey to upload are available on the github page.
                If you require additionnal metadata, please let us know by opening an issue <a href="https://github.com/agrogeophy/geometadp" target="_blank">on github</a>.
                </p>

            ''')
        text = widgets.HTML('''
        Replace all the field by the uploaded json fields
        ''')
        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_button(self):
       """Import pre-existing JSON file"""

       self.json_upload = widgets.FileUpload(
               accept='',  # Accepted file extension
               multiple=False  # True to accept multiple files upload else False
           )

       vbox = widgets.VBox([self.json_upload])


       def on_upload_change(change):
            for name, file_info in self.json_upload.value.items():
                with open(name) as json_file:
                    self.data_uploaded = json.load(json_file)

            self._parse_json()
            self._update_fields_values_JSON()

       self.json_upload.observe(on_upload_change, names='_counter')


       return vbox

    def _update_fields_values(self,metadata_key):
        """Update all fields from data metadata harvester"""
        for i in enumerate(metadata_key):
            if hasattr(self, 'widget_' + i[1]):
               widget2fill = eval('self.widget_' + i[1])
               if "date" not in i[1]: 
                    widget2fill.value = self.metadata[i[1]]
               else:
                    date_time_obj = datetime.strptime(self.metadata[i[1]],  "%Y-%m-%d")
                    widget2fill.value = date_time_obj

    def _update_fields_values_JSON(self):
        """Update all fields from uploaded JSON"""
        json_tmp = json.dumps(self.data_uploaded, indent=0)
        mylist = json.loads(json_tmp)
        for i in enumerate(mylist):
            if hasattr(self, 'widget_' + str(i[1])):
               widget2fill = eval('self.widget_' + str(i[1]) )
               if "date" not in str(i[1]): 
                    widget2fill.value = '{}'.format(self.data_uploaded[i[1]])
               else:
                    date_time_obj = datetime.strptime(self.data_uploaded[i[1]],  "%Y-%m-%d")
                    widget2fill.value = date_time_obj


    def _parse_json(self):
        """Fill out metadata container (for export)"""
        for i in enumerate(self.data_uploaded):
            if hasattr(self, 'widget_' + i[1]):
                self.metadata[i[1]] = self.data_uploaded[i[1]]
            else:
                warning = 'metadata no matching:' + str(i[1])
                self._update_widget_log(warning)


    def _widget_download_buttons(self):
        """Download JSON file"""

        self.download = widgets.Button(
                value=False,
                description='Download',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Download',
                icon='download' # (FontAwesome names without the `fa-` prefix)
            )

        metadata_json_raw = json.dumps(self.metadata, indent=4)
        # write tmp json file


        vbox = widgets.VBox([self.download])

        with open('json_backup.txt', 'w') as outfile:
                json.dump(self.metadata, outfile)

        self._add_to_Zip('json_backup.txt','','')

        def on_download_change(change): # read an display
             with open('json_backup.txt', 'w') as outfile:
                json.dump(self.metadata, outfile)
             link2file = FileLink(r'json_backup.txt')
             linkwidget = widgets.HTML(
                        value="<a href={code}>link2file to click</a>".format(code=link2file),
                        description='Some HTML',
             )

             vbox_link = widgets.HBox([vbox,linkwidget])

        self.download.on_click(on_download_change)

        return vbox


    def _add_to_Zip(self,filename, target_dir, level_dir):
        z = zipfile.ZipFile("project.zip", 'a')

        
        path = target_dir + '\\' + level_dir + '\\' +  os.path.basename(filename)


        def zipdir(path, filename, ziph):
            #filePath = os.path.join(os.getcwd(), path)
            ziph.write(filename,path)
        zipdir(path, filename, z)
        z.close()


    def _display_Zip(self):

        try:
            z = zipfile.ZipFile("project.zip", 'r')
            header= widgets.HTML('''
                    <h2>File Structure<h2/>
                    ''')

            struct_str = self.ulify(z.namelist())


            zipstruct = widgets.HTML(
                        value=struct_str,
                        description='Some HTML')
            vbox_zip = widgets.VBox([header, zipstruct])

        # Do something with the file
        except IOError:
            print("File not accessible")
        finally:
            z.close()

        z = zipfile.ZipFile("project.zip", 'r')

        return vbox_zip



        #self.z.printdir()
        #self.z.write(filename,target_dir)
        #self.z.close()

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

        self.vbox_guidelines = widgets.VBox(self.widget_guidelines)

        self.vbox = widgets.VBox(self.widget_ownership)
        self.vbox_survey = widgets.VBox(self.widget_survey)
        self.vbox_survey_map = widgets.VBox(self.widget_survey_map)

        self.vbox_ERT = widgets.VBox(self.widget_ERT)
        self.vbox_upload_ERT_data = widgets.VBox(self.widget_ERT_upload)
        self.vbox_upload_ERT_files = widgets.VBox(self.widget_ERT_files)     

        self.vbox_EM = widgets.VBox(self.widget_EM)
        self.vbox_upload_EM_data = widgets.VBox(self.widget_EM_upload)
        self.vbox_upload_EM_files = widgets.VBox(self.widget_EM_files)     


        self.vbox_quality = widgets.VBox(self.widget_quality)
        self.vbox_sampling = widgets.VBox(self.widget_sampling)
        self.vbox_import = widgets.VBox(self.widget_import)
        self.vbox_export = widgets.VBox(self.widget_export)
        self.vbox_logger = widgets.VBox(self.widget_logger)
        #self.vbox_data_structure = widgets.VBox(self.widget_data_structure)

        self.vbox_data_structure = widgets.VBox(self.widget_data_structure)

        self.vbox_about = widgets.VBox(self.widget_about)


        accordion_tab0 = widgets.Accordion(children=[self.vbox, self.vbox_survey, self.vbox_survey_map],
                                                       selected_index = None)
        accordion_tab0.set_title(0, 'Owner*')
        accordion_tab0.set_title(1, 'General Survey description*')
        accordion_tab0.set_title(2, 'Geolocalisation*')

        accordion_tab_ERT = widgets.Accordion(children=[self.vbox_upload_ERT_data,
                                                       self.vbox_upload_ERT_files],
                                                       selected_index = None)
        accordion_tab_ERT.set_title(0, 'Upload ERT file')
        accordion_tab_ERT.set_title(1, 'Related data ressources')

        accordion_tab_EM = widgets.Accordion(children=[self.vbox_upload_EM_data,
                                                       self.vbox_upload_EM_files],
                                                       selected_index = None)
        accordion_tab_EM.set_title(0, 'Upload EM file')
        accordion_tab_EM.set_title(1, 'Related data ressources')

        vbox_tab0 = widgets.VBox([self.vbox_guidelines,accordion_tab0])
        vbox_tab_ERT = widgets.VBox([self.vbox_ERT,accordion_tab_ERT])        
        vbox_tab_EM = widgets.VBox([self.vbox_EM,accordion_tab_EM])
                          

        
        
        self._update_widget_export()


        tab  = widgets.Tab(children = [vbox_tab0, 
                                       self.vbox_import,
                                       vbox_tab_ERT,
                                       vbox_tab_EM,                                       
                                       self.vbox_quality,
                                       #self.vbox_sampling,
                                       #self.vbox_data_structure,
                                       self.vbox_export,
                                       self.vbox_logger,
                                       self.vbox_about
                                      ])


        tab.set_title(0, 'Home')
        tab.set_title(1, 'Import')
        tab.set_title(2, 'ERT')
        tab.set_title(3, 'EM')
        tab.set_title(4, 'Quality')
        #tab.set_title(4, 'Sampling')
        tab.set_title(5, 'Export')
        #tab.set_title(5, 'Data structure')
        tab.set_title(6, 'Logger')
        tab.set_title(7, 'About')

        display(tab)
