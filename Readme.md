# Geophysical Metadata Management using a Juypter Notebook

## Usage

A full Anaconda install should provide all packages required to run the
metadata manager.




Open a new Jupyter Notebook (Python 3 >= 3.7) and execute the
following code within on cell:

	%gui qt
	import geometadp
	obj = geometadp.geo_metadata()
	obj.manage()

## Wishlist

* import functionality: import a given JSON-file and edit it
