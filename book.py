from flask import Flask,render_template,request,redirect,url_for
from flask_pymongo import PyMongo
from datetime import datetime,timedelta
from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient

"""
DB deki kitapları gösterme/listeleme
kurallar;-kitaplar sadece 30 gün kiralanabilir,...
kullanıcılar kendi ellerindeki kitapları sisteme girebilir 
kitapların durumu; nerede, eğerkimdeyse nere de ,
borçlanma kayıtları, cezalar ve rezervasyonlar.
"""
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://onurkmo53:kmoonur.1999@onurkmo.9h9b3tx.mongodb.net/lib_base"
mongo = PyMongo(app).db


def show_books():
    """
    kitaplar tümüyle uygulamada gösterilip 
    kira durumu ve kime kiralandı,
    kira süresi
    """
    books=mongo.book.find({},{"_id":False})
    return books 
    
    
def rent_book(book):
    from main import _online_user
    a,token=_online_user()
    user=mongo.token_user.find_one({"token":token})["pasaport_no"]
    now = datetime.now()
    end_day=now+timedelta(days=30)
    if a == True:
        book_rent= mongo.book.find_one({"title":book["title"]},{"_id":False})
        if int(book_rent["rent_time"]) == 0 :
            mongo.book.update_many({"title":book["title"]},{"$set":{"rent_time":30,
                                                                    "start_time_rent":now.strftime("%d/%m/%Y"),
                                                                    "end_time_rent":end_day.strftime("%d/%m/%Y"),
                                                                    "rent_user":user,
                                                                    "refound":"False"}})
            
            return book_rent

    else:
        return False
        
def rez_book(rez_book):
    """
    kitapların rezervasyon yapılması 
    fonksiyona, kiralama sayfasından gelen string değeri data base de eşleştirip
    eşleşen kitabı yeni bir değişken ile tanımlayıp, veri güncellemesi.
    """
    from main import _online_user
    a,token=_online_user
    user=mongo.token_user.find_one({"token":token})["pasaport_no"]
    book=mongo.book.find_one({"title":rez_book})#html den gelen string DB de eşleşip, yeni bir değişken 
    if book["rent_user"] != None:
        mongo.book.update_one({"title":book["title"]},{"$set":{"rez_user":user}})
        return True
    else:
        return False

        
def where_book():
    """kütüphanede bulunan kitaplar
    kitap kullanıcıdamı, kütüphanedenmi
    """
    pass


def update_rent_book():
    
    """
    kirada olan kitapların gün takibi
    VE günü biten kitapların güncellenmesi
    teslim günü geçen kitapların,geçen gün kadar kullanıcıya ceza işlenmesi
    """
    now=datetime.now()

    books=mongo.book.find({})#DB deki kitaplar
    for i in books:
        if int(i["rent_time"]) != 0: #kiralık olan kitapların gün güncellemesi 
            end_time=i["end_time_rent"]
            end_time=end_time=datetime.strptime(end_time,"%d/%m/%Y")#DB deki tarihi datetime nesnesine çevrilir
            difference=end_time-now
            mongo.book.update_one({"title":i["title"]},{"$set":{"rent_time":difference.days}})
        
            
        if int(i["rent_time"])>=0 and i["refound"] == "True":#teslim gününden önce veya teslim günü iade eden kullanıcıların güncellemesi
            new_add={"end_time_rent":"", #!!!! burda sıkınıt var kullanıcı kitap kiralıyo tekrar güncelleme yapılınca 0 lanıyor
                     "start_time_rent":"",
                     "rent_time":int(0),
                     "rent_user":None,
                     "refound":""}
            mongo.book.update_one({"title":i["title"]},{"$set":new_add})
        
        elif int(i["rent_time"])<0 and i["refound"] == "True":#gecikmeli teslim eden kullanıcı
            new_add={"end_time_rent":"",
                     "start_time_rent":"",
                     "rent_time":int(0),
                     "rent_user":None,
                     "refound":""}
            mongo.book.update_one({"title":i["title"]},{"$set":new_add})
        elif int(i["rent_time"])< 0 and i["refound"] == "False": # kullanıcı eğer gününde teslim etmediyse geciken gün kadar ceza
            end_time=i["end_time_rent"]
            end_time=datetime.strptime(end_time,"%d/%m/%Y")
            difference=end_time-now
            mongo.book.update_one({"pasaport_no":i["rent_user"]},{"$set":{"late_day":difference.days}})
        
        
            
def refound(book):
    from main import _online_user
    a,token=_online_user()
    user=mongo.token_user.find_one({"token":token}["pasaport_no"])
    book=mongo.book.find_one({"title":book})
    if book["rent_user"] ==user:
        mongo.book.update_one({"title":book["title"]}, {"$set":{"refound":"True"}})
                                                                
        
       
            
def update_rez_book():
    """
    Eğer kitap kira durumu bitdiyse ve rezervasyonda bekleyen kullanıcı varsa
    kitap kiralama durumu kullanıcıya geçer
    """
    
    
    now=datetime.now()
    book=mongo.book.find({})

    for i in book:
        now = datetime.now()
        end_day =now+timedelta(days=30)
        if  i["rent_user"]== None and i["rez_user"] != None:
            
            mongo.book.update_one({"title":i["title"]},{"$set":{"rent_user":i["rez_user"],
                                                                "rez_user":None,
                                                                "rent_time":30,
                                                                "start_time_rent":now.strftime("%d/%m/%Y"),
                                                                "end_time_rent":end_day.strftime("%d/%m/%Y"),
                                                                "refound":"False"}})


def test_book():
    pass
    # asıl="onur"
    # user="user"+asıl
    # a= mongo.book.find({},{"_id":False})
    # mongo.book.update_one({"title":"fairy TALES deneme"},{"$set":{"where":user}})
    # print(a)
    # for  document in a:
        
    #     pprint.pprint(document)    
    
    
    # return mongo.book.update_many({}, {"$set": {"rent_time":"Available"}})

    #veri kümesini güncelleme

    # filter_query = {'username': 'kullaniciAdi'}
    # update_query = {'$set': {'yeniAlan': 'yeniDeger'}}

    # result = collection.update_one(filter_query, update_query)
    
    
# test_book()



# mongo.book.update_many({},{"$set": {"refound":"True"}})
                                    
                                     
# mongo.book.
# a=mongo.book.find_one({"title":"Things Fall Apart"})
# print(a)
# if int(a["rent_time"]) == 0:
#     mongo.book.update_one({"title":a["title"]},{"$set": {"rent_time":"5"}})


# if __name__=="__main__":
#     app.run(debug=True)

# a = mongo.book.find({})
# for i in a:
#     print(i["title"])


user_book=mongo.book.find({"rent_user":"43057138012"})

if user_book == None:
    print("götoldum")