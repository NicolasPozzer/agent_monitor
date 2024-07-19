from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
import subprocess
import os

router = APIRouter()

CRON_FILE = "crontab.txt"

# Función para obtener el contenido del crontab
def get_crontab():
    if os.path.exists(CRON_FILE):
        with open(CRON_FILE, 'r') as file:
            return file.read()
    return ""

# Función para establecer el contenido del crontab
def set_crontab(crontab):
    with open(CRON_FILE, 'w') as file:
        file.write(crontab)
    p = subprocess.Popen(['crontab', CRON_FILE], stdin=subprocess.PIPE)
    p.communicate()

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    crontab += cron_job + '\n'
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    new_crontab = "\n".join(line for line in crontab.split('\n') if line.strip() != cron_job.strip())
    set_crontab(new_crontab)
    return RedirectResponse("/", status_code=303)
