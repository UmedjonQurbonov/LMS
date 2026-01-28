from server.routers import app
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware



origins = [
    "http://localhost:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # какие домены разрешены
    allow_credentials=True,     # нужно для cookie или авторизации
    allow_methods=["*"],        # GET, POST, PUT, DELETE, PATCH
    allow_headers=["*"],        # все заголовки
)

@app.get("/health")
def health_check():
    return {"status": "ok"}




if __name__ == '__main__':
    uvicorn.run('server.routers:app', port=8000, host='localhost', reload=True)

