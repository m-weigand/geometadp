import sys
import ipywidgets as widgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
from IPython.core.display import display
import ipydatetime

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

class _widget_select_jsonfile(object):

    def __init__(self, output_dict, key, help_text, callback=None):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter("json files (*.json)")
        filenames = QStringList()



class _widget_select_directory(object):
    """Use the QT5 widget to select a directory
    """
    def __init__(self, output_dict, key, help_text, callback=None):
        self.dialog = QFileDialog(None)
        self.dialog.setFileMode(QFileDialog.Directory)
        self.dialog.setOption(self.dialog.ShowDirsOnly, True)
        self.output_dict = output_dict
        self.key = key
        self.help_text = help_text
        self.callback = callback

    def _select_dir(self):
        fname = self.dialog.getExistingDirectory(
            None,
            self.help_text,
            # '/',
        )
        return fname

    def _button_click(self, x):
        directory = self._select_dir()
        self.label.value = directory
        self.output_dict[self.key] = directory
        if self.callback is not None:
            self.callback()

    def get_widget(self):

        button = widgets.Button(description=self.help_text)
        self.label = widgets.Label()

        button.on_click(self._button_click)
        return widgets.HBox([button, self.label])


class geo_metadata(object):
    def __init__(self):
        self.app = QApplication(sys.argv)

        # this stores the actual values exported to json/xml
        self.metadata = {}

        # stores the various widget objects. They are shown in this order
        self.widget_objects = []

        self._prepare_widgets()

    def _prepare_widgets(self):
        self.widget_objects.append(self._widget_header())
      
        #%% REPORT: title/authors
        self.widget_objects.append(self._widget_report_title())
        self.widget_objects.append(self._widget_report_authors())
        self.widget_objects.append(self._widget_owner())
        self.widget_objects.append(self._widget_email())
        self.widget_objects.append(self._widget_dataset_DOI())
        self.widget_objects.append(self._widget_variables())
        self.widget_objects.append(self._widget_location_bounds())

        # SURVEY: method/type/instrument
        self.widget_objects.append(self._widgets_survey_doc())
        self.widget_objects.append(self._widget_method())
        self.widget_objects.append(self._widget_measurement_type())

        #%% ERT metadata: Date_measure/ Time_measure/ Elec_conf/ Elec_spacing
        self.widget_objects.append(self._widgets_ERT_doc())
        self.widget_objects.append(self._widget_instrument())
        self.widget_objects.append(self._widget_datetime())
        # self.widget_objects.append(self._widget_time())
        self.widget_objects.append(self._widget_elec_config())
        self.widget_objects.append(self._widget_elec_seq())
        self.widget_objects.append(self._widget_elec_spacing())
        self.widget_objects.append(self._widget_free_ERT())

        #%% EM metadata
        self.widget_objects.append(self._widgets_EM_doc())
        self.widget_objects.append(self._widget_coil_config())
        self.widget_objects.append(self._widget_coil_height())
        self.widget_objects.append(self._widget_coil_spacing())
        self.widget_objects.append(self._widget_free_EM())

        #%% DATA QUALITY ASSESSEMENT metadata
        self.widget_objects.append(self._widgets_quality_doc())
        self.widget_objects.append(self._widget_peer_reviewed())
        self.widget_objects.append(self._widget_peer_reviewer_contact())
        self.widget_objects.append(self._widget_replicate_datasets())
        self.widget_objects.append(self._widget_comparison_ref_data())
        self.widget_objects.append(self._widget_ref_data())
        self.widget_objects.append(self._widget_free_quality())

        #%% SAMPLING
        self.widget_objects.append(self._widgets_sampling_doc())
        self.widget_objects.append(self._widget_free_sampling())

        #%% DATA structure 
        self.widget_objects.append(self._widgets_dataset_structure_doc())
        self.widget_objects.append(self._widget_data_directory())
        self.widget_objects.append(self._widget_output_directory())

        #%% Export 
        self.widget_objects.append(self._widget_export())

    def _widget_header(self):
        """Show the header of the data mangement gui that explains the basic concepts
        """
        title = widgets.HTML(
            '<h2>Data Manager and Metadata Collector for CGAGS - DEV version <h2/>')
        text = widgets.HTML('''
            This gui is designed to help with the initial preparation of one
            geophysical dataset. Starting from one or multiple input
            directories, a cleanly structured output directory is generated
            (without deleting any input files).

            <ol>
             <li>Copy measurement data files and auxiliary files (pictures,
             etc.) into the output directory structure</li>
             <li>Generate suitable metadata from user input</li>
             <li>Write this metadata into the directory structure, making it
             ready for further distribution</li>
            </ol>

            <b>Hit ENTER after finishing any one-line text input!<b />
             <hr
             style=
             "height:5px;border-width:0;color:black;background-color:gray">
        ''')

        vbox = widgets.VBox([title, text])
        return vbox

#%% REPORT: title/authors

    def _widget_report_title(self):
        self.widget_report_title = widgets.Text(
            description='Short title description of the dataset',
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_report_title(change):
            self.metadata['report_title'] = self.widget_report_title.value
            self._update_widget_export()

        self.widget_report_title.observe(_observe_report_title)
        return self.widget_report_title

    def _widget_report_authors(self):
        self.widget_report_authors = widgets.Text(
            description='Reporting authors names',
            style={'description_width': 'initial'}
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

    def _widget_location_bounds(self):
        self.widget_location_bounds = widgets.Text(
            description='North, West, East, and South Bounding Latitudes:',
            style={'description_width': 'initial'}
            )

        @debounce(0.2)
        def _observe_location_bounds(change):
            self.metadata['location_bounds'] = self.widget_location_bounds.value
            self._update_widget_export()

        self.widget_location_bounds.observe(_observe_location_bounds)
        return self.widget_location_bounds

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


    def _widget_data_directory(self):
        data_directory = _widget_select_directory(
            self.metadata, 'data_dir', 'Data input directory',
            callback=self._update_widget_export
        )
        data_widget = data_directory.get_widget()

        return data_widget

    def _widget_output_directory(self):
        output_directory = _widget_select_directory(
            self.metadata, 'output_dir', 'Output directory',
            callback=self._update_widget_export
        )
        output_widget = output_directory.get_widget()
        return output_widget


    def _widget_export(self):
        """Preview of metadata export"""

        self.widget_export = widgets.HTML()
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
                self.widget_export
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
        import html
        # self.widget_export.value = metadata_str
        self.widget_export.value = "<pre>{}</pre>".format(
            html.escape(metadata_str))

    def manage(self):
        self.vbox = widgets.VBox(self.widget_objects)
        # display(self.vbox)

        # self.metadata['test1'] = 'balbaba'
        # self.metadata['test2'] = 832

        self._update_widget_export()
        tab  = widgets.Tab(children = [self.vbox, self.vbox,self.widget_export])
        tab.set_title(0, 'Step1')
        tab.set_title(1, 'Step2')
        tab.set_title(2, 'Export')

        display(tab)
