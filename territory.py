## Justin Wong
## google maps project
##
## some documentation used:
## https://developers.google.com/maps/documentation/maps-static/dev-guide

import requests
import polyline
import json
import random

IMG_FORMAT = 'png'      # png (detail), jpg (compression), pr gif
MAP_TYPE = 'roadmap'    # roadmap, satellite, or hybrid
SCALE = 2               # 1 default, 2 for hi-res pixels (eg dpi, printing)
IMG_SIZE = (500, 500)   # size of output image
TERRITORY_TYPES = ('Apartment','Door to door','Business','Phone/Letter')

def get_api_key():
    """
    Returns Google Maps API key from file.

    # INPUT -----------

    # RETURN ----------
    api_key     [str]
    """
    with open('google_api_key.txt')as file:
        api_key = file.readline()
        file.close()
    return api_key

api_key = get_api_key()

def save_img(name, content):
    """
    Saves image to this directory.

    # INPUT -----------
    name         [str]
    content      [raw bytes?]

    # RETURN ----------
    """
    with open(name + '.' + IMG_FORMAT, 'wb') as file:
        file.write(content)
        file.close()
    return

def get_territories():
    """
    Returns territories from JSON export file from Territory Helper.

    Output format: dict{terr_type[territories[name, num, coords]]}

    # INPUT -----------

    # RETURN ----------
    territories  [dict] all{type[terrs[name, num, coords]]}
    """
    with open('territories.json') as file:
        data = json.load(file)
##        territories = {}
##        for typ in TERRITORY_TYPES:
##            territories[typ] = []
        territories = {'Apartment': [],
                       'Door to door': [],
                       'Business': [],
                       'Phone/Letter': []
                       }
        for terr in data['features']:
            terr_type = terr['properties']['TerritoryType']            
            name = terr['properties']['name']
            num = int(terr['properties']['TerritoryNumber'])
            coords = terr['geometry']['coordinates'][0]
                # [...][0] because it's doubly nested by geojson format 
            coords = [(pt[1], pt[0]) for pt in coords]  # swap coords

            territories[terr_type].append((name, num, coords))
                
        return territories

#######################
###    GEOCODING    ###
#######################

def get_lat_lng(api_key, place):
    """
    Returns latitude and longitude of a place.
    Accepts addresses or plain language searches.

    # INPUT -----------
    api_key     [str]
    place       [str]

    # RETURN ----------
    lat         [float]
    lng         [float]
    """
    url = ('https://maps.googleapis.com/maps/api/geocode/json?' +
           'address={}&key={}'
           .format(place.replace(' ','+'), api_key))
    print(url)
    try:
        response = requests.get(url)
        resp_json_payload = response.json()
        lat = resp_json_payload['results'][0]['geometry']['location']['lat']
        lng = resp_json_payload['results'][0]['geometry']['location']['lng']
    except:
        print('ERROR: {}'.format(address))
        lat = 0
        lng = 0
    return lat, lng

def get_address(api_key, latlng):
    """
    Returns addresses/unique place IDs of locations closest to given point.
    Can return more than one if Google thinks multiple addresses are close.

    # INPUT -----------
    api_key     [str]
    address     [tuple]   (lat, lng)

    # RETURN ----------
    addresses   [list]
    """
    url = ('https://maps.googleapis.com/maps/api/geocode/json?' +
           'latlng={}&result_type=street_address&key={}'
           .format('{},{}'.format(latlng[0], latlng[1]),
                   api_key))
    print(url)
    try:
        response = requests.get(url)
        resp_json_payload = response.json()
        results = resp_json_payload['results']
        places = [possible['formatted_address'] for possible in results]
    except:
        print('ERROR: {}'.format(latlng))
        places = None
    return places

def get_addresses_in(api_key, path):
    """
    Warning! Method can consume many API calls quickly
    and cause charges to account.
    
    Returns most if not all addresses within a given region.
    
    Pings around points within the region,
    and keeps all unique addresses returned.
    
    # INPUT -----------
    api_key     [str]
    path        [list]   [(lat, lng)]

    # RETURN ----------
    addresses   [list]
    """
    addresses = []
    
    coords_to_test = points_inside(path)
    for point in coords_to_test:
        addresses += get_address(api_key, point)
        
    addresses = set(addresses)  # remove duplicates
    return addresses

def points_inside(path):
    """
    Warning! Small increment can consume many API calls quickly
    and cause charges to account.
    
    Calculate points to check for nearby addresses within given region.

    Tries to optimize for least points necessary to still find all addresses,
    in an effort to make the least API calls.

    # INPUT -----------
    path        [list]   [(lat, lng)]

    # RETURN ----------
    points      [list]   [(lat, lng)]
    """
    increment = 0.001
    # randomly tile region with points approximately that far apart?
    # maybe find average house distance and use that.    
    # Hexagon tiling shape using points as circle centers.

    # or maybe use 1.5 or 2 times the average house distance since
    #   each call usually returns multiple addresses anyways.

    # or maybe make calls following streets in the neighborhood,
    #   and it wouldn't be so random anymore

    # or maybe use machine learning to predict where the best points would be
    #   to find the most addresses,
    #   eg it learns to place more densely for tight neighborhoods but sparser
    #   for rural areas. Or it learns average house sizing. Or it learns how
    #   to put points to reduce redundant results from Google's algorithm.

    # to check if a given point is inside the shape: use ray casting probably:
    # https://en.wikipedia.org/wiki/Point_in_polygon
    

    # safe starting method: just choose like 7, 1 for the averaged center and
    #   6 around the middle ring area between the center and the edges. who knows.
    def avg_center(path):
        center = ( sum((pt[0] for pt in path)) / len(path),
                   sum((pt[1] for pt in path)) / len(path))
        return center
    def pt_on_perimeter(path, angle):
        
    center_pt = avg_center(path)
    mid_ring_pts = []
    num_pts_around = 6
    for i in range(num_pts_around):
        angle = (2 * math.pi) / num_pts_around
        outer_pt = pt_on_perimeter(angle, path)
        midpt = mdpt(center, outer_pt)
        mid_ring_pts.append(midpt)    
    return mid_ring_pts + center_pt
    
############################
###    MAP PRODUCTION    ###
############################

def map_img(api_key, center, zoom):
    """
    Returns an image of the map of an area around a location.
    Input lat,lng point and zoom level

    # INPUT -----------
    api_key     [str]
    center      [tuple]
    zoom        [int]   1 (world) -> 15 (streets) -> 20 (buildings)

    # RETURN ----------
    img_data    [raw bytes?]
    """
    size = IMG_SIZE         
    scale = SCALE           
    img_format = IMG_FORMAT  
    map_type = MAP_TYPE     
    url = ('https://maps.googleapis.com/maps/api/staticmap?' +
           'style=feature:poi|visibility:off' +     # no businesses, markers
           '&center={}&zoom={}&size={}&scale={}&format={}&maptype={}&key={}'
           .format('{},{}'.format(center[0], center[1]),
                   zoom,
                   '{}x{}'.format(size[0], size[1]),   
                   scale,           
                   img_format,       
                   map_type,    
                   api_key))
    print(url)
    try:
        response = requests.get(url)
        img_data = response.content
    except:
        print('ERROR: {}'.format(center))
        img_data = None
    return img_data

def map_img(api_key, path):
    """
    Returns an image of the map of an area around a location.
    Input list of lat,lng coordinates.

    # INPUT -----------
    api_key     [str]
    path        [list]    [(lat,lng)]

    # RETURN ----------
    img_data    [raw bytes?]
    """
    fill_color = '0xAA000033'
    enc_path = polyline.encode(path)
    path_str = 'fillcolor:{}|enc:{}'.format(fill_color,
                                            enc_path)
    size = IMG_SIZE         
    scale = SCALE           
    img_format = IMG_FORMAT  
    map_type = MAP_TYPE     
    url = ('https://maps.googleapis.com/maps/api/staticmap?' +
           'style=feature:poi|visibility:off' + 
           '&path={}&size={}&scale={}&format={}&maptype={}&key={}'
           .format(path_str,
                   '{}x{}'.format(size[0], size[1]),   
                   scale,           
                   img_format,       
                   map_type,    
                   api_key))
    print(url)
    try:
        response = requests.get(url)
        img_data = response.content
    except:
        print('ERROR: {}'.format(path))
        img_data = None
    return img_data

def maps_for_type(terr_type):
    """
    Gets and saves images for all territories of given type.

    # INPUT -----------
    terr_type    [str]  of TERRITORY_TYPES

    # RETURN ----------
    """
    territories = get_territories()
    for terr in territories[terr_type]:
        name = terr[0]
        coords = terr[2]
        img_data = map_img(api_key, coords)
        save_img(name, img_data)    

#####################
###     TESTS     ###
#####################

def test_geocoding():
    address = '2835 Yonkers Court, Oviedo, FL'
    address = 'maple street oviedo'
    print(get_lat_lng(api_key, address))

def test_rev_geocoding():
    latlng = (28.6335359, -81.19505219999999)
    latlng = (28.656202, -81.2026264)
    print(get_address(api_key, latlng))

def test_sample_area():
    oviedo_coords = (28.6700, -81.2081)  
    img_data = map_img(api_key, oviedo_coords, 17)
    save_img('sample_area_test', img_data)

def test_sample_path():
    path = [(-81.203413903713241, 28.615474969803429),
            (-81.203368306159987, 28.612065472508572),
            (-81.204607486724868, 28.612065472508572),
            (-81.204639673233046, 28.6130638450546),
            (-81.2051546573639, 28.613365238675311),
            (-81.205181479454055, 28.615470260629358),
            (-81.203413903713241, 28.615474969803429)]
    path = [(x[1], x[0]) for x in path]
            
    img_data = map_img(api_key, path)
    save_img('sample_path_test', img_data)
    
def test_sample_type():    
    maps_for_type('Apartment')

def test_territory_bounding_points():
    territories = get_territories()
    all_coord_amounts = []
    for each_terr_type, each_terr_list in territories.items():
        this_type_coord_amounts = [len(terr[2]) for terr in each_terr_list]
        all_coord_amounts += this_type_coord_amounts
    print('list of num bounding points',
          all_coord_amounts)
    print('avg num bounding points',
          sum(all_coord_amounts) / len(all_coord_amounts))
    return

test_territory_bounding_points()
