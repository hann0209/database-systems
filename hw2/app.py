from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Definisi Model
class Kategori(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Pemasok(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_info = db.Column(db.String(150))

class Produk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('kategori.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('pemasok.id'), nullable=False)
    category = db.relationship('Kategori', backref=db.backref('products', lazy=True))
    supplier = db.relationship('Pemasok', backref=db.backref('products', lazy=True))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Inisialisasi Database
with app.app_context():
    db.create_all()


# List kategori
@app.route('/')
def index():
    if(not current_user.is_authenticated):
        return redirect(url_for('login'))
    categories = Kategori.query.all()
    return render_template('kategori_list.html', categories=categories)


# List kategori
@app.route('/kategori')
def kategori_list():
    categories = Kategori.query.all()
    return render_template('kategori_list.html', categories=categories)

# Tambah kategori
@app.route('/kategori/add', methods=['GET', 'POST'])
def add_kategori():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        new_kategori = Kategori(name=name, description=description)
        db.session.add(new_kategori)
        db.session.commit()
        flash('Succesfuly Add Category!')
        return redirect(url_for('kategori_list'))
    return render_template('add_kategori.html')

# Edit kategori
@app.route('/kategori/edit/<int:id>', methods=['GET', 'POST'])
def edit_kategori(id):
    kategori = Kategori.query.get_or_404(id)
    if request.method == 'POST':
        kategori.name = request.form['name']
        kategori.description = request.form['description']
        db.session.commit()
        flash('Succesfuly Edit Category!')
        return redirect(url_for('kategori_list'))
    return render_template('edit_kategori.html', kategori=kategori)

# Hapus kategori
@app.route('/kategori/delete/<int:id>', methods=['POST'])
def delete_kategori(id):
    kategori = Kategori.query.get_or_404(id)
    db.session.delete(kategori)
    db.session.commit()
    flash('Succesfuly Delete Category!')
    return redirect(url_for('kategori_list'))

# List pemasok
@app.route('/pemasok')
def pemasok_list():
    suppliers = Pemasok.query.all()
    return render_template('pemasok_list.html', suppliers=suppliers)

# Tambah pemasok
@app.route('/pemasok/add', methods=['GET', 'POST'])
def add_pemasok():
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']
        new_pemasok = Pemasok(name=name, contact_info=contact_info)
        db.session.add(new_pemasok)
        db.session.commit()
        flash('Succesfuly Add Supplier!')
        return redirect(url_for('pemasok_list'))
    return render_template('add_pemasok.html')

# Edit pemasok
@app.route('/pemasok/edit/<int:id>', methods=['GET', 'POST'])
def edit_pemasok(id):
    pemasok = Pemasok.query.get_or_404(id)
    if request.method == 'POST':
        pemasok.name = request.form['name']
        pemasok.contact_info = request.form['contact_info']
        db.session.commit()
        flash('Succesfuly Edit Supplier!')
        return redirect(url_for('pemasok_list'))
    return render_template('edit_pemasok.html', pemasok=pemasok)

# Hapus pemasok
@app.route('/pemasok/delete/<int:id>', methods=['POST'])
def delete_pemasok(id):
    pemasok = Pemasok.query.get_or_404(id)
    db.session.delete(pemasok)
    db.session.commit()
    flash('Succesfuly Delete Supplier!')
    return redirect(url_for('pemasok_list'))


# List produk
@app.route('/produk')
def produk_list():
    products = Produk.query.all()
    return render_template('produk_list.html', products=products)

# Tambah produk
@app.route('/produk/add', methods=['GET', 'POST'])
def add_produk():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        category_id = request.form['category_id']
        supplier_id = request.form['supplier_id']
        new_produk = Produk(name=name, price=price, description=description,
                            category_id=category_id, supplier_id=supplier_id)
        db.session.add(new_produk)
        db.session.commit()
        flash('Succesfuly Add Product!')
        return redirect(url_for('produk_list'))
    categories = Kategori.query.all()
    suppliers = Pemasok.query.all()
    return render_template('add_produk.html', categories=categories, suppliers=suppliers)

# Edit produk
@app.route('/produk/edit/<int:id>', methods=['GET', 'POST'])
def edit_produk(id):
    produk = Produk.query.get_or_404(id)
    if request.method == 'POST':
        produk.name = request.form['name']
        produk.price = request.form['price']
        produk.description = request.form['description']
        produk.category_id = request.form['category_id']
        produk.supplier_id = request.form['supplier_id']
        db.session.commit()
        flash('Succesfuly Add Product!')
        return redirect(url_for('produk_list'))
    categories = Kategori.query.all()
    suppliers = Pemasok.query.all()
    return render_template('edit_produk.html', produk=produk, categories=categories, suppliers=suppliers)

# Hapus produk
@app.route('/produk/delete/<int:id>', methods=['POST'])
def delete_produk(id):
    produk = Produk.query.get_or_404(id)
    db.session.delete(produk)
    db.session.commit()
    flash('Succesfuly Delete Product!')
    return redirect(url_for('produk_list'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('Email or Username Already Registered!', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Successfuly Registered! Please Login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Successfuly Login!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect Email or Password!', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout Successfuly.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
