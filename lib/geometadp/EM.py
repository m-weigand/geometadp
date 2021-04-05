import ipywidgets as widgets
from emagpy import Problem

"""
EM tab

"""

from lib.geometadp.md_manager import _update_widget_export

def _widgets_EM_doc():
    title = widgets.HTML('''
        <h3> EM metadata </h3>
        <hr style="height:1px;border-width:0;color:black;background-color:gray">
        <b> Minimum required metadata. </b>
        Please refer to the <a href="https://agrogeophy.github.io/catalog/schema_documentation.html#table-em-metadata">online EM metadata documentation </a>
         ''')
    vbox = widgets.VBox([title])
    return vbox

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
        _update_widget_export()

    coil_config.observe(_observe_coil_config)
    return coil_config
