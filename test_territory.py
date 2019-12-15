## Justin Wong
## testing and optimizing territory project

import timeit
import territory as t

api_key = t.get_api_key()

#########################
###    PERFORMANCE    ###
#########################

setup = """
path = [(-81.203413903713241, 28.615474969803429),
        (-81.203368306159987, 28.612065472508572),
        (-81.204607486724868, 28.612065472508572),
        (-81.204639673233046, 28.6130638450546),
        (-81.2051546573639, 28.613365238675311),
        (-81.205181479454055, 28.615470260629358),
        (-81.203413903713241, 28.615474969803429)]
path = [(x[1], x[0]) for x in path]
path *= 2

##########
## Finding center of path
##########

def avg_2loops():
# quickest for large paths (like 14+ points)
    center = ( sum((pt[0] for pt in path)) / len(path),
               sum((pt[1] for pt in path)) / len(path))
    return center

def avg_1loop_list():
    sums = [0, 0]
    for pt in path:
        sums[0] += pt[0]
        sums[1] += pt[1]
    center = (sums[0] / len(sums),
              sums[1] / len(sums))
    return center

def avg_1loop_tuple():
# quickest for short paths (like 7 points)
    sums = (0, 0)
    for pt in path:
        sums = (sums[0] + pt[0],
                sums[1] + pt[1])
    center = (sums[0] / len(sums),
              sums[1] / len(sums))
    return center
########
"""

def test_center_calculation_versions_time():
    t1 = timeit.Timer(stmt='avg_2loops()', setup=setup)
    print(t1.timeit(100000))

    t2 = timeit.Timer(stmt='avg_1loop_list()', setup=setup)
    print(t2.timeit(100000))

    t3 = timeit.Timer(stmt='avg_1loop_tuple()', setup=setup)
    print(t3.timeit(100000))

###########################
###    FUNCTIONALITY    ###
###########################

def test_geocoding():
    address = 'maple street oviedo'
    address = '2847 Yonkers Court, Oviedo, FL'
    address = '1533 sultan cir'
    address = '3205 Town and Country Rd, Oviedo, FL 32766, USA'
    print(t.get_lat_lng(api_key, address))

def test_rev_geocoding():
    latlng = (28.656202, -81.2026264)    
    latlng = (28.6262682, -81.1088977)
    latlng = (28.652851, -81.186386)    # middle of culdesac
    print(t.get_address(api_key, latlng))

def test_map_centerzoom():
    oviedo_coords = (28.6700, -81.2081)  
    img_data = t.map_img_center(api_key, oviedo_coords, 17)
    t.save_img('sample_area_test', img_data)

def test_map_path():
    path = t.territory_bounds()
    img_data = t.map_img_path(api_key, path)
    t.save_img('sample_path_test', img_data)

def test_map_markers():
    territories = t.get_territories()
    t54 = territories['Door to door'][54-1]
    path = t54[2]
    points = t.points_inside(path)
    img_data = t.map_img_markers(api_key, points)
    t.save_img('t54_markers', img_data)

def test_maps_of_type():    
    t.maps_for_type('Apartment')

def test_bounding_point_count():
    t.bounding_points_count()

def test_rev_geocoding_accuracy():
    rand_addresses = ['1054 Long Branch Ln, Oviedo, FL 32765, USA',
                      '1007 Gore Dr, Oviedo, FL 32765, USA']
    t.rev_geocoding_accuracy(rand_addresses)

def test_points_inside():
    territories = t.get_territories()
    t52 = territories['Door to door'][52-1]
    path = t52[2]
    points = t.points_inside(path)
    print(len(points))
    print(points)

def test_get_addresses_in():
    territories = t.get_territories()
    t52 = territories['Door to door'][51]
    path = t52[2]
    addresses = t.get_addresses_in(api_key, path)
    print(addresses)

def test_parcel_vs_latlng():
    p1 = [593603.3760954104, 1563091.1136661917]
    l1 = (28.6335359, -81.19505219999999)
    p2 = [607784.3310925364, 1568306.8572325185]
    l2 = (28.6479385, -81.1508453)

    p2 = [601687.0365386121, 1580730.8377347142]
    l2 = (28.6820661, -81.16990489999999)
    t.parcel_vs_latlng(p1, p2, l1, l2)


test_bounding_point_count()
