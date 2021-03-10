import ipywidgets as widgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
from ipywidgets import FileUpload, Button
import sys
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

class geo_metadata(object):
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.metadata = {}
        self.metadata['Metadata to fill'] = 'init value'
        self.widget_upload = []
        self.widget_export = []
        self._prepare_widgets()

    def _prepare_widgets(self):
        self.widget_upload.append(self._widget_upload_json())
        self.widget_upload.append(self._widget_import_buttons())
        self.widget_upload.append(self.widget_test_md2fill())

        #%% Import/ Export
        self.widget_export.append(self._widget_export())

    def widget_test_md2fill(self):

        self.widget_md2fill = widgets.Text(
            description='Metadata to fill',
            value = self.metadata['Metadata to fill'],
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_test_md2fill(change):
            self.metadata['Metadata to fill'] = self.widget_md2fill.value
            self._update_widget_export()

        self.widget_md2fill.observe(_observe_test_md2fill)


        print('json file uploaded?: ' + str(hasattr(self, 'data_uploaded'))) # check if data has been uploaded
        if hasattr(self, 'data_uploaded'):
            print('replace init value by metadata uploaded from JSON file')

            @debounce(0.2)
            def _on_change(change):
                self.widget_md2fill.value = self.metadata['Metadata to fill'] # change initial widget value
            self.widget_md2fill.observe(_on_change)

        return self.widget_md2fill

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

    def _widget_import_buttons(self):
       """Import pre-existing JSON file"""

       self.json_upload = widgets.FileUpload(
               accept='.json',  # Accepted file extension
               multiple=False  # True to accept multiple files upload else False
           )

       vbox = widgets.VBox([self.json_upload])


       def on_upload_change(change): # read an display
            print('Upload file')

            for name, file_info in self.json_upload.value.items():
                with open(name) as json_file:
                    self.data_uploaded = json.load(json_file)
            print(json.dumps(self.data_uploaded, indent=4))


            self._parse_json()
            self._update_widget_values()

       self.json_upload.observe(on_upload_change, names='_counter')


       return vbox

    def _update_widget_values(self):
        self.widget_md2fill.value = 'maxi {}'.format(
            self.data_uploaded['method']
        )
    	# self.widget_test_md2fill()
    #     print(hasattr(self, 'data_uploaded'))
    #     if hasattr(self, 'data_uploaded'):
    #         print('new metadata from uploaded')
    #         @debounce(0.2)
    #         def _on_change(change):
    #             self.widget_md2fill.value = self.metadata['Metadata to fill']
    #             #print(widget_parse_json.value)
    #         self.widget_md2fill.observe(_on_change)

    #     return self.widget_md2fill

    def _parse_json(self):
        """Fill out metadata container (for export)"""
        self.metadata['Metadata to fill'] = self.data_uploaded['method']

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
        import html
        # self.widget_export.value = metadata_str
        self.export.value = "<pre>{}</pre>".format(
            html.escape(metadata_str))


    def manage(self):

        self._update_widget_export()

        self.vbox_upload = widgets.VBox(self.widget_upload)
        self.vbox_export = widgets.VBox(self.widget_export)


        tab  = widgets.Tab(children = [self.vbox_upload,
                                       self.vbox_export
                                      ])
        tab.set_title(0, 'Upload')
        tab.set_title(1, 'Export')

        display(tab)