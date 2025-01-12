# GEDI---globaleco
![gedi-agbd-us-cloudfree--2-07-2023](https://github.com/user-attachments/assets/f3bdecc6-951d-4cb3-9cbb-81276e99f559)
## A simple python module for downloading and visualizing GEDI L4A dataset

This module has 2 classes:
1. globaleco.gedi
2. globaleco.gedi_reader

globaleco.gedi focuses solely on acquiring the data and it has 2 methods:
1. get_links
2. download

globaleco.gedi_reader focuses on converting the H5 GEDI file to Geodataframe and visualization and it has 2 methods:
1. get_gdf
2. visualize
