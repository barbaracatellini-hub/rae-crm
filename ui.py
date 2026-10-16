import streamlit as st

def applica_stile_hubspot():
    stile_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Nunito:wght@600;800&display=swap');

        /* Sfondo generale grigio chiaro */
        [data-testid="stAppViewContainer"] {
            background-color: #F4F6F8 !important;
        }
        
        /* Sfondo barra laterale bianco */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
        }

        /* Rimuove la barra superiore */
        [data-testid="stHeader"] {
            background-color: transparent !important;
        }

        /* Colori Testi: Blu Pastello */
        h1, h2, h3, h4, p, label, li, .stMarkdown {
            color: #5C7C99 !important; 
        }
        
        /* Font titoli e testi */
        h1, h2, h3, h4 { font-family: 'Nunito', sans-serif !important; }
        p, label, li { font-family: 'Inter', sans-serif !important; }

        /* Pulsanti: Arancione Pastello */
        .stButton > button, .stFormSubmitButton > button {
            background-color: #F4A261 !important;
            border: 1px solid #F4A261 !important;
            color: white !important;
            border-radius: 8px !important;
            font-family: 'Nunito', sans-serif !important;
            font-weight: 600 !important;
        }
        
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            background-color: #FFFFFF !important;
            color: #F4A261 !important;
            border: 1px solid #F4A261 !important;
        }

        /* Metriche: Verde Pastello */
        [data-testid="stMetricValue"] {
            color: #81C784 !important;
            font-family: 'Nunito', sans-serif !important;
        }

        /* FIX: Forza i box di testo (Login e Form) a essere chiari */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div, 
        div[data-baseweb="textarea"] > div {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 6px !important;
        }
        
        /* Colore del testo digitato dentro i box */
        input, select, textarea {
            color: #5C7C99 !important;
            -webkit-text-fill-color: #5C7C99 !important;
        }

        /* Box, Card e Form bianchi */
        [data-testid="stForm"], [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
        }
    </style>
    """
    st.markdown(stile_css, unsafe_allow_html=True)