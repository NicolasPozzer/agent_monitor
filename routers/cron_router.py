from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import subprocess

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class CronJob:
    def __init__(self, job: str, name: str, job_state: str = 'active'):
        self.job = job
        self.name = name
        self.job_state = job_state

    def __str__(self):
        return f"{self.job} {self.name} {self.job_state}"

    @staticmethod
    def from_string(cron_string: str):
        parts = cron_string.split()
        if len(parts) < 6:
            raise ValueError("Invalid cron string")
        job = " ".join(parts[:5])
        name = " ".join(parts[5:-1])
        job_state = parts[-1] if len(parts) > 5 and parts[-1] in ["active", "paused"] else 'active'
        return CronJob(job, name, job_state)

def get_crontab(state=None):
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""
    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            parts = line.split()
            job = " ".join(parts[:5])
            name = " ".join(parts[5:-1])
            job_state = parts[-1] if len(parts) > 5 and parts[-1] in ["active", "paused"] else "active"
            cron_jobs.append(CronJob(job, name, job_state))
    return cron_jobs

def set_crontab(crontab):
    new_crontab = "\n".join([str(job) for job in crontab])
    new_crontab += "\n"
    p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
    p.communicate(input=new_crontab.encode('utf-8'))

@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    active_crontab = get_crontab(state="active")
    paused_crontab = get_crontab(state="paused")
    return templates.TemplateResponse("index.html", {"request": request, "active_crontab": active_crontab, "paused_crontab": paused_crontab})

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    new_cron = CronJob(cron_job, name)
    crontab.append(new_cron)
    set_crontab(crontab)
    return RedirectResponse("/crons", status_code=303)

@router.post("/crons/delete")
async def delete_cron_job(cron_job: str = Form(...)):
    crontab = get_crontab()
    crontab = [job for job in crontab if job.job.strip() != cron_job.strip()]
    set_crontab(crontab)
    return RedirectResponse("/crons", status_code=303)

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
    return RedirectResponse("/crons", status_code=303)

@router.post("/crons/run")
async def run_cron_job(cron_job: str = Form(...), action: str = Form(...)):
    active_crontab = get_crontab(state="active")
    paused_crontab = get_crontab(state="paused")

    if action == "Run":
        for job in paused_crontab:
            if job.job.strip() == cron_job.strip():
                job.job_state = "active"
                active_crontab.append(job)
        paused_crontab = [job for job in paused_crontab if job.job.strip() != cron_job.strip()]
    elif action == "Pause":
        for job in active_crontab:
            if job.job.strip() == cron_job.strip():
                job.job_state = "paused"
                paused_crontab.append(job)
        active_crontab = [job for job in active_crontab if job.job.strip() != cron_job.strip()]

    set_crontab(active_crontab)
    set_crontab(paused_crontab)

    return RedirectResponse("/crons", status_code=303)
