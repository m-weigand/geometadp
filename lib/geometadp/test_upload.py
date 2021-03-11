import ipywidgets as widgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
import json
import dicttoxml
from ipywidgets import FileUpload, Button
import sys
import asyncio
import html

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
        self.warnings = [] # report all the warmings

        self.widget_upload = []
        self.widget_export = []
        self.widget_logger = []
        self._prepare_widgets()

    def _prepare_widgets(self):
        self.widget_upload.append(self._widget_upload_json())
        self.widget_upload.append(self._widget_import_buttons())
        self.widget_upload.append(self._widget_method())

        #%% Import/ Export
        self.widget_export.append(self._widget_export())
        self.widget_export.append(self._widget_download_buttons())

        #%% Logger
        self.widget_logger.append(self._widget_log())



    def _widget_method(self):

        self.widget_method = widgets.Text(
            description='Metadata to fill',
            style={'description_width': 'initial'}
        )

        @debounce(0.2)
        def _observe_method(change):
            self.metadata['method'] = self.widget_method.value
            self._update_widget_export()

        self.widget_method.observe(_observe_method)

        return self.widget_method

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


    def print_ul(self, elements):
        print("<ul>")
        for s in elements:
                ul = "<li>" + str(s) + "</li>"
                print(ul)
        print("</ul>")


    def _update_widget_log(self):
        """Report errors
        """
        warnings_raw = json.dumps(self.warnings)
        self.log.value = "<pre>{}</pre>".format(html.escape(warnings_raw))
        #self.log.value  = ' '.join(self.warnings)
        # self.log.value  = self.warnings


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
            #print(json.dumps(self.data_uploaded, indent=4))


            self._parse_json()
            self._update_fields_values()

       self.json_upload.observe(on_upload_change, names='_counter')


       return vbox

    def _update_fields_values(self):
        # for i in enumerate(self.data_uploaded):

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
            from IPython.display import FileLink
            link2file = FileLink(r'json2import.json')
            linkwidget = widgets.HTML(
                        value="<a href={code}>link2file to click</a>".format(code=link2file),
                        placeholder='Some HTML',
                        description='Some HTML',
            )

            display(linkwidget)

       self.download.observe(on_download_change)

       return vbox


    def manage(self):

        self._update_widget_export()

        self.vbox_upload = widgets.VBox(self.widget_upload)
        self.vbox_export = widgets.VBox(self.widget_export)
        self.vbox_logger = widgets.VBox(self.widget_logger)


        tab  = widgets.Tab(children = [self.vbox_upload,
                                       self.vbox_export,
                                       self.vbox_logger
                                      ])
        tab.set_title(0, 'Upload')
        tab.set_title(1, 'Export')
        tab.set_title(2, 'Log')

        display(tab)