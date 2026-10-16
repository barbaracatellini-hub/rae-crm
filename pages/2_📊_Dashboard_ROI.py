import streamlit as st
import pandas as pd
from database import get_connection

from ui import applica_stile_hubspot
applica_stile_hubspot()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Per favore, effettua il login dalla pagina principale.")
    st.stop()

st.title("Dashboard Marketing & ROI")
st.write("Monitoraggio trasparente dei costi di marketing e delle vendite reali generate.")

if st.session_state.get("ruolo") == "sales":
    st.error("🔒 Accesso riservato. Questa sezione è visibile solo al Management e all'Admin Marketing.")
    st.stop()

with st.expander("Aggiungi Nuova Campagna (Admin)"):
    with st.form("new_campaign"):
        nome_campagna = st.text_input("Nome Campagna (es. FB Retargeting Q3)")
        budget = st.number_input("Budget Speso (€)", min_value=0.0, step=50.0)
        
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Data Inizio")
        end_date = col2.date_input("Data Fine")
        
        if st.form_submit_button("Salva Campagna"):
            if nome_campagna:
                conn = get_connection()
                conn.execute("INSERT INTO marketing_campaigns (name, budget, start_date, end_date) VALUES (?, ?, ?, ?)",
                             (nome_campagna, budget, str(start_date), str(end_date)))
                conn.commit()
                conn.close()
                st.success("Campagna salvata!")
                st.rerun()
            else:
                st.error("Inserisci il nome della campagna.")

st.divider()
st.subheader("Riepilogo Performance Globali")

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM marketing_campaigns")
campagne_data = [dict(row) for row in c.fetchall()]

c.execute("SELECT * FROM leads")
leads_data = [dict(row) for row in c.fetchall()]
conn.close()

totale_speso = sum(c['budget'] for c in campagne_data) if campagne_data else 0.0

fatturato_generato = 0.0
if leads_data:
    for lead in leads_data:
        if lead.get('status') == 'Chiuso Vinto' and lead.get('estimated_value'):
            fatturato_generato += float(lead['estimated_value'])

roi_percentuale = 0.0
if totale_speso > 0:
    roi_percentuale = ((fatturato_generato - totale_speso) / totale_speso) * 100

colA, colB, colC = st.columns(3)
colA.metric(label=" Costo Marketing Totale", value=f"€ {totale_speso:,.2f}")
colB.metric(label=" Fatturato (Chiuso Vinto)", value=f"€ {fatturato_generato:,.2f}")

roi_color = "normal" if roi_percentuale >= 0 else "inverse"
colC.metric(label=" ROI %", value=f"{roi_percentuale:,.1f}%", delta=f"{roi_percentuale:,.1f}%", delta_color=roi_color)

st.markdown("### Dettaglio Campagne Attive")
if campagne_data:
    df_campagne = pd.DataFrame(campagne_data)
    df_display = df_campagne[['name', 'budget', 'start_date', 'end_date']]
    df_display.columns = ['Nome Campagna', 'Budget (€)', 'Inizio', 'Fine']
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("Nessuna campagna marketing inserita.")