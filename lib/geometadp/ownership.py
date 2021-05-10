import ipywidgets as widgets
"""
Ownership widgets
"""
# some css
style = {'description_width': '300px'}
layout = {'width': 'auto'}


def widget_report_title():
    widget_report_title = widgets.Text(
        description='Short title description of the dataset',
        style=style,
        layout=layout)
    widget_report_title.add_class("box_style")

    return widget_report_title

def _widget_report_authors(self):
    self.widget_report_authors = widgets.Text(
        description='Reporting authors names',
        style=style,
        layout=layout)
    return self.widget_report_authors

def _widget_owner(self):
    self.widget_owner = widgets.Text(
        description='Owner:',
        style=style,
        layout=layout)

    return self.widget_owner

def _widget_email(self):
    self.widget_email = widgets.Text(
        description='Email:',
        style=style,
        layout=layout)

    return self.widget_email

def _widget_dataset_DOI(self):
    self.widget_dataset_DOI = widgets.Text(
        description='Dataset DOI:',
        style=style,
        layout=layout)

    return self.widget_dataset_DOI
