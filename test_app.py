## Justin Wong
## testing remote streamlit for territory app

import streamlit as st

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

setup()