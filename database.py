import sqlite3
import uuid

def init_db():
    conn = sqlite3.connect('crm_database.db')
    c = conn.cursor()
    
    # Tabelle del DB (Profili, Leads, Interazioni, Campagne, Approvazioni)
    c.execute('''CREATE TABLE IF NOT EXISTS profiles (
        id TEXT PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        email TEXT UNIQUE,
        role TEXT,
        password TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        company_name TEXT,
        email TEXT,
        phone TEXT,
        status TEXT,
        estimated_value REAL,
        tipo_profilo TEXT,
        zona TEXT,
        tipo_agenzia TEXT,
        numero_agenti INTEGER,
        owner_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        user_id TEXT,
        interaction_type TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        budget REAL,
        start_date TEXT,
        end_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS strategy_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        status TEXT,
        proposed_by TEXT,
        reviewed_at TEXT,
        approved_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Creazione automatica dei 3 Admin
    c.execute("SELECT COUNT(*) FROM profiles WHERE role='management'")
    if c.fetchone()[0] == 0:
        admins = [
            (uuid.uuid4().hex, 'Admin', 'Uno', 'admin1@realalert.it', 'management', 'admin123'),
            (uuid.uuid4().hex, 'Admin', 'Due', 'admin2@realalert.it', 'management', 'admin123'),
            (uuid.uuid4().hex, 'Admin', 'Tre', 'admin3@realalert.it', 'management', 'admin123')
        ]
        c.executemany("INSERT INTO profiles (id, first_name, last_name, email, role, password) VALUES (?, ?, ?, ?, ?, ?)", admins)
                  
    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect('crm_database.db')
    conn.row_factory = sqlite3.Row
    return conn