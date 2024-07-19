from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from routers.cron_router import router as cron_rout
import subprocess

app = FastAPI()  # Crea la Aplicación

# Configurar las plantillas
templates = Jinja2Templates(directory="templates")

# Implementar Rutas o Controllers
app.include_router(cron_rout)

# Endpoint que devuelve un mensaje y muestra el HTML
@app.get("/", response_class=HTMLResponse)
async def message(request: Request):
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        # Maneja el caso en que no hay crontab
        crontab = ""

    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            parts = line.split()
            # Asegúrate de que el índice 5 esté dentro del rango
            name = " ".join(parts[5:]) if len(parts) > 5 else ""
            job = " ".join(parts[:5])
            cron_jobs.append({"name": name, "job": job})

    return templates.TemplateResponse("index.html", {"request": request, "crontab": cron_jobs})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
