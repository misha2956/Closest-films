# Closest Films (python, folium)

## Description

This projects allows user to find films which were filmed nearby.\
Takes into account that the movies should be in the same country/region.

## Installation

To install this app, you will first need to clone the repository:\
```$ git clone https://github.com/misha2956/Closest-films.git```\
Then, setup a `virtualenv`:\
```$ virtualenv -p python3 venv```\
```$ source venv/bin/activate```\
Then, type the following to install the required packages:\
```$ pip install -r requirements.txt```\
You are now ready to run the app!

# Usage

To run the app, simply type:\
```$ python main.py```\
It will then prompt you to enter your location. You need your internet connection to be stable.\
You are now ready to open the `map.html` in your browser!\
Results will look similar to the following:

![Example 1](examples/img_Lviv.png?raw=true "Example 1")\
![Example 2](examples/img_NewYork.png?raw=true "Example 2")

### HTML structure
Folium automatiacally generates an html file containing multiple layers, with map itself, films' marks and a user location mark.\
```<div class="leaflet-pane leaflet-map-pane" ... >```\
This tag is a container for the map itself\
```<div class="leaflet-control-container">```\
This tag is a container for the controls.\
The first one contains multiple `<img>` that form a map, loaded from https://b.tile.openstreetmap.org.\
The second one contains buttons in `<a>` used for zooming and some other controls.
