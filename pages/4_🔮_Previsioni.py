import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objs as go
from database import get_connection

from ui import applica_stile_hubspot
applica_stile_hubspot()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Per favore, effettua il login dalla pagina principale.")
    st.stop()

st.title("Modello Predittivo")
st.write("Previsione dell'andamento delle vendite future elaborata tramite algoritmo predittivo in Machine Learning.")

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM leads")
dati_leads = [dict(row) for row in c.fetchall()]
conn.close()

if not dati_leads:
    st.info("Nessun dato presente nel CRM per elaborare previsioni.")
    st.stop()

df = pd.DataFrame(dati_leads)

if 'status' in df.columns and 'Chiuso Vinto' in df['status'].values:
    df_vinti = df[df['status'] == 'Chiuso Vinto'].copy()
    
    df_vinti['ds'] = pd.to_datetime(df_vinti['created_at']).dt.tz_localize(None)
    df_vinti['y'] = pd.to_numeric(df_vinti['estimated_value'], errors='coerce').fillna(0)
    
    df_storico = df_vinti.groupby(df_vinti['ds'].dt.date)['y'].sum().reset_index()
    df_storico['ds'] = pd.to_datetime(df_storico['ds'])
    
    if len(df_storico) < 3:
        st.warning("Dati storici insufficienti. Il modello richiede almeno 3 vendite in date diverse per elaborare un forecast accurato.")
    else:
        st.success("Modello addestrato con successo sui dati storici.")
        
        modello = Prophet(yearly_seasonality=False, weekly_seasonality=True, daily_seasonality=False)
        modello.fit(df_storico)
        
        futuro = modello.make_future_dataframe(periods=90)
        previsione = modello.predict(futuro)
        
        st.subheader("Forecast Fatturato (Prossimi 90 giorni)")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_storico['ds'], y=df_storico['y'], mode='markers+lines', name='Vendite Reali', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=previsione['ds'], y=previsione['yhat'], mode='lines', name='Previsione', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(
            x=pd.concat([previsione['ds'], previsione['ds'][::-1]]),
            y=pd.concat([previsione['yhat_upper'], previsione['yhat_lower'][::-1]]),
            fill='toself', fillcolor='rgba(255, 0, 0, 0.2)', line=dict(color='rgba(255,255,255,0)'), name='Margine di Incertezza'
        ))
        
        fig.update_layout(xaxis_title="Data", yaxis_title="Valore Vendite (€)", hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.divider()
        st.subheader("Analisi Profilo Cliente Ideale (ICP)")
        st.write("In base allo storico delle vendite chiuse, ecco l'identikit dei contatti più redditizi su cui focalizzare le campagne.")
        
        colonne_icp = ['zona', 'tipo_profilo', 'tipo_agenzia', 'numero_agenti', 'estimated_value']
        for col in colonne_icp:
            if col not in df_vinti.columns:
                df_vinti[col] = "Dato Mancante"
                
        if len(df_vinti) > 0:
            colA, colB, colC = st.columns(3)
            
            zona_top = df_vinti.groupby('zona')['estimated_value'].sum().idxmax()
            fatturato_zona = df_vinti.groupby('zona')['estimated_value'].sum().max()
            colA.metric(label="Zona Migliore", value=str(zona_top), delta=f"€ {fatturato_zona:,.2f} generati")
            
            profilo_top = df_vinti['tipo_profilo'].mode()[0]
            conteggio_profilo = df_vinti[df_vinti['tipo_profilo'] == profilo_top].shape[0]
            colB.metric(label="Profilo più Frequente", value=str(profilo_top), delta=f"{conteggio_profilo} chiusure")
            
            agenzia_top = df_vinti['tipo_agenzia'].mode()[0]
            colC.metric(label="Tipologia Agenzia Top", value=str(agenzia_top))
            
            st.markdown("**Insight Operativo:**")
            media_agenti = pd.to_numeric(df_vinti['numero_agenti'], errors='coerce').mean()
            if pd.notna(media_agenti) and media_agenti > 0:
                st.info(f"Le agenzie che chiudono con maggiore facilità hanno in media **{media_agenti:.0f} agenti** nel loro team. Usa questo dato per qualificare i lead futuri.")
            else:
                st.info("Non ci sono ancora dati sufficienti sul numero di agenti per elaborare una media.")
else:
    st.info("Non ci sono ancora abbastanza vendite nello stato 'Chiuso Vinto'. Il modello si attiverà non appena registrerai le prime chiusure.")