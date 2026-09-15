# Scheduling

```python
from package_name import schedule

schedule.job(sync_data).every_five_minutes().without_overlapping()
schedule.job(generate_report).daily_at("02:00").timezone("Africa/Cairo").on_one_server()
schedule.job(weekly_report).weekly_on("monday", "08:00")
schedule.job(custom).cron("*/5 * * * *")
```

Timezone behavior is explicit. Never rely silently on the machine local timezone.

## without_overlapping vs on_one_server

| API | Purpose |
| --- | --- |
| `without_overlapping()` | Prevents a second run of the **same schedule entry** while a previous run is still considered active (overlap lock + TTL). |
| `on_one_server()` | Ensures only **one app server** wins the right to dispatch a due tick (leader/coordination lock). |

They compose: multi-server deployments often want both.
