from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess
import tempfile
import os
from models import CronJob  # Asegúrate de que el archivo models.py esté en el mismo directorio o ajusta el import

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Función para obtener el contenido del crontab
def get_crontab():
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""

    cron_jobs = []
    if crontab.strip():  # Solo procesar si no está vacío
        for line in crontab.split('\n'):
            if line.strip():
                try:
                    cron_job = CronJob.from_string(line)
                    cron_jobs.append(cron_job)
                except ValueError:
                    continue  # Ignorar líneas inválidas
    return cron_jobs


# Función para establecer el contenido del crontab
def set_crontab(crontab):
    new_crontab = "\n".join(str(job) for job in crontab)
    new_crontab = new_crontab + "\n"  # Asegura que haya una nueva línea al final

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(new_crontab.encode('utf-8'))
        temp_file.close()
        subprocess.run(['crontab', temp_file.name])
        os.remove(temp_file.name)  # Eliminar el archivo temporal después de usarlo

@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    crontab = get_crontab()  # Obtener las tareas cron
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})


@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    crontab.append(CronJob(cron_job, name))
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    cron_job_obj = CronJob.from_string(cron_job)
    crontab = [job for job in crontab if not (job.job.strip() == cron_job_obj.job.strip() and job.name.strip() == cron_job_obj.name.strip())]
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/edit")
async def edit_cron_job(cron_job: str = Form(...), new_cron_job: str = Form(...)):
    crontab = get_crontab()
    old_cron_job_obj = CronJob.from_string(cron_job)
    new_cron_job_obj = CronJob.from_string(new_cron_job)

    for i, job in enumerate(crontab):
        if job.job.strip() == old_cron_job_obj.job.strip() and job.name.strip() == old_cron_job_obj.name.strip():
            crontab[i] = new_cron_job_obj
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/run")
async def run_cron_job(cron_job: str = Form(...)):
    subprocess.Popen(cron_job.split(), shell=True)
    return RedirectResponse("/", status_code=303)
