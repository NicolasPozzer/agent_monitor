from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse  # Importa RedirectResponse
from routers.cron_router import router as cron_rout

app = FastAPI()  # Crea la Aplicación

# Configurar las plantillas
templates = Jinja2Templates(directory="templates")

# Implementar Rutas o Controllers
app.include_router(cron_rout)

# Endpoint que devuelve un mensaje y muestra el HTML
@app.get("/", response_class=HTMLResponse)
async def message(request: Request):
    # Redirige al endpoint que maneja la visualización de crons
    return RedirectResponse(url='/crons', status_code=303)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
