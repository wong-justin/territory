# territory
Geolocation project using Google Maps API and local address data.

- Regions and addresses are imported from exernal json files.
- Maps generated using Google Maps.
- Finds addresses in regions.
    - Method 1 - pulling from local address data
    - Method 2 - reverse geocoding from Google Maps

Interactive web app uses [Streamlit](https://streamlit.io/).
```python
pip install streamlit
```
To view, download this repo and cd to the main folder `territory/`. Then:
```python
streamlit run app.py
```

Thanks to open-source algorithm contributions from [polyline](https://pypi.org/project/polyline/) for implementing Google Maps' path encoding and [point-in-polygon](./geometry.py) for checking points within regions.
