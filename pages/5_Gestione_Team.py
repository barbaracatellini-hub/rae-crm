import streamlit as st
import uuid
from database import get_connection

from ui import applica_stile_hubspot
applica_stile_hubspot()

if "user" not in st.session_state or st.session_state.user is None:
    st.warning("Per favore, effettua il login dalla pagina principale.")
    st.stop()

# ALLINEATO: ora controlla "management"
if st.session_state.get("ruolo") != "management":
    st.error("Accesso negato. Questa pagina è riservata agli amministratori del sistema.")
    st.stop()

st.title("Gestione Team e Accessi")
st.write("Crea nuovi account per il management o per la rete vendita.")

with st.container(border=True):
    st.subheader("Crea un nuovo utente")
    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome *")
        cognome = col2.text_input("Cognome *")
        
        email = st.text_input("Email lavorativa *")
        password = st.text_input("Password (minimo 6 caratteri) *", type="password")
        
        ruolo = st.selectbox("Ruolo nel CRM", ["management", "sales"])
        
        submit = st.form_submit_button("Crea Account")
        
        if submit:
            if nome and cognome and email and password:
                try:
                    new_id = uuid.uuid4().hex # Genera un ID univoco casuale
                    conn = get_connection()
                    conn.execute("INSERT INTO profiles (id, first_name, last_name, email, role, password) VALUES (?, ?, ?, ?, ?, ?)",
                                 (new_id, nome, cognome, email, ruolo, password))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"Account creato con successo per {nome} ({ruolo})!")
                    st.info("Nota: In questa modalità database locale la sessione non passa automaticamente al nuovo utente. Esci per testare un nuovo login (se riattivato in futuro).")
                except Exception as e:
                    if "UNIQUE constraint" in str(e):
                        st.error("Esiste già un utente con questa email.")
                    else:
                        st.error(f"Errore durante la creazione dell'account: {e}")
            else:
                st.error("Tutti i campi con l'asterisco sono obbligatori.")