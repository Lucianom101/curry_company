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

    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ') 
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Road_traffic_density'] != 'NaN ') 
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['City'] != 'NaN') 
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Festival'] != 'NaN ') 
    df = df.loc[linhas_selecionadas, :].copy()

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

def calc_tempo_medio_dp_cidade( df, tp_grafico ):
    if tp_grafico == 'barras':
        cols = [ 'Time_taken(min)', 'City' ]
        df2 = df.loc[ :, cols ].groupby( ['City'] ).agg( Tempo_Médio_Entrega = ('Time_taken(min)', 'mean'), Desvio_Padrão = ('Time_taken(min)', 'std') ).reset_index()
        fig = go.Figure()
        fig.add_trace( go.Bar( name='Control', x=df2[ 'City' ], y=df2[ 'Tempo_Médio_Entrega' ], error_y=dict( type='data', array=df2[ 'Desvio_Padrão' ] ) ) )
        fig.update_layout( barmode='group' )

        return fig
    
    elif tp_grafico == 'solar':
        cols = [ 'Time_taken(min)', 'City', 'Road_traffic_density' ]
        df2 = (df.loc[ :, cols ].groupby( ['City', 'Road_traffic_density'] )
                                .agg( Tempo_Médio_Entrega = ('Time_taken(min)', 'mean'), Desvio_Padrão = ('Time_taken(min)', 'std') )
                                .reset_index() )
        fig = px.sunburst( df2
                        , path=[ 'City', 'Road_traffic_density' ]
                            , values='Tempo_Médio_Entrega'
                            , color='Desvio_Padrão'
                            , color_continuous_scale='RdBu'
                            , color_continuous_midpoint=np.average( df2[ 'Desvio_Padrão' ] ) )
        
        return fig
    
    elif tp_grafico == 'pizza':
        cols = [ 'Distance_km', 'City' ]
        df1 = df.loc[ :, cols ].groupby( ['City'] ).mean().reset_index()
        fig = go.Figure( data=[ go.Pie( labels=df1['City'], values=df1['Distance_km'], pull=[ 0, 0.1 ] ) ] )

        return fig
    
    elif tp_grafico == 'tabela':
        cols = [ 'Time_taken(min)', 'City', 'Type_of_order' ]
        df2 = ( df.loc[ :, cols ].groupby( ['City', 'Type_of_order'] )
                                 .agg( Tempo_Médio_Entrega = ('Time_taken(min)', 'mean'), Desvio_Padrão = ('Time_taken(min)', 'std') )
                                 .reset_index() )
        return df2

def calc_tempo_medio_dv_festival( df, festival, tp_operacao ):
    if festival == 'sim':
        op_fest = 'Yes'
    
    elif festival == 'nao':
        op_fest = 'No'
    
    if tp_operacao == 'media':
        v_test = df.loc[ ( df['Festival'] == op_fest ), [ 'Time_taken(min)' ] ].mean()
        v_test = round( v_test.astype(float), 2)

    elif tp_operacao == 'desvio padrao':
        v_test = df.loc[ ( df['Festival'] == op_fest ), [ 'Time_taken(min)' ] ].std()
        v_test = round( v_test.astype(float), 2)
    
    return v_test

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

vImagemIcon = Image.open( 'images/restaurantes.png' )

st.set_page_config( page_title='Visão Restaurantes', layout='wide', page_icon=vImagemIcon )

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
        st.header( 'Métricas Gerais' )

        col1, col2, col3, col4, col5, col6 = st.columns( 6, gap='large' )

        with col1:
            v_qtd_entreg_unicos = df[ 'Delivery_person_ID' ].nunique()
            st.metric( 'Entregadores Únicos', v_qtd_entreg_unicos )
        
        with col2:
            v_media_dist = round( df[ 'Distance_km' ].mean(), 2 )
            st.metric( 'Distância média (km)', v_media_dist )

        with col3:
            st.metric( 'Média c/ Festival(min)', calc_tempo_medio_dv_festival( df, 'sim', 'media' ) )

        with col4:
            st.metric( 'Desv. Pad. c/ Festival(min)', calc_tempo_medio_dv_festival( df, 'sim', 'desvio padrao' ) )

        with col5:
            st.metric( 'Média s/ Festival(min)', calc_tempo_medio_dv_festival( df, 'nao', 'media' ) )

        with col6:
            st.metric( 'Desv. Pad. s/ Festival(min)', calc_tempo_medio_dv_festival( df, 'nao', 'desvio padrao' ) )
    
    with st.container():
        st.divider()
        st.markdown( '### Tempo médio e desvio padrão por cidade' )
        fig = calc_tempo_medio_dp_cidade( df, 'barras' )
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        st.divider()
        col1, col2 = st.columns( 2, gap='large' )
        
        with col1:
            st.markdown( '### Tempo médio de entrega por cidade' )
            fig = calc_tempo_medio_dp_cidade( df, 'pizza' )
            st.plotly_chart( fig )

        with col2:
            st.markdown( '### Tempo médio e desvio padrão por cidade - Sunburst' )
            fig = calc_tempo_medio_dp_cidade( df, 'solar' )
            st.plotly_chart( fig )

    with st.container():
        st.divider()
        st.markdown( '### Tempo médio e desvio padrão por cidade e tipo de pedido' )
        st.dataframe( calc_tempo_medio_dp_cidade( df, 'tabela' ) )

with tab2:
    st.divider()
with tab3:
    st.divider()