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

def pedidos_dia( df ):
    cols = ['ID', 'Order_Date']
    df_aux = df.loc[:, cols].groupby(by = ['Order_Date']).count().reset_index()
    df_aux.columns = ['Data_Entrega', 'Qtde_Entrega']

    #Criação do gráfico
    fig = px.bar(df_aux, x = 'Data_Entrega', y = 'Qtde_Entrega')

    return fig

def pedidos_trafego( df ):
    cols = [ 'ID', 'Road_traffic_density' ]
    df_aux = df.loc[:, cols].groupby( [ 'Road_traffic_density' ] ).count().reset_index()
    df_aux['Perc_per_traffic'] = 100 * ( df_aux[ 'ID' ] / df_aux[ 'ID' ].sum() )

    fig = px.pie( df_aux, values='Perc_per_traffic', names='Road_traffic_density' )

    return fig

def pedidos_cidade_trafego( df ):
    cols = [ 'ID', 'City', 'Road_traffic_density' ]
    df_aux = df.loc[ :, cols ].groupby( [ 'City', 'Road_traffic_density' ] ).count().reset_index()

    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID' )
    return fig

def pedidos_semana( df ):
    df['Order_Date'] = pd.to_datetime(df.Order_Date, format='%Y-%m-%d')
    df['Week_Year'] = df['Order_Date'].dt.strftime( "%U" )

    cols = ['ID', 'Week_Year']
    df_aux = df.loc[:, cols].groupby( ['Week_Year'] ).count().reset_index()
    df_aux.columns = ['Semana do ano', 'Qtde entrega']

    fig = px.line( df_aux, x = 'Semana do ano', y = 'Qtde entrega' )
    return fig

def pedidos_entregador_semana( df ):
    cols1 = [ 'ID', 'Week_Year' ]
    cols2 = [ 'Delivery_person_ID', 'Week_Year' ]
    df_aux1 = df.loc[ :, cols1 ].groupby( [ 'Week_Year' ] ).count().reset_index()
    df_aux2 = df.loc[ :, cols2 ].groupby( [ 'Week_Year' ] ).nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )

    df_aux['Order_by_deliver'] = df_aux[ 'ID' ] / df_aux[ 'Delivery_person_ID' ]

    fig = px.line( df_aux, x='Week_Year', y='Order_by_deliver' )
    return fig

def mapa_localizacao_cidade_trafego( df ):
    cols = [ 'City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]
    df_aux = df.loc[ :, cols ].groupby( [ 'City', 'Road_traffic_density' ] ).median().reset_index()

    map = folium.Map( zoom_start=11 )

    for index, location_info in df_aux.iterrows():
        folium.Marker( [ location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude'] ],
                        popup=location_info[ [ 'City', 'Road_traffic_density' ] ] ).add_to( map )
    
    folium_static( map, width=1024, height=600 )

#==========================================================Início da estrutura do código===========================================================================
#==================================================================================================================================================================
# Leitura do dataset para as operações
#==================================================================================================================================================================

df_original = pd.read_csv('dataset/train.csv')

#==================================================================================================================================================================
# Chamada da limpeza dos dados
#==================================================================================================================================================================

df = clean_code( df_original )

#==================================================================================================================================================================
# Barra Lateral - Streamlit
#==================================================================================================================================================================

vImagemIcon = Image.open( 'images/empresas.png' )
st.set_page_config( page_title='Visão Cliente', layout='wide', page_icon=vImagemIcon )

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
tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', 'Visão Tática', 'Visão Geográfica' ] )

with tab1:
    with st.container():
        fig = pedidos_dia( df )
        st.markdown( '### Pedidos por dia' )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        col1, col2 = st.columns( 2 )

        with col1:
            st.markdown( '### Pedidos por semana.' )
            fig = pedidos_trafego( df )
            st.plotly_chart( fig )
        
        with col2:
            st.markdown( 'Comparação do volume de pedidos por cidade e tipo de tráfego' )
            fig = pedidos_cidade_trafego( df )
            st.plotly_chart( fig )

with tab2:
    with st.container():
        st.markdown( '## Pedidos por semana' )
        fig = pedidos_semana( df )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        st.markdown( '## Quantidade de pedidos por entregador por semana' )
        fig = pedidos_entregador_semana( df )
        st.plotly_chart( fig, use_container_width=True )

with tab3:
    st.markdown( '## Localização central de cada cidade por tipo de tráfego' )
    mapa_localizacao_cidade_trafego( df )