# # kullanıcı1={
# #     "_id":1,
# #     "username":"onur",
# #     "pass":"denem123",

# #     "_id" : 43,
# #     "username":"hasan",
# #     "pass":"denem123",
    
# #     "_id":25,
# #     "username":"veli",
# #     "pass":"denem123",
    
# #     "_id":15,
# #     "username":"onur",
# #     "pass":"değişik_onur",

onur=None
if onur == None:
    print("okey")

# # }



# # print(kullanıcı1.get("username"))


# # def my_decorator():
# #     def wrapper():
# #         print("Fonksiyon öncesi işlemler")
        
# #         print("Fonksiyon sonrası işlemler")
        

# #     def ikinci_deneme():
       
# #         return "deneme 2"

# # @my_decorator 
# # def say_hello():
# #     return




# # # say_hello fonksiyonunu çağırdığımızda, aslında my_decorator fonksiyonu tarafından sarmalanmış olacak



# user ={
#   "pasaport_no": "43057138012",
#   "username": "onur",
#   "password": "535353"
#     }



# # if user.items() in
# #     print("okey")
# # else:
# #     print("yok")

# user_name="onur"
# userpass="535353"
# pasaport="43057138012"

# if pasaport in user.values():
#     print("yeah")






# from datetime import datetime, timedelta

# # Kitap kiralama tarihi
# kiralama_tarihi = datetime(2024, 1, 15)

# # Kiralama süresi (örneğin, 14 gün)
# kiralama_suresi = timedelta(days=14)

# # Kitap iade tarihi hesapla
# iade_tarihi = kiralama_tarihi + kiralama_suresi

# # Şu anki tarihi al
# bugun = datetime.now()

# # Geçen süreyi hesapla
# gecen_sure = bugun - kiralama_tarihi

# # Kira süresi doldu mu kontrol et
# if bugun > iade_tarihi:
#     print("Kitap iade süresi doldu!")
#     gecikme_suresi = bugun - iade_tarihi
#     print(f"Toplam gecikme süresi: {gecikme_suresi.days} gün")
# else:
#     print("Kitap iade süresi devam ediyor.")
#     kalan_sure = iade_tarihi - bugun
#     print(f"Kalan iade süresi: {kalan_sure.days} gün")






# import jwt
# import datetime

# secret_key="onur"
# algorithm = "HS256"  # HMAC-SHA256 algoritması kullanılacak
# user={
#   "_id": {
#     "$oid": "65a3b78f1afa59005c0d246f"
#   },
#   "pasaport_no": "43057138012",
#   "username": "onur",
#   "password": "kmo"
# }
# token = jwt.encode( user,secret_key, algorithm=algorithm)
# print(token)
# print(user)

# if token =="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOnsiJG9pZCI6IjY1YTNiNzhmMWFmYTU5MDA1YzBkMjQ2ZiJ9LCJwYXNhcG9ydF9ubyI6IjQzMDU3MTM4MDEyIiwidXNlcm5hbWUiOiJvbnVyIiwicGFzc3dvcmQiOiJrbW8ifQ.fxZAs2DhgMYIyDZ45QRqyAwGD3-pS_zsXrwED6O17Y8":
#     print("DOĞRU")


# user={
  
#   "pasaport_no": "43057138012",
#   "username": "onur",
#   "password": "kmo"
# }

# username="onur"
# userpass="kmo"
# userpap="43057138012"

# if userpass and username and userpap in user.values():
#     print("doğru")
