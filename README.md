# GEDI---globaleco
## A simple python module for downloading and visualizing GEDI L4A dataset

This module has has 2 classes:
1. globaleco.gedi
2. globaleco.gedi_reader

globaleco.gedi focuses solely on acquiring the data and it has 2 methods:
1. get_links
2. download

globaleco.gedi_reader focuses on converting the H5 GEDI file to Geodataframe and visualization and it has 2 methods:
1. get_gdf
2. visualize
