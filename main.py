import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers.cron_router import router as cron_rout

app = FastAPI()  # Crea la Aplicación

# Configurar las plantillas
templates = Jinja2Templates(directory="templates")

# Implementar Rutas o Controllers
app.include_router(cron_rout)

# Endpoint que devuelve un mensaje y muestra el HTML
@app.get("/", response_class=HTMLResponse)
async def message(request: Request):
    crontab = open("crontab.txt").read() if os.path.exists("crontab.txt") else ""
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
