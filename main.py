from flask import Flask,render_template,request,redirect,url_for,session
from flask_pymongo import PyMongo
import jwt
import datetime
from fastapi import FastAPI
from dotenv import load_dotenv
import os
# from flask_oauthlib.client import OAuth
from google_auth_oauthlib.flow import Flow
load_dotenv()


class lib_app(Flask):
    """kütüphane uygulamasının main class
    bu sınıfta tüm route lar bir fonksiyonun altında toplandı ve yeni gelecek routlar
    bu fonksiyonun altında olucaklar,
    """
    
    client_secret_file="client_secret.json"
    
    """ scopes
    #kullanıcının email ve herkese açık profili ele alınır   
    daha fazlasıhttps://developers.google.com/identity/protocols/oauth2/scopes?hl=tr
    """
    flow=Flow.from_client_secrets_file(client_secrets_file=client_secret_file,
                                       scopes=["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile","Openid" ],
                                       redirect_uri="http://127.0.0.1:8000/callback" )
                                        

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config["MONGO_URI"] = os.getenv("mongo_uri")
        self.mongo = PyMongo(self.app).db
        self.app.secret_key = os.getenv("secret_key")
        self.jwt_key=  os.getenv("jwt_key")# token üretilirken kullanılan key
        self.fastapi = FastAPI()
        self.google_secret=os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret_file="client_secret.json"
        self.flow=Flow.from_client_secrets_file(client_secrets_file=self.client_secret_file,
                                       scopes=["https://www.googleapis.com/auth/userinfo.email","https://www.googleapis.com/auth/userinfo.profile","Openid" ],
                                       redirect_uri="http://127.0.0.1:8000/callback" )
        self.Allroutes()
        self.update_books()#program çalıştığında tüm kitapların gün takibi 
        # self.app_logout()
        self.online_user=None#şuan boşta burası session gibi çalışacak sistem olucak
        # self.oauth = OAuth(self.app)
        # self.google = self.oauth.remote_app(
        #     'google',
        #     consumer_key=os.getenv('GOOGLE_CLIENT_ID'),
        #     consumer_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        #     request_token_params={
        #         'scope': 'email',
        #     },
        #     base_url='https://www.googleapis.com/oauth2/v1/',
        #     authorize_url='https://accounts.google.com/o/oauth2/auth',
        #     authorize_params=None,
        #     request_token_url=None,
        #     access_token_method='POST',
        #     access_token_url='https://accounts.google.com/o/oauth2/token',
        #     redirect_uri=url_for('google_authorized', _external=True),
        #     )
  
    
    
    def Allroutes(self):
        
        @self.app.route("/")
        def home():
            """home page
            hali hazırda login varsa after_login sayfasına yönlendirecek  yoksa home.html
            """
            
            check,a=self._online_user()
            if check == True:
                user=self.mongo.token_user.find_one({"token":a})["username"]  
                return render_template("afterLogin.html",user=user,login=True)
            elif check == False:
                self.app_logout()
                return  render_template("home.html")


        
        # @self.app.route("/home_page/<string:user>/<string:login>")
        # def home_page(user,login):
        #     """kullanıcı  giriş yaptıkdan sonraki ana sayfa
        #     """
        #     return render_template("afterLogin.html",user=user,login=login)
            
        
        @self.fastapi.get("/fastapi_endpoint")
        def fastapi_endpoint():
            return {"message":"hello from Fastapi endpoint"}

        @self.app.route("/book")
        def show_book():
            from book import show_books
            """KİTAP GÖSTERİMİ
            book.py den kitapları gösteren fonksiyonunu çağırır
            !!!! book.py deki ismi show_books dikkat et
            """
            self._online_user()
            show= show_books()
            return render_template("show_book.html",books=show,users=self.online_user )


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


        @self.app.route("/callback")
        def loginGoogle():
            self.flow.fetch_token(authorization_response=request.url)

        
        
        
        @self.app.route("/login",methods=["GET","POST"])
        def login():
            authorization_url_state=self.flow.authorization_url()
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
                            return redirect(url_for('home',login=True,user=user_name)),self.token_user(loginuser=login_user,pasaport=user_pasaport)
                            

                    else:
                        return render_template("login.html",eror=True)
            else:
                return redirect(url_for("home"))
            return render_template("login.html")
        

                
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
                new_user_surname=request.form.get("new_user_surname")
                new_user_pass=request.form.get("new_user_pass")
                new_user_pasaport=request.form.get("new_user_pasaport")
                chek=self.check_users(pasaport=new_user_pasaport,username=new_user_name,pswd=new_user_pass,surname=new_user_surname)
                
                if chek == False:
                    self.mongo.users.insert_one({"pasaport_no":new_user_pasaport,
                                                 "username":new_user_name,#kullanıcı kayıt
                                                 "password":new_user_pass,
                                                 "surname":new_user_surname})
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

        @self.app.route("/logout")
        def logout():
            self.app_logout()
            return redirect(url_for("home"))
      
    def token_user(self,loginuser,pasaport):
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
            user=self.mongo.token_user.find_one({"pasaport_no": pasaport},
                                                {"token":True,"_id":False})["token"]
            session["token"]=user
            
                
        else:
            user_token=jwt.encode(loginuser,self.jwt_key,algorithm = "HS256")
            session["token"]=user_token
            self.mongo.token_user.insert_one({"username":username,
                                              "pasaport_no":pasaport,
                                              "token":user_token,
                                              'timestamp': current_time,
                                              'expireAt': expire_time})
        

    def check_users(self,pasaport,username,pswd,surname):
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


    def app_logout(self):
        self.online_user=None
        return session.pop("token",None)
    

    # def check_token_expire(self, token_data):
    #     """Token'ın süresinin dolup dolmadığını kontrol eder."""
    #     current_time = datetime.now()
    #     expire_time = datetime.fromtimestamp(token_data["exp"])
    #     return current_time < expire_time    burası süresi dolan token ları belirleyip logout yaptıracak

    def _online_user(self):
        """online olan kullanıcı 
        """
        if "token" in session:
            if self.mongo.token_user.find_one({"token":session["token"]}) is not None:#session da token key olup  value si olmuyor
                user=self.mongo.token_user.find_one({"token":session["token"]})
                self.online_user=True
                return True , user["token"]
            else:
                self.app_logout()
                return False,False
        else:
            return False,False
                
        

    def update_books(self):
        from book import update_rent_book,update_rez_book
        update_rez_book()
        update_rent_book()
    
    def RunApps(self):
        """program start
        program çalıştığında flask ve fastAPİ çalışacak
        """
        from threading import Thread
        def run_flask():
            self.app.run(debug=True)

        flask_thread=Thread(target=run_flask())
        flask_thread.start()
   
        
        
        
if __name__ == "__main__":
    libary = lib_app()  
    libary.RunApps()

   
    
    


    
    
    
    

