## Justin Wong
## using streamlit for territory app

import streamlit as st
import time
import territory as t
import test_territory as test
from PIL import Image

def setup():
    st.title('Territory')

    st.write('markdown here')
    st.write('___')
      
    user_modes = {
        'discovery': {
            'descrip': 'play around, find new data, produce images',
            'func': discovery_mode
        },
        'review': {
            'descrip': 'look at my results and data analysis',
            'func': review_mode
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
    
    if st.checkbox('Call sample img fom google'):
        call_sample_img()
    else:
        # don't show anything
        pass
    
    'starting a long sample computation...'
    latest_iter = st.empty()
    bar = st.progress(0)

    for i in range(100):
        latest_iter.text('iteration {}'.format(i+1))
        bar.progress(i+1)
        time.sleep(0.1)

    '... and finished now!'

    st.write('making a sample array')
    st.write([1,2,3,4])

    st.write('showing sample data')
    data = [5, 6, 7, 8]

    *data

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
    

    
    
def call_sample_img():
    update = st.empty()    
    bar = st.progress(0)

    api_key = t.get_api_key()
    path = t.territory_bounds()

    update.text('calling google API...')
    bar.progress(33)
    img_data = t.map_img_path(api_key, path)

    update.text('img retrieved')
    bar.progress(100)
    st.image(img_data, 
             caption='sample image',
             use_column_width=True,
             format='PNG')
setup()