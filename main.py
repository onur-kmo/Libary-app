from flask import Flask,render_template,request,redirect,url_for,session
from flask_pymongo import PyMongo
import jwt
import datetime
     
class lib_app(Flask):
    

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["MONGO_URI"] = "mongodb+srv://onurkmo53:kmoonur.1999@onurkmo.9h9b3tx.mongodb.net/lib_base"
        self.mongo = PyMongo(self.app).db
        self.app.secret_key = "admin"
        self.jwt_key="admin"
        self.Allroutes()
        self.update_books()
  
        
    # app = Flask(__name__)
    # app.config["MONGO_URI"] = "mongodb+srv://onurkmo53:kmoonur.1999@onurkmo.9h9b3tx.mongodb.net/lib_base"
    # mongo = PyMongo(app).db
    # secret_key="admin"
    # app.secret_key="admin"

    def Allroutes(self):
        
        @self.app.route("/")
        def home():
            return render_template("home.html")
        

        @self.app.route("/book")
        def show_book():
            from book import show_books
            """KİTAP GÖSTERİMİ
            book.py den kitapları gösteren fonksiyonunu çağırır
            !!!! book.py deki ismi show_books dikkat et
            """
            show= show_books()
            return render_template("show_book.html",books=show)


        @self.app.route("/rez_books",methods=["POST"])
        def rez_books():
            """ REZERVASYON
            rent_book.html da rez_books formundan gelen kitap ismini 
            book.py deki rezervasyon işlemini yapan fonksiyona gönderiyor
            """
            from book import rez_book
            if request.method=="POST":
                book=request.form.get("reserve_book")
                rez_book(book)
                return redirect(url_for("rent_books"))
            else :
                return redirect(url_for("home"))

        @self.app.route("/rent_books",methods=["GET","POST"])
        def rent_books():
            from book import rent_book
            a,tokenn=self._online_user()
            if a == True:
                if request.method=="POST":
                    if request.form.get("rent_book"):

                        form_book=request.form.get("rent_book")
                        books=self.mongo.book.find_one({"title":form_book})
                        true=rent_book(book=books)
                        if true is not None:
                            return redirect(url_for("property_user"))
                    
            else:
                return redirect(url_for("login"))
            book=self.mongo.book.find({})#! burada 2 değişkenin olma sebebi html ye tek değişken gönderip 1 den fazla formda kullanınca her zaman 2. form ve sonra çalışmıyor
            book2=self.mongo.book.find({})
            return render_template("rent_book.html",rentbook=book,rezbook=book2)

                
        @self.app.route("/login",methods=["GET","POST"])
        def login():
            if "token" not in session:

                if  request.method == "POST":
                    user_name=request.form.get("user_name")
                    user_pass=request.form.get("user_pass")
                    user_pasaport=request.form.get("pasaport_no")
                
                    login_user=self.mongo.users.find_one({"pasaport_no":user_pasaport},{"_id":False})
                    
                    if login_user != None:
                        if user_name  and user_pasaport and user_pass in login_user.values():
                            
                            """giriş yapıldıktan sonra token oluşturulacak
                            """
                            return redirect(url_for('home',login=True,user=user_name)),token_user(loginuser=login_user,pasaport=user_pasaport)
                            

                    else:
                        return render_template("login.html",eror=True)
            else:
                return redirect(url_for("home"))
            return render_template("login.html")
        

        def token_user(loginuser,pasaport):
            """
            !!!!token oluştururken _id alınmıyor
            giriş yapan kullanıcı için token oluşturulacak ve DB ye gönderilecek
            eğer DB de aynı pasaporta uygun token duruyorsa oluşturulmadan DBdeki hazır 
            tokeını kullancak
            token lar 1 saat süreden sonra kendisini silecek ve kullanıcı yeniden login işlemi yapmak zorunda
            """
            
            ttl_duration = 3600 #second
            current_time=datetime.datetime.now()
            expire_time = current_time + datetime.timedelta(seconds=ttl_duration)
            username=loginuser["username"]
            
            if  self.mongo.token_user.find_one({"pasaport_no":pasaport}) != None:
                user=self.mongo.token_user.find_one({"pasaport_no": pasaport},{"token":True,"_id":False})["token"]
                session["token"]=user
            
                
            else:
                user_token=jwt.encode(loginuser,self.jwt_key,algorithm = "HS256")
                session["token"]=user_token
                self.mongo.token_user.insert_one({"username":username,"pasaport_no":pasaport,"token":user_token,'timestamp': current_time,'expireAt': expire_time})
                
        @self.app.route("/register",methods=["GET","POST"])
        def register():
            """ KULLANICI KAYIT
            Register.html den gelen 3 veriyi "request" ederek aldık
            bunların kontrolü için Check_users foksiyonuna gönderiyoruz
            gelen true veya false kayıt işlemi devam ediyor
            kayıt işleminde "_id" dataBASE e otomatik bir şekilde kendisi oluşturuluyor, mongoDB nin kendi obje tanımlama sistemi
            bunu değişebilirsiniz ama kaldıramazsınız. 
            """
            if request.method=="POST":
                new_user_name=request.form.get("new_user_name")
                new_user_pass=request.form.get("new_user_pass")
                new_user_pasaport=request.form.get("new_user_pasaport")
                chek=self.check_users(pasaport=new_user_pasaport,username=new_user_name,pswd=new_user_pass)
                
                if chek == False:
                    self.mongo.users.insert_one({"pasaport_no":new_user_pasaport,"username":new_user_name,"password":new_user_pass})
                    user=True
                    return render_template("register.html",user=user)
                elif chek==True:
                    user=False
                    return render_template("register.html",user=user)
            
            return render_template("register.html")




        @self.app.route("/refound",methods=["POST"])
        def refound():
            from book import refound
            if request.method=="POST":
                refound_book=request.form.get("refound")
                refound(refound_book)
                return redirect(url_for("property_user")) 
            else:
                return redirect(url_for("property_user"))    
                
                
        @self.app.route("/user_setting",methods=["GET","POST"])
        def property_user():
            """kullanıcıya ait özel bilgiler
            sisteme kayıt olduktan sonra yeni bir sayfada;
            meslek bilgisi, kendine ait olan kitaplar, yaş, cinsiyet, yaşadığı yer, 
            """
            true,token=self._online_user()

            if true == True:
                pasaport=self.mongo.token_user.find_one({"token":session["token"]},{"_id":False})
                user_info=self.mongo.users.find({"pasaport_no":pasaport["pasaport_no"]},{"_id":False})#eğer find_one yaparsan for la içinde sadece key dönersin
                
                # if mongo.book.find_one({"rent_user":pasaport["pasaport_no"]})is not None:# ["title] gibi eğer boş bir dosyaya indexlem yaparsan nonetype hatası alırsın
                #     user_book=mongo.book.find({"rent_user":pasaport["pasaport_no"]})#sorgusuz gönderildiğinde none obje problemi yaşatıyor
                # else:
                #     user_book=None
                user_book=self.mongo.book.find({"rent_user":pasaport["pasaport_no"]})
                if request.method=="POST":
                    user_city=request.form.get("user_city")
                    user_job=request.form.get("user_job")
                    user_mail=request.form.get("user_mail")
                    user_phone=request.form.get("user_phone")
                    new_add={"$set":{"city":user_city,
                            "job":user_job,
                            "mail":user_mail,
                            "phone":user_phone}}
                    self.mongo.users.update_one({"pasaport_no":pasaport["pasaport_no"]},new_add)
                    if self.mongo.book.find_one({"rent_user":pasaport["pasaport_no"]}) != None:
                        user_books=self.mongo.book.find_one({"rent_user":pasaport["pasaport_no"]})["title"]
                        return render_template("add_user_property.html",user_book=user_books,user_info=user_info,login=True)
                    else:
                        return render_template("add_user_property.html",user_info=user_info,login=True)
            else:
                return redirect(url_for("login"))
                        
            return render_template("add_user_property.html",user_book=user_book,user_info=user_info,login=True)

        @self.app.route('/logout')
        def logout():
            session.pop("token",None)
            return redirect(url_for('home'))
            

    def check_users(self,pasaport,username,pswd):
        """
        register dan gelen 3 bilgiyi data base de sorgu olarak alıyoruz
        önce pasaport kontrol den sonra bilgilerin hepsi gelip 
        aynı tc ile farklı kullanıcı adı ile yeniden kullanıcı oluşturulmaması için 
        DB den gelen bilgilerle USER dan gelen bilgiler karşılaştırılıp eğer aynı değilse
            sonuç olarak  TRUE ve FALSE döndürüyor
            DİPNOT: eğer "find_one" DB de sorguya karşılık veri  bulamıyorsa NONE gönderiyor
        """
        user_cont =  self.mongo.users.find_one({'pasaport_no': pasaport})
        
        if user_cont != None:
            if pasaport  and username  and pswd in user_cont.values():
                return True
        else:
            return False
    
    def _online_user(self):
        if "token" in session:
            if self.mongo.token_user.find_one({"token":session["token"]}) is not None:
                return True , self.mongo.token_user.find_one({"token":session["token"]})["token"]
            else:
                return False,False
        else:
            return False,False
    
    def update_books(self):
        from book import update_rent_book,update_rez_book
        update_rez_book()
        update_rent_book()
if __name__ == "__main__":
    libary = lib_app()
    libary.app.run(debug=True)
    
    

# if __name__=="__main__":
#     from book import update_rent_book,update_rez_book
#     update_rent_book()
#     update_rez_book()
#     app.run(debug=True)
    
    
    
    

