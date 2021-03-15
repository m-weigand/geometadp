import sys
import ipywidgets as widgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
from IPython.core.display import display
import ipydatetime
from ipywidgets import FileUpload, Button
from IPython.display import FileLink
import html
from ipyleaflet import Map, basemaps, basemap_to_tiles, GeoJSON, Marker
from ipywidgets import Layout, HBox, VBox, FloatText
from ipywidgets import *
import pandas as pd
import numpy as np
from IPython.display import display, clear_output

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
layout = {'width': '400px'}

# https://ipywidgets.readthedocs.io/en/latest/examples/Widget%20Events.html#Debouncing
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
        self.app = QApplication(sys.argv)

        # this stores the actual values exported to json/xml
        self.metadata = {}
        self.warnings = [] # report all the warmings

        # stores the various widget objects. They are shown in this order
        self.widget_guidelines = []
        self.widget_objects = []
        self.widget_survey = []
        self.widget_survey_map = []

        self.widget_ERT = []
        self.widget_ERT_upload = []

        self.widget_EM = []
        self.widget_EM_upload = []

        self.widget_quality = []
        self.widget_sampling = []
        self.widget_data_structure = []

        self.widget_upload = []
        self.widget_export = []
        self.widget_logger = []


        self._prepare_widgets()

    def _prepare_widgets(self):
        self.widget_guidelines.append(self._widget_header())
      
        #%% REPORT: title/authors
        self.widget_objects.append(self._widget_report_title())
        self.widget_objects.append(self._widget_report_authors())
        self.widget_objects.append(self._widget_owner())
        self.widget_objects.append(self._widget_email())


        # SURVEY: method/type/instrument
        self.widget_survey.append(self._widgets_survey_doc())
        # self.widget_survey.append(self._widget_upload_CAGS()) # not yet implemented

        self.widget_survey.append(self._widget_method())
        self.widget_survey.append(self._widget_measurement_type())
        self.widget_survey.append(self._widget_dataset_DOI())
        self.widget_survey.append(self._widget_variables())
        # self.widget_survey.append(self._widget_location_bounds()) # deprecated (use leaflet instead)

        # SURVEY: map
        self.widget_survey_map.append(self._widget_leaflet())
        


        #%% ERT metadata: Date_measure/ Time_measure/ Elec_conf/ Elec_spacing
        self.widget_ERT.append(self._widgets_ERT_doc())
        self.widget_ERT.append(self._widget_instrument())
        self.widget_ERT.append(self._widget_datetime())
        # self.widget_objects.append(self._widget_time())
        self.widget_ERT.append(self._widget_elec_config())
        self.widget_ERT.append(self._widget_elec_seq())
        self.widget_ERT.append(self._widget_elec_spacing())
        self.widget_ERT.append(self._widget_free_ERT())
        self.widget_ERT.append(self._widget_elec_geom())
        self.widget_ERT_upload.append(self._widget_upload_ERT())  # not yet implemented


        #%% EM metadata
        self.widget_EM.append(self._widgets_EM_doc())
        self.widget_EM.append(self._widget_coil_config())
        self.widget_EM.append(self._widget_coil_height())
        self.widget_EM.append(self._widget_coil_spacing())
        self.widget_EM.append(self._widget_free_EM())
        self.widget_EM_upload.append(self._widget_upload_EM())  # not yet implemented

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
        #self.widget_data_structure.append(self._widget_data_directory())
        #self.widget_data_structure.append(self._widget_output_directory())

        #%% Upload 
        self.widget_export.append(self._widget_export())
        self.widget_export.append(self._widget_download_buttons())

        #%% Export 
        self.widget_upload.append(self._widget_upload_json())
        self.widget_upload.append(self._widget_upload_button())

        #%% Logger
        self.widget_logger.append(self._widget_log())

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
            '<h2>Data Manager and Metadata Collector for CGAGS - DEV version <h2/>')
        text = widgets.HTML('''
            This gui is designed to help with the initial preparation of one
            geophysical dataset metadata. In order to make the dataset FAIR, simple metadata descriptors must be filled. 
            if you require additionnal dataset, please let us know by opening an issue <a href="https://github.com/agrogeophy/geometadp" target="_blank">on github </a>
            Note that this is a lightened version of the metadata manager as the full version must be run locally to interact with files. See github for <a href="https://github.com/agrogeophy/geometadp" target="_blank">more informations.</a> 
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
            style={'description_width': 'initial'},
        )

        @debounce(0.2)
        def _observe_report_authors(change):
            self.metadata['report_authors'] = self.widget_report_authors.value
            self._update_widget_export()

        self.widget_report_authors.observe(_observe_report_authors)
        return self.widget_report_authors

    def _widget_owner(self):
        self.widget_owner = widgets.Text(
            description='Owner:'
        )

        @debounce(0.2)
        def _observe_owner(change):
            self.metadata['owner'] = self.widget_owner.value
            self._update_widget_export()

        self.widget_owner.observe(_observe_owner)
        return self.widget_owner

    def _widget_email(self):
        self.widget_email = widgets.Text(
            description='Email:'
        )

        @debounce(0.2)
        def _observe_email(change):
            self.metadata['email'] = self.widget_email.value
            self._update_widget_export()

        self.widget_email.observe(_observe_email)
        return self.widget_email

    def _widget_dataset_DOI(self):
        self.widget_dataset_DOI = widgets.Text(
            description='Dataset DOI:',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_dataset_DOI(change):
            self.metadata['dataset_DOI'] = self.widget_dataset_DOI.value
            self._update_widget_export()

        self.widget_dataset_DOI.observe(_observe_dataset_DOI)
        return self.widget_dataset_DOI

    def _widget_variables(self):
        self.widget_variables = widgets.Text(
            description='Physical property investigated:',
            style={'description_width': 'initial'}
            )

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



    def _widget_upload_GeoJSON_button(self):
       """Import GeoJSON file"""

       self.geojson_upload = widgets.FileUpload(
               description = 'geo.json',
               accept='.json',  # Accepted file extension
               multiple=False  # True to accept multiple files upload else False
           )

       vbox = widgets.VBox([self.geojson_upload])

       def _on_upload_change(change):
            print('Upload file')

            for name, file_info in self.geojson_upload.value.items():
                with open(name, 'r') as f:
                    self.geojson_data = json.load(f)

                # self._overlay_layer()
                # print(self.geojson_data['features'])
                # for feature in self.geojson_data['features']:
                #     feature['properties']['style'] = {
                #         'color': 'grey',
                #         'weight': 1,
                #         'fillColor': 'grey',
                #         'fillOpacity': 0.5
                #     }
                #     geo = GeoJSON(data=self.geojson_data, hover_style={'fillColor': 'red'}, name='Countries')
                #     self.m_top.add_layer(geo)
                #     # print(self.m_top)
                #     # print(self.m_top.basemap)
                self.geo_json = GeoJSON( data=self.geojson_data,
                                    style={'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.1, 'weight': 1},
                                    hover_style={'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5},
                                )
                # self.m_top.basemap = self.geo_json
                self.m_top.add_layer(self.geo_json)
                

       @debounce(0.2)
       def _observe_geojson(change):
            # print('print to metadata')
            for name, file_info in self.geojson_upload.value.items():
                # print(name)
                self.metadata['geojson_file'] = name
                self._update_widget_export()



       self.geojson_upload.observe(_on_upload_change, names='_counter') # plot into leaflet
       self.geojson_upload.observe(_observe_geojson) # add to metadata export
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

        header = HTML("<h3>Import tools for 1d to 2d maps</h3>", layout=Layout(height='auto'))
        header.style.text_align='center'
        details = HTML("For geophysical maps and 2d lines, import directly a geojson file", layout=Layout(height='auto'))


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

        # Create the two text boxes
        self.widget_latitude = widgets.Text(
            value=str(center[0]),
            description='Lat:'
        )

        self.widget_longitude = widgets.Text(
            value= str(center[1]),
            description='Lng:'
        )

        # Create a buton for GeoJson import
        vbox_geojson = self._widget_upload_GeoJSON_button()


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


        bmap = widgets.Button(
            description='Show on map',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )
        # display(b)

        out = widgets.Output()
        # display(out)

        def on_button_clicked(bmap):
            with out:
                clear_output()
                # self.m_top.clear_layers()
                # self.m_top = Map(
                #     zoom=-10, 
                #     basemap=basemaps.Esri.WorldTopoMap, 
                #     attribution_control=False, 
                #     zoom_control=True, 
                #     width='100%',
                #     fullscreenControl=True,
                #     # layout=Layout(height='800px'),
                #     flex=1
                #     )
                display(self.m_top)

        bmap.on_click(on_button_clicked)

        # Create the horizontal container containing the two textboxes
        hbox = widgets.HBox([self.widget_latitude, self.widget_longitude,vbox_geojson])

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
             For the choice of the method please report to <a href="https://agrogeophy.github.io/datasets/glossary.html">the online documentation glossary</a>
             ''')
        vbox = widgets.VBox([title])
        return vbox


    def _widget_method(self):
        method = widgets.RadioButtons(
            options=[
                'Geoelectrical - ERT',
                'Geoelectrical - TDIP',
                'Geoelectrical - sEIT',
                'Geoelectrical - SIP/EIS',
                'GPR',
                'EM',
                'Seismic',
            ],
            default='Geoelectrical - ERT',
            description='Method:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        # set initial metadata
        self.metadata['method'] = 'Geoelectrical - ERT'

        def _observe_method(change):
            self.metadata['method'] = method.value
            self._update_widget_export()

        method.observe(_observe_method)
        return method

    def _widget_measurement_type(self):
        type_measurement = widgets.RadioButtons(
            options=['Laboratory Measurement', 'Field Measurement'],
            default='Laboratory Measurement',
            description='Measurement type:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        # set initial metadata
        self.metadata['measurement_type'] = 'laboratory'

        def _observe_measurement_type(change):
            self.metadata['measurement_type'] = type_measurement.value
            self._update_widget_export()

        type_measurement.observe(_observe_measurement_type)
        return type_measurement

    def _widget_instrument(self):
        self.widget_instrument = widgets.Text(
            description='Instrument',
        )

        @debounce(0.2)
        def _observe_instrument(change):
            self.metadata['instrument'] = self.widget_instrument.value
            self._update_widget_export()

        self.widget_instrument.observe(_observe_instrument)
        return self.widget_instrument


    def _widget_datetime(self):
        widget_dt = widgets.DatePicker(
            description='Datetime of measurement',
            disabled=False
        )

        def _observe_dt(change):
            date = widget_dt.value
            if date is not None:
                self.metadata['date'] = date.isoformat()
                self._update_widget_export()

        widget_dt.observe(_observe_dt)
        return widget_dt

 
    #%% ERT metadata: Time_measure/ Elec_conf/ Elec_spacing
    def _widgets_ERT_doc(self):
        title = widgets.HTML('''
                <h3> ERT metadata </h3>
                <hr style="height:1px;border-width:0;color:black;background-color:gray">
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
        elec_config = widgets.RadioButtons(
            options=['1D', '2D','3D'],
            default='1D',
            description='Electrode configuration:',
            disabled=False,
            style={'description_width': 'initial'}
        )
        

        elec_config.layout.display   = 'none'
        if  self.metadata['method'] is 'Geoelectrical - ERT':
            elec_config.layout.display   = 'block'

        # set initial metadata
        # self.metadata['elec_config'] = '1D'

        def _observe_elec_config(change):
            self.metadata['elec_config'] = elec_config.value
            self._update_widget_export()

        elec_config.observe(_observe_elec_config)
        return elec_config



    def _widget_elec_geom(self):

        # Data examples
        my_columns = list(['elecs_geom', 'other'])
        df = pd.DataFrame(np.random.randint(0,100,size=(100, np.shape(my_columns)[0])), columns=my_columns)

        # Our filter generator
        def generate_filter(button):
            # Check if exist before creating
            new_widget = widgets.Text(description=select_definition.value) # Value from the user
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

        button = widgets.Button(description="Add")  
        # Define button and event
        button.on_click(generate_filter)

        # Where we will put all our filters
        filters = widgets.VBox()
        # Put Dropdown and button together
        choose_filter = widgets.VBox([select_definition, button, filters])





        return choose_filter


        # button = widgets.Button(description="Add elecs .XYZ")

        # def _gen_widget_ERT_geom(self):
        #     self.widget_elec_geom = widgets.Text(
        #         description='Free ERT metadata to add',
        #         style={'description_width': 'initial'}
        #         )
        #     # Append created filter
        #     filters.children=tuple(list(filters.children) + [new_filter])

        # def _observe_elec_geom(change):
        #     self.metadata['elec_geom'] = self.widget_elec_geom.value
        #     self._update_widget_export()

        #     self.widget_elec_geom.observe(_observe_elec_geom)

        # button.on_click(_gen_widget_ERT_geom)



    def _widget_elec_seq(self):
        elec_seq = widgets.RadioButtons(
            options=['Wenner', 'WS','user defined'],
            default='WS',
            description='Electrode sequence:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        # set initial metadata
        self.metadata['elec_seq'] = 'WS'

        def _observe_elec_seq(change):
            self.metadata['elec_seq'] = elec_seq.value
            self._update_widget_export()

        elec_seq.observe(_observe_elec_seq)
        return elec_seq

    def _widget_elec_spacing(self):
        self.widget_elec_spacing = widgets.Text(
            description='Electrode spacing:',
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_widget_elec_spacing(change):
            self.metadata['elec_spacing'] = self.widget_elec_spacing.value
            self._update_widget_export()

        self.widget_elec_spacing.observe(_observe_widget_elec_spacing)
        return self.widget_elec_spacing

    def _widget_free_ERT(self):
        self.widget_free_ERT = widgets.Text(
            description='Free ERT metadata to add',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_free_ERT(change):
            self.metadata['free_ERT'] = self.widget_free_ERT.value
            self._update_widget_export()

        self.widget_free_ERT.observe(_observe_free_ERT)
        return self.widget_free_ERT

    def _widget_upload_ERT(self):
        """upload ERT file and parse metadata
        """
        title = widgets.HTML(
        '<h2>upload ERT file<h2/>')
        text = widgets.HTML('''
        Infer all the ERT metadata from the ERT uploaded data
        ''')
        vbox = widgets.VBox([title, text])
        return vbox




    #%% EM metadata
    def _widgets_EM_doc(self):
        title = widgets.HTML('''
            <h3> EM metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-em-metadata">online EM metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox


    # Date_measure

    def _widget_coil_config(self):
        coil_config = widgets.RadioButtons(
            options=['VCP', 'VMD','PRP', 'HCP', 'HMD'],
            default='VCP',
            description='Coil orientation:',
            disabled=False,
            style={'description_width': 'initial'}
        )

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
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_coil_height(change):
            self.metadata['coil_height'] = self.widget_coil_height.value
            self._update_widget_export()

        self.widget_coil_height.observe(_observe_coil_height)
        return self.widget_coil_height

    def _widget_coil_spacing(self):
        coil_spacing = widgets.SelectMultiple(
            options=['0.2', '1','3'],
            description='Coil spacing:',
            disabled=False,
            style={'description_width': 'initial'}
        )

        # set initial metadata
        # self.metadata['coil_spacing'] = 'VCP'

        def _observe_coil_spacing(change):
            self.metadata['coil_spacing'] = coil_spacing.value
            self._update_widget_export()

        coil_spacing.observe(_observe_coil_spacing)
        return coil_spacing

    def _widget_free_EM(self):
        self.widget_free_EM = widgets.Text(
            description='Free EM metadata to add',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_free_EM(change):
            self.metadata['free_EM'] = self.widget_free_EM.value
            self._update_widget_export()

        self.widget_free_EM.observe(_observe_free_EM)
        return self.widget_free_EM

    def _widget_upload_EM(self):
        """upload ERT file and parse metadata
        """
        title = widgets.HTML(
        '<h2>upload EM file<h2/>')
        text = widgets.HTML('''
        Infer all the EM metadata from the ERT uploaded data
        ''')
        vbox = widgets.VBox([title, text])
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
        '<h2>upload json file<h2/>')
        text = widgets.HTML('''
        Replace all the field by the uploaded json fields
        ''')
        vbox = widgets.VBox([title, text])
        return vbox

    def _widget_upload_button(self):
       """Import pre-existing JSON file"""

       self.json_upload = widgets.FileUpload(
               accept='.json',  # Accepted file extension
               multiple=False  # True to accept multiple files upload else False
           )

       vbox = widgets.VBox([self.json_upload])


       def on_upload_change(change):
            print('Upload file')
            print(self.json_upload.value)

            for name, file_info in self.json_upload.value.items():
                with open(name) as json_file:
                    self.data_uploaded = json.load(json_file)

            self._parse_json()
            self._update_fields_values()

       self.json_upload.observe(on_upload_change, names='_counter')


       return vbox

    def _update_fields_values(self):
        """Update all fields from uploaded JSON"""
        json_tmp = json.dumps(self.data_uploaded, indent=0)
        mylist = json.loads(json_tmp)
        for i in enumerate(mylist):
            if hasattr(self, 'widget_' + str(i[1])):
               widget2fill = eval('self.widget_' + str(i[1]) )
               widget2fill.value = 'maxi {}'.format(self.data_uploaded[i[1]])



    def _parse_json(self):
        """Fill out metadata container (for export)"""
        for i in enumerate(self.data_uploaded):
            if hasattr(self, 'widget_' + i[1]):
                self.metadata[i[1]] = self.data_uploaded[i[1]]
            else:
                warning = 'metadata no matching:' + str(i[1])
                self.warnings.append(warning) 
                self._update_widget_log()


    def _widget_download_buttons(self):
       """Download JSON file"""

       self.download = widgets.ToggleButton(
                value=False,
                description='Download',
                disabled=False,
                button_style='', # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Download',
                icon='download' # (FontAwesome names without the `fa-` prefix)
            )

       vbox = widgets.VBox([self.download])

       def on_download_change(change): # read an display
            link2file = FileLink(r'json2import.json')
            linkwidget = widgets.HTML(
                        value="<a href={code}>link2file to click</a>".format(code=link2file),
                        placeholder='Some HTML',
                        description='Some HTML',
            )

            display(linkwidget)

       self.download.observe(on_download_change)

       return vbox

    def _widget_log(self):
        """Report errors
        """
        self.log = widgets.HTML()
        vbox = widgets.VBox(
            [
                widgets.HTML(
                    '<h2>Logger<h2/>'),
                widgets.HTML('''
                    <hr style="height:1px;border-width:0;color:black;background-color:gray">
                    Before downloading your metadata pay attention to the following warmings:
                    '''),
                    self.log
            ]
        )

        return vbox

    def _update_widget_log(self):
        """Report errors
        """
        warnings_raw = json.dumps(self.warnings)
        self.log.value = "<pre>{}</pre>".format(html.escape(warnings_raw))
        #self.log.value  = ' '.join(self.warnings)
        # self.log.value  = self.warnings

    def manage(self):

        self.vbox_guidelines = widgets.VBox(self.widget_guidelines)

        self.vbox = widgets.VBox(self.widget_objects)
        self.vbox_survey = widgets.VBox(self.widget_survey)
        self.vbox_survey_map = widgets.VBox(self.widget_survey_map)

        self.vbox_ERT = widgets.VBox(self.widget_ERT)
        self.vbox_upload_ERT_data = widgets.VBox(self.widget_ERT_upload)

        self.vbox_EM = widgets.VBox(self.widget_EM)
        self.vbox_upload_EM_data = widgets.VBox(self.widget_EM_upload)

        self.vbox_quality = widgets.VBox(self.widget_quality)
        self.vbox_sampling = widgets.VBox(self.widget_sampling)
        self.vbox_upload = widgets.VBox(self.widget_upload)
        self.vbox_export = widgets.VBox(self.widget_export)
        self.vbox_logger = widgets.VBox(self.widget_logger)
        #self.vbox_data_structure = widgets.VBox(self.widget_data_structure)


        accordion_tab0 = widgets.Accordion(children=[self.vbox, self.vbox_survey, self.vbox_survey_map])
        accordion_tab0.set_title(0, 'Owner')
        accordion_tab0.set_title(1, 'General Survey description')
        accordion_tab0.set_title(2, 'Geolocalisation')

        accordion_tab_ERT = widgets.Accordion(children=[self.vbox_upload_ERT_data])
        accordion_tab_ERT.set_title(0, 'Upload')

        accordion_tab_EM = widgets.Accordion(children=[self.vbox_upload_EM_data])
        accordion_tab_EM.set_title(0, 'Upload')

        vbox_tab0 = widgets.VBox([self.vbox_guidelines,accordion_tab0])
        vbox_tab_ERT = widgets.VBox([self.vbox_ERT,accordion_tab_ERT])        
        vbox_tab_EM = widgets.VBox([self.vbox_EM,accordion_tab_EM])
                          
        #self.vbox_import = widgets.VBox(self.upload_widget)
        # display(self.vbox)
        # self.metadata['test1'] = 'balbaba'
        # self.metadata['test2'] = 832       
        
        
        self._update_widget_export()


        tab  = widgets.Tab(children = [vbox_tab0, 
                                       vbox_tab_ERT,
                                       vbox_tab_EM,                                       
                                       self.vbox_quality,
                                       self.vbox_sampling,
                                       #self.vbox_data_structure,
                                       self.vbox_upload,
                                       self.vbox_export,
                                       self.vbox_logger
                                      ])
        tab.set_title(0, 'Home')
        tab.set_title(1, 'ERT')
        tab.set_title(2, 'EM')
        tab.set_title(3, 'Quality')
        tab.set_title(4, 'Sampling')
        tab.set_title(5, 'Upload')
        tab.set_title(6, 'Export')
        #tab.set_title(5, 'Data structure')
        tab.set_title(7, 'Logger')

        display(tab)
