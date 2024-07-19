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
