## Justin Wong
## territory project
##
## some documentation used:
## https://developers.google.com/maps/documentation/maps-static/dev-guide

import requests
import polyline
import json
import random
import geometry as geo

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

###############################
###    DATA & FORMATTING    ###
###############################

def address(short_addr, city, zip_code, latlng):
    """
    A closure function to hold address data like a class.
    
    Usage:
    
    >> some_addr = address('21 some st', 'oviedo', 32766, (23.2222221, -81.3333332))
    [...later on...]
    >> some_addr()
    >> ('21 SOME ST', 'OVIEDO', 32766, (23.222222, -81.333333))
    >> some_addr()[0]
    >> '21 SOME ST'
    
    # INPUT -----------
    short_addr  [str]   '[number] [street name] [suffix]' 
        * no punctuation on suffix
    city        [str]
    zip         [str]    doesn't support extra like 32765-8412
    latlng      [tuple]  coordinates
    # RETURN ----------
    lambda      [function]  returns formatted inputs
    """
    short_addr = short_addr.upper()
    city = None if zip_code is None else city.upper()
    zip_code = None if zip_code is None else int(zip_code)
    latlng = shorten_latlng(latlng)
    return lambda: (short_addr, city, zip_code, latlng)

def shorten_latlng(pt):
    """
    Returns latlng pair rounded to 6 decimal places,
    which is the max amount that Google will use.

    # INPUT -----------
    pt    [tuple]

    # RETURN ----------
    pt    [tuple]
    """
    return None if pt is None else (round(pt[0], 6), round(pt[1], 6))  

def split_full_addr(full_addr):
    """
    Split up pieces of full address.
    
    # INPUT -----------
    full_addr    [str]
        *format: 1188 E Mitchell Hammock Rd, Oviedo, FL 32765, USA
    # RETURN ----------
    short_addr
    city
    zip
    """
    chunks = full_addr.split(',')
    short_addr = chunks[0]
    city = chunks[1].strip()
    zip_chars = [c for c in chunks[2] if c.isdigit()]
    zip_code = int(''.join(zip_chars))
    return short_addr, city, zip_code    
 
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
    latlng      [tuple]   (lat, lng)

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
        
        addresses = []
        for addr in results:
            short_addr, city, zip_code = split_full_addr(
            addr['formatted_address'])
            coords = (addr['geometry']['location']['lat'], 
                      addr['geometry']['location']['lng'])
            this_addr = address(short_addr, city, zip_code, coords)
            addresses.append(this_addr)

    except:
        print('ERROR: {}'.format(latlng))
        addresses = None
    return addresses

def get_addresses_in(api_key, path):
    """
    Warning! Method can consume many API calls quickly
    and cause charges to account.
    
    Returns some real and fake addresses within a given region.
    
    Pings around points within the region retrieved from 
    geo.points_inside()
    
    # INPUT -----------
    api_key     [str]
    path        [list]   [(lat, lng)]

    # RETURN ----------
    addresses   [list]
    """
    safety_limit = 500     # API calls
    
    coords_to_test = geo.points_inside(path)
    if len(coords_to_test) > safety_limit:
        print('expensive amount of API calls; took first',
              safety_limit,
              'points inside')
        coords_to_test = coords_to_test[0:safety_limit]

    addresses = []

    for point in coords_to_test:
        addresses += get_address(api_key, point)
    return addresses
    
def remove_duplicates(addresses):
    """
    Returns most if not all addresses within a given region.
    
    Pings around points within the region,
    and keeps all unique addresses returned.
    
    # INPUT -----------
    addresses   [list]

    # RETURN ----------
    unique_addresses   [list]
    """
    unique_addresses = {}
    for addr in addresses:
        if addr()[0] not in unique_addresses.keys():
            unique_addresses[addr()[0]] = addr
    old_length = len(addresses)
    new_length = len(unique_addresses)
    print('duplicates removed:', old_length - new_length)
    print('unique addresses:', new_length)
    return list(unique_addresses.values())
    
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
    default_size = (500, 500)
    default_scale = 2
    default_img_format = 'png'
    default_map_type = 'roadmap'
    store(default_size, 
          default_scale, 
          default_img_format, 
          default_map_type)

def create_map(api_key, center=None, zoom=None, path=None, markers=None):
    size, scale, img_format, map_type = store()
    center_str = '' if center is None else '&center={},{}'.format(center[0], center[1])
    zoom_str = '' if zoom is None else '&zoom={}'.format(zoom)
    fill_color = '0xAA000033'
    enc_path = None if path is None else polyline.encode(path) 
    path_str = '' if path is None else '&path=fillcolor:{}|enc:{}'.format(fill_color, enc_path)
    markers = None if markers is None else [shorten_latlng(m) for m in markers]
    markers_str = '' if markers is None else '&markers=size:tiny|{}'.format('|'.join(
        ['{},{}'.format(pt[0], pt[1]) for pt in markers]))
    
    api_base_str = 'https://maps.googleapis.com/maps/api/staticmap?'
    no_poi_str = 'style=feature:poi|visibility:off'
    
    img_settings_str = '&size={}&scale={}&format={}&maptype={}&key={}'.format(
        '{}x{}'.format(size[0], size[1]), 
        scale,           
        img_format,      
        map_type,    
        api_key)
    url = api_base_str + no_poi_str + center_str + zoom_str + path_str + markers_str + img_settings_str
    
    print(url)
    
    try:
        response = requests.get(url)
        img_data = response.content
    except:
        print('ERROR: {}'.format(center))
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
    img_format = store()[2]
    with open(name + '.' + img_format, 'wb') as file:
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
    territories  [dict] {type[name, num, coords]}
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
def get_dtd_territories():
    with open('dtd_terrs_with_numhouses.json', 'r') as file:
        data = json.load(file)
        return data
    
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
    addresses   [list]
    """
    with open('data/seminole_data.json') as file:
        data = json.load(file)

        addresses = []
        print(data['features'][0])  # see example structure
        for feature in data['features']:
            short_addr = feature['properties']['ADDRESS']
            city = feature['properties']['CITY']
            zip_code = feature['properties']['ZIP']
            latlng = None   # parcel coords apparently doesn't convert to global latlng
            
            address_call = address(short_addr, city, zip_code, latlng)
            addresses.append(address_call)
            
            # extra info in case needed later
#            parcel = feature['properties']['PARCEL']
#            parcel_coords = feature['geometry']['coordinates']
#            full_addr = '{} {}, FL {}'.format(short_addr, city, zip_code)

        print('addresses/parcels in seminole', len(addresses))
        return addresses
            
def get_town_addresses(town='oviedo'):
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
    newly built homes (where the owner lives somewhere else or it's a company
    
    Example json feature:
    
    "attributes":{
    "OBJECTID":165, 
    "PARCEL":"2121325CF16000060", 
    "PARCELTEXT":"21-21-32-5CF-1600-0060", 
    "GIS_ACRES":0.25826515, 
    "LAT":28.64588294, 
    "LON":-81.12306277, 
    "TD":"Unincorporated", 
    "DORRes":"SINGLE FAMILY", 
    "DORComm":"", 
    "OWNER":"SOMEBODY'S NAME AND SOMEBODY ELSE", 
    "FACILITY_NAME":"", 
    "TOTAL_JUST_VALUE":95697, 
    "BLDG_VALUE":44684,  
    "EXFT_VALUE":800, 
    "LAND_VALUE":50213, 
    "SUB_NAME":"NORTH CHULUOTA", 
    "YEAR_BLT":1958, 
    "GROSS_AREA":1170, 
    "BEDROOMS":1, 
    "BATHROOMS":1, 
    "DORVac":"", 
    "OWNERADDRESS":"320 1ST ST CHULUOTA FL 32766", 
    "SITEADDRESS":"320 1ST ST CHULUOTA, FL 32766", 
    "PAT_SUB_ID":2170, 
    "ASSESSED_VALUE":51493, 
    "TAXABLE_VALUE":0, 
    "EXEMPT_VALUE":51493, 
    "TAXES":234.52, 
    "LATEST_SALE_DATE":null, 
    "LATEST_SALE_AMT":null, 
    "PAD_NUM":"320", 
    "PAD_DIR":"E", 
    "PAD_NAME":"1ST", 
    "PAD_SUFFIX":"ST", 
    "PAD_CITY":"CHULUOTA", 
    "PAD_STATE":"FL", 
    "PAD_ZIP":"32766", 
    "ADD2":"320 1ST ST", 
    "CITY":"CHULUOTA", 
    "STATE":"FL", 
    "ZIP":"32766",
    "LIVING_AREA":840}},
    {"geometry":
    {"rings":
    [[[613469.0470155776,1566860.0192047432],[613394.0576642454,1566858.7619894072],[613391.4421839118,1567014.7639739886],[613466.431535244,1567016.0211893246],[613469.0470155776,1566860.0192047432]]],
    "spatialReference":{"wkid":102658,"latestWkid":2236}}
    
    # INPUT -----------
    town           [str]  <'oviedo', 'geneva', or 'chuluota'>
    # RETURN ----------
    addresses      [list]
    Outdated - 
    in_territory   [dict] {[short_addr]:(addr2, full_addr, latlng)}
    """
    with open('data/{}.json'.format(town)) as file:
        data = json.load(file)
        
    territory_boundary = territory_bounds()  

#    properties_with_known_addr = {}
#    in_terr_but_weird_addr = {}
    
    addresses = []
    for feature in data['features']:
        pad_num = feature['attributes']['PAD_NUM']
        pad_dir = feature['attributes']['PAD_DIR']
        pad_name = feature['attributes']['PAD_NAME']
        pad_suffix = feature['attributes']['PAD_SUFFIX']
        
        short_addr = ' '.join(
            filter(None, (pad_num, pad_dir, pad_name, pad_suffix)))
        city = feature['attributes']['PAD_CITY']
        zip_code = feature['attributes']['PAD_ZIP']
        latlng = (feature['attributes']['LAT'],
                  feature['attributes']['LON'])
        
        
        
        address_call = address(short_addr, city, zip_code, latlng)
        addresses.append(address_call)
        
        # extra info in case need later
#        addr_2 = feature['attributes']['ADD2'] # user input
#        full_addr = feature['attributes']['SITEADDRESS'] # full except 'USA'
        
    return addresses

#        key, val = short_addr, address_call
#
#        if geo.is_point_inside(latlng, territory_boundary):
#            if pad_num == '':
#                # address must be messed up; manually check
#                in_terr_but_weird_addr[key] = val
#            else:
#                # assume addr_1 having a number is correct
#                properties_with_known_addr[key] = val
#        else:
#            #print('not inside overall territory', short_addr)
#            pass
#    terr_in_town = {**in_terr_but_weird_addr, **properties_with_known_addr}
##    print('properties w good address:', len(properties_with_known_addr))
##    print('properties w bad address: ', len(in_terr_but_weird_addr))
##    print('properties in this town in territory:', len(terr_in_town))
##    print('properties in this town but not territory:',
##          len(data['features']) - len(terr_in_town))
#    return terr_in_town

def get_all_towns_addresses():
    """
    Combines data from oviedo, geneva, chuluota.

    # INPUT -----------
    # RETURN ----------
    terr_from_towns   [dict]   {[addr_str]: (addr_2, full_addr, latlng)}
    """
    oviedo = get_town_addresses('oviedo')
    geneva = get_town_addresses('geneva')
    chuluota = get_town_addresses('chuluota')
    addresses = oviedo + geneva + chuluota
##    print('terrs in town:', len(terr_from_towns))
##    print('random addr:', random.choice(list(terr_from_towns.items())))
    return addresses

def get_streets_in(addresses):
    """
    Returns sorted list of street names in given list, and num houses on each.

    # INPUT -----------
    addresses    [list]

    # RETURN ----------
    street_names [list]    [(str, num_occurrences)]
    """
    street_names = {}
    for addr in addresses:
        chunks = addr()[0].split()
        chunks = chunks[1:] # remove first part of short address (the num)
        street = ' '.join(chunks)
        if street not in street_names:
            street_names[street] = 1
        else:
            street_names[street] += 1
    # now sort by most occurrences
    street_names = sorted(list(street_names.items()), key=lambda x: x[1], reverse=True)
    for street in street_names:
        print(street, street_names.index(street)+1)
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
        data = get_all_towns_addresses()
    else:
        data = get_town_addresses(town)
    addresses = [addr for addr in data
                 if geo.is_point_inside(addr()[3], path)]
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
