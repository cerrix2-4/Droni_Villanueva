# Sistema Gestione Consegne Droni

Sistema web completo per la gestione di consegne con droni, sviluppato con Flask e MySQL. Include interfacce cliente e admin con tracking GPS in tempo reale.

## 📋 Requisiti

- Python 3.8 o superiore
- MySQL 8.0+ (database cloud Aiven)
- Browser moderno (Chrome, Firefox, Edge)

## 🚀 Installazione Rapida

### 1. Clona o scarica il progetto

```bash
cd proj_droni
```

### 2. Crea ambiente virtuale

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura database Aiven

Copia il file di esempio e modifica con le tue credenziali:

```bash
cp .env.example .env
```

Modifica `.env` con i dati del tuo database Aiven MySQL:

```env
DB_HOST=tuo-host.aiven.net
DB_PORT=12345
DB_USER=avnadmin
DB_PASSWORD=tua_password_sicura
DB_NAME=droni_db
SECRET_KEY=genera_chiave_random_32_caratteri
FLASK_ENV=development
```

**Genera una chiave segreta sicura:**

```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Verifica schema database

Assicurati che il database Aiven contenga le seguenti 8 tabelle:

- `Utente` (ID, Nome, Mail, Password, Ruolo)
- `Drone` (ID, Modello, Batteria, Capacita)
- `Pilota` (ID, Nome, Cognome, Turno, Brevetto)
- `Missione` (ID, DataMissione, Ora, Stato, IdDrone, IdPilota, Valutazione, Commento)
- `Ordine` (ID, Tipo, PesoTotale, Orario, IndirizzoDestinazione, ID_Utente, ID_Missione)
- `Prodotto` (ID, nome, categoria, peso)
- `Contiene` (ID_Ordine, ID_Prodotto, Quantita)
- `Traccia` (ID_Drone, ID_Missione, Latitudine, Longitudine, TIMESTAMP)

**Script SQL per creare utente admin di test:**

```sql
INSERT INTO Utente (Nome, Mail, Password, Ruolo) 
VALUES ('Admin', 'admin@mail.com', 'scrypt:32768:8:1$<hash_generato>', 'admin');
```

Genera l'hash della password con Python:

```python
from werkzeug.security import generate_password_hash
print(generate_password_hash('admin123'))
```

### 6. Avvia il server

**Accesso solo locale:**
```bash
flask run
```

**Accesso da rete locale (smartphone/tablet):**
```bash
flask run --host=0.0.0.0 --port=5000
```

### 7. Apri browser

**Stesso PC:**
- http://localhost:5000

**Altri dispositivi nella stessa rete WiFi:**
1. Trova l'IP del PC che esegue il server:
   ```powershell
   ipconfig  # Windows
   ifconfig  # Linux/Mac
   ```
2. Usa l'indirizzo IP locale (es: 192.168.1.100):
   - http://192.168.1.100:5000

## 👥 Account di Test

**Admin:**
- Email: admin@mail.com
- Password: admin123
- Redirect: /admin

**Cliente:**
- Crea un nuovo account dalla pagina di registrazione
- Oppure inserisci manualmente nel database con Ruolo='cliente'
- Redirect: /customer

## 🎯 Funzionalità

### Interfaccia Cliente (`/customer`)

1. **Dashboard Ordini:**
   - Visualizza tutti gli ordini personali
   - Filtra per stato (in corso, completata, annullata)
   - Click su ordine per vedere dettagli

2. **Dettaglio Ordine:**
   - Informazioni ordine (tipo, peso, indirizzo)
   - Lista prodotti con quantità
   - Dettagli missione associata

3. **Tracking Live:**
   - Mappa Leaflet con tracciato GPS
   - Aggiornamento automatico ogni 3 secondi
   - Marker posizione drone in tempo reale

4. **Valutazione Missione:**
   - Form voto (1-10) + commento
   - Disponibile solo per missioni completate
   - Salvataggio nel database

### Interfaccia Admin (`/admin`)

1. **Dashboard KPI:**
   - Missioni in corso / completate / annullate
   - Peso medio ordini
   - Voto medio missioni

2. **Gestione Droni:**
   - CRUD completo (Create, Read, Update, Delete)
   - Campi: Modello, Batteria, Capacità
   - Modal Bootstrap per add/edit

3. **Gestione Piloti:**
   - CRUD completo
   - Campi: Nome, Cognome, Turno, Brevetto

4. **Gestione Missioni:**
   - Filtri: Stato, Pilota, Drone, Date
   - Modifica stato inline (select dropdown)
   - Esporta risultati in CSV

5. **Statistiche:**
   - Grafico Chart.js a barre
   - Missioni per data e stato
   - Ultimi 10 giorni

## 🔧 Struttura Progetto

```
proj_droni/
├── app.py                 # Entry point Flask
├── config.py              # Configurazione da .env
├── db.py                  # Layer database con pool
├── auth.py                # Decoratori autenticazione
├── api.py                 # API REST JSON
├── routes.py              # Route HTML
├── requirements.txt       # Dipendenze Python
├── .env                   # Configurazione locale (NON committare)
├── .env.example           # Template configurazione
├── README.md              # Questo file
├── templates/
│   ├── base.html          # Layout comune
│   ├── index.html         # Landing page pubblica
│   ├── login.html         # Form login
│   ├── register.html      # Form registrazione
│   ├── customer.html      # Dashboard cliente
│   └── admin.html         # Dashboard admin
└── static/
    ├── css/
    │   └── style.css      # Stili custom
    └── js/
        ├── auth.js        # Gestione autenticazione
        ├── app_client.js  # Logica cliente
        └── app_admin.js   # Logica admin
```

## 🔐 Sicurezza

- Password hash con `werkzeug.security`
- Query SQL parametrizzate (prevenzione SQL injection)
- Sessioni Flask sicure
- Decoratori `@login_required` e `@role_required`
- Security headers HTTP (X-Content-Type-Options, X-Frame-Options)

## 🌐 API REST Endpoints

### Autenticazione
- `POST /api/auth/register` - Registrazione
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Utente corrente

### Cliente (require role='customer')
- `GET /api/orders` - Lista ordini
- `GET /api/orders/<id>` - Dettaglio ordine
- `GET /api/missions/<id>` - Dettaglio missione
- `GET /api/missions/<id>/tracks` - Tracce GPS
- `POST /api/missions/<id>/rating` - Valuta missione

### Admin (require role='admin')
- `GET /api/admin/dashboard` - KPI dashboard
- `GET /api/admin/drones` - Lista droni
- `POST /api/admin/drones` - Crea drone
- `PUT /api/admin/drones/<id>` - Aggiorna drone
- `DELETE /api/admin/drones/<id>` - Elimina drone
- `GET /api/admin/pilots` - Lista piloti
- `POST /api/admin/pilots` - Crea pilota
- `PUT /api/admin/pilots/<id>` - Aggiorna pilota
- `DELETE /api/admin/pilots/<id>` - Elimina pilota
- `GET /api/admin/missions` - Lista missioni (con filtri)
- `PUT /api/admin/missions/<id>` - Aggiorna stato
- `GET /api/admin/stats` - Statistiche chart

## 🛠️ Tecnologie

**Backend:**
- Flask 3.0
- mysql-connector-python 8.2
- python-dotenv 1.0
- flask-cors 4.0
- werkzeug 3.0

**Frontend:**
- HTML5 + Jinja2
- CSS: Bootstrap 5.3
- JavaScript: Vanilla ES6+
- Leaflet.js 1.9 (mappe)
- Chart.js 4.x (grafici)

## 🐛 Troubleshooting

**Errore connessione database:**
```
mysql.connector.errors.DatabaseError: 2003 (HY000): Can't connect to MySQL server
```
- Verifica credenziali in `.env`
- Controlla che il database Aiven sia attivo
- Verifica firewall/network

**Errore import moduli:**
```
ModuleNotFoundError: No module named 'flask'
```
- Attiva ambiente virtuale: `venv\Scripts\activate`
- Reinstalla: `pip install -r requirements.txt`

**Sessione non persistente:**
- Verifica `SECRET_KEY` in `.env`
- Controlla che i cookie siano abilitati nel browser

**Mappa non si carica:**
- Controlla connessione internet (Leaflet usa tile OpenStreetMap)
- Verifica console browser per errori JavaScript

**API ritorna 401/403:**
- Verifica di essere loggato
- Controlla che il ruolo sia corretto (admin vs customer)

## 📱 Accesso Multi-Dispositivo

1. **Avvia server accessibile in rete:**
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

2. **Trova IP del PC:**
   ```powershell
   ipconfig  # Cerca "Indirizzo IPv4"
   ```

3. **Connetti dispositivi alla stessa WiFi**

4. **Apri browser su smartphone/tablet:**
   ```
   http://192.168.X.X:5000
   ```

5. **Login e usa normalmente**

**Nota:** Il PC deve avere il firewall configurato per permettere connessioni sulla porta 5000.

## 📄 Licenza

Progetto scolastico - Solo scopo educativo

## 👨‍💻 Supporto

Per problemi o domande:
1. Controlla la sezione Troubleshooting
2. Verifica i log Flask nel terminale
3. Ispeziona console browser (F12)

---

**Buon lavoro! 🚁**
