from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from auth import login_required, role_required, login_user, logout_user, current_user
from db import query_one, query_all, execute

api = Blueprint('api', __name__, url_prefix='/api')

# ===== AUTENTICAZIONE =====

@api.route('/auth/register', methods=['POST'])
def register():
    """Registrazione nuovo utente"""
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'error': 'Tutti i campi sono obbligatori'}), 400
        
        # Verifica se email esiste già
        existing = query_one("SELECT ID FROM Utente WHERE Mail = %s", (email,))
        if existing:
            return jsonify({'error': 'Email già registrata'}), 400
        
        # Crea utente
        hashed = generate_password_hash(password)
        user_id = execute(
            "INSERT INTO Utente (Nome, Mail, Password, Ruolo) VALUES (%s, %s, %s, %s)",
            (name, email, hashed, 'cliente')
        )
        
        # Crea sessione
        user_data = {
            'id': user_id,
            'name': name,
            'email': email,
            'role': 'customer'
        }
        login_user(user_data)
        
        return jsonify(user_data), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/login', methods=['POST'])
def login():
    """Login utente"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not all([email, password]):
            return jsonify({'error': 'Email e password obbligatorie'}), 400
        
        # Trova utente
        user = query_one("SELECT ID, Nome, Mail, Password, Ruolo FROM Utente WHERE Mail = %s", (email,))
        if not user:
            return jsonify({'error': 'Credenziali non valide'}), 401
        
        # Verifica password
        if not check_password_hash(user['Password'], password):
            return jsonify({'error': 'Credenziali non valide'}), 401
        
        # Normalizza ruolo
        role = 'admin' if user['Ruolo'] == 'admin' else 'customer'
        
        # Crea sessione
        user_data = {
            'id': user['ID'],
            'name': user['Nome'],
            'email': user['Mail'],
            'role': role
        }
        login_user(user_data)
        
        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/auth/logout', methods=['POST'])
def logout():
    """Logout utente"""
    logout_user()
    return jsonify({'message': 'Logout effettuato'}), 200

@api.route('/auth/me', methods=['GET'])
def me():
    """Ottiene utente corrente"""
    user = current_user()
    if not user:
        return jsonify({'error': 'Non autenticato'}), 401
    return jsonify(user), 200

# ===== API CLIENTE =====

@api.route('/orders', methods=['GET'])
@login_required
@role_required('customer')
def get_orders():
    """Lista ordini del cliente"""
    try:
        user = current_user()
        orders = query_all("""
            SELECT 
                o.ID as id,
                o.Tipo as type,
                o.PesoTotale as total_weight,
                o.Orario as scheduled_at,
                o.IndirizzoDestinazione as address,
                o.ID_Missione as mission_id,
                COALESCE(m.Stato, 'in attesa') as status
            FROM Ordine o
            LEFT JOIN Missione m ON o.ID_Missione = m.ID
            WHERE o.ID_Utente = %s
            ORDER BY o.Orario DESC
        """, (user['id'],))
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/orders/<int:order_id>', methods=['GET'])
@login_required
@role_required('customer')
def get_order_detail(order_id):
    """Dettaglio ordine con prodotti e missione"""
    try:
        user = current_user()
        
        # Verifica proprietà ordine
        order = query_one("""
            SELECT 
                o.ID as id,
                o.Tipo as type,
                o.PesoTotale as total_weight,
                o.Orario as scheduled_at,
                o.IndirizzoDestinazione as address,
                o.ID_Missione as mission_id,
                o.ID_Utente as user_id
            FROM Ordine o
            WHERE o.ID = %s
        """, (order_id,))
        
        if not order or order['user_id'] != user['id']:
            return jsonify({'error': 'Ordine non trovato'}), 404
        
        # Prodotti
        products = query_all("""
            SELECT 
                p.ID as id,
                p.nome as name,
                c.Quantita as quantity,
                p.peso as weight
            FROM Contiene c
            JOIN Prodotto p ON c.ID_Prodotto = p.ID
            WHERE c.ID_Ordine = %s
        """, (order_id,))
        
        # Missione
        mission = None
        if order['mission_id']:
            mission_data = query_one("""
                SELECT 
                    m.ID as id,
                    m.Stato as status,
                    d.Modello as drone,
                    CONCAT(pi.Nome, ' ', pi.Cognome) as pilot
                FROM Missione m
                LEFT JOIN Drone d ON m.IdDrone = d.ID
                LEFT JOIN Pilota pi ON m.IdPilota = pi.ID
                WHERE m.ID = %s
            """, (order['mission_id'],))
            mission = mission_data
        
        return jsonify({
            'order': order,
            'products': products,
            'mission': mission
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/missions/<int:mission_id>', methods=['GET'])
@login_required
@role_required('customer')
def get_mission(mission_id):
    """Dettaglio missione"""
    try:
        mission = query_one("""
            SELECT 
                m.ID as id,
                m.DataMissione as date,
                m.Ora as time,
                m.Stato as status,
                m.Valutazione as rating,
                m.Commento as comment,
                d.ID as drone_id,
                d.Modello as drone_model,
                d.Batteria as drone_battery,
                pi.ID as pilot_id,
                pi.Nome as pilot_name,
                pi.Cognome as pilot_surname
            FROM Missione m
            LEFT JOIN Drone d ON m.IdDrone = d.ID
            LEFT JOIN Pilota pi ON m.IdPilota = pi.ID
            WHERE m.ID = %s
        """, (mission_id,))
        
        if not mission:
            return jsonify({'error': 'Missione non trovata'}), 404
        
        # Formatta risposta
        result = {
            'id': mission['id'],
            'date': str(mission['date']) if mission['date'] else None,
            'time': str(mission['time']) if mission['time'] else None,
            'status': mission['status'],
            'rating': mission['rating'],
            'comment': mission['comment'],
            'drone': {
                'id': mission['drone_id'],
                'model': mission['drone_model'],
                'battery': mission['drone_battery']
            } if mission['drone_id'] else None,
            'pilot': {
                'id': mission['pilot_id'],
                'name': mission['pilot_name'],
                'surname': mission['pilot_surname']
            } if mission['pilot_id'] else None
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/missions/<int:mission_id>/tracks', methods=['GET'])
@login_required
@role_required('customer')
def get_mission_tracks(mission_id):
    """Tracce GPS della missione"""
    try:
        tracks = query_all("""
            SELECT 
                Latitudine as lat,
                Longitudine as lng,
                TIMESTAMP as timestamp
            FROM Traccia
            WHERE ID_Missione = %s
            ORDER BY TIMESTAMP ASC
        """, (mission_id,))
        
        # Converti timestamp in stringhe
        for track in tracks:
            track['timestamp'] = str(track['timestamp']) if track['timestamp'] else None
        
        return jsonify(tracks), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/missions/<int:mission_id>/rating', methods=['POST'])
@login_required
@role_required('customer')
def rate_mission(mission_id):
    """Valuta missione completata"""
    try:
        data = request.get_json()
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 10):
            return jsonify({'error': 'Valutazione deve essere tra 1 e 10'}), 400
        
        # Verifica che missione sia completata
        mission = query_one("SELECT Stato FROM Missione WHERE ID = %s", (mission_id,))
        if not mission:
            return jsonify({'error': 'Missione non trovata'}), 404
        
        if mission['Stato'] != 'completata':
            return jsonify({'error': 'Puoi valutare solo missioni completate'}), 400
        
        # Aggiorna valutazione
        execute(
            "UPDATE Missione SET Valutazione = %s, Commento = %s WHERE ID = %s",
            (rating, comment, mission_id)
        )
        
        return jsonify({'message': 'Valutazione salvata'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ===== API ADMIN =====

@api.route('/admin/dashboard', methods=['GET'])
@login_required
@role_required('admin')
def admin_dashboard():
    """KPI dashboard admin"""
    try:
        # Missioni in corso
        in_progress = query_one("SELECT COUNT(*) as count FROM Missione WHERE Stato = 'in corso'")
        
        # Missioni completate
        completed = query_one("SELECT COUNT(*) as count FROM Missione WHERE Stato = 'completata'")
        
        # Missioni annullate
        cancelled = query_one("SELECT COUNT(*) as count FROM Missione WHERE Stato = 'annullata'")
        
        # Peso medio ordini
        avg_weight = query_one("SELECT AVG(PesoTotale) as avg FROM Ordine")
        
        # Voto medio
        avg_rating = query_one("SELECT AVG(Valutazione) as avg FROM Missione WHERE Valutazione IS NOT NULL")
        
        return jsonify({
            'missions_in_progress': in_progress['count'] if in_progress else 0,
            'missions_completed': completed['count'] if completed else 0,
            'missions_cancelled': cancelled['count'] if cancelled else 0,
            'avg_order_weight': round(float(avg_weight['avg']), 2) if avg_weight['avg'] else 0,
            'avg_rating': round(float(avg_rating['avg']), 2) if avg_rating['avg'] else 0
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/drones', methods=['GET'])
@login_required
@role_required('admin')
def get_drones():
    """Lista droni"""
    try:
        drones = query_all("""
            SELECT 
                ID as id,
                Modello as model,
                Batteria as battery,
                Capacita as capacity
            FROM Drone
            ORDER BY ID
        """)
        return jsonify(drones), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/drones', methods=['POST'])
@login_required
@role_required('admin')
def create_drone():
    """Crea nuovo drone"""
    try:
        data = request.get_json()
        model = data.get('model')
        battery = data.get('battery', 100)
        capacity = data.get('capacity')
        
        if not all([model, capacity]):
            return jsonify({'error': 'Modello e capacità obbligatori'}), 400
        
        drone_id = execute(
            "INSERT INTO Drone (Modello, Batteria, Capacita) VALUES (%s, %s, %s)",
            (model, battery, capacity)
        )
        
        return jsonify({'id': drone_id, 'message': 'Drone creato'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/drones/<int:drone_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_drone(drone_id):
    """Aggiorna drone"""
    try:
        data = request.get_json()
        model = data.get('model')
        battery = data.get('battery')
        capacity = data.get('capacity')
        
        if not all([model, battery is not None, capacity]):
            return jsonify({'error': 'Tutti i campi sono obbligatori'}), 400
        
        execute(
            "UPDATE Drone SET Modello = %s, Batteria = %s, Capacita = %s WHERE ID = %s",
            (model, battery, capacity, drone_id)
        )
        
        return jsonify({'message': 'Drone aggiornato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/drones/<int:drone_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_drone(drone_id):
    """Elimina drone"""
    try:
        execute("DELETE FROM Drone WHERE ID = %s", (drone_id,))
        return jsonify({'message': 'Drone eliminato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/pilots', methods=['GET'])
@login_required
@role_required('admin')
def get_pilots():
    """Lista piloti"""
    try:
        pilots = query_all("""
            SELECT 
                ID as id,
                Nome as name,
                Cognome as surname,
                Turno as shift,
                Brevetto as license
            FROM Pilota
            ORDER BY ID
        """)
        return jsonify(pilots), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/pilots', methods=['POST'])
@login_required
@role_required('admin')
def create_pilot():
    """Crea nuovo pilota"""
    try:
        data = request.get_json()
        name = data.get('name')
        surname = data.get('surname')
        shift = data.get('shift')
        license = data.get('license')
        
        if not all([name, surname, shift, license]):
            return jsonify({'error': 'Tutti i campi sono obbligatori'}), 400
        
        pilot_id = execute(
            "INSERT INTO Pilota (Nome, Cognome, Turno, Brevetto) VALUES (%s, %s, %s, %s)",
            (name, surname, shift, license)
        )
        
        return jsonify({'id': pilot_id, 'message': 'Pilota creato'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/pilots/<int:pilot_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_pilot(pilot_id):
    """Aggiorna pilota"""
    try:
        data = request.get_json()
        name = data.get('name')
        surname = data.get('surname')
        shift = data.get('shift')
        license = data.get('license')
        
        if not all([name, surname, shift, license]):
            return jsonify({'error': 'Tutti i campi sono obbligatori'}), 400
        
        execute(
            "UPDATE Pilota SET Nome = %s, Cognome = %s, Turno = %s, Brevetto = %s WHERE ID = %s",
            (name, surname, shift, license, pilot_id)
        )
        
        return jsonify({'message': 'Pilota aggiornato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/pilots/<int:pilot_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_pilot(pilot_id):
    """Elimina pilota"""
    try:
        execute("DELETE FROM Pilota WHERE ID = %s", (pilot_id,))
        return jsonify({'message': 'Pilota eliminato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/missions', methods=['GET'])
@login_required
@role_required('admin')
def get_missions():
    """Lista missioni con filtri"""
    try:
        # Parametri filtro
        stato = request.args.get('stato')
        pilota_id = request.args.get('pilota_id')
        drone_id = request.args.get('drone_id')
        dal = request.args.get('dal')
        al = request.args.get('al')
        
        # Query base
        query = """
            SELECT 
                m.ID as id,
                m.DataMissione as date,
                m.Ora as time,
                m.Stato as status,
                m.Valutazione as rating,
                d.Modello as drone_model,
                CONCAT(pi.Nome, ' ', pi.Cognome) as pilot_name
            FROM Missione m
            LEFT JOIN Drone d ON m.IdDrone = d.ID
            LEFT JOIN Pilota pi ON m.IdPilota = pi.ID
            WHERE 1=1
        """
        params = []
        
        # Filtri
        if stato:
            query += " AND m.Stato = %s"
            params.append(stato)
        
        if pilota_id:
            query += " AND m.IdPilota = %s"
            params.append(int(pilota_id))
        
        if drone_id:
            query += " AND m.IdDrone = %s"
            params.append(int(drone_id))
        
        if dal:
            query += " AND m.DataMissione >= %s"
            params.append(dal)
        
        if al:
            query += " AND m.DataMissione <= %s"
            params.append(al)
        
        query += " ORDER BY m.DataMissione DESC, m.Ora DESC"
        
        missions = query_all(query, tuple(params))
        
        # Converti date in stringhe
        for mission in missions:
            mission['date'] = str(mission['date']) if mission['date'] else None
            mission['time'] = str(mission['time']) if mission['time'] else None
        
        return jsonify(missions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/missions/<int:mission_id>', methods=['PUT'])
@login_required
@role_required('admin')
def update_mission_status(mission_id):
    """Aggiorna stato missione"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if status not in ['in corso', 'completata', 'annullata']:
            return jsonify({'error': 'Stato non valido'}), 400
        
        execute(
            "UPDATE Missione SET Stato = %s WHERE ID = %s",
            (status, mission_id)
        )
        
        return jsonify({'message': 'Stato missione aggiornato'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/admin/stats', methods=['GET'])
@login_required
@role_required('admin')
def get_stats():
    """Statistiche per chart"""
    try:
        stats = query_all("""
            SELECT 
                DataMissione as date,
                Stato as status,
                COUNT(*) as count
            FROM Missione
            WHERE DataMissione IS NOT NULL
            GROUP BY DataMissione, Stato
            ORDER BY DataMissione DESC
            LIMIT 30
        """)
        
        # Organizza dati per Chart.js
        dates_dict = {}
        for stat in stats:
            date_str = str(stat['date'])
            if date_str not in dates_dict:
                dates_dict[date_str] = {'in corso': 0, 'completata': 0, 'annullata': 0}
            dates_dict[date_str][stat['status']] = stat['count']
        
        # Converti in array
        dates = sorted(dates_dict.keys(), reverse=True)[:10]
        dates.reverse()
        
        result = {
            'dates': dates,
            'in_corso': [dates_dict[d]['in corso'] for d in dates],
            'completata': [dates_dict[d]['completata'] for d in dates],
            'annullata': [dates_dict[d]['annullata'] for d in dates]
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
