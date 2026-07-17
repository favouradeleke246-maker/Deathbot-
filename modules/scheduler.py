from apscheduler.schedulers.background import BackgroundScheduler
from modules.utils import db_list_targets
import logging

logger = logging.getLogger(__name__)
sched = BackgroundScheduler()

def rescan_all():
    # Lazy import to avoid circular import
    from orchestrator import Orchestrator
    orch = Orchestrator()
    targets = db_list_targets()
    for t in targets:
        try:
            orch.track(t['identifier'])
            logger.info(f"Rescanned {t['identifier']}")
        except Exception as e:
            logger.error(f"Rescan failed for {t['identifier']}: {e}")

def start_scheduler():
    if not sched.running:
        sched.add_job(rescan_all, 'interval', hours=24)
        sched.start()
        logger.info("Scheduler started – rescans every 24 hours.")
