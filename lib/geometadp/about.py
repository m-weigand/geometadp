import ipywidgets as widgets
"""
About tab
"""

def ulify(elements):
    string = "<ul>\n"
    string += "\n".join(["<li>" + str(s) + "</li>" for s in elements])
    string += "\n</ul>"
    return string

def _widget_about():
    """References
    """
    header_version = widgets.HTML(
        '''<h3>Version<h3/>
           <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
    with open('setup.py') as f:
        for line in f:
            if line.startswith('version'):
                _, _, version = line.replace("'", '').split()
                break
        f.close()


    version_str = "\n".join(['Geometadp version: ' + "<b>" + str(version) + "</b>"])
    current_version = widgets.HTML(version_str)

    vbox_version = widgets.VBox([header_version,current_version])

    header_refs= widgets.HTML(
        '''<h3>References<h3/>
           <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
    refs = ['Richards, J. D. (1997). Preservation and re-use of digital data: the role of the Archaeology Data Service. Antiquity, 71(274), 1057.',
            'Adrian, B. M. (2014, December). National geological and geophysical data preservation program: successes and lessons learned. In AGU Fall Meeting Abstracts (Vol. 2014, pp. IN23A-3723).']
    refs_str= widgets.HTML(ulify(refs))
    vbox_refs = widgets.VBox([header_refs,refs_str])


    header_cite = widgets.HTML(
        '''<h3>Cite us<h3/>
           <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
    vbox_cite = widgets.VBox([header_cite])



    with open('LICENSE') as f:
        for line in f:
            license_str = f.read()
        f.close()

    header_license = widgets.HTML(
        '''<h3>License<h3/>
           <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
    license_str = widgets.HTML(license_str)
    vbox_license = widgets.VBox([header_license,license_str])


    header_interpolability = widgets.HTML(
        '''<h3>Interpolability<h3/>
           <hr style="height:1px;border-width:0;color:black;background-color:gray">
        ''')
    vbox_interpolability = widgets.VBox([header_interpolability])

    vbox = widgets.VBox([vbox_version, vbox_refs, vbox_cite, vbox_license, vbox_interpolability])

    return vbox