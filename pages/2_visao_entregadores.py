#==================================================================================================================================================================
# Importação das bibliotecas necessárias para o trabalho
#==================================================================================================================================================================
import pandas as pd
import plotly.express as px
import folium
import numpy as np
import plotly.graph_objects as go
import geopy.distance
import streamlit as st
from haversine import haversine
from datetime import date
from PIL import Image
from streamlit_folium import folium_static

#================================================================================================================================================================
# Funções
#================================================================================================================================================================

#==================================================================================================================================================================
# Limpeza dos dados do dataset
#==================================================================================================================================================================

def clean_code( df ):
    """Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( Remoção do texto da variável numérica )
        6. Criação da variável "Distance_km" que mostra a distância geográgica entre o restaurante e o endereço de entrega
    
    """

    #1.Fazendo uma cópia do DataFrame Lido
    df = df_original.copy()

    #2.Removendo o espaço dos valores das colunas
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()

    #3.Excluir as linhas com a idade dos entregadores vazia ( Conceitos de seleção condicional )
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    linhas_vazias = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[linhas_vazias, :]

    #4.Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    #5.Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    #6.Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    #7.Remove as linhas da culuna multiple_deliveries que tenham o conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    #8. Limpando a coluna de time taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df['Time_taken(min)']  = df['Time_taken(min)'].astype( int )

    #9.Removendo "conditions " do campo "Weatherconditions"
    df['Weatherconditions'] = df['Weatherconditions'].str.replace( 'conditions ', '' )

    #10.Criando coluna da distancia entre o restaurante e o endereço de entrega em quilômetros
    # Opção com Lambda
    # colunas_selecionadas = [ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
    # df[ 'Distance_km' ] = ( df.loc[ :, colunas_selecionadas ].apply( lambda x:round( geopy.distance.geodesic( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ).km, 2) , axis=1) )
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df['Distance_km'] = df.loc[:, cols].apply( lambda x: haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                                     (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 )

    return df

def calc_top_entregadores( df, tp_entregador, asc_bool ):
    cols = [ 'Delivery_person_ID', 'City', 'Time_taken(min)' ]

    if tp_entregador == 'R': #Entregadores mais rápidos
        df_aux = df.loc[ :, cols ].groupby( [ 'City', 'Delivery_person_ID' ] ).min().sort_values( [ 'City', 'Time_taken(min)' ], ascending = asc_bool ).reset_index()
    
    elif tp_entregador == 'L': #Entregadores mais lentos
        df_aux = df.loc[ :, cols ].groupby( [ 'City', 'Delivery_person_ID' ] ).max().sort_values( [ 'City', 'Time_taken(min)' ], ascending = asc_bool ).reset_index()

    df_aux01 = df_aux.loc[ ( df_aux['City'] == 'Metropolitian' ), : ].head(10)
    df_aux02 = df_aux.loc[ ( df_aux['City'] == 'Urban' ), : ].head(10)
    df_aux03 = df_aux.loc[ ( df_aux['City'] == 'Semi-Urban' ), : ].head(10)

    df1 = pd.concat( [ df_aux01, df_aux02, df_aux03 ] ).reset_index( drop=True )
    
    return df1

#==========================================================Início da estrutura do código===========================================================================
#==================================================================================================================================================================
# Leitura do dataset para as operações
#==================================================================================================================================================================

df_original = pd.read_csv('dataset/train.csv')

#==================================================================================================================================================================
# Chamada da limpeza dos dados
#==================================================================================================================================================================

df = clean_code( df_original )
# #==================================================================================================================================================================
# # Barra Lateral - Streamlit
# #==================================================================================================================================================================

vImagemIcon = Image.open( 'images/entregadores.png' )

st.set_page_config( page_title='Visão Entregadores', layout='wide', page_icon=vImagemIcon )

vImagem = Image.open( 'images/curry_logo.png' )
st.sidebar.image( vImagem, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '# A entrega mais rápida da cidade' )
st.sidebar.markdown( """---""" )

vDataPedido_slider = st.sidebar.slider(
    label='Selecione uma data'
   ,value=pd.datetime( 2022, 4, 13 )
   ,min_value=pd.datetime( 2022, 2, 11 )
   ,max_value=pd.datetime( 2022, 4, 13 )
   ,format='DD/MM/YYYY'
    )

st.sidebar.markdown( """---""" )

vTrafego_select = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    [ 'Low', 'Medium', 'High', 'Jam' ],
    default=[ 'Low', 'Medium', 'High', 'Jam' ]
)

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Filtro de data
linhas_selecionadas = df['Order_Date'] < vDataPedido_slider
df = df.loc[ linhas_selecionadas, : ]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( vTrafego_select )
df = df.loc[ linhas_selecionadas, : ]

# st.dataframe( df )

# #==================================================================================================================================================================
# # Layout Page - Streamlit
# #==================================================================================================================================================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '---', '---'] )

with tab1:
    with st.container():
        st.title( 'Métricas gerais' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
    
        with col1:
            v_max_age = df['Delivery_person_Age'].max()
            st.metric( 'Maior Idade', v_max_age )

        with col2:
            v_min_age = df['Delivery_person_Age'].min()
            st.metric( 'Menor Idade', v_min_age )

        with col3:
            v_max_vc = df['Vehicle_condition'].max()
            st.metric( 'Melhor Condição Veículo', v_max_vc )

        with col4:
            v_min_vc = df['Vehicle_condition'].min()
            st.metric( 'Pior Condição Veículo', v_min_vc )
    
    with st.container():
        st.divider()

        st.title( 'Avaliações' )

        col1, col2 = st.columns( 2, gap='large' )

        with col1:
            st.markdown( '### Média por entregador' )
            cols = [ 'Delivery_person_ID' , 'Delivery_person_Ratings' ]

            df1 = df.loc[:, cols].groupby( [ 'Delivery_person_ID' ] ).mean().reset_index()

            st.dataframe( df1 )

        with col2:
            st.markdown( '### Média por trânsito' )
            cols = [ 'Delivery_person_Ratings' , 'Road_traffic_density' ]
            df1 = df.loc[:, cols].groupby( [ 'Road_traffic_density' ] ).agg( Média = ( 'Delivery_person_Ratings', 'mean' ), Desvio_Padrão = ( 'Delivery_person_Ratings', 'std' ) ).reset_index()
            st.dataframe( df1 )

            st.markdown( '### Média por condições climáticas' )
            cols = [ 'Delivery_person_Ratings' , 'Weatherconditions' ]
            df1 = df.loc[:, cols].groupby( [ 'Weatherconditions' ] ).agg( Média = ( 'Delivery_person_Ratings', 'mean' ), Desvio_Padrão = ( 'Delivery_person_Ratings', 'std' ) ).reset_index()
            st.dataframe( df1 )

    with st.container():
        st.divider()
        
        st.title( 'Velocidade de entrega' )

        col1, col2 = st.columns( 2, gap='large' )

        with col1:
            st.markdown( '### Top entregadores mais rápidos' )
            st.dataframe( calc_top_entregadores( df, 'R', True ) )

        
        with col2:
            st.markdown( '### Top entregadores mais lentos' )
            st.dataframe( calc_top_entregadores( df, 'L', False ) )

with tab2:
    st.divider()

with tab3:
    st.divider()