import streamlit as st
from PIL import Image

vImagemIcon = Image.open( 'images/home.png' )

st.set_page_config( page_title='Home', page_icon=vImagemIcon, layout='wide' )

vImagem = Image.open( 'images/curry_logo.png' )
st.sidebar.image( vImagem, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '# A entrega mais rápida da cidade' )
st.sidebar.markdown( """---""" )

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    ### Ajuda?
    https://www.linkedin.com/in/mauriciolucianods/
    """
)