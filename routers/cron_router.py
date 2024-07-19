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
        return f"{self.job} {self.name}"

    @staticmethod
    def from_string(cron_string: str):
        parts = cron_string.split()
        if len(parts) < 6:
            raise ValueError("Invalid cron string")
        job = " ".join(parts[:5])
        name = " ".join(parts[5:])
        return CronJob(job, name)


    def to_crontab_string(self):
        return f"{self.job} {self.name}"



def get_crontab(state=None):
    try:
        crontab = subprocess.check_output(['crontab', '-l']).decode('utf-8')
    except subprocess.CalledProcessError:
        crontab = ""
    cron_jobs = []
    for line in crontab.split('\n'):
        if line.strip():
            parts = line.split()
            name = " ".join(parts[5:])
            job = " ".join(parts[:5])
            job_state = "active" if state is None else state
            cron_jobs.append(CronJob(job, name, job_state))
    return cron_jobs


def set_crontab(crontab):
    new_crontab = "\n".join([str(job) for job in crontab])
    # Añadir una nueva línea al final del archivo crontab
    new_crontab += "\n"
    p = subprocess.Popen(['crontab'], stdin=subprocess.PIPE)
    p.communicate(input=new_crontab.encode('utf-8'))




@router.get("/crons", response_class=HTMLResponse)
async def read_crontab(request: Request):
    crontab = get_crontab()
    return templates.TemplateResponse("index.html", {"request": request, "crontab": crontab})

@router.post("/crons/add")
async def add_cron_job(cron_job: str = Form(...), name: str = Form(...)):
    crontab = get_crontab()
    # Crear un nuevo objeto CronJob
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
    active_crontab = get_crontab(state="active")
    paused_crontab = get_crontab(state="paused")

    if action == "Run":
        # Reactivar el cron job
        for job in paused_crontab:
            if job.job.strip() == cron_job.strip():
                job.state = "active"
                active_crontab.append(job)
            else:
                active_crontab.append(job)
        paused_crontab = [job for job in paused_crontab if job.job.strip() != cron_job.strip()]
    elif action == "Pause":
        # Pausar el cron job
        for job in active_crontab:
            if job.job.strip() == cron_job.strip():
                job.state = "paused"
                paused_crontab.append(job)
            else:
                paused_crontab.append(job)
        active_crontab = [job for job in active_crontab if job.job.strip() != cron_job.strip()]

    # Actualizar crontab
    set_crontab(active_crontab, state="active")
    set_crontab(paused_crontab, state="paused")

    return RedirectResponse("/", status_code=303)

