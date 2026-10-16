import streamlit as st
from ui import applica_stile_hubspot
from database import init_db, get_connection

# 1. Configurazione base
st.set_page_config(page_title="Real Alert CRM", page_icon="🏢", layout="centered")
applica_stile_hubspot()

# Inizializza il DB all'avvio
init_db()

# 2. Inizializzazione Session State
if "user" not in st.session_state:
    st.session_state.user = None

# 3. Funzioni di Login e Logout su SQLite
def do_login(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE email = ? AND password = ?", (email, password))
    user_row = c.fetchone()
    conn.close()

    if user_row:
        # Ricreiamo la struttura utente necessaria per le altre pagine
        class LoggedUser:
            def __init__(self, uid, email):
                self.id = uid
                self.email = email
                
        st.session_state.user = LoggedUser(user_row['id'], user_row['email'])
        st.session_state.ruolo = user_row['role']
        st.session_state.nome_completo = f"{user_row['first_name']} {user_row['last_name']}"
        st.rerun()
    else:
        st.error("Email o password errati. Riprova.")

def do_logout():
    st.session_state.user = None
    st.rerun()

# 4. Gestione Schermate
if st.session_state.user is None:
    st.title("REALalertESTATE - Login")
    with st.form("login_form"):
        email_input = st.text_input("Email")
        password_input = st.text_input("Password", type="password")
        submit = st.form_submit_button("Entra")
        
        if submit:
            do_login(email_input, password_input)
else:
    st.title("Benvenuto nel CRM!")
    st.write(f"Sei entrato come: **{st.session_state.nome_completo}** ({st.session_state.user.email})")
    st.write(f"Ruolo attivo: **{st.session_state.ruolo}**")
    
    st.success("Autenticazione completata. Ora puoi navigare nel menu laterale.")
    st.button("Esci (Logout)", on_click=do_logout)