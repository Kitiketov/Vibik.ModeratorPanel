from __future__ import annotations

import io
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.common.models.metric_model import MetricModel, MetricType


@dataclass
class MetricsSummary:
    average_submissions_per_user: float
    change_percent: float
    average_submit_minutes: float | None
    average_between_submits_minutes: float | None
    submit_count: int
    change_count: int
    user_count: int


@dataclass
class MetricsVisualization:
    summary: MetricsSummary
    image_bytes: bytes
    filename: str = "metrics.png"


def build_metrics_visualization(
    metrics: Sequence[MetricModel], *, now: datetime | None = None, weeks: int = 4
) -> MetricsVisualization:
    """
    Собирает агрегированную статистику (последняя неделя) и строит диаграмму по неделям.
    """
    now = now or datetime.now(timezone.utc)
    weeks = max(1, weeks)

    events: list[tuple[MetricModel, datetime, MetricType]] = []
    for metric in metrics:
        metric_type = _normalize_metric_type(metric.type)
        if metric_type is None:
            continue
        ts = _to_utc(metric.time)
        events.append((metric, ts, metric_type))

    # Сводка за последнюю неделю (7 дней от текущего момента)
    summary_start_dt = datetime.combine(
        now.date() - timedelta(days=6), datetime.min.time(), tzinfo=timezone.utc
    )
    summary_submit = [
        (m, ts)
        for m, ts, m_type in events
        if ts >= summary_start_dt and m_type == MetricType.Submit
    ]
    summary_change = [
        (m, ts)
        for m, ts, m_type in events
        if ts >= summary_start_dt and m_type == MetricType.Change
    ]
    summary = _build_summary(summary_submit, summary_change)

    # Диаграмма по неделям
    current_week_start = now.date() - timedelta(days=now.weekday())
    chart_start_date = current_week_start - timedelta(days=7 * (weeks - 1))
    chart_start_dt = datetime.combine(
        chart_start_date, datetime.min.time(), tzinfo=timezone.utc
    )
    chart_events = [(m, ts, t) for m, ts, t in events if ts >= chart_start_dt]
    (
        labels,
        submit_counts,
        change_counts,
        total_counts,
        avg_per_user,
        avg_submit_per_user,
        avg_change_per_user,
    ) = _weekly_counts(chart_events, chart_start_date, weeks)

    image_bytes = _render_chart(
        labels,
        submit_counts,
        change_counts,
        total_counts,
        avg_per_user,
        avg_submit_per_user,
        avg_change_per_user,
    )
    return MetricsVisualization(summary=summary, image_bytes=image_bytes)


def format_average_time(avg_minutes: float | None) -> str:
    if avg_minutes is None:
        return "нет данных"

    total_minutes = int(round(avg_minutes))
    hours, minutes = divmod(total_minutes, 60)
    hours = hours % 24
    return f"{hours:02d}:{minutes:02d}"


def format_duration_minutes(avg_minutes: float | None) -> str:
    if avg_minutes is None:
        return "нет данных"

    total_minutes = int(round(avg_minutes))
    days, rem_minutes = divmod(total_minutes, 60 * 24)
    hours, minutes = divmod(rem_minutes, 60)
    if days > 0:
        return f"{days}д {hours}ч {minutes}м"
    if hours > 0:
        return f"{hours}ч {minutes}м"
    return f"{minutes}м"


def _build_summary(
    submit_events: Sequence[tuple[MetricModel, datetime]],
    change_events: Sequence[tuple[MetricModel, datetime]],
) -> MetricsSummary:
    submit_count = len(submit_events)
    change_count = len(change_events)

    user_submissions: dict[str, int] = defaultdict(int)
    for metric, _ in submit_events:
        user_submissions[metric.username] += 1
    user_count = len(user_submissions)

    avg_submissions = submit_count / user_count if user_count else 0.0
    change_percent = (change_count / submit_count * 100) if submit_count else 0.0
    avg_submit_minutes = _average_submit_time(submit_events)
    avg_between_submits = _average_between_submits(submit_events)

    return MetricsSummary(
        average_submissions_per_user=avg_submissions,
        change_percent=change_percent,
        average_submit_minutes=avg_submit_minutes,
        average_between_submits_minutes=avg_between_submits,
        submit_count=submit_count,
        change_count=change_count,
        user_count=user_count,
    )


def _average_submit_time(
    events: Sequence[tuple[MetricModel, datetime]],
) -> float | None:
    if not events:
        return None

    total_minutes = sum(
        ts.hour * 60 + ts.minute + ts.second / 60 for _, ts in events
    )
    return total_minutes / len(events)


def _average_between_submits(
    events: Sequence[tuple[MetricModel, datetime]],
) -> float | None:
    if len(events) < 2:
        return None

    per_user: dict[str, list[datetime]] = defaultdict(list)
    for metric, ts in events:
        per_user[metric.username].append(ts)

    deltas: list[float] = []
    for timestamps in per_user.values():
        timestamps.sort()
        for first, second in zip(timestamps, timestamps[1:]):
            delta_minutes = (second - first).total_seconds() / 60
            if delta_minutes >= 0:
                deltas.append(delta_minutes)

    if not deltas:
        return None
    return sum(deltas) / len(deltas)


def _weekly_counts(
    events: Sequence[tuple[MetricModel, datetime, MetricType]],
    start_week_date: date,
    weeks: int,
) -> tuple[
    list[str],
    list[int],
    list[int],
    list[int],
    list[float],
    list[float],
    list[float],
]:
    labels: list[str] = []
    submit_counts = [0 for _ in range(weeks)]
    change_counts = [0 for _ in range(weeks)]
    total_counts = [0 for _ in range(weeks)]
    users_per_week: list[set[str]] = [set() for _ in range(weeks)]
    submit_users_per_week: list[set[str]] = [set() for _ in range(weeks)]
    change_users_per_week: list[set[str]] = [set() for _ in range(weeks)]

    for i in range(weeks):
        week_start = start_week_date + timedelta(days=7 * i)
        week_end = week_start + timedelta(days=6)
        labels.append(f"{week_start.strftime('%d.%m')}-{week_end.strftime('%d.%m')}")

    for metric, ts, m_type in events:
        week_index = (ts.date() - start_week_date).days // 7
        if 0 <= week_index < weeks:
            users_per_week[week_index].add(metric.username)
            if m_type == MetricType.Submit:
                submit_counts[week_index] += 1
                submit_users_per_week[week_index].add(metric.username)
            elif m_type == MetricType.Change:
                change_counts[week_index] += 1
                change_users_per_week[week_index].add(metric.username)
            total_counts[week_index] += 1

    avg_per_user: list[float] = []
    avg_submit_per_user: list[float] = []
    avg_change_per_user: list[float] = []
    for total, users in zip(total_counts, users_per_week):
        user_count = len(users)
        avg_per_user.append(total / user_count if user_count else 0.0)

    for submit_total, users in zip(submit_counts, submit_users_per_week):
        user_count = len(users)
        avg_submit_per_user.append(submit_total / user_count if user_count else 0.0)

    for change_total, users in zip(change_counts, change_users_per_week):
        user_count = len(users)
        avg_change_per_user.append(change_total / user_count if user_count else 0.0)

    return (
        labels,
        submit_counts,
        change_counts,
        total_counts,
        avg_per_user,
        avg_submit_per_user,
        avg_change_per_user,
    )


def _render_chart(
    labels: Sequence[str],
    submit_counts: Sequence[int],
    change_counts: Sequence[int],
    total_counts: Sequence[int],
    avg_per_user: Sequence[float],
    avg_submit_per_user: Sequence[float],
    avg_change_per_user: Sequence[float],
) -> bytes:
    fig, ax = plt.subplots(figsize=(9, 4))
    x_positions = list(range(len(labels)))
    width = 0.18

    offsets = [-1.5 * width, -0.5 * width, 0.5 * width, 1.5 * width]
    ax.bar(
        [x + offsets[0] for x in x_positions],
        submit_counts,
        width=width,
        label="Сдачи (общее)",
        color="#4CAF50",
    )
    ax.bar(
        [x + offsets[1] for x in x_positions],
        change_counts,
        width=width,
        label="Замены (общее)",
        color="#FF9800",
    )
    ax.bar(
        [x + offsets[2] for x in x_positions],
        avg_submit_per_user,
        width=width,
        label="Сдачи (ср/польз)",
        color="#8BC34A",
        alpha=0.8,
    )
    ax.bar(
        [x + offsets[3] for x in x_positions],
        avg_change_per_user,
        width=width,
        label="Замены (ср/польз)",
        color="#FFB74D",
        alpha=0.85,
    )

    ax.set_ylabel("Количество событий")
    ax.set_title("Метрики по неделям")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.5)

    # Текстовые подписи: общее количество и среднее на пользователя
    for idx, x in enumerate(x_positions):
        total = total_counts[idx]
        avg = avg_per_user[idx]
        text = f"{total} (ср {avg:.1f}/польз)"
        max_height = max(
            submit_counts[idx],
            change_counts[idx],
            avg_submit_per_user[idx],
            avg_change_per_user[idx],
        )
        ax.text(
            x,
            max_height + max(max_height * 0.05, 0.2),
            text,
            ha="center",
            va="bottom",
            fontsize=8,
            color="#333333",
        )

    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=200)
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _normalize_metric_type(raw: object) -> MetricType | None:
    if isinstance(raw, MetricType):
        return raw

    try:
        return MetricType(raw)  # tries int/enum value
    except Exception:
        pass

    if isinstance(raw, str):
        lower = raw.lower()
        if lower.startswith("submit"):
            return MetricType.Submit
        if lower.startswith("change") or lower.startswith("replace"):
            return MetricType.Change

    return None
