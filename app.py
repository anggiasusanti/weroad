#=1
# app.py — Main Flask App (RoadScan)

import os, uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config

# --- Import model ---
import numpy as np
from PIL import Image
import tensorflow as tf

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.errorhandler(413)
def file_terlalu_besar(e):
    flash('File terlalu besar! Maksimal ukuran file adalah 10MB.', 'error')
    return redirect(url_for('deteksi'))

# =2
# WAKTU WIB
def waktu_wib():
    """Return waktu sekarang dalam zona WIB (UTC+7)."""
    return datetime.utcnow() + timedelta (hours=7)

# DATABASE MODELS

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    nama_depan    = db.Column(db.String(50), nullable=False)
    nama_belakang = db.Column(db.String(50), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(10), default='user')
    aktif         = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=waktu_wib)
    deteksi       = db.relationship('HasilDeteksi', backref='user', lazy=True)

    @property
    def total_deteksi(self):
        return len(self.deteksi)

class HasilDeteksi(db.Model):
    __tablename__ = 'hasil_deteksi'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    foto_path        = db.Column(db.String(255), nullable=False)
    jenis_kerusakan  = db.Column(db.String(50), nullable=False)
    confidence       = db.Column(db.Float, nullable=False)
    tanggal          = db.Column(db.DateTime, default=waktu_wib)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =3
# MODEL AI

model = None
KELAS = ['Berlubang', 'Retak Kulit Buaya', 'Retak Memanjang']

def load_model():
    global model
    if os.path.exists(app.config['MODEL_PATH']):
        model = tf.keras.models.load_model(app.config['MODEL_PATH'])
        print(" MODEL BERHASIL DIMUAT!")
    else:
        print("  Model belum ada. Taruh file model di folder model/")

def predict_image(foto_path):
    """Prediksi jenis kerusakan dari path foto."""
    img = Image.open(foto_path).convert('RGB').resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    predictions = model.predict(img_array)
    idx = np.argmax(predictions[0])
    confidence = float(predictions[0][idx])
    if confidence < app.config['CONFIDENCE_THRESHOLD']:
        return 'Tidak Terdeteksi', confidence
    return KELAS[idx], confidence

# =4
# DATABASE INFO KERUSAKAN

INFO_KERUSAKAN = {
    'Berlubang': {
        'penyebab': [
            'Air yang meresap ke dalam lapisan perkerasan yang retak-retak',
            'Beban kendaraan berlebih secara berulang',
            'Penuaan material aspal',
            'Rapuhnya lapisan-lapisan jalan',
        ],
        'metode': [
            {
                'kode': 'P5 - Penambalan Lubang',
                'judul': 'Penambalan Lubang',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan area lubang dengan air compressor.',
                    'Gali material pondasi hingga mencapai lapisan keras.',
                    'Padatkan material lapisan dasar menggunakan vibrating hammer',
                    'Tambahkan agregat klas “A” dengan ketebalan max.100 mm dalam keadaan OMC, kemudian padatkan dengan Vibrating Plate Temper.',
                    'Laburkan prime coat pada dasar lubang menggunakan Asphalt Sprayer.',
                    'Taburkan campuran aspal dingin ke dalam lubang.',
                    'Padatkan menggunakan Baby Roller (min. 5 lintasan).',
                    'Periksa kerataan permukaan dan bersihkan lokasi pekerjaan.',
                ]
            },
            {
                'kode': 'P6 - Perataan',
                'judul': 'Perataan',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan lubang menggunakan air compressor.',
                    'Laburkan tack coat pada permukaan lubang.',
                    'Taburkan campuran aspal dingin pada lubang (min. ketebalan 10 mm).',
                    'Padatkan menggunakan Baby Roller (min. 5 lintasan).',
                    'Periksa kerataan permukaan dan bersihkan lokasi pekerjaan.',
                ]
            },
        ],
        'referensi': 'No. 001-02/M/BM/2011 — Manual Perbaikan Standar untuk Pemeliharaan Rutin Jalan, Ditjen Bina Marga'
    },
    'Retak Kulit Buaya': {
        'penyebab': [
            'Beban kendaraan yang berlebihan secara berulang',
            'Material lapisan perkerasan yang kelelahan',
            'Sistem drainase (pengaliran kelebihan air) yang buruk',
            'Tidak stabilnya lapisan bawah atau tanah dasar permukaan',
        ],
        'metode': [
            {
                'kode': 'P2 - Pengaspalan',
                'judul': 'Pengaspalan',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan retakan menggunakan air compressor.',
                    'Semprotkan aspal emulsi 1.5 liter/m2 pada area perbaikan dan tunggu sampai aspal mulai pecah.',
                    'Taburkan pasir kasar atau agregat 5 mm pada retakan',
                    'Padatkan menggunakan Baby Roller (min. 3 lintasan).',
                    'Bersihkan lokasi pekerjaan.',
                ]
            },
            {
                'kode': 'P5 - Penambalan',
                'judul': 'Penambalan',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan retakan dengan air compressor.',
                    'Gali material pondasi hingga mencapai lapisan keras.',
                    'Padatkan material lapisan dasar menggunakan vibrating hammer',
                    'Tambahkan agregat klas “A” dengan ketebalan max.100 mm dalam keadaan OMC, kemudian padatkan dengan Vibrating Plate Temper.',
                    'Laburkan prime coat menggunakan Asphalt Sprayer.',
                    'Taburkan campuran aspal dingin.',
                    'Padatkan menggunakan Baby Roller (min. 5 lintasan).',
                    'Periksa kerataan permukaan dan bersihkan lokasi pekerjaan.',
                ]
            },
        ],
        'referensi': 'No. 001-02/M/BM/2011 — Manual Perbaikan Standar untuk Pemeliharaan Rutin Jalan, Ditjen Bina Marga'
    },
    'Retak Memanjang': {
        'penyebab': [
            'Pergerakan tanah dasar secara vertikal',
            'Sistem drainase (pengaliran kelebihan air) yang buruk',
            'Beban lalu lintas berulang pada jalur roda',
            'Sambungan konstruksi yang kurang baik',
        ],
        'metode': [
            {
                'kode': 'P3 - Penutupan Retak',
                'judul': 'Penutupan Retak',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan retakan menggunakan air compressor.',
                    'Semprotkan tack coat (0.2 liter/m2) pada area perbaikan.',
                    'Taburkan campuran aspal (emulsi dan pasir kasar) pada retakan (min. ketebalan 10 mm).',
                    'Padatkan campuran aspal menggunakan Baby Roller.',
                ]
            },
            {
                'kode': 'P4 - Pengisian Retak',
                'judul': 'Pengisian Retak',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan retakan menggunakan air compressor.',
                    'Isi celah retakan dengan aspal emulsi menggunakan Asphalt Sprayer atau Asphalt Kettle.',
                    'taburkan pasir kasar pada area perbaikan',
                    'Padatkan pasir menggunakan Baby Roller (min. 3 lintasan).',
                ]
            },
            {
                'kode': 'P5 - Penambalan',
                'judul': 'Penambalan',
                'langkah': [
                    'Mobilisasi peralatan dan pasang rambu pengaman pada area perbaikan.',
                    'Bersihkan retakan dengan air compressor.',
                    'Gali material pondasi hingga mencapai lapisan keras.',
                    'Padatkan material lapisan dasar menggunakan vibrating hammer',
                    'Tambahkan agregat klas “A” dengan ketebalan max.100 mm dalam keadaan OMC, kemudian padatkan dengan Vibrating Plate Temper.',
                    'Laburkan prime coat menggunakan Asphalt Sprayer.',
                    'Taburkan campuran aspal dingin.',
                    'Padatkan menggunakan Baby Roller (min. 5 lintasan).',
                    'Periksa kerataan permukaan dan bersihkan lokasi pekerjaan.',
                ]
            },
        ],
        'referensi': 'No. 001-02/M/BM/2011 — Manual Perbaikan Standar untuk Pemeliharaan Rutin Jalan, Ditjen Bina Marga'
    },
}

# =5
# HELPER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_unique_filename(original_filename, upload_folder):
    """
    Cek apakah nama file sudah ada di folder upload.
    Kalau sudah ada, tambahkan (1), (2), dst seperti File Explorer.
    """
    name, ext = os.path.splitext(original_filename)
    filename = original_filename
    counter = 1
    while os.path.exists(os.path.join(upload_folder, filename)):
        filename = f"{name} ({counter}){ext}"
        counter += 1
    return filename

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# =6
# ROUTES — USER

@app.route('/')
def landing():
    return render_template('user/landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role='user').first()
        if not user or not check_password_hash(user.password, password):
            flash('Email atau kata sandi salah.', 'error')
            return redirect(url_for('login'))
        if not user.aktif:
            flash('Akun kamu telah dinonaktifkan. Hubungi admin.', 'error')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('deteksi'))
    return render_template('user/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama_depan    = request.form.get('nama_depan')
        nama_belakang = request.form.get('nama_belakang')
        email         = request.form.get('email')
        password      = request.form.get('password')
        password2     = request.form.get('password2')
        if len(password) < 8:
            flash('Kata sandi minimal 8 karakter.', 'error')
            return redirect(url_for('register'))
        if password != password2:
            flash('Kata sandi tidak cocok.', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email sudah terdaftar.', 'error')
            return redirect(url_for('register'))
        user = User(
            nama_depan=nama_depan, nama_belakang=nama_belakang,
            email=email, password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('deteksi'))
    return render_template('user/register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/deteksi', methods=['GET', 'POST'])
@login_required
def deteksi():
    if request.method == 'POST':
        file = request.files.get('foto')
        if not file or not allowed_file(file.filename):
            flash('File tidak valid. Gunakan JPG atau PNG.', 'error')
            return redirect(url_for('deteksi'))

        # Simpan foto dengan nama asli (jika duplikat akan ada (1), (2), dst...)
        original_name = secure_filename(file.filename)
        filename = get_unique_filename(original_name, app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Nama File Upload Foto Random
        #ext      = file.filename.rsplit('.', 1)[1].lower()
        #filename = f"{uuid.uuid4().hex}.{ext}"
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Prediksi
        foto_full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        jenis, confidence = predict_image(foto_full_path)
        # Simpan ke DB
        hasil = HasilDeteksi(
            user_id=current_user.id,
            foto_path=filename,
            jenis_kerusakan=jenis,
            confidence=confidence
        )
        db.session.add(hasil)
        db.session.commit()
        return redirect(url_for('hasil', id=hasil.id))
    return render_template('user/deteksi.html')

@app.route('/hasil/<int:id>')
@login_required
def hasil(id):
    hasil = HasilDeteksi.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    info  = INFO_KERUSAKAN.get(hasil.jenis_kerusakan, None)
    return render_template('user/hasil.html', hasil=hasil, info_kerusakan=info, enumerate=enumerate)

@app.route('/riwayat')
@login_required
def riwayat():
    page         = request.args.get('page', 1, type=int)
    filter_jenis = request.args.get('filter', '')
    per_page     = 10
    query = HasilDeteksi.query.filter_by(user_id=current_user.id)
    if filter_jenis:
        query = query.filter_by(jenis_kerusakan=filter_jenis)
    query        = query.order_by(HasilDeteksi.tanggal.desc())
    total        = query.count()
    data_riwayat = query.offset((page-1)*per_page).limit(per_page).all()
    pages        = (total + per_page - 1) // per_page
    tahun_ini    = HasilDeteksi.query.filter(
        HasilDeteksi.user_id == current_user.id,
        db.extract('year', HasilDeteksi.tanggal) == waktu_wib().year
    ).count()
    # Jenis terbanyak
    from sqlalchemy import func
    top = db.session.query(HasilDeteksi.jenis_kerusakan, func.count(HasilDeteksi.id).label('c'))\
        .filter_by(user_id=current_user.id).group_by(HasilDeteksi.jenis_kerusakan)\
        .order_by(db.text('c DESC')).first()
    terbanyak = top[0] if top else None
    return render_template('user/riwayat.html',
        data_riwayat=data_riwayat, total=total, tahun_ini=tahun_ini,
        terbanyak=terbanyak, pages=pages, current_page=page)

# =7
# ROUTES — ADMIN

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(email=username, role='admin').first()
        if not user:
            user = User.query.filter(User.role=='admin', User.nama_depan==username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Username atau kata sandi salah.', 'error')
            return redirect(url_for('admin_login'))
        login_user(user)
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    from sqlalchemy import func
    total_user    = User.query.filter_by(role='user').count()
    user_baru     = User.query.filter(
        User.role=='user',
        db.extract('year', User.created_at)==waktu_wib().year).count()
    total_deteksi = HasilDeteksi.query.count()
    deteksi_tahun = HasilDeteksi.query.filter(
        db.extract('year', HasilDeteksi.tanggal)==waktu_wib().year).count()
    total_foto    = deteksi_tahun

    def hitung(jenis):
        n = HasilDeteksi.query.filter(
            HasilDeteksi.jenis_kerusakan == jenis,
            db.extract('year', HasilDeteksi.tanggal) == waktu_wib().year
        ).count()
        p = round(n / deteksi_tahun * 100) if deteksi_tahun else 0
        return n, p

    jb, pb = hitung('Retak Kulit Buaya')
    jl, pl = hitung('Berlubang')
    jm, pm = hitung('Retak Memanjang')
    jt, pt = hitung('Tidak Terdeteksi')

    top = db.session.query(HasilDeteksi.jenis_kerusakan, func.count(HasilDeteksi.id).label('c'))\
        .group_by(HasilDeteksi.jenis_kerusakan).order_by(db.text('c DESC')).first()

    deteksi_terbaru = HasilDeteksi.query.order_by(HasilDeteksi.tanggal.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
        total_user=total_user, user_baru=user_baru,
        total_deteksi=total_deteksi, deteksi_tahun=deteksi_tahun, total_foto=total_foto,
        jumlah_buaya=jb, persen_buaya=pb, jumlah_lubang=jl, persen_lubang=pl,
        jumlah_memanjang=jm, persen_memanjang=pm, jumlah_tidak=jt, persen_tidak=pt,
        kerusakan_terbanyak=top[0] if top else '-', persen_terbanyak=top[1] if top else 0,
        deteksi_terbaru=deteksi_terbaru)

@app.route('/admin/data-deteksi')
@login_required
@admin_required
def admin_data_deteksi():
    page         = request.args.get('page', 1, type=int)
    filter_jenis = request.args.get('filter_jenis', '')
    filter_user  = request.args.get('filter_user', '', type=str)
    per_page     = 10
    query = HasilDeteksi.query
    if filter_jenis: query = query.filter_by(jenis_kerusakan=filter_jenis)
    if filter_user:  query = query.filter_by(user_id=int(filter_user))
    query        = query.order_by(HasilDeteksi.tanggal.desc())
    total        = query.count()
    data         = query.offset((page-1)*per_page).limit(per_page).all()
    pages        = (total + per_page - 1) // per_page
    daftar_user  = User.query.filter_by(role='user').all()
    return render_template('admin/data_deteksi.html',
        data=data, total=total, pages=pages, current_page=page, daftar_user=daftar_user)

@app.route('/admin/data-deteksi/hapus/<int:id>')
@login_required
@admin_required
def admin_hapus_deteksi(id):
    item = HasilDeteksi.query.get_or_404(id)
    # Hapus file foto
    foto_path = os.path.join(app.config['UPLOAD_FOLDER'], item.foto_path)
    if os.path.exists(foto_path): os.remove(foto_path)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_data_deteksi'))

@app.route('/admin/user')
@login_required
@admin_required
def admin_manajemen_user():
    page     = request.args.get('page', 1, type=int)
    per_page = 10
    total    = User.query.filter_by(role='user').count()
    users    = User.query.filter_by(role='user').order_by(User.created_at.desc())\
                   .offset((page-1)*per_page).limit(per_page).all()
    pages    = (total + per_page - 1) // per_page
    user_baru = User.query.filter(
        User.role=='user',
        db.extract('year', User.created_at)==waktu_wib().year).count()
    return render_template('admin/manajemen_user.html',
        users=users, total_user=total, user_baru=user_baru,
        user_aktif=User.query.filter_by(role='user', aktif=True).count(),
        user_nonaktif=User.query.filter_by(role='user', aktif=False).count(),
        pages=pages, current_page=page)

@app.route('/admin/user/toggle/<int:id>')
@login_required
@admin_required
def admin_toggle_user(id):
    user = User.query.get_or_404(id)
    user.aktif = not user.aktif
    db.session.commit()
    return redirect(url_for('admin_manajemen_user'))

@app.route('/admin/user/hapus/<int:id>')
@login_required
@admin_required
def admin_hapus_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin_manajemen_user'))

# =8
# JALANKAN APP

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_model()
    app.run(debug=True, host='0.0.0.0')
# 192.168.100.1