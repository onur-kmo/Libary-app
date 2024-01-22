from flask import Flask,render_template,request,redirect,url_for

app = Flask(__name__)

@app.route("/")
def hello_world():
    numbers=[1,2,13,1,23,132,1,321,32]
    mesaj="bu birmesajdır"
    return render_template("index.html",number1=20335553,number2=5666565,numbers=numbers)
@app.route("/anasayfa")
def index():
    return "<p>Hello, anasayfa!</p>"

@app.route("/no_request")
def main_page():
    return "zort geri dön"
    
""" <string:id> dediğimizde 
(id kısmını flask otomatik algılıyo ve dinamik bir hal oluyo)
"""
@app.route("/delete/<string:id>")
def deleteId(id):
    return "ıd: "+id

@app.route("/toplam",methods=["GET","POST"])
def toplam():
    if request.method=="POST":
        numberr1=request.form.get("deneme1")
        numberr2=request.form.get("deneme2")
        return render_template("number.html",total=int(numberr1)+int(numberr2))
    else:
        return redirect(url_for("main_page"))#fonksiyon ismine göre atanır

"""
/////////////////////////////////////////////////////
"""

@app.route("/")# buradaki name i fonksiyon içinde kullanabiliyoruz
def welcome_page(name):
    return redirect(url_for("welcome_page",name="onur"))
"""şimdi burası name değişkenimi welcome fonksiyonuna gönderiyor ve 
welcomepage sayfasını yöneten fonksiyon hangisiyse ona 

"""


@app.route("/welcome<name>")# buradaki name i fonksiyon içinde kullanabiliyoruz
def welcome_page(name):
    return f"<p> welcome{name}<p>"
"""şimdi buras

"""



    

app.run(debug=True)


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Flask session için gizli anahtar
mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client['your_database']
users_collection = db['users']

def generate_token(username):
    payload = {
        'username': username
    }
    return jwt.encode(payload, 'your_secret_key', algorithm='HS256').decode('utf-8')

def decode_token(token):
    try:
        payload = jwt.decode(token, 'your_secret_key', algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None  # Token süresi dolmuş
    except jwt.InvalidTokenError:
        return None  # Geçersiz token

@app.route('/')
def home():
    token = session.get('token')
    if token:
        username = decode_token(token)
        if username:
            return f"Merhaba, {username}! <a href='/logout'>Çıkış Yap</a>"
    return "Hoş geldiniz! <a href='/login'>Giriş Yap</a>"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            # Kullanıcı girişi başarılı
            session['token'] = generate_token(username)
            users_collection.update_one({'username': username}, {'$set': {'token': session['token']}})
            return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('home'))




