from server.routers import app
import uvicorn


if __name__ == '__main__':
    uvicorn.run('server.routers:app', port=8000, host='localhost', reload=True)

