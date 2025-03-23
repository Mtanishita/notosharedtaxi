### パッケージの読み込み
import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np
import plotly.express as px

## データの読み込み
df = pd.read_csv("nototaxi2.csv",encoding="cp932", header=1)

### サイドバー
st.sidebar.write("能登町予約制乗合タクシー利用状況")

# ユニークな値を変更
new_options = ['1:2月', '2:5-6月', '3:7月','4:11月','5:2025年1月']  # 新しいオプションリスト

# 対応関係を辞書で定義
option_to_term = {
    '1:2月': 1,
    '2:5-6月': 2,
    '3:7月': 3,
    '4:11月': 4,
    '5:2025年1月': 5
}

Term = st.sidebar.multiselect(
    "Select Terms",
    options=new_options,
    default=new_options
)
#Day = st.sidebar.slider("Select a day", 0, 31, (0, 31))

Day = st.sidebar.multiselect(
    "Select Days of Week",
    options=df["yobi"].unique(),
    default=df["yobi"].unique()
)

Binn = st.sidebar.multiselect(
    "Select 便 numbers",
    options=df["binn"].unique(),
    default=df["binn"].unique()
)

if Term:
    # 対応するtermを取得
    cterms = [option_to_term[option] for option in Term if option in option_to_term]
    df = df[df["term"].isin(cterms)]

if Day:
#   df = df[df["day"].between(Day[0], Day[1])]
    df = df[df["yobi"].isin(Day)]

if Binn:
    df = df[df["binn"].isin(Binn)]

### 右側

### ヒストグラム
#df['year2'] = df['year'].apply(lambda x: '2023' if x == 2023 else ('2024' if x == 2024 else '0'))
#fig =px.histogram(df,x='age', color='year2', nbins=10, barmode='overlay',
#     color_discrete_sequence=['green', 'blue'], opacity=0.3) 
#st.plotly_chart(fig)

yl = 500 *len(df)/3300

df['fX'] = np.where(df['binn']<3, df['O_X'], df['D_X'])
df['fY'] = np.where(df['binn']<3, df['O_Y'], df['D_Y'])

df23 = df[df['year'] == 2023]
df24 = df[df['year'] != 2023]

df231 =df23[["age","fX","fY"]].rename(columns={'fX': 'lon', 'fY': 'lat'})
df241 =df24[["age","fX","fY"]].rename(columns={'fX': 'lon', 'fY': 'lat'})

# lonとlatの列でデータを集計
size_df231 = df231.groupby(['lon', 'lat']).agg(
    mean=('age', 'mean'),
    count=('age', 'count')
).reset_index()

# サイズを調整（例: countの平方根をサイズに使用）
size_df231['size'] = size_df231['count'] ** 0.5 * 100  # スケーリングの調整
size_df231['mean_scaled'] = np.clip(size_df231['mean'], 0, 255)

df23_passenger = df[df['year'] == 2023]['passenger'].value_counts().reset_index()
df23_passenger.columns = ['passenger', 'count']
df23_passenger['count'] = df23_passenger['count']/df23_passenger['passenger']
df23_passenger['passenger'] = df23_passenger['passenger'].astype(str)

df241 =df24[["age","fX","fY"]].rename(columns={'fX': 'lon', 'fY': 'lat'})
df241['age'] = df241['age'].fillna(65)

# lonとlatの列でデータを集計
size_df241 = df241.groupby(['lon', 'lat']).agg(
    mean=('age', 'mean'),
    count=('age', 'count')
).reset_index()

# サイズを調整（例: countの平方根をサイズに使用）
size_df241['size'] = size_df241['count'] ** 0.5 * 100  # スケーリングの調整
size_df241['mean_scaled'] = np.clip(size_df241['mean'], 0, 255)

df24_passenger = df[df['year'] != 2023]['passenger'].value_counts().reset_index()
df24_passenger.columns = ['passenger', 'count']
df24_passenger['count'] = df24_passenger['count']/df24_passenger['passenger']
df24_passenger['passenger'] = df24_passenger['passenger'].astype(str)
 
# マップを作成
view_state = pdk.ViewState(
    latitude=37.311396,
    longitude=137.1451836,
    zoom=9,
    pitch=0,
)

# ヒストグラムを2023年と2024年で分けて表示
col_1, col_2 = st.columns(2)

with col_1:
    st.title("2023")
    fig23 = px.histogram(df23, x='age', nbins=20, 
                         title="年齢のヒストグラム", 
                         color_discrete_sequence=['green'], 
                         opacity=0.7)
    fig23.update_yaxes(range=[0, yl])
    st.plotly_chart(fig23, use_container_width=True)

    st.write("地区別利用者数")
    layer = pdk.Layer(
       "ScatterplotLayer",
       size_df231,
       get_position='[lon, lat]',
       get_fill_color='[mean_scaled, 255, 0]',  # 色を指定
       get_radius='size',
       pickable=True,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

    fig_pie23 = px.pie(
        df23_passenger, 
        names='passenger', 
        values='count', 
        title='乗車人数分布',
        color_discrete_sequence=px.colors.sequential.Greens,
        category_orders={"passenger": ["1", "2", "3", "4"]}
    )
    st.plotly_chart(fig_pie23, use_container_width=True)

with col_2:
    st.title("2024")
    fig24 = px.histogram(df24, x='age', nbins=20, 
                         title="年齢のヒストグラム", 
                         color_discrete_sequence=['blue'], 
                         opacity=0.7)
    fig24.update_yaxes(range=[0, yl])
    st.plotly_chart(fig24, use_container_width=True)

    st.write("地区別利用者数")
    layer2 = pdk.Layer(
       "ScatterplotLayer",
       size_df241,
       get_position='[lon, lat]',
       get_fill_color='[mean_scaled, 200, 200]',  # 色を指定
       get_radius='size',
       pickable=True,
    )
    st.pydeck_chart(pdk.Deck(layers=[layer2], initial_view_state=view_state))

    fig_pie24 = px.pie(
        df24_passenger, 
        names='passenger', 
        values='count', 
        title="乗車人数分布",
        color_discrete_sequence=px.colors.sequential.Blues,
        category_orders={"passenger": ["1", "2", "3", "4"]}
    )
    st.plotly_chart(fig_pie24, use_container_width=True)