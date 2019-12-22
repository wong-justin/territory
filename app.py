## Justin Wong
## using streamlit for territory app

import streamlit as st
import time
import territory as t
from PIL import Image

api_key = t.get_api_key()

def setup():
    st.title('Territory')
    st.write('look at address data')
    st.write('___')
      
    user_modes = {
        'discovery': {
            'descrip': 'play around, find new data, produce images',
            'func': discovery_mode
        },
        'review': {
            'descrip': 'look at my results and data analysis',
            'func': review_mode
        },
        'reverse geocode': {
            'descrip': 'ping grid to find addresses in region',
            'func': rev_geocode_mode
        }
    }
    options = list(user_modes.keys())

    # mode options
    st.sidebar.markdown('### modes:')
    choice = st.sidebar.radio('', options, index=1)
    # display descrip below radio
    st.sidebar.markdown(user_modes[choice]['descrip'])
    st.sidebar.markdown('___')

    # run mode in main window
    user_modes[choice]['func']()

def discovery_mode():
    st.write('you are in discovery mode')
    
    
    size = st.sidebar.slider('img size:', 100, 2000, 500, 50)
    img_size = (size, size)
    scale = st.sidebar.radio('scale for dpi:',
                     [1, 2])
    img_format = st.sidebar.radio('img type:',
                          ['PNG', 'JPG', 'GIF'])
    map_type = st.sidebar.radio('type of map:',
                        ['roadmap', 'satellite', 'hybrid', 'terrain'])

#    center = (28.0, -81.0)
    center = None
    zoom = None
    path = None
    markers = None
    #    path = [(28.0, -81.0), (28.1, -81.0), (28.0, -81.1), (28.0, -81.0)]
    #    markers = [(28.0, -81.0), (28.1, -81.0)]

    if st.sidebar.checkbox('add region?'):
        terr = st.sidebar.selectbox(
            'select a territory',
            range(1,120))
        path = t.get_territories()['Door to door'][terr-1][2]
    
    if st.sidebar.checkbox('add zoom?'):
        zoom = st.sidebar.slider('zoom level:', 0, 21, 17, 1)
        
    if st.sidebar.button('create map'):
        with st.spinner('calling google api...'):
            t.store(img_size, scale, img_format, map_type)
            img_data = t.create_map(api_key, 
                                    center=center,
                                    zoom=zoom,
                                    path=path,
                                    markers=markers)

            st.image(img_data, 
                     caption='you just created this map',
                     use_column_width=True,
                     format=img_format)        
    
    st.sidebar.markdown('___')
        
    
#    'starting a long sample computation...'
#    latest_iter = st.empty()
#    bar = st.progress(0)
#
#    for i in range(100):
#        latest_iter.text('iteration {}'.format(i+1))
#        bar.progress(i+1)
#        time.sleep(0.1)
#
#    '... and finished now!'

    st.write('making a sample array')
    st.write([1,2,3,4])

    st.write('showing sample data')
    data = [5, 6, 7, 8]

    *data
    
    st.help(time)

def rev_geocode_mode():
    terr = st.sidebar.selectbox(
            'select a territory',
            range(1,120))
    
    path = t.get_territories()['Door to door'][terr-1][2]

    points_to_test = t.points_inside(path)
    num_points = len(points_to_test)

    img_data = t.create_map(api_key, 
                            markers=points_to_test, 
                            path=path)
    st.sidebar.image(img_data, 
             caption="you're going to ping these {} points".format(num_points), 
             use_column_width=True, 
             format='PNG')
            
    if st.sidebar.button('start?'):

        with st.spinner('getting addresses from rev geocoding...'):

            addresses_1 = t.get_addresses_in(api_key, 
                                           path)
            a1 = [a[0] for a in addresses_1]

            a1

        with st.spinner('getting addresses from county data...'):
            addresses_2 = t.get_houses_in(path)

            a2 = [a[0] for a in addresses_2]

            a2

        with st.spinner('analyzing results...'):
            pass
    
def review_mode():
    option = st.sidebar.selectbox(
        'select a territory',
        range(1,120))
    
    st.write('you selected terr: {}'.format(option))

    # show territory image
    img = Image.open('sample_dtd_v1/Door to door {}.png'.format(option))
    st.image(img,
             caption='territory {}'.format(option),
             use_column_width=True,
             format='PNG')
    
    # show terr houses
    # get houses per terr
    
setup()