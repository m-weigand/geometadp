import ipywidgets as widgets
from emagpy import Problem

"""
EM tab

"""


class EM_widgets(object):

    def __init__(self):
        self.metadata = {}
        self.warnings = [] # report all the warnings

        self.widget_EM = [] # min required EM metadata
        self.widget_EM_upload = []
        self.widget_EM_files = []

        self._prepare_widgets_EM()
        self._manage_EM()


    def _prepare_widgets_EM(self):

        #%% EM metadata
        self.widget_EM.append(self._widgets_EM_doc())
        self.widget_EM.append(self._widget_instrument_EM())
        self.widget_EM.append(self._widget_datetime_EM())
        self.widget_EM.append(self._widget_coil_config())
        self.widget_EM.append(self._widget_coil_height())
        self.widget_EM.append(self._widget_coil_spacing())
        self.widget_EM.append(self._widget_description_EM())
        #self.widget_EM.append(self._timelapse_option())

        self.widget_EM_upload.append(self._widget_upload_EM_button())  # upload EM data from emagpy
        self.widget_EM_files.append(self._widgets_EM_add_file())


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

    def _widgets_EM_add_file(self):


        columns = list(['raw file','processed file'])
        vbox_EM_add_files = self._widget_add_external_ressource(columns,'EM')

        vbox_files = self._widgets_related_external_resources_files_doc()
        vbox_figs = self._widgets_related_external_resources_fig_doc()
        vbox_codes = self._widgets_related_external_resources_codes_doc()

        vbox = widgets.VBox([vbox_files,vbox_EM_add_files,vbox_figs,vbox_codes])

        return vbox

    def _manage_EM(self):
    
        self.vbox_EM = widgets.VBox(self.widget_EM)
        self.vbox_upload_EM_data = widgets.VBox(self.widget_EM_upload)
        self.vbox_upload_EM_files = widgets.VBox(self.widget_EM_files)

        accordion_tab_EM = widgets.Accordion(children=[self.vbox_upload_EM_data,
                                                       self.vbox_upload_EM_files],
                                                       selected_index = None)
        accordion_tab_EM.set_title(0, 'Upload EM file')
        accordion_tab_EM.set_title(1, 'Related data ressources')

        self.vbox_tab_EM = widgets.VBox([self.vbox_EM,accordion_tab_EM])
