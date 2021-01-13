# Geophysical Metadata Management using a Juypter Notebook

## Usage

A full Anaconda install should provide all packages required to run the
metadata manager.

Open a new Jupyter Notebook (Python 3 >= 3.7) and execute the
following code within on cell:

	!pip install git+https://github.com/m-weigand/geometadp
	import IPython
	IPython.display.clear_output()
	%gui qt
	import geometadp
	obj = geometadp.geo_metadata()
	obj.manage()

.. note::

	The first three lines do install the metadata manager and can be omitted
	once it is installed.

![Screenshot of the CAGS metadata manager](https://github.com/agrogeophy/geometadp/blob/CAGS_metadata_Manager.png?raw=true)

## Wishlist

* import functionality: import a given JSON-file and edit it
