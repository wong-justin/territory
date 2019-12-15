## Justin Wong
## google maps project
##
## some documentation used:
## https://developers.google.com/maps/documentation/maps-static/dev-guide

import requests
import polyline
import json
import random
import math
import point_in_polygon

IMG_FORMAT = 'png'      # png (detail), jpg (compression), pr gif
MAP_TYPE = 'roadmap'    # roadmap, satellite, or hybrid
SCALE = 2               # 1 default, 2 for hi-res pixels (eg dpi, printing)
IMG_SIZE = (500, 500)   # size of output image
TERRITORY_TYPES = ('Apartment','Business','Door to door','Phone/Letter')

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

##########################
###    CALCULATIONS    ###
##########################

def dist(p1, p2):
    """
    Returns distances between two points.

    # INPUT -----------
    p1     [tuple]
    p2     [tuple]

    # RETURN ----------
    d      [float]
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 +
                     (p2[1] - p1[1]) ** 2)

def is_point_inside(pt, path):
    """
    Calls some person's point-in-polygon algorithm.

    # INPUT -----------
    pt     [tuple]
    path   [list[tuple]]

    # RETURN ----------
    is_inside   [bool]
    """
    return point_in_polygon.cn_PnPoly(pt, path) == 1

def points_inside(path):
    """
    Calculate points that will be checked for nearby addresses within given region.

    Tries to optimize for least points necessary to still find all addresses,
    in an effort to make the least API calls.

    # INPUT -----------
    path          [list]   [(lat, lng)]

    # RETURN ----------
    pts_inside    [list]   [(lat, lng)]
    """
    # try tiling as a grid
    # or maybe use 1.5 or 2 times the average house distance since
    #   each call usually returns multiple addresses anyways.

    # or maybe make calls following streets in the neighborhood,
    #   and it wouldn't be so random anymore

    # or maybe use machine learning to predict where the best points would be
    #   to find the most addresses,
    #   eg it learns to place more densely for tight neighborhoods but sparser
    #   for rural areas. Or it learns average house sizing. somehow learns how
    #   to put points to reduce redundant results from Google's algorithm.    

    increment = .0002

    xvals = [pt[0] for pt in path]
    yvals = [pt[1] for pt in path]
    x0 = min(xvals)
    y0 = min(yvals)
    x_max = max(xvals)
    y_max = max(yvals)
    print('xdist bounds', x_max-x0, 'ydist bounds', y_max-y0)

    pts_inside = []
    
    # safe starting method: just choose like 7, 1 for the averaged center and
    #   6 around the middle ring area between the center and the edges. who knows.
    def ring_method():
        def avg_center(path):
            center = ( sum((pt[0] for pt in path)) / len(path),
                       sum((pt[1] for pt in path)) / len(path))
            return center
        def pt_on_perimeter(path, angle):
            # find point eminating from center thats on perimeter
            return
        center_pt = avg_center(path)
        mid_ring_pts = []
        num_pts_around = 6
        for i in range(num_pts_around):
            angle = (2 * math.pi) / num_pts_around
            outer_pt = pt_on_perimeter(angle, path)
            midpt = mdpt(center, outer_pt)
            mid_ring_pts.append(midpt)    
        return mid_ring_pts + center_pt

    # easiest starting method: square grid
    def square_tiling():        
        x = x0
        while x < x_max:
            y = y0        
            while y < y_max:
                if is_point_inside((x, y), path):
                    pts_inside.append((x, y))
                #else:
                    #print('not inside:', (x, y))
                y += increment
            x += increment
        return pts_inside

    def hexagon_tiling():
        return 0

    pts_inside = square_tiling()    # or ring_method() or
                                    # whatever_nested_method()
    return pts_inside

def bounding_points_count():
    """
    Finds the number of points each territory is bounded by, then overall avg.
    
    # INPUT -----------
    # RETURN ----------
    """
    
    territories = get_territories()
    all_coord_amounts = []
    for each_terr_type, each_terr_list in territories.items():
        this_type_coord_amounts = [len(terr[2]) for terr in each_terr_list]
        all_coord_amounts += this_type_coord_amounts
    print('list of num bounding points',
          all_coord_amounts)
    print('avg num bounding points',
          sum(all_coord_amounts) / len(all_coord_amounts))

def parcel_vs_latlng(p1, p2, l1, l2):
    """
    Compares seminole county parcel coords to global latlngs.
    Appears that they are not consistent distance ratios.
    
    # INPUT -----------
    p1     [float]
    p2     [float]
    l1     [float]
    l2     [float]

    # RETURN ----------
    """
    x_diff_parcel = p2[0] - p1[0]
    x_diff_latlng = l2[0] - l1[0]
    x_ratio = x_diff_parcel / x_diff_latlng

    y_diff_parcel = p2[1] - p1[1]
    y_diff_latlng = l2[1] - l1[1]
    y_ratio = y_diff_parcel / y_diff_latlng

    print(x_diff_parcel, x_diff_latlng, 'xratio', x_ratio)
    print(y_diff_parcel, y_diff_latlng, 'yratio', y_ratio)
    
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
    addresses   [list[tuple]]    (address_str, (lat,lng), place_id_str)
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
        places = [(possible['formatted_address'],
                   (possible['geometry']['location']['lat'],
                    possible['geometry']['location']['lng']),
                  possible['place_id'])
                  for possible in results]
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
    safety_limit = 500     # API calls
    
    coords_to_test = points_inside(path)
    if len(coords_to_test) > safety_limit:
        print('expensive amount of API calls; took first',
              safety_limit,
              'points inside')
        coords_to_test = coords_to_test[0:safety_limit]

    addresses = []

    for point in coords_to_test:
        addresses += get_address(api_key, point)

    #addresses = [addr[0] for addr in addresses] # just names (strings)
    old_length = len(addresses)
    addresses = set(addresses)  # remove duplicates
    print('duplicates removed:', old_length - len(addresses))
    return addresses

def rev_geocoding_accuracy(addresses):
    """
    Using any addresses, finds coordinates and then reverse geocode.
    Compares results to how close it is to original address.
    Appends results to text file.

    # INPUT -----------
    addresses     [list[str]]    'num street, city, state zip, USA'

    # RETURN ----------
    """
    with open('rev_geocoding_results.txt', 'a+') as file:
        for address in addresses:
            latlng = get_lat_lng(api_key, address)
            rev_addresses = get_address(api_key, latlng)
            found_original = address in [rev_addr[0] for rev_addr in rev_addresses]
            distances = [dist(latlng, rev_addr[1]) for rev_addr in rev_addresses]
            avg_distance = sum(distances) / len(distances)
            # format output #
            s1 = address + ' - ' + str(latlng)
            s2 = '\n'.join(['\t' + rev_addr[0] + ' - ' + str(rev_addr[1])
                            for rev_addr in rev_addresses])
            s3 = ''
            s4 = '\t' + 'found original? ' + str(found_original)
            s5 = '\t' + 'distances from original: ' + str(distances)
            s6 = '\t' + 'avg distance: ' + str(avg_distance)
            s7 = '\n'
            lines = '\n'.join((s1, s2, s3, s4, s5, s6, s7))
            print(lines)
            file.write(lines)
        
############################
###    MAP PRODUCTION    ###
############################

def map_img_center(api_key, center, zoom):
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

def map_img_path(api_key, path):
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

def map_img_markers(api_key, markers):
    """
    Returns an image of the map of an area given points.

    # INPUT -----------
    api_key     [str]
    markers     [list]    [(lat,lng)]

    # RETURN ----------
    img_data    [raw bytes?]
    """
    size = IMG_SIZE         
    scale = SCALE           
    img_format = IMG_FORMAT  
    map_type = MAP_TYPE
    markers_str = '|'.join(
        ['{},{}'.format(pt[0], pt[1]) for pt in markers])
    url = ('https://maps.googleapis.com/maps/api/staticmap?' +
           'style=feature:poi|visibility:off' + 
           '&markers=size:tiny|{}&size={}&scale={}&format={}&maptype={}&key={}'
           .format(markers_str,
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

#########################
###    DATA ACCESS    ###
#########################
        
def get_territories():
    """
    Returns territories from JSON export file from Territory Helper.

    Output format: dict{terr_type[territories[name, num, coords]]}

    # INPUT -----------

    # RETURN ----------
    territories  [dict] all{type[terrs[name, num, coords]]}
    """
    with open('data/territories.json') as file:
        data = json.load(file)
##        territories = {}
##        for typ in TERRITORY_TYPES:
##            territories[typ] = []
        territories = {'Apartment': [],
                       'Business': [],
                       'Door to door': [],
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

def open_seminole_data():
    """
    Opens json file that was downloaded from website:
    http://www.seminolecountyfl.gov/departments-services/information-services/gis-geographic-information-systems/gis-data.stml

    Used situs (Addresses) .gdb file, coverted to json by means of ogr2ogr GDAL:
    https://gdal.org/drivers/vector/openfilegdb.html#vector-openfilegdb

    Used that CLI with the line:
    ogr2ogr -f "GeoJSON" <src_file.gdb> <destination_file.geojson>
    Renamed to .json file.
    
    """
    with open('data/seminole_data.json') as file:
        data = json.load(file)
        
    print(data['features'])
    for feature in data['features']:
        parcel = feature['properties']['PARCEL']        
        address = feature['properties']['ADDRESS']
        city = feature['properties']['CITY']
        zip_code = feature['properties']['ZIP']
        coords = feature['geometry']['coordinates']
##        if address == '827 DAKOTA PRAIRIE CT':
##            print(feature)
            
def open_oviedo_data():
    """
    Opens json features file downloaded from this website:
    https://maps2.scpafl.org/SCPAExternal/?query=PARCELS;PARCEL;2621315KR00000730

    Searched 'oviedo' in address box and 24770 results appeared.
    Clicked 'load more' until all were loaded, then
    options menu -> export as features (json) file.
    """
    with open('data/oviedo_features.json') as file:
        data = json.load(file)
        
    sr434_lng = -81.208
    territory_boundary = territory_bounds()  

    valid_terrs = []
    for feature in data['features']:
        latlng = (feature['attributes']['LAT'],
                  feature['attributes']['LON'])
        short_addr = feature['attributes']['ADD2']
        full_addr = feature['attributes']['SITEADDRESS'] # full except 'USA'

        if is_point_inside(latlng, territory_boundary):
            #print(short_addr, latlng)
            valid_terrs.append((short_addr, latlng))
##        else:
##            print('NOPE', short_addr)
    print(len(valid_terrs))
    
def territory_bounds():
    return [
        (28.670365, -81.208512),
        (28.636491, -81.207935),
        (28.633872, -81.207297),
        (28.63094, -81.207883),
        (28.611765, -81.207534),
        (28.613597, -81.055922),
        (28.648673, -81.030304),
        (28.721254, -81.045243),
        (28.778786, -81.078637),
        (28.780479, -81.081234),
        (28.774938, -81.086234),
        (28.771082, -81.104056),
        (28.770835, -81.112641),
        (28.767232, -81.115673),
        (28.758446, -81.115877),
        (28.757974, -81.125327),
        (28.780698, -81.168006),
        (28.723094, -81.168017),
        (28.684473, -81.167447),
        (28.682734, -81.174349),
        (28.677829, -81.183579),
        (28.67704, -81.18888),
        (28.676894, -81.199471),
        (28.673564, -81.204406),
        (28.670365, -81.208512)] #included first again


if __name__ == '__main__':
    open_oviedo_data()
