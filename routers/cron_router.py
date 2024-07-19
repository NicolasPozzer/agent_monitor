from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class CronJob:
    def __init__(self, job: str, name: str, state: str = "paused"):
        self.job = job
        self.name = name
        self.state = state

    def __str__(self):
        return f"{self.job} {self.name}"

    @staticmethod
    def from_string(cron_string: str):
        parts = cron_string.split()
        if len(parts) < 6:
            raise ValueError("Invalid cron string")
        job = " ".join(parts[:5])
        name = " ".join(parts[5:])
        return CronJob(job, name, state="paused")

    def to_crontab_string(self):
        return f"{self.job} {self.name}"

def get_crontab():
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""
    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            try:
                job = CronJob.from_string(line.strip())
                cron_jobs.append(job)
            except ValueError:
                continue
    return cron_jobs

def set_crontab(crontab):
    new_crontab = "\n".join([job.to_crontab_string() for job in crontab])
    p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
    p.communicate(input=new_crontab.encode('utf-8'))

@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    crontab = get_crontab()
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    crontab.append(CronJob(cron_job, name, state="paused"))
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    crontab = [job for job in crontab if job.job.strip() != cron_job.strip()]
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/edit")
async def edit_cron_job(cron_job: str = Form(...), new_cron_job: str = Form(...)):
    crontab = get_crontab()
    for job in crontab:
        if job.job.strip() == cron_job.strip():
            job.job = new_cron_job
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)

@router.post("/crons/run")
async def run_cron_job(cron_job: str = Form(...), state: str = Form(...)):
    crontab = get_crontab()
    for job in crontab:
        if job.job.strip() == cron_job.strip():
            job.state = state
    set_crontab(crontab)
    return RedirectResponse("/", status_code=303)
