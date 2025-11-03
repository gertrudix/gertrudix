# app.py  — versión compacta basada en tu calculadora
import streamlit as st
import numpy as np

import sys, subprocess
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib>=3.8"])
    import matplotlib.pyplot as plt

REGIONES = {"Andalucía":1750,"Aragón":1650,"Asturias":1350,"Baleares":1600,"Canarias":1800,
"Cantabria":1350,"Castilla-La Mancha":1700,"Castilla y León":1550,"Cataluña":1550,
"Comunidad de Madrid":1600,"Comunidad Valenciana":1650,"Extremadura":1750,"Galicia":1350,
"La Rioja":1600,"Murcia":1700,"Navarra":1600,"País Vasco":1400,"Ceuta":1700,"Melilla":1700}
PRECIO_KWH=0.20; COSTE_PV_KWP=1200; FACTOR_CO2=0.231

st.set_page_config(page_title="Calculadora Energética", page_icon="🔆", layout="centered")
st.title("🔆 Calculadora Energética")

col1,col2=st.columns(2)
tipo=col1.selectbox("Tipo de vivienda",["Piso","Casa","Chalet"])
m2=col1.number_input("Metros cuadrados",20,1000,80,5)
personas=col1.number_input("Número de personas",1,12,3,1)

modo=col2.radio("Consumo en",["€ / mes","kWh / mes"])
valor=col2.number_input("Valor",min_value=0.0,value=60.0,step=1.0)
region=col2.selectbox("Región",list(REGIONES.keys()))
energias=st.multiselect("Tipo de energía de interés",["Solar","Eólica"],default=["Solar"])

def consumo_anual_kwh(modo,valor):
    kwh_mes = (valor/PRECIO_KWH) if modo=="€ / mes" else valor
    return kwh_mes*12

consumo_anual=consumo_anual_kwh(modo,valor)

# Modelo FV simple (ilustrativo)
prod_kwp=REGIONES[region]
ahorro_kwh = min(consumo_anual, prod_kwp*max(0.5, consumo_anual/prod_kwp*0.6))
kwp = max(0.5, ahorro_kwh/prod_kwp)
inversion = kwp*COSTE_PV_KWP
ahorro_eur = ahorro_kwh*PRECIO_KWH
payback = (inversion/ahorro_eur) if ahorro_eur>0 else None
co2 = ahorro_kwh*FACTOR_CO2

st.subheader("Resultados")
c1,c2,c3 = st.columns(3)
c1.metric("Consumo anual", f"{consumo_anual:,.0f} kWh/a")
c2.metric("Ahorro potencial", f"{ahorro_kwh:,.0f} kWh/a")
c3.metric("CO₂ evitado", f"{co2:,.0f} kg/a")
c1.metric("FV estimada", f"{kwp:.2f} kWp")
c2.metric("Inversión", f"{inversion:,.0f} €")
c3.metric("Payback", "n/d" if payback is None else f"{payback:.1f} años")

# Gráfico simple
import matplotlib.pyplot as plt
fig = plt.figure()
plt.bar(["Consumo","Ahorro"],[consumo_anual,ahorro_kwh])
plt.ylabel("kWh/año"); plt.title("Consumo vs Ahorro")
st.pyplot(fig)

# PDF: exporta datos como texto (para algo rápido); si quieres PDF real añade reportlab en servidor
from io import StringIO
csv = StringIO()
csv.write("kpi,valor\n")
csv.write(f"Consumo anual,{consumo_anual:.0f}\n")
csv.write(f"Ahorro kWh,{ahorro_kwh:.0f}\n")
csv.write(f"FV kWp,{kwp:.2f}\n")
csv.write(f"Inversión €,{inversion:.0f}\n")
csv.write(f"Payback años,{'' if payback is None else f'{payback:.1f}'}\n")
csv.write(f"CO2 kg/a,{co2:.0f}\n")
st.download_button("Descargar resultados (CSV)", csv.getvalue(), "informe.csv", "text/csv")
