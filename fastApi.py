# fastapi_app.py
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from main import lib_app

# Flask uygulamasını oluştur
flask_lib_app = lib_app()
flask_app = flask_lib_app.app

# FastAPI uygulamasını oluştur
fastapi_app = FastAPI()

# Flask uygulamasını FastAPI uygulamasına monte et
fastapi_app.mount("/", WSGIMiddleware(flask_app))

# FastAPI endpoint
@fastapi_app.get("/fastapi_endpoint")
def fastapi_endpoint():
    return {"message": "Hello from FastAPI endpoint"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
    
#deneme