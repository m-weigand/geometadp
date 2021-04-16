[<img src="https://img.shields.io/badge/Slack-agrogeophy-1.svg?logo=slack">](https://agrogeophy.slack.com)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/agrogeophy/geometadp.git/HEAD)

# Geophysical Metadata Management using a Juypter Notebook

### Introduction

This gui is designed to help with the initial preparation of one geophysical dataset metadata. Simple metadata descriptors must be filled in order to:

1.  Make your survey datasets reusable for you
2.  And for the community. Descriptors with * are minimum required metadata identified for your research to be considered FAIR

### Tips

1.  Use data importers for automatic metadata extraction
2.  Use it locally for a maximum flexibility
3.  Keep track of your datasets structure/metadata during every stages: acquisition/processing/publication: Use the import/export tabs respectively to import a pre-existing JSON file and save your work as:
    - a zip file containing the files structure
    - a Json formatted file in which metadata are saved

### Recommandations

1.  Fill out the maximum number of metadata fields
2.  Check if a metadata descriptor exist before creating a new one
3.  Check the logger for possible errors

## Usage

The GUI can be run online through Binder, or downloaded and run locally.

1. Launch the binder
2. Select the notebook 'run_GUI' and run it

### Standards

Geometadp metadata heavily rely on the two following standards: 
- <cite>Richards, J. D. (1997). Preservation and re-use of digital data: the role of the Archaeology Data Service. Antiquity, 71(274), 1057.</cite>  
- <cite>Adrian, B. M. (2014, December). National geological and geophysical data preservation program: successes and lessons learned. In AGU Fall Meeting Abstracts (Vol. 2014, pp. IN23A-3723).</cite>  

#### Dependencies

We integrated an automatic metadata extraction using external dependencies:

- [REDA](https://github.com/geophysics-ubonn/reda)
- [EMagPy](https://gitlab.com/hkex/emagpy)

## Wishlist

* add Time-lapse and multiples datasets option 
* We would love to hear from users feedback to continuously improve the GUI. Let us know by submitting an issue or via our Slack channel using the #geometadp room (https://agrogeophy.slack.com)


Contributors
------------
- Maximilian Weigand, Ubonn
- Benjamin Mary, University of Padua
