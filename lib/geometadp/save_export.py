import ipywidgets as widgets
import xarray as xr
from ipyfilechooser import FileChooser
from ipywidgets import Layout, HBox, VBox, FloatText
from emagpy import Problem
import pandas as pd
"""
EM tab

"""

class netcdf_export(object):

    def __init__(self):
        self._widget_upload_EM_button()

    def _widgets_EM_doc():
        title = widgets.HTML('''
            <h3> EM metadata </h3>
            <hr style="height:1px;border-width:0;color:black;background-color:gray">
            <b> Minimum required metadata. </b>
            Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-em-metadata">online EM metadata documentation </a>
             ''')
        vbox = widgets.VBox([title])
        return vbox

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

       vbox = widgets.VBox([vbox_doc,self.EM_upload])

       display(vbox)

       def on_upload_change(change):
            #for name, file_info in self.EM_upload.value.items():
            name = self.EM_upload.selected

            df = pd.read_csv(name)
            df.head() # see how the header are formatted
            xx=df.to_xarray()
            print(xx)
       #self.EM_upload.observe(on_upload_change, names='_counter')
       self.EM_upload.register_callback(on_upload_change)


       return vbox