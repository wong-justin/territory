## Justin Wong
## territory project
##
## some documentation used:
## https://developers.google.com/maps/documentation/maps-static/dev-guide

import requests
import polyline
import json
import random
import math
import point_in_polygon

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

def store(*values):
    """
    Method (for outside callers) to set map parameters
    
    Usage (set): store(new_img_size, new_scale, new_img_format, new_map_type)
    (get): params = store()
    
    
    *values
    img_size    [tuple]   (width, height) size of output image
    scale       [int]     1, or 2 for hi-res pixels (eg dpi, printing)
    img_format  [str]     'png' (detail), 'jpg' (compression), or 'gif'
    map_type    [str]     'roadmap', 'satellite', or 'hybrid'
    
    # INPUT -----------
    values    (setter) if params 
    
    # RETURN ----------
    values    (getter) if no params
    
    """
    store.values = values or store.values
    return store.values

def store_defaults():
    store((500, 500), 2, 'png', 'roadmap')

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
    size, scale, img_format, map_type = store()
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
    size, scale, img_format, map_type = store()
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
    size, scale, img_format, map_type = store()
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
    terr_type    [str]

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

    Output format: dict{terr_type: [name, num, coords]]}

    # INPUT -----------

    # RETURN ----------
    territories  [dict] all{type[terrs[name, num, coords]]}
    """
    with open('data/territories.json') as file:
        data = json.load(file)
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

            #territories[terr_type].append((name, num, coords))
            territories[terr_type].append([name, num, coords])
                
        return territories

def open_county_data():
    """
    Opens json file that was downloaded from website:
    http://www.seminolecountyfl.gov/departments-services/information-services/gis-geographic-information-systems/gis-data.stml

    Used situs (Addresses) .gdb file, coverted to json by means of ogr2ogr GDAL:
    https://gdal.org/drivers/vector/openfilegdb.html#vector-openfilegdb

    Used that CLI with the line:
    ogr2ogr -f "GeoJSON" <src_file.gdb> <destination_file.geojson>
    Renamed to .json file.

    Cleaner data than property apprasiers data! But no latlng, so this dataset
    will not be used much.
    ~160,000 items
    
    # INPUT -----------
    # RETURN ----------
    seminole_parcels   [dict] {[short_addr]:(full_addr, parcel, parcel_coords)}
    """
    with open('data/seminole_data.json') as file:
        data = json.load(file)

        seminole_parcels = {}
        print(data['features'][0])  # see example structure
        for feature in data['features']:
            parcel = feature['properties']['PARCEL']        
            short_addr = feature['properties']['ADDRESS']
            city = feature['properties']['CITY']
            zip_code = feature['properties']['ZIP']
            full_addr = '{} {}, FL {}'.format(short_addr, city, zip_code)
            parcel_coords = feature['geometry']['coordinates']
            seminole_parcels[short_addr] = (full_addr, parcel, parcel_coords)

        print('addresses/parcels in seminole', len(seminole_parcels))
        return seminole_parcels
            
def open_town_data(town='oviedo'):
    """
    Opens json features file downloaded from this website:
    https://maps2.scpafl.org/SCPAExternal/?query=PARCELS;PARCEL;2621315KR00000730

    Searched 'oviedo' or 'geneva' or 'chuluota' in address box
    and 24770/3381/3622 results appeared.
    Clicked 'load more' until all were loaded, then
    options menu -> export as features (json) file.

    Lots of data errors makes this dataset hard to clean.
    But lat/lng is the most reliable data here, accurate virtually every time,
    because this is from the property appraiser.
        Sometimes ADD2 is outside Oviedo, but [addr_1] matches up with latlng
            in Oviedo and that is verified and acceptable.
        Sometimes ADD2 is outside Oviedo, but [addr_1] is empty
            so you have to go by latlng.
        Sometimes ADD2 is correct address and [addr_1] is the road it's off of.
        Sometimes ADD2 is correct but [addr_1] is the same only without number.
        Sometimes ADD2 is correct and [addr_1] is empty.
        Sometimes there's only a PO Box.
        Sometimes ADD2 is a company like 1511 E STATE ROAD 434 STE 3001
            and [addr_1] is empty.
        Sometimes there's a mispelling ('LOOKWOOD'), but it's rarer.
        Sometimes ADD2 is a suite (?) num (eg 'STE 115') and [addr_1] is empty.
    Errors seem to be from data entry problems, misunderstandings or
    lack of standard address rules. Many people don't know how to use ADD2!
    Many corrupted addresses seem to have latlngs for undeveloped properties or
    newly built homes (where the owner lives somewhere else or it's a company)

    # INPUT -----------
    town           [str]  <'oviedo', 'geneva', or 'chuluota'>
    # RETURN ----------
    in_territory   [dict] {[short_addr]:(addr2, full_addr, latlng)}
    """
    with open('data/{}.json'.format(town)) as file:
        data = json.load(file)
        
    territory_boundary = territory_bounds()  

    properties_with_known_addr = {}
    in_terr_but_weird_addr = {}
    #print(data['features'][0]) # see example structure
    for feature in data['features']:
        latlng = (feature['attributes']['LAT'],
                  feature['attributes']['LON'])
        pad_num = feature['attributes']['PAD_NUM']
        pad_dir = feature['attributes']['PAD_DIR']
        pad_name = feature['attributes']['PAD_NAME']
        pad_suffix = feature['attributes']['PAD_SUFFIX']
        short_addr = ' '.join(
            filter(None, (pad_num, pad_dir, pad_name, pad_suffix)))
        addr_2 = feature['attributes']['ADD2']
        full_addr = feature['attributes']['SITEADDRESS'] # full except 'USA'

        key, val = short_addr, (addr_2, full_addr, latlng)

        if is_point_inside(latlng, territory_boundary):
            if pad_num == '':
                # address must be messed up; manually check
                in_terr_but_weird_addr[key] = val
            else:
                # assume addr_1 having a number is correct
                properties_with_known_addr[key] = val
        else:
            #print('not inside overall territory', short_addr)
            pass
    terr_in_town = {**in_terr_but_weird_addr, **properties_with_known_addr}
##    print('properties w good address:', len(properties_with_known_addr))
##    print('properties w bad address: ', len(in_terr_but_weird_addr))
##    print('properties in this town in territory:', len(terr_in_town))
##    print('properties in this town but not territory:',
##          len(data['features']) - len(terr_in_town))
    return terr_in_town

def get_terr_from_towns():
    """
    Combines data from oviedo, geneva, chuluota.

    # INPUT -----------
    # RETURN ----------
    terr_from_towns   [dict]   {[addr_str]: (addr_2, full_addr, latlng)}
    """
    oviedo = open_town_data('oviedo')
    geneva = open_town_data('geneva')
    chuluota = open_town_data('chuluota')
    terr_from_towns = {**oviedo, **geneva, **chuluota}
##    print('terrs in town:', len(terr_from_towns))
##    print('random addr:', random.choice(list(terr_from_towns.items())))
    return terr_from_towns

def get_streets_in(town_data):
    """
    Returns sorted list of street names in given region, and num houses on each.

    # INPUT -----------
    town_data    [dict]    {[addr_str] : ...}

    # RETURN ----------
    street_names [list]    [(str, num_occurrences)]
    """
    street_names = {}
    for addr in town_data.keys():
        chunks = addr.split()
        chunks = chunks[1:] # remove first part of address (the num)
        street = ' '.join(chunks)
        if street not in street_names:
            street_names[street] = 1
        else:
            street_names[street] += 1
    # order by most occurrences
    street_names = sorted(list(street_names.items()), key=lambda x: x[1], reverse=True)
    for street in street_names:
        print(street, street_names.index(street))
    return street_names

def get_houses_in(path, town=None):
    """
    Finds addresses within given region.
    Include optional param town (if known) to speed up the search.

    # INPUT -----------
    path        [list[tuple]]
    town        [str]
    # RETURN ----------
    addresses   [list]
    """
    if town is None:
        data = get_terr_from_towns()
    else:
        data = open_town_data(town)
    addresses = [(addr, *v) for addr, v in data.items()
                 if is_point_inside(v[2], path)]
    print('num houses in region:', len(addresses))
    return addresses

def sort_houses_into_territories():
    """
    Finds all houses in each territory.

    # INPUT -----------
    # RETURN ----------
    territories    [dict]   {types[name, num, path, addresses]}
    """
    terrs = get_territories()
    #terrs = {key: list(val) for key, val in terrs.items()}  # change from immutable tuple
    terrs = terrs['Door to door']
    for terr in terrs:
        path = terr[2]
        print(terr[1])
        addresses = get_houses_in(path)
        terr.append(addresses)
    return terrs
        
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

def write_terrs_with_addrs_to_file():
    terrs = sort_houses_into_territories()
    with open('terrs_with_addrs.json', 'w') as file:
        json.dump(terrs, file)

def init():
    """
    Get api key, set default map settings
    """
    api_key = get_api_key()
    store_defaults() 


init()