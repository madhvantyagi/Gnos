"""Shared evidence chronology without inventing times for historical chat work."""
from collections import defaultdict
from datetime import datetime, timezone


def occurrence_time(event):
    value = event.get('occurred_at')
    if value is None:
        return None
    if not isinstance(value, str) or not value.endswith('Z'):
        raise ValueError('occurred_at must be an ISO UTC timestamp')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('occurred_at must be a real ISO UTC timestamp') from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError('occurred_at must be an ISO UTC timestamp')
    return parsed


def ordered_events(events):
    """Order known times within each day; keep untimed legacy slots in place.

    Pure legacy records retain their established date/insertion behavior. Mixed
    same-day timed/untimed observations cannot establish a total chronology;
    summaries separately retain that uncertainty when the outcomes conflict.
    """
    days = defaultdict(list)
    for event in events:
        days[event['date']].append(event)
    result = []
    for day in sorted(days):
        group = days[day]
        timed = iter(sorted((e for e in group if occurrence_time(e) is not None),
                            key=lambda e: (occurrence_time(e), e['id'])))
        result.extend(next(timed) if occurrence_time(e) is not None else e for e in group)
    return result


def uncertain_outcomes(events):
    """Identify conflicting outcomes whose same-day ordering is not known."""
    observations = defaultdict(list)
    for event in events:
        # Within one event the attempt array already records a known sequence.
        for attempt in {a['concept']: a for a in event['attempts']}.values():
            observations[(event['date'], attempt['concept'])].append((event['id'], occurrence_time(event), attempt))
    result = {}
    for key, rows in observations.items():
        event_times = {id_: stamp for id_, stamp, _ in rows}
        timed = [stamp for stamp in event_times.values() if stamp is not None]
        mixed = bool(timed) and len(timed) < len(event_times)
        # A known later observation resolves an earlier tied timestamp.
        candidates = rows if mixed else [row for row in rows if timed and row[1] == max(timed)]
        tied = len(candidates) > 1
        success = any(a['result'] == 'correct' and a['help'] == 'none' for _, _, a in candidates)
        other = [a for _, _, a in candidates if a['result'] != 'correct' or a['help'] != 'none']
        if (mixed or tied) and success and other:
            result[key] = other[-1]
    return result
