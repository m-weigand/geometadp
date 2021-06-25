# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
from IPython.display import display_html
def restartkernel() :
    display_html("<script>Jupyter.notebook.kernel.restart()</script>",raw=True)
restartkernel()
import IPython

import os 
#os.chdir('../test_ERT_TL/')
p#rint(os.getcwd())

# %% [markdown]
# ## Full GUI

# %%
from lib.geometadp import md_manager
obj = md_manager.geo_metadata()
obj.manage()

# %%
import ipywidgets as widgets
up = widgets.FileUpload()

def onclick(change):
    #print(change.new)
    #print(change.new)
    uploaded_file = up.value[0]
    uploaded_file["size"]
    uploaded_file.size

up.observe(onclick,'value')

up



# %%

# %%

# %%
