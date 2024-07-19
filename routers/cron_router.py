from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CRON_FILE = "crontab.txt"

def get_crontab():
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""
    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            parts = line.split()
            if len(parts) < 6:
                continue
            job = " ".join(parts[:5])
            name = " ".join(parts[5:])
            cron_jobs.append({"job": job, "name": name, "state": "running"})
    return cron_jobs

def set_crontab(crontab):
    new_crontab = "\n".join([f"{job['job']} {job['name']}" for job in crontab])
    p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
    p.communicate(input=new_crontab.encode('utf-8'))

@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    crontab = get_crontab()
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    crontab.append({"job": cron_job, "name": name, "state": "paused"})
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    crontab = [job for job in crontab if job["job"].strip() != cron_job.strip()]
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/edit")
async def edit_cron_job(cron_job: str = Form(...), new_cron_job: str = Form(...)):
    crontab = get_crontab()
    for job in crontab:
        if job["job"].strip() == cron_job.strip():
            job["job"] = new_cron_job
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/run")
async def run_cron_job(cron_job: str = Form(...), state: str = Form(...)):
    crontab = get_crontab()
    for job in crontab:
        if job["job"].strip() == cron_job.strip():
            job["state"] = state
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/restore")
async def restore_cron_jobs():
    # Código para restaurar el crontab desde un archivo de respaldo
    return RedirectResponse("/", status_code=303)
