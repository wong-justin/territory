# territory
Geolocation project using Google Maps API and local address data.

- Regions and addresses are imported from exernal json files.
- Maps generated using Google Maps.
- Finds addresses in regions.

Interactive web app uses [Streamlit](https://streamlit.io/).
To view, 
```python
pip install streamlit

streamlit run https://raw.githubusercontent.com/wong-justin/territory/master/app.py
```

Thanks to open-source algorithm contributions from [polyline](https://pypi.org/project/polyline/) for implementing Google Maps' path encoding and [point-in-polygon](./point_in_polygon.py) for checking points within regions.