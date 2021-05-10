import ipywidgets as widgets
import xarray as xr
import exdir
from ipyfilechooser import FileChooser
from ipywidgets import Layout, HBox, VBox, FloatText
from emagpy import Problem
import pandas as pd
import numpy as np
import zipfile
import tempfile
import shutil
import os 
import expipe
from expipe import widgets as widgets_ex
from expipe.widgets import display as display_ex

from lib.geometadp.ownership import *
import asyncio

import json
import dicttoxml
import html

"""
Simple GUI demonstrating the upload/save to structured folder pipeline

"""
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


class dir_struct(object):

    def __init__(self):

        # this stores the actual values exported to json/xml
        self.metadata = {}

        self.widget_add2pipe = []
        self.widget_EM = []
        self.widget_EM_upload = []
        self.widget_EM_files = []

        self.widget_dir_struct = []

        self.widget_modules = []
        self.widget_entities = []
        self.widget_actions = []
        self._prepare_widgets()

    def _prepare_widgets(self):

        self.widget_add2pipe.append(self._create_project_button())
        self.widget_add2pipe.append(self._load_project_button())
        self.widget_add2pipe.append(self._action_button())
        self.widget_add2pipe.append(self._action_from_template_button())
        self.widget_add2pipe.append(self._widget_export())


        #%% EM metadata
        self.widget_EM.append(self._widgets_EM_doc())
        self.widget_EM.append(self._widget_instrument())
        self.widget_EM.append(self._widget_datetime())
        self.widget_EM.append(self._widget_coil_config())
        self.widget_EM.append(self._widget_coil_height())
        self.widget_EM.append(self._widget_coil_spacing())
        self.widget_EM.append(self._widget_description_EM())
        #self.widget_EM.append(self._timelapse_option())

        self.widget_EM_upload.append(self._widget_upload_EM_button())  # upload EM data from emagpy
        #self.widget_EM_files.append(self._widgets_EM_add_file())

        #self.widget_add2pipe.append(self._entities_button())
        #self.widget_add2pipe.append(self._modules_button())

        self.widget_dir_struct.append(self._dir_struct_doc())
        self.widget_dir_struct.append(self._widget_upload_data_type0())
        self.widget_dir_struct.append(self._widget_upload_figures_type0())
        self.widget_dir_struct.append(self._widget_upload_data_type1())
        self.widget_dir_struct.append(self._widget_upload_figures_type1())

        self.widget_modules.append(self._pipe_modules())
        self.widget_entities.append(self._pipe_entities())
        self.widget_actions.append(self._pipe_actions())


    def _create_project_button(self):
        # create a project
        title = widgets.HTML('''
            <h3> Create a new project </h3>
             ''')

        action_button = widgets.Button(
            description='Create project',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        out = widgets.Output()

        def on_button_clicked(bmap):
            with out:
                #add_expipe_action()
                self.project = expipe.create_project('project_test2')

        action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([title, action_button])

        return vbox

    def _load_project_button(self):
        # load a project (just need to set the path)
        title = widgets.HTML('''
            <h3> Load project </h3>
             ''')

        action_button = widgets.Button(
            description='Load project',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        #out = widgets.Output()

        #def on_button_clicked(bmap):
            #with out:
                #add_expipe_action()

        #action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([title, action_button])

        return vbox


    def _action_button(self):
        # add an action
        title = widgets.HTML('''
            <h3> Add action </h3>
            Actions represent things that have happened at a specific point in time, such as an experiment, an analysis, or a simulation run.
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        action_button = widgets.Button(
            description='Add an action',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        #out = widgets.Output()

        #def on_button_clicked(bmap):
            #with out:
                #add_expipe_action()

        #action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([title, action_button])

        return vbox

    def _action_from_template_button(self):
        # add an action

        action_template_button = widgets.Button(
            description='Add an action from template',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        #out = widgets.Output()

        #def on_button_clicked(bmap):
            #with out:
                #add_expipe_action()

        #action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([action_template_button])

        return vbox



    def _entities_button(self):
        # add an action
        title = widgets.HTML('''
            <h3> Add entity </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        action_button = widgets.Button(
            description='Add an action',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        #out = widgets.Output()

        #def on_button_clicked(bmap):
            #with out:
                #add_expipe_action()

        #action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([title, action_button])

        return vbox

    def _modules_button(self):
        # add an action
        title = widgets.HTML('''
            <h3> Make an action to your project </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')

        action_button = widgets.Button(
            description='Add an action',
            disabled=False,
            button_style='info',
            tooltip='Click me',
            icon='check'
        )

        #out = widgets.Output()

        #def on_button_clicked(bmap):
            #with out:
                #add_expipe_action()

        #action_button.on_click(on_button_clicked)

        vbox = widgets.VBox([title, action_button])

        return vbox

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


    def _widget_instrument(self):
        self.widget_instrument = widgets.Text(
            description='Instrument',
            style=style,
            layout=layout)

        @debounce(0.2)
        def _observe_instrument(change):
            self.metadata['instrument'] = self.widget_instrument.value
            self._update_widget_export()
            self._add_metadata_to_Expipe(type_register='module',module_name='EM acquisition parameters',meta_key='instrument')
        self.widget_instrument.observe(_observe_instrument)
        return self.widget_instrument

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
            self._add_metadata_to_Expipe(type_register='module',module_name='EM acquisition parameters',meta_key='coil_config')

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
            self._add_metadata_to_Expipe(type_register='module',module_name='EM acquisition parameters',meta_key='coil_height')

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
            self._add_metadata_to_Expipe(type_register='module',module_name='EM acquisition parameters',meta_key='coil_spacing')

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
            self._add_metadata_to_Expipe(type_register='module',module_name='EM acquisition parameters',meta_key='description_EM')

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


    def _dir_struct_doc(self):
        title = widgets.HTML('''
            <h3> Upload files and save it to a structured directory </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
             ''')
        vbox = widgets.VBox([title])
        return vbox

    def _widget_upload_data_type0(self):
        """upload EM file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>Upload data type 0 <h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
        self.data0 = FileChooser(use_dir_icons=True)
        self.data0.title = '<b>data type 0</b>'

        vbox = widgets.VBox([title,self.data0])

        def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.data0.selected
            self._add_to_Exdir(name, target_dir='data', level_dir='type0')
            self._add_file_to_Expipe(name, target_dir='data', level_dir='type0')
            #self._add_to_Zip(name, target_dir='data', level_dir='type0')

        self.data0.register_callback(on_upload_change)

        return vbox

    def _widget_upload_figures_type0(self):
        """upload EM file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>Upload figures type 0 <h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
        self.fig0 = FileChooser(use_dir_icons=True)
        self.fig0.title = '<b>figure type 0</b>'

        vbox = widgets.VBox([title,self.fig0])

        def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.fig0.selected
            self._add_to_Exdir(name, target_dir='fig', level_dir='type0')
            self._add_file_to_Expipe(name, target_dir='fig', level_dir='type0')
            #self._add_to_Zip(name, target_dir='fig', level_dir='type0')
            #self._display()
            
        self.fig0.register_callback(on_upload_change)


        return vbox


    def _widget_upload_data_type1(self):
        """upload EM file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>Upload data type 1 <h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')

        self.data1 = FileChooser(use_dir_icons=True)
        self.data1.title = '<b>data type 1</b>'

        vbox = widgets.VBox([title,self.data1])

        def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.data0.selected
            self._add_to_Exdir(name, target_dir='data', level_dir='type1')
            self._add_file_to_Expipe(name, target_dir='data', level_dir='type1')
            #self._add_to_Zip(name, target_dir='data', level_dir='type1')

        self.data0.register_callback(on_upload_change)

        return vbox

    def _widget_upload_figures_type1(self):
        """upload EM file and parse metadata
        """
        title = widgets.HTML(
        '''<h5>Upload figures type 1 <h5/>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
        self.fig1 = FileChooser(use_dir_icons=True)
        self.fig1.title = '<b>figure type 1</b>'

        vbox = widgets.VBox([title,self.fig1])

        def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.fig1.selected
            print(name)
            self._add_to_Exdir(name, target_dir='fig', level_dir='type1')
            self._add_file_to_Expipe(name, target_dir='fig', level_dir='type1')
            #self._add_to_Zip(name, target_dir='fig', level_dir='type1')

        self.fig1.register_callback(on_upload_change)

        return vbox

    def _add_to_Exdir(self,name,target_dir,level_dir):
        """_add_to_Exdir
        """
        experiment = exdir.File("experiment.exdir")
        group = experiment.require_group(level_dir)
        #print(group.path)
        data = np.arange(10)
        dataset = group.require_dataset(target_dir, data=data)
        group.attrs["room_number"] = 1234
        dataset.attrs["recoring_date"] = "2018-02-04"


    def _add_data_to_Expipe(self,module_name,meta_key):
        """_add_to_Exdir
        """
        print('test _add_data_to_Expipe')



    def _add_metadata_to_Expipe(self,type_register,module_name,meta_key):
        """_add_to_Exdir
        """
        self.project = expipe.require_project('project_test')

        if type_register == 'module':
          self.project.require_module(name=module_name, contents={meta_key:{self.metadata[meta_key]}})

        # Entities represent physical or conceptual things, such as experimental equipment or subjects (like rats and mice)
        # Actions represent things that have happened at a specific point in time, such as an experiment, an analysis, or a simulation run.
        # A Module holds metadata in key-value form, which is similar to a map or hash table 


    def _add_file_to_Expipe(self,name,target_dir,level_dir):
        """_add_to_Exdir
        """

        self.project = expipe.require_project('project_test')
        self.project.modules['project-module'] = {"environment":{"type": "laboratory"}, "method":{"type": "EM"}}
        entity = self.project.create_entity('equipment') 
        action = self.project.create_action('acquisition') 
        action.type = 'Collection of dataset'
        # Entities represent physical or conceptual things, such as experimental equipment or subjects (like rats and mice)
        # Actions represent things that have happened at a specific point in time, such as an experiment, an analysis, or a simulation run.
        # A Module holds metadata in key-value form, which is similar to a map or hash table 

    def _pipe_modules(self):
        """ display modules
        """
        self.project = expipe.require_project('project_test')
        modules = display_ex.modules_view(self.project)

        return modules

    def _pipe_entities(self):
        """ display entities
        """
        self.project = expipe.require_project('project_test')
        entities = display_ex.entities_view(self.project)

        return entities

    def _pipe_actions(self):
        """ display actions
        """
        self.project = expipe.require_project('project_test')
        actions = display_ex.actions_view(self.project)

        return actions



    def _add_to_hdf5(self,name,target_dir,level_dir):
        """_add_to_Exdir
        """
        hf = h5py.File('data.h5', 'w')
        data = np.arange(10)
        g1 = hf.create_group(level_dir)
        g1.create_dataset(target_dir, data=data)
        hf.close()

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


    def manage(self):



        vbox_add2pipe= widgets.VBox(self.widget_add2pipe)

        vbox_EM= widgets.VBox(self.widget_EM)

        vbox_dir_struct = widgets.VBox(self.widget_dir_struct)
        vbox_modules = widgets.VBox(self.widget_modules)
        vbox_entities = widgets.VBox(self.widget_entities)
        vbox_actions = widgets.VBox(self.widget_actions)


        accordion_pipelines = widgets.Accordion(children=[vbox_modules, 
                                                          vbox_entities, 
                                                          vbox_actions],
                                                          selected_index = None)
        accordion_pipelines.set_title(0, 'Modules')
        accordion_pipelines.set_title(1, 'Entities')
        accordion_pipelines.set_title(2, 'Actions')

        tab  = widgets.Tab(children = [vbox_add2pipe,
                                       vbox_EM,
                                       vbox_dir_struct, 
                                       accordion_pipelines
                                      ])

        tab.set_title(0, 'Create pipeline')
        tab.set_title(1, 'Modules EM')
        tab.set_title(2, 'Upload datasets')
        tab.set_title(3, 'Pipelines history')

        display(tab)
