import streamlit as st
from datetime import datetime
from database import get_connection

from ui import applica_stile_hubspot
applica_stile_hubspot()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Per favore, effettua il login dalla pagina principale.")
    st.stop()

st.title("Approvazioni Strategiche")

if st.session_state.get("ruolo") == "sales":
    st.error("🔒 Accesso riservato. Questa sezione è visibile solo al Management e all'Admin Marketing.")
    st.stop()

ruolo_utente = st.session_state.get("ruolo", "sales")

# ALLINEATO: ora controlla "management"
if ruolo_utente == "management":
    st.write("Area Admin: proponi nuove strategie al management.")
    with st.expander("Proponi Nuovo Step Strategico"):
        with st.form("new_strategy_form", clear_on_submit=True):
            titolo = st.text_input("Titolo della Strategia")
            descrizione = st.text_area("Descrizione dettagliata")
            
            if st.form_submit_button("Invia Proposta"):
                if titolo and descrizione:
                    conn = get_connection()
                    conn.execute("INSERT INTO strategy_steps (title, description, status, proposed_by) VALUES (?, ?, ?, ?)",
                                 (titolo, descrizione, "In Attesa", st.session_state.user.id))
                    conn.commit()
                    conn.close()
                    st.success("Proposta inviata con successo.")
                    st.rerun()
                else:
                    st.error("Compila sia il titolo che la descrizione.")
else:
    st.write("Area Management: visiona e approva le strategie proposte dal team marketing.")

st.divider()
st.subheader("Stato delle Proposte")

conn = get_connection()
c = conn.cursor()
c.execute("SELECT * FROM strategy_steps ORDER BY created_at DESC")
strategies = [dict(row) for row in c.fetchall()]

if strategies:
    for strat in strategies:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{strat['title']}**")
                st.write(strat['description'])
                st.caption(f"Status: {strat['status']}")
            
            with col2:
                if strat['status'] == 'In Attesa':
                    if ruolo_utente == "admin_marketing":
                        st.info("In attesa di risposta")
                    else:
                        if st.button("Approva", key=f"app_{strat['id']}", type="primary", use_container_width=True):
                            conn.execute("UPDATE strategy_steps SET status = ?, reviewed_at = ?, approved_by = ? WHERE id = ?",
                                         ("Approvata", datetime.now().isoformat(), st.session_state.user.id, strat['id']))
                            conn.commit()
                            conn.close()
                            st.rerun()
                            
                        if st.button("Rifiuta", key=f"rif_{strat['id']}", use_container_width=True):
                            conn.execute("UPDATE strategy_steps SET status = ?, reviewed_at = ?, approved_by = ? WHERE id = ?",
                                         ("Rifiutata", datetime.now().isoformat(), st.session_state.user.id, strat['id']))
                            conn.commit()
                            conn.close()
                            st.rerun()
                else:
                    if strat['status'] == 'Approvata':
                        st.success("Approvata")
                    else:
                        st.error("Rifiutata")
else:
    st.info("Nessuna proposta strategica presente a sistema.")