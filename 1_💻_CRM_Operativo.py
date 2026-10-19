import streamlit as st
import pandas as pd
from database import get_connection

from ui import applica_stile_hubspot
applica_stile_hubspot()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Per favore, effettua il login dalla pagina principale.")
    st.stop()

st.title("CRM Operativo")
st.write("Gestione anagrafica, pipeline e storico interazioni.")

# -- SEZIONE 1: INSERIMENTO --
with st.expander("Aggiungi Nuovo Contatto (Persona o Agenzia)"):
    with st.form("new_lead_form", clear_on_submit=True):
        st.write("Dati Anagrafici")
        col1, col2, col3 = st.columns(3)
        nome = col1.text_input("Nome *")
        cognome = col2.text_input("Cognome *")
        agenzia = col3.text_input("Nome Agenzia (Opzionale)")
        
        col4, col5 = st.columns(2)
        email = col4.text_input("Email")
        telefono = col5.text_input("Telefono")
        
        st.write("Dati di Profilazione Strategica")
        col8, col9 = st.columns(2)
        tipo_profilo = col8.selectbox("Tipo Contatto", ["Agenzia", "Agente Singolo/Privato", "Altro"])
        zona = col9.text_input("Zona/Città Operativa")
        
        col10, col11 = st.columns(2)
        tipo_agenzia = col10.selectbox("Tipologia Agenzia", ["Non Applicabile", "Franchising", "Indipendente", "Costruttore"])
        numero_agenti = col11.number_input("Numero di Agenti stimati", min_value=0, step=1)
        
        st.write("Pipeline e Prossimi Passi")
        col6, col7, col12 = st.columns(3)
        status = col6.selectbox("Stato Iniziale", ['Nuovo', 'Contattato', 'In Trattativa', 'Chiuso Vinto', 'Chiuso Perso'])
        valore_stimato = col7.number_input("Valore Stimato (€)", min_value=0.0, step=100.0)
        # NUOVO CAMPO: Evento Futuro
        evento_futuro = col12.selectbox("Evento Futuro", ["Nessuna", "Da Chiamare", "Inviare Email", "Fissare Demo", "Inviare Preventivo", "Follow-up", "Incontro di persona"])
        
        submit_lead = st.form_submit_button("Salva Contatto")
        
        if submit_lead:
            if nome and cognome:
                try:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute('''INSERT INTO leads 
                        (first_name, last_name, company_name, email, phone, status, estimated_value, tipo_profilo, zona, tipo_agenzia, numero_agenti, owner_id, evento_futuro) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (nome, cognome, agenzia, email, telefono, status, valore_stimato, tipo_profilo, zona, tipo_agenzia, numero_agenti, st.session_state.user.id, evento_futuro))
                    conn.commit()
                    conn.close()
                    st.success("Contatto aggiunto con successo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
            else:
                st.error("Nome e Cognome sono obbligatori.")

# -- SEZIONE 2: LETTURA E DIVISIONE DATI --
st.divider()

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM leads ORDER BY created_at DESC")
leads_data = [dict(row) for row in c.fetchall()]

c.execute("SELECT id, first_name, last_name FROM profiles")
prof_data = [dict(row) for row in c.fetchall()]
conn.close()

if leads_data:
    df_leads = pd.DataFrame(leads_data)
    df_prof = pd.DataFrame(prof_data)
    
    if not df_prof.empty:
        df_prof['Proprietario'] = df_prof['first_name'] + " " + df_prof['last_name']
    else:
        df_prof['Proprietario'] = "Sconosciuto"
        
    if 'owner_id' not in df_leads.columns:
        df_leads['owner_id'] = None
        
    # Gestione compatibilità vecchi lead senza evento futuro
    if 'evento_futuro' not in df_leads.columns:
        df_leads['evento_futuro'] = "Nessuna"
    df_leads['evento_futuro'] = df_leads['evento_futuro'].fillna("Nessuna")

    df_merged = pd.merge(df_leads, df_prof[['id', 'Proprietario']], how='left', left_on='owner_id', right_on='id', suffixes=('', '_prof'))
    df_merged['Proprietario'] = df_merged['Proprietario'].fillna("Non Assegnato (Storico)")
    
    if 'company_name' not in df_merged.columns:
        df_merged['company_name'] = ""
    df_merged = df_merged.fillna("")

    mio_id = st.session_state.user.id
    df_miei = df_merged[df_merged['owner_id'] == mio_id].copy()
    df_team = df_merged[df_merged['owner_id'] != mio_id].copy()

    tab1, tab2 = st.tabs(["I Miei Lead", "Lead del Team"])

    with tab1:
        st.subheader("La Tua Pipeline")
        if not df_miei.empty:
            # Aggiunto 'evento_futuro' alla visualizzazione
            df_miei_display = df_miei[['first_name', 'last_name', 'company_name', 'status', 'evento_futuro', 'email', 'phone', 'estimated_value']]
            df_miei_display.columns = ['Nome', 'Cognome', 'Agenzia', 'Stato', 'Prossima Azione', 'Email', 'Telefono', 'Valore (€)']
            st.dataframe(df_miei_display, use_container_width=True)
            
            st.subheader("Gestione e Storico Note")
            def format_name(row):
                base = f"{row['first_name']} {row['last_name']}"
                if row['company_name'] != "":
                    base += f" ({row['company_name']})"
                return f"{base} - [{row['status']}]"

            lead_options = {format_name(row): row['id'] for index, row in df_miei.iterrows()}
            selected_lead_name = st.selectbox("Seleziona un tuo Contatto", list(lead_options.keys()))
            selected_lead_id = lead_options[selected_lead_name]
            
            colA, colB = st.columns(2)
            
            with colA:
                st.markdown("**1. Aggiorna Pipeline e Prossima Azione**")
                current_status = df_miei[df_miei['id'] == selected_lead_id]['status'].values[0]
                current_evento = df_miei[df_miei['id'] == selected_lead_id]['evento_futuro'].values[0]
                
                stati_possibili = ['Nuovo', 'Contattato', 'In Trattativa', 'Chiuso Vinto', 'Chiuso Perso']
                nuovo_stato = st.selectbox("Nuovo Stato", stati_possibili, index=stati_possibili.index(current_status))
                
                eventi_possibili = ["Nessuna", "Da Chiamare", "Inviare Email", "Fissare Demo", "Inviare Preventivo", "Follow-up", "Incontro di persona"]
                if current_evento not in eventi_possibili and current_evento:
                    eventi_possibili.append(current_evento)
                
                # Se è vuoto, imposta su Nessuna
                idx_evento = eventi_possibili.index(current_evento) if current_evento in eventi_possibili else 0
                nuovo_evento = st.selectbox("Nuova Prossima Azione", eventi_possibili, index=idx_evento)
                
                if st.button("Aggiorna Contatto"):
                    conn = get_connection()
                    conn.execute("UPDATE leads SET status = ?, evento_futuro = ? WHERE id = ?", (nuovo_stato, nuovo_evento, selected_lead_id))
                    conn.commit()
                    conn.close()
                    st.success("Stato e Prossima Azione aggiornati!")
                    st.rerun()
                    
            with colB:
                st.markdown("**2. Aggiungi Interazione**")
                tipo_interazione = st.selectbox("Tipo", ['Chiamata', 'Email', 'Nota Interna', 'Meeting'])
                nota = st.text_area("Testo della nota/Esito")
                
                if st.button("Salva Nota"):
                    if nota:
                        conn = get_connection()
                        conn.execute("INSERT INTO interactions (lead_id, user_id, interaction_type, notes) VALUES (?, ?, ?, ?)",
                                     (selected_lead_id, st.session_state.user.id, tipo_interazione, nota))
                        conn.commit()
                        conn.close()
                        st.success("Nota aggiunta!")
                        st.rerun()
                    else:
                        st.warning("Scrivi qualcosa.")
                        
            st.markdown("---")
            st.markdown(f"**Cronologia di {selected_lead_name.split(' -')[0]}**")
            
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT * FROM interactions WHERE lead_id = ? ORDER BY created_at DESC", (selected_lead_id,))
            inter_data = [dict(row) for row in c.fetchall()]
            conn.close()
            
            if inter_data:
                for inter in inter_data:
                    date_str = inter['created_at'][:10]
                    with st.container(border=True): 
                        st.markdown(f"**{date_str}** | **{inter['interaction_type']}**")
                        st.write(inter['notes'])
            else:
                st.info("Nessuna nota per questo contatto.")
        else:
            st.info("Non hai ancora inserito nessun lead. Usa il modulo sopra per iniziare!")

    with tab2:
        st.subheader("Visibilità Globale Team")
        if not df_team.empty:
            # Aggiunto 'evento_futuro' anche qui
            df_team_display = df_team[['Proprietario', 'first_name', 'last_name', 'company_name', 'status', 'evento_futuro', 'estimated_value']]
            df_team_display.columns = ['Agente/Proprietario', 'Nome', 'Cognome', 'Agenzia', 'Stato', 'Prossima Azione', 'Valore (€)']
            st.dataframe(df_team_display, use_container_width=True)
            st.caption("In questa sezione puoi vedere l'andamento dei contatti gestiti dai tuoi colleghi.")
        else:
            st.info("Non ci sono lead inseriti da altri utenti.")
else:
    st.info("Nessun lead presente nel database generale.")