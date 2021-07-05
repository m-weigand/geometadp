[<img src="https://img.shields.io/badge/Slack-agrogeophy-1.svg?logo=slack">](https://agrogeophy.slack.com)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/agrogeophy/geometadp.git/HEAD)

# Geophysical Metadata Management using a Juypter Notebook

## Usage

The supported way to install geometadp use the Anaconda python distribution. If you do not already have it, first install a 3.x version for your platform from [here](https://docs.conda.io/en/latest/miniconda.html). Familiarise yourself with Conda before going further.

Once you have Anaconda installed, install the metadata manager using 'pip install git+https://github.com/m-weigand/geometadp'. 

Finally, open a new Jupyter Notebook (Python 3 >= 3.7) and execute the following code within on cell:

	import geometadp
	obj = geometadp.geo_metadata()
	obj.manage()

**NOTE**

	For a nicer visualisation run the code in Voilà. Execute the following code in the console:
    voila <path-to-notebook> run_GUI.ipynb
    
**NOTE**

    The GUI can be run online through Binder but in that case you need to create a github repo to interact with your files:
    1. Launch the binder
    2. Select the notebook 'run_GUI' and run it

#### Dependencies

We integrated an automatic metadata extraction using external dependencies:

- [REDA](https://github.com/geophysics-ubonn/reda)
- [EMagPy](https://gitlab.com/hkex/emagpy)
 
### Introduction

This gui is designed to help with the initial preparation of one geophysical dataset metadata. Simple metadata descriptors must be filled in order to:

1.  Make your survey datasets reusable for you
2.  And for the community. Descriptors with * are minimum required metadata identified for your research to be considered FAIR


### Standards

Geometadp metadata heavily rely on the two following standards: 
- <cite>Richards, J. D. (1997). Preservation and re-use of digital data: the role of the Archaeology Data Service. Antiquity, 71(274), 1057.</cite>  
- <cite>Adrian, B. M. (2014, December). National geological and geophysical data preservation program: successes and lessons learned. In AGU Fall Meeting Abstracts (Vol. 2014, pp. IN23A-3723).</cite>  



## Wishlist

* add Time-lapse and multiples datasets option 
* We would love to hear from users feedback to continuously improve the GUI. Let us know by submitting an issue or via our Slack channel using the #geometadp room (https://agrogeophy.slack.com)


Contributors
------------
- Maximilian Weigand, Ubonn
- Benjamin Mary, University of Padua
