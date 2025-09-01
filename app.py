import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px
from datetime import datetime


# Configuración de la página

st.set_page_config(
    page_title="Dashboard de Ventas Dariel",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard de Ventas - Dariel")
st.markdown("Este dashboard interactivo muestra las ventas simuladas **por producto, región y tiempo**.")

st.markdown("---")

# Generación de datos realistas

np.random.seed(42)
fechas = pd.date_range('2023-01-01', '2025-12-31', freq='D')
productos = ['Laptop','Teclado Gamer','NVIDIA 5090 XT','Silla Gamer']
regiones = ['Norte','Sur','Este','Oeste','Centro']

data = []
for fecha in fechas:
    for _ in range(np.random.poisson(20)):  # promedio 20 ventas por día
        data.append({
            'fecha': fecha,
            'producto': np.random.choice(productos),
            'region': np.random.choice(regiones),
            'cantidad': np.random.randint(1,10),
            'precio_unitario': np.random.uniform(200,4000),
            'vendedor': f'Vendedor_{np.random.randint(1,21)}'
        })

df = pd.DataFrame(data)
df['venta_total'] = df['cantidad'] * df['precio_unitario']


# Barra lateral de filtros

st.sidebar.header(" Filtros")
producto_sel = st.sidebar.multiselect("Selecciona producto(s)", productos, default=productos)
region_sel = st.sidebar.multiselect("Selecciona región(es)", regiones, default=regiones)
fecha_sel = st.sidebar.date_input("Rango de fechas", [df['fecha'].min(), df['fecha'].max()])

# Filtrado de datos
df_filtro = df[
    (df['producto'].isin(producto_sel)) &
    (df['region'].isin(region_sel)) &
    (df['fecha'] >= pd.to_datetime(fecha_sel[0])) &
    (df['fecha'] <= pd.to_datetime(fecha_sel[1]))
]


# KPIs principales

total_ventas = df_filtro['venta_total'].sum()
total_unidades = df_filtro['cantidad'].sum()
ticket_promedio = total_ventas / total_unidades if total_unidades > 0 else 0

st.subheader(" KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Totales", f"${total_ventas:,.0f}")
col2.metric("Unidades Vendidas", f"{total_unidades:,}")
col3.metric("Ventas Promedio", f"${ticket_promedio:,.2f}")

st.markdown("---")


# Gráficos


# 1. Ventas mensuales
df_monthly = df_filtro.groupby(df_filtro['fecha'].dt.to_period('M'))['venta_total'].sum().reset_index()
df_monthly['fecha'] = df_monthly['fecha'].astype(str)

fig_monthly = px.line(
    df_monthly, x='fecha', y='venta_total',
    title=" Tendencia de Ventas Mensuales",
    labels={'venta_total': 'Ventas ($)', 'fecha': 'Mes'}
)
fig_monthly.update_traces(mode="lines+markers", line=dict(color="royalblue"))

# 2. Ventas por producto
df_producto = df_filtro.groupby('producto')['venta_total'].sum().reset_index().sort_values(by="venta_total", ascending=False)
fig_producto = px.bar(
    df_producto, x='producto', y='venta_total', text_auto='.2s',
    title=" Ventas por Producto", color="producto"
)

# 3. Ventas por región
df_region = df_filtro.groupby('region')['venta_total'].sum().reset_index()
fig_region = px.pie(
    df_region, values='venta_total', names='region',
    title=" Distribución de Ventas por Región",
    hole=0.4
)

# Colocamos los gráficos en 2 filas
st.subheader(" Visualizaciones")
col1, col2 = st.columns(2)
col1.plotly_chart(fig_monthly, use_container_width=True)
col2.plotly_chart(fig_producto, use_container_width=True)
st.plotly_chart(fig_region, use_container_width=True)

st.markdown("---")


# Tabla de datos

st.subheader(" Vista de Datos Filtrados")
st.dataframe(df_filtro.head(50))
