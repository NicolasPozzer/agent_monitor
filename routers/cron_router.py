from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class CronJob:
    def __init__(self, job: str, name: str):
        self.job = job
        self.name = name

    def __str__(self):
        return f"{self.job} # {self.name}"

    @staticmethod
    def from_string(cron_string: str):
        parts = cron_string.split(" # ")
        job = parts[0]
        name = parts[1] if len(parts) > 1 else ''
        return CronJob(job, name)

def get_crontab():
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""
    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            cron_jobs.append(CronJob.from_string(line.strip()))
    return cron_jobs

def set_crontab(crontab):
    new_crontab = "\n".join([str(job) for job in crontab])
    # Asegurarse de que haya una línea en blanco al final
    if not new_crontab.endswith('\n'):
        new_crontab += '\n'
    p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
    p.communicate(input=new_crontab.encode('utf-8'))


@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    crontab = get_crontab()
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    new_cron = CronJob(cron_job, name)
    crontab.append(new_cron)
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    crontab = [job for job in crontab if job.job.strip() != cron_job.strip()]
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/edit")
async def edit_cron_job(cron_job: str = Form(...), new_cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    updated = False
    for job in crontab:
        if job.job.strip() == cron_job.strip():
            job.job = new_cron_job
            job.name = name
            updated = True
            break
    if updated:
        set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/run")
async def run_cron_job(cron_job: str = Form(...), action: str = Form(...)):
    crontab = get_crontab()
    updated = False
    for job in crontab:
        if job.job.strip() == cron_job.strip():
            if action == "Run":
                job.job = job.job.lstrip("# ").strip()
            elif action == "Pause":
                job.job = f"# {job.job}"
            updated = True
            break
    if updated:
        set_crontab(crontab)
    return RedirectResponse("/", status_code=303)
