## Justin Wong
## testing and optimizing territory project

from timeit import default_timer as timer
import territory as t
import json

api_key = t.get_api_key()

#########################
###    PERFORMANCE    ###
#########################

def time(func, *args, n=100000):
    start = timer()
    for _ in range(n):
        func(*args)
    end = timer()
    print(end - start)
    return end - start
    
def test_center_calculation_versions_time():
    path = [(-81.203413903713241, 28.615474969803429),
        (-81.203368306159987, 28.612065472508572),
        (-81.204607486724868, 28.612065472508572),
        (-81.204639673233046, 28.6130638450546),
        (-81.2051546573639, 28.613365238675311),
        (-81.205181479454055, 28.615470260629358),
        (-81.203413903713241, 28.615474969803429)]
    path = [(x[1], x[0]) for x in path]
    path *= 2
    
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
    
    time(avg_2loops)
    time(avg_1loop_list)
    time(avg_1loop_tuple)

def test_houses_search_versions_time():
    terrs = t.get_territories()
    t52 = terrs['Door to door'][52-1]
    t52_boundary = t52[2]

    t1 = time(t.get_houses_in, t52_boundary, 'oviedo', n=2)
    t2 = time(t.get_houses_in, t52_boundary, n=2)
    print('v1:', t1)
    print('v2:', t2)

def test_loop_vs_list_comp_time():
    # results: about same timing
    terrs = t.get_territories()
    
    def loop(data):
        addresses = []
        for addr, addr_details in data.items():
            if t.is_point_inside(addr_details[2], t52_boundary):
                addresses.append((addr, addr_details))
        return addresses

    def list_comp(data):
        addresses = [(addr, v) for addr, v in data.items()
                     if t.is_point_inside(v[2], t52_boundary)]
        return addresses
        
    t52_boundary = terrs['Door to door'][52-1][2]
    oviedo_data = t.open_town_data('oviedo')
    
    print('oviedo search (large)')
    time(loop, oviedo_data, n=20)
    time(list_comp, oviedo_data, n=20)

    t110_boundary = terrs['Door to door'][110-1][2]
    geneva_data = t.open_town_data('geneva')

    print('geneva search (smaller)')
    time(loop, geneva_data, n=150)
    time(list_comp, geneva_data, n=150)

def test_house_sorting_time():
    oviedo = t.open_town_data('oviedo')
    geneva = t.open_town_data('geneva')
    chuluota = t.open_town_data('chuluota')
    all_towns = {**oviedo, **geneva, **chuluota}
    territories = t.get_territories()['Door to door']
    town_data = {'oviedo': oviedo, 'geneva': geneva, 'chuluota': chuluota}
    
    def loop_terrs():
        houses_in_each = []
        for terr in territories:
            houses_in_each.append(
                [(addr, *details) for addr, details in all_towns.items()
                 if t.is_point_inside(details[2], terr[2])])
        return houses_in_each

    def loop_houses():
        houses_in_each = []
        for addr, details in all_towns.items():
            houses_in_each.append(
                [(addr, *details) for terr in territories
                 if t.is_point_inside(details[2], terr[2])])
        return houses_in_each
    
    def loop_terrs_refine():
        areas = ['oviedo']*52 + ['chuluota']*14 + ['oviedo']*21 + ['chuluota']*17 + ['geneva']*12 + ['oviedo']*3
        houses_in_each = []
        for terr in territories:
            town_of_terr = areas[terr[1]-1]
            data = town_data[town_of_terr]
            houses_in_each.append(
                [(addr, *details) for addr, details in data.items()
                 if t.is_point_inside(details[2], terr[2])])
        return houses_in_each
    
    time(loop_terrs, n=1)
    time(loop_houses, n=1) 
    time(loop_terrs_refine, n=1)

    

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
    img_data = t.create_map(api_key, markers=points)
    #img_data = t.map_img_markers(api_key, points)
    t.save_img('t54_markers_new', img_data)

def test_create_map():
    center = None
    zoom = 17
    path = t.get_territories()['Door to door'][82-1][2]
    path = None
    markers = None
    img_data = t.create_map(api_key, 
                            center=center,
                            zoom=zoom,
                            path=path,
                            markers=markers)
    t.save_img('sample_new_map', img_data)
    
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

def get_addresses_in_territory():
    terrs = t.get_territories()
    t52 = terrs['Door to door'][52-1]
    t52_boundary = t52[2]

    oviedo_properties = t.open_oviedo_data()
    addr_in_t52 = [i for i in oviedo_properties.values()
                   if t.is_point_inside(i[2], t52_boundary)]
    print(addr_in_t52)
    print(len(addr_in_t52))
    
def test_open_town_data():
    t.open_town_data('chuluota')

def test_terr_from_town_data():
    t.get_terr_from_towns()

def test_get_streets():
    town_data = t.get_all_town_data()
    t.get_streets_in(town_data)    

def test_get_houses_in():
    terrs = t.get_territories()
    t52 = terrs['Door to door'][52-1]
    t52_boundary = t52[2]

    t.get_houses_in(t52_boundary, town='oviedo')
    t.get_houses_in(t52_boundary, town='geneva')

def test_sort_houses_into_territories():
    t.sort_houses_into_territories()

def test_store():  
    print(type(t.store))
    print(type(t.store.values))
    print(t.store)
    
    old_values = t.store()
    t.store((5, 7), 1, 'jpg', 'hybrid')
    new_values = t.store()
    t.store_defaults()
    back_to_old = t.store()
    
    print(old_values, new_values, back_to_old)    

if __name__ == '__main__':
    test_map_markers()