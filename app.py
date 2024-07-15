from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import requests
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    nombre = db.Column(db.String(150), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def create_tables():
    db.create_all()

def get_weather_data(city):
    API_KEY = '4a30f12a18c4d06bbe8dfc186a44cb85'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}'
    r = requests.get(url).json()
    return r

def get_unsplash_image(city, api_key):
    url = f'https://api.unsplash.com/search/photos?query={city}&client_id={api_key}'
    r = requests.get(url).json()
    if r['results']:
        return r['results'][0]['urls']['full']
    return None

def get_default_image():
    hour = datetime.now().hour
    if 6 <= hour < 8:
        return 'https://github.com/whosleviandre/App-weather-Levi/blob/main/static/vecteezy_sunrise-from-the-sea_45637165.JPG?raw=true'
    elif 8 <= hour < 17:
        return 'https://github.com/whosleviandre/App-weather-Levi/blob/main/static/vecteezy_cloudy-and-bluesky-in-the-morning-background-soft-focus_6835788.JPG?raw=true'
    elif 17 <= hour < 19:
        return 'https://github.com/whosleviandre/App-weather-Levi/blob/main/static/vecteezy_sunset-over-tranquil-seascape-blurred-motion-waves_25484887.jpg?raw=true'
    else:
        return 'https://github.com/whosleviandre/App-weather-Levi/blob/main/static/noche.jpg?raw=true'

@app.route("/", methods=['GET', 'POST'])
def index():
    context = None
    error = None
    city_image_url = get_default_image()  # Imagen predeterminada

    if request.method == 'POST':
        city = request.form.get('txtciudad')
        if city:
            api_key = '4a30f12a18c4d06bbe8dfc186a44cb85'
            try:
                response = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}')
                data = response.json()
                if data['cod'] == 200:
                    context = data
                    # Obtener imagen de Unsplash
                    unsplash_api_key = 'bqd2VY0lqhfOgh7UJlc1VeUx4lAky53jkeYmbJcRJ5c'
                    city_image_url = get_unsplash_image(city, unsplash_api_key) or get_default_image()
                else:
                    error = data.get('message', 'Error fetching weather data')
            except Exception as e:
                error = str(e)

    return render_template('index.html', context=context, city_image_url=city_image_url, error=error)

@app.route("/cv", methods=['GET'])
def cv():
    return render_template('cv.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/base')
@login_required
def base():
    return render_template('base.html')

@app.route("/segura")
@login_required
def segura():
    return render_template('segura.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nombre = request.form['nombre']
        if not email or not password or not nombre:
            flash('Error: campos vacíos', 'danger')
            return redirect(url_for('register'))
        user = Usuario.query.filter_by(email=email).first()
        if user:
            flash('Error: usuario ya existe', 'danger')
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        usuario = Usuario(email=email, password=hashed_password, nombre=nombre)
        db.session.add(usuario)
        db.session.commit()
        flash('Registro exitoso, puedes iniciar sesión ahora', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/change_password", methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        user = Usuario.query.get(current_user.id)
        if check_password_hash(user.password, old_password):
            hashed_password = generate_password_hash(new_password, method='sha256')
            user.password = hashed_password
            db.session.commit()
            flash('Contraseña cambiada exitosamente', 'success')
            return redirect(url_for('index'))
        else:
            flash('La contraseña actual es incorrecta', 'danger')
    return render_template('change_password.html')

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", error=error), 404

if __name__ == '__main__':
    app.run(debug=True)
