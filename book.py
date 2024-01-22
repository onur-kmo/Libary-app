from flask import Flask,render_template,request,redirect,url_for
from flask_pymongo import PyMongo
from datetime import datetime,timedelta


"""
DB deki kitapları gösterme/listeleme
kurallar;-kitaplar sadece 30 gün kiralanabilir,...
kullanıcılar kendi ellerindeki kitapları sisteme girebilir 
kitapların durumu; nerede, eğerkimdeyse nere de ,
borçlanma kayıtları, cezalar ve rezervasyonlar.
"""
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/lib_base"
mongo = PyMongo(app).db




def show_books():
    """
    kitaplar tümüyle uygulamada gösterilip 
    kira durumu ve kime kiralandı,
    kira süresi
    """
    books=mongo.book.find({},{"_id":False})
    rent_book=mongo.book.find({"rent_time": {"$gt": "0"}})
    
    return books #render_template("show_book.html",books=books)
    
 
def rent_book(book):
    from main import _online_user
    a,token=_online_user()
    user=mongo.token_user.find_one({"token":token})["pasaport_no"]
    now = datetime.now()
    end_day=now+timedelta(days=30)
    if a == True:
        
        book_rent= mongo.book.find_one({"title":book["title"]},{"_id":False})
        if int(book_rent["rent_time"]) == 0 :
            mongo.book.update_many({"title":book["title"]},{"$set":{"rent_time":"30",
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
    """
    from main import _online_user
    a,token=_online_user
    user=mongo.token_user.find_one({"token":token})["pasaport_no"]
    if rez_book["rent_time"] >0 and  rez_book["ren_user"] != None:
        mongo.book.update_one({"title":rez_book["title"]},{"$set":{"rez_user":user,"rez_start_time":rez_book["end_time_rent"]}})
        return True,rez_book
    else:
        return False,False

        
        


    
        

def where_book():
    """kütüphanede bulunan kitaplar
    kitap kullanıcıdamı, kütüphanedenmi
    """
    pass


def update_rent_book():
    
    """
    kirada olan kitapların gün takibi
    VE günü biten kitapların güncellenmesi
    """
    now=datetime.now()

    books=mongo.book.find({})
    # "end_time_rent":end_day("%d/%m/%Y")
    
    for i in books:
        if int(i["rent_time"])>0 and i["refound"] == "False": #burada kalan gün güncellemesi yapılır
            end_time=i["end_time_rent"]
            end_time=datetime.strptime(end_time,"%d/%m/%Y")
            "kitaplarda bululnan zamanları  datetine nesnesine çevrildi"
            
            # start_time_rent=i["start_time_rent"]
            # start_time_rent=datetime.strptime(start_time_rent,"%d/%m/%Y")
            
            difference=end_time-now # güncelleme için gün farkını alıyoruz
            mongo.book.update_many({"title":i["title"]},{"$set":{"rent_time":difference.days}})
            

        elif int(i["rent_time"])==0 and i["refound"] == "True" or int(i["rent_time"])>0 and i["refound"] == "True":
            new_add={"end_time_rent":"",
                     "start_time_rent":"",
                     "rent_time":"0",
                     "rent_user":"",
                     "refound":"False"}
            mongo.book.update_many({"title":i["title"]},{"$set":new_add})
        elif int(i["rent_time"])==0 and i["refound"] == "False":
            mongo.book.update_one({"pasaport_no":i["rent_user"]},{"$set":{"late_day":difference.days}})
        
        

def refound(book):
    from main import _online_user
    a,token=_online_user()
    user=mongo.token_user.find_one({"token":token}["pasaport_no"])
    if book["rent_user"] ==user:
        if book["rent_time"] >0 or book["rent_time"] == 0:
            mongo.book.update_one({"title":book["title"]}, {"$set":{"rent_time":"0",
                                                                    "end_time_rent":"",
                                                                    "start_time_rent":"",
                                                                    "rent_user":"",
                                                                    "refound":"True"}})
        elif book["rent_time"] <0:
            mongo.book.update_one({"title":book["title"]},{"$set":{"day_penalty":""}})


       
       
        pass

    
    
    pass

def update_rez_book():
    now=datetime.now()
    books=mongo.book.find({})

    for i in books:
        if  books["rez_start_time"]==now.strftime("%d/%m/%Y"):
            pass
    
    pass


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



# mongo.book.update_many({}, {"$set": {"rez_user:""}})
# mongo.book.
# a=mongo.book.find_one({"title":"Things Fall Apart"})
# print(a)
# if int(a["rent_time"]) == 0:
#     mongo.book.update_one({"title":a["title"]},{"$set": {"rent_time":"5"}})


# if __name__=="__main__":
#     app.run(debug=True)