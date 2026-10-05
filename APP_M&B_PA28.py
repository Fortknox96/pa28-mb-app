import streamlit as st
import plotly.graph_objects as go

# --- CONFIGURAZIONE MOBILE ---
st.set_page_config(page_title="PA-28RT M&B", page_icon="✈️", layout="centered")

# Nasconde i menu di Streamlit per farla sembrare un'app nativa
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ PA-28RT-201T")
st.markdown("**Mass & Balance Calculator**")

# --- DATI DAL MANUALE (POH) ---
MAX_TAKEOFF_WT = 2900.0
MAX_RAMP_WT = 2912.0
MAX_BAGGAGE = 200.0
TAXI_FUEL_LBS = 12.0

ARM_FRONT = 80.5
ARM_REAR = 118.1
ARM_FUEL = 95.0
ARM_BAGGAGE = 142.8
FUEL_LBS_PER_GAL = 6.0

# Inviluppo CG (Coordinate Poligono Sicurezza)
CG_ENV_X = [85.0, 89.0, 93.0, 93.0, 85.0, 85.0]
CG_ENV_Y = [1400, 2900, 2900, 1400, 1400, 2400]

# --- INPUT DATI ---
st.subheader("1. Aereo Vuoto")
col1, col2 = st.columns(2)
# Dati di esempio basati sul POH (Aggiornabili con il Basic Empty Weight reale)
bew = col1.number_input("Basic Empty Wt (lbs)", value=1896.0, step=10.0)
bew_cg = col2.number_input("Empty CG (in)", value=88.2, step=0.1)

st.subheader("2. Equipaggio e Passeggeri (lbs)")
col3, col4 = st.columns(2)
front_pax = col3.number_input("Sedili Anteriori", value=340, step=5)
rear_pax = col4.number_input("Sedili Posteriori", value=0, step=5)

st.subheader("3. Bagagli e Carburante")
col5, col6 = st.columns(2)
baggage = col5.number_input("Bagagliaio (Max 200)", value=0, max_value=int(MAX_BAGGAGE), step=5)
fuel_gal = col6.number_input("Carburante (Gal)", value=72, max_value=72, step=1)

# --- CALCOLI M&B ---
fuel_wt = fuel_gal * FUEL_LBS_PER_GAL
ramp_wt = bew + front_pax + rear_pax + baggage + fuel_wt
takeoff_wt = ramp_wt - TAXI_FUEL_LBS
zero_fuel_wt = ramp_wt - fuel_wt

mom_bew = bew * bew_cg
mom_front = front_pax * ARM_FRONT
mom_rear = rear_pax * ARM_REAR
mom_bag = baggage * ARM_BAGGAGE
mom_fuel = fuel_wt * ARM_FUEL
mom_taxi = TAXI_FUEL_LBS * ARM_FUEL

mom_ramp = mom_bew + mom_front + mom_rear + mom_bag + mom_fuel
mom_takeoff = mom_ramp - mom_taxi
mom_zfw = mom_ramp - mom_fuel

cg_ramp = mom_ramp / ramp_wt if ramp_wt > 0 else 0
cg_takeoff = mom_takeoff / takeoff_wt if takeoff_wt > 0 else 0
cg_zfw = mom_zfw / zero_fuel_wt if zero_fuel_wt > 0 else 0

# --- VERDETTO E RISULTATI ---
st.markdown("---")
if ramp_wt > MAX_RAMP_WT:
    st.error(f"⚠️ Ramp Weight Eccessivo! ({ramp_wt:.1f} lbs / Max {MAX_RAMP_WT} lbs)")
elif takeoff_wt > MAX_TAKEOFF_WT:
    st.error(f"⚠️ Sovrappeso al Decollo! ({takeoff_wt:.1f} lbs / Max {MAX_TAKEOFF_WT} lbs)")
else:
    st.success(f"✅ Pesi nei limiti. Takeoff Wt: {takeoff_wt:.1f} lbs")

col7, col8 = st.columns(2)
col7.metric("Takeoff CG", f"{cg_takeoff:.2f} in")
col8.metric("Zero Fuel CG", f"{cg_zfw:.2f} in")

# --- GRAFICO PLOTLY ---
fig = go.Figure()

# Disegna Poligono Inviluppo
fig.add_trace(go.Scatter(x=CG_ENV_X, y=CG_ENV_Y, fill='toself', 
                         fillcolor='rgba(0, 150, 0, 0.2)', line=dict(color='green', width=2), name='Limiti CG'))

# Punto Decollo
fig.add_trace(go.Scatter(x=[cg_takeoff], y=[takeoff_wt], mode='markers+text',
                         marker=dict(color='blue', size=12, symbol='circle'),
                         text=['Takeoff'], textposition='top right', name='Takeoff'))

# Punto Zero Fuel
fig.add_trace(go.Scatter(x=[cg_zfw], y=[zero_fuel_wt], mode='markers+text',
                         marker=dict(color='red', size=10, symbol='x'),
                         text=['Zero Fuel'], textposition='bottom left', name='Zero Fuel'))

# Linea consumo carburante
fig.add_trace(go.Scatter(x=[cg_takeoff, cg_zfw], y=[takeoff_wt, zero_fuel_wt],
                         mode='lines', line=dict(color='black', dash='dash'), name='Fuel Burn'))

fig.update_layout(title="Inviluppo Centro di Gravità", xaxis_title="CG (inches aft of datum)",
                  yaxis_title="Weight (lbs)", xaxis_range=[84, 95], yaxis_range=[1400, 3000],
                  margin=dict(l=20, r=20, t=40, b=20), height=450)

st.plotly_chart(fig, use_container_width=True)