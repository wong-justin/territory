## Justin Wong
## testing and optimizing territory project

from timeit import default_timer as timer
import territory as t
import json
import geometry as geo

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
        for addr in data:
            if geo.is_point_inside(addr()[3], t52_boundary):
                addresses.append(addr)
        return addresses

    def list_comp(data):
        addresses = [addr for addr in data
                     if geo.is_point_inside(addr()[3], t52_boundary)]
        return addresses
        
    t52_boundary = terrs['Door to door'][52-1][2]
    oviedo_data = t.get_town_addresses('oviedo')
    
    print('oviedo search (large)')
    time(loop, oviedo_data, n=20)
    time(list_comp, oviedo_data, n=20)

    t110_boundary = terrs['Door to door'][110-1][2]
    geneva_data = t.get_town_addresses('geneva')

    print('geneva search (smaller)')
    time(loop, geneva_data, n=150)
    time(list_comp, geneva_data, n=150)

def test_house_sorting_time():
    oviedo = t.get_town_addresses('oviedo')
    geneva = t.get_town_addresses('geneva')
    chuluota = t.get_town_addresses('chuluota')
    all_towns = oviedo + chuluota + geneva
    territories = t.get_territories()['Door to door']
    town_data = {'oviedo': oviedo, 'geneva': geneva, 'chuluota': chuluota}
    
    def loop_terrs():
        houses_in_each = []
        for terr in territories:
            houses_in_each.append(
                [addr for addr in all_towns
                 if geo.is_point_inside(addr()[3], terr[2])])
        return houses_in_each

    def loop_houses():
        houses_in_each = []
        for addr in all_towns:
            houses_in_each.append(
                [addr for terr in territories
                 if geo.is_point_inside(addr()[3], terr[2])])
        return houses_in_each
    
    def loop_terrs_refine():
        areas = ['oviedo']*52 + ['chuluota']*14 + ['oviedo']*21 + ['chuluota']*17 + ['geneva']*12 + ['oviedo']*3
        houses_in_each = []
        for terr in territories:
            town_of_terr = areas[terr[1]-1]
            data = town_data[town_of_terr]
            houses_in_each.append(
                [addr for addr in data
                 if geo.is_point_inside(addr()[3], terr[2])])
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

def test_create_map():
    territories = t.get_territories()
    t52 = territories['Door to door'][52-1]
    
    center = (28.6700, -81.2081)  # oviedo center
    zoom = 17
    path = t52[2]
    markers = geo.points_inside(path)
    
    img_data = t.create_map(api_key, 
                            center=center,
                            zoom=zoom)
    t.save_img('sample_map_center_zoom', img_data)
    img_data = t.create_map(api_key, 
                            markers=markers)
    t.save_img('sample_map_markers', img_data)
    img_data = t.create_map(api_key, 
                            path=path,
                            markers=markers)
    t.save_img('sample_map_path_markers', img_data)
    
def test_maps_of_type():    
    t.maps_for_type('Apartment')

def test_bounding_point_count():
    """
    Finds the number of points each territory is bounded by, then overall avg.
    
    # INPUT -----------
    # RETURN ----------
    """
    
    territories = t.get_territories()
    all_coord_amounts = []
    for each_terr_type, each_terr_list in territories.items():
        this_type_coord_amounts = [len(terr[2]) for terr in each_terr_list]
        all_coord_amounts += this_type_coord_amounts
    print('list of num bounding points',
          all_coord_amounts)
    print('avg num bounding points',
          sum(all_coord_amounts) / len(all_coord_amounts))

def test_rev_geocoding_accuracy():
    """
    Using any addresses, finds coordinates and then reverse geocode.
    Compares results to how close it is to original address.
    Appends results to text file.
    """
    addresses = ['1054 Long Branch Ln, Oviedo, FL 32765, USA', 
                 '1007 Gore Dr, Oviedo, FL 32765, USA']
    
    with open('rev_geocoding_results.txt', 'a+') as file:
        for address in addresses:
            latlng = t.get_lat_lng(api_key, address)
            rev_addresses = t.get_address(api_key, latlng)
            found_original = address in [rev_addr()[0] for rev_addr in rev_addresses]
            distances = [geo.dist(latlng, rev_addr()[3]) for rev_addr in rev_addresses]
            avg_distance = sum(distances) / len(distances)
            # format output #
            s1 = address + ' - ' + str(latlng)
            s2 = '\n'.join(['\t' + rev_addr()[0] + ' - ' + str(rev_addr()[3])
                            for rev_addr in rev_addresses])
            s3 = ''
            s4 = '\t' + 'found original? ' + str(found_original)
            s5 = '\t' + 'distances from original: ' + str(distances)
            s6 = '\t' + 'avg distance: ' + str(avg_distance)
            s7 = '\n'
            lines = '\n'.join((s1, s2, s3, s4, s5, s6, s7))
            print(lines)
            file.write(lines)

def test_points_inside():
    territories = t.get_territories()
    t52 = territories['Door to door'][52-1]
    path = t52[2]
    points = geo.points_inside(path)
    print(len(points))
    print(points)

def test_get_addresses_in():
    territories = t.get_territories()
    t52 = territories['Door to door'][51]
    path = t52[2]
    addresses = t.get_addresses_in(api_key, path)
    addresses = t.remove_duplicates(addresses)
    print([addr()[0] for addr in addresses])

def get_addresses_in_territory():
    terrs = t.get_territories()
    t52 = terrs['Door to door'][52-1]
    t52_boundary = t52[2]

    oviedo_properties = t.get_town_addresses('oviedo')
    addrs_in_t52 = [addr for addr in oviedo_properties
                    if geo.is_point_inside(addr()[3], t52_boundary)]
    print(len(addrs_in_t52))
    print([addr()[0] for addr in addrs_in_t52])
    
def test_get_town_addresses():
    addresses = t.get_town_addresses('chuluota')
    print([addr()[0] for addr in addresses])

def test_get_streets():
    town_data = t.get_all_towns_addresses()
    t.get_streets_in(town_data)    

def test_get_houses_in():
    terrs = t.get_territories()
    t52 = terrs['Door to door'][52-1]
    t52_boundary = t52[2]

    t.get_houses_in(t52_boundary, town='oviedo')
    t.get_houses_in(t52_boundary, town='geneva')

def test_sort_houses_into_territories():
    print(t.sort_houses_into_territories())

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

def test_address_lambda():
    some_house = t.address('2999 Yonkers Ct', 'Oviedo', '32765', (21.111321441, -83.124981250))
    print(some_house)
    
    print(some_house())
    print(some_house())
    
def test_shorten_latlng():
    pt = (21.111321441, -83.124981250)
    print(pt)
    print(t.shorten_latlng(pt))
    
def test_parcel_vs_latlng():
    """
    Compares seminole county parcel coords to global latlngs.
    Appears that they are not consistent distance ratios.
    """
    
    p1 = [593603.3760954104, 1563091.1136661917]
    l1 = (28.6335359, -81.19505219999999)
    p2 = [607784.3310925364, 1568306.8572325185]
    l2 = (28.6479385, -81.1508453)

    p2 = [601687.0365386121, 1580730.8377347142]
    l2 = (28.6820661, -81.16990489999999)
    x_diff_parcel = p2[0] - p1[0]
    x_diff_latlng = l2[0] - l1[0]
    x_ratio = x_diff_parcel / x_diff_latlng

    y_diff_parcel = p2[1] - p1[1]
    y_diff_latlng = l2[1] - l1[1]
    y_ratio = y_diff_parcel / y_diff_latlng

    print(x_diff_parcel, x_diff_latlng, 'xratio', x_ratio)
    print(y_diff_parcel, y_diff_latlng, 'yratio', y_ratio)

if __name__ == '__main__':
    test_sort_houses_into_territories()