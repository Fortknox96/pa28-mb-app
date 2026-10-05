import streamlit as st
import plotly.graph_objects as go

# --- CONFIGURAZIONE MOBILE ---
st.set_page_config(page_title="PA-28RT M&B", page_icon="✈️", layout="centered")

# Nasconde i menu di Streamlit per farla sembrare un'app nativa su iPhone
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("✈️ PA-28RT-201T")
st.markdown("**Mass & Balance Calculator (Metric Input)**")

# --- DATI DAL MANUALE (POH) ---
MAX_TAKEOFF_WT = 2900.0
MAX_RAMP_WT = 2912.0
MAX_BAGGAGE = 200.0
TAXI_FUEL_LBS = 12.0

ARM_FRONT = 80.5
ARM_REAR = 118.1
ARM_FUEL = 95.0
ARM_BAGGAGE = 142.8

# Inviluppo CG (Coordinate Poligono Sicurezza)
CG_ENV_X = [85.0, 89.0, 93.0, 93.0, 85.0, 85.0]
CG_ENV_Y = [1400, 2900, 2900, 1400, 1400, 2400]

# --- FATTORI DI CONVERSIONE ---
KG_TO_LBS = 2.20462
LITRI_TO_GAL = 0.264172
GAL_TO_LBS = 6.0  # Peso standard Avgas 100LL
LITRI_TO_LBS = LITRI_TO_GAL * GAL_TO_LBS  # Circa 1.585 lbs per litro

# --- INPUT DATI: AEREO VUOTO ---
st.subheader("1. Aereo Vuoto (da POH)")
col1, col2 = st.columns(2)
bew = col1.number_input("Basic Empty Wt (lbs)", value=1896.0, step=10.0)
bew_cg = col2.number_input("Empty CG (in)", value=88.2, step=0.1)

# --- INPUT DATI: VISTA DALL'ALTO DELL'AEREO ---
st.subheader("2. Carico (Sistema Metrico)")

# Riga 1: Ali e Sedili Anteriori
col_ala_sx, col_pilota, col_pax_ant, col_ala_dx = st.columns(4)
with col_ala_sx:
    fuel_sx_litri = st.number_input("⛽ Ala SX (L)", value=136, step=5, max_value=136)
with col_pilota:
    pilota_kg = st.number_input("🧑‍✈️ Pilota (kg)", value=77, step=1)
with col_pax_ant:
    pax_ant_kg = st.number_input("🧑‍🤝‍🧑 Pax Ant (kg)", value=0, step=1)
with col_ala_dx:
    fuel_dx_litri = st.number_input("⛽ Ala DX (L)", value=136, step=5, max_value=136)

# Riga 2: Sedili Posteriori
col_vuota1, col_pax_post_sx, col_pax_post_dx, col_vuota2 = st.columns(4)
with col_pax_post_sx:
    pax_post_sx_kg = st.number_input("💺 Post SX (kg)", value=0, step=1)
with col_pax_post_dx:
    pax_post_dx_kg = st.number_input("💺 Post DX (kg)", value=0, step=1)

# Riga 3: Bagagliaio
col_vuota3, col_bagagliaio, col_vuota4 = st.columns([1, 2, 1])
with col_bagagliaio:
    bagagliaio_kg = st.number_input("🎒 Bagagli (kg - Max 90)", value=0, step=1, max_value=90)

# --- CONVERSIONI IN LBS PER I CALCOLI ---
front_pax_lbs = (pilota_kg + pax_ant_kg) * KG_TO_LBS
rear_pax_lbs = (pax_post_sx_kg + pax_post_dx_kg) * KG_TO_LBS
baggage_lbs = bagagliaio_kg * KG_TO_LBS
fuel_wt = (fuel_sx_litri + fuel_dx_litri) * LITRI_TO_LBS

# --- CALCOLI M&B ---
ramp_wt = bew + front_pax_lbs + rear_pax_lbs + baggage_lbs + fuel_wt
takeoff_wt = ramp_wt - TAXI_FUEL_LBS
zero_fuel_wt = ramp_wt - fuel_wt

mom_bew = bew * bew_cg
mom_front = front_pax_lbs * ARM_FRONT
mom_rear = rear_pax_lbs * ARM_REAR
mom_bag = baggage_lbs * ARM_BAGGAGE
mom_fuel = fuel_wt * ARM_FUEL
mom_taxi = TAXI_FUEL_LBS * ARM_FUEL

mom_ramp = mom_bew + mom_front + mom_rear + mom_bag + mom_fuel
mom_takeoff = mom_ramp - mom_taxi
mom_zfw = mom_ramp - mom_fuel

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

# --- GRAFICO 1: PROFILO BARICENTRO PULITO ---
st.subheader("Posizione Baricentro")

fig_cg_profile = go.Figure()

# Aggiunge le zone di colore (Sotto-limiti, Sicuro, Oltre-limiti)
fig_cg_profile.add_vrect(x0=82, x1=85, fillcolor="lightgray", opacity=0.5, line_width=0, annotation_text="Anticipato/Fwd", annotation_position="top left")
fig_cg_profile.add_vrect(x0=85, x1=93, fillcolor="lightgreen", opacity=0.5, line_width=0, annotation_text="RANGE SICURO", annotation_position="top center")
fig_cg_profile.add_vrect(x0=93, x1=95, fillcolor="lightcoral", opacity=0.5, line_width=0, annotation_text="Aft/Post", annotation_position="top right")

# Aggiunge il punto esatto del baricentro attuale
fig_cg_profile.add_trace(go.Scatter(
    x=[cg_takeoff], y=[1],
    mode="markers+text",
    marker=dict(color="darkblue", size=20, symbol="diamond"),
    text=[f"CG: {cg_takeoff:.2f} in"],
    textposition="top center"
))

fig_cg_profile.update_layout(
    xaxis=dict(range=[82, 95], title="CG Location (inches)"),
    yaxis=dict(showticklabels=False, range=[0, 2]),
    height=140,
    margin=dict(l=20, r=20, t=10, b=20),
    showlegend=False
)

st.plotly_chart(fig_cg_profile, use_container_width=True)

# --- GRAFICO 2: INVILUPPO COMPLETO ---
st.subheader("Inviluppo di Volo")
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

fig.update_layout(xaxis_title="CG Location (inches aft of datum)", yaxis_title="Weight (lbs)", 
                  xaxis_range=[84, 95], yaxis_range=[1400, 3000],
                  margin=dict(l=20, r=20, t=20, b=20), height=400)

st.plotly_chart(fig, use_container_width=True)

st.caption("Nota: App a solo scopo didattico/informativo. Fare sempre riferimento al POH ufficiale.")
