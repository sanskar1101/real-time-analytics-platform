from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from src.celery_app import celery_app
from src.core.config import settings
from src.db.session import AsyncSessionLocal
from src.models.report_frequency import ReportFrequency
from src.repositories.analytics import AnalyticsRepository
from src.repositories.dashboard import DashboardRepository
from src.repositories.report import ReportRepository

logger = logging.getLogger(__name__)

_TABLE_HEADER_BG = colors.HexColor("#16213e")
_TABLE_ROW_STRIPE = colors.HexColor("#f5f5f5")
_TABLE_GRID = colors.HexColor("#cccccc")
_TITLE_COLOR = colors.HexColor("#1a1a2e")
_HEADING_COLOR = colors.HexColor("#16213e")
_META_COLOR = colors.HexColor("#555555")

_DEFAULT_TABLE_STYLE = [
    ("BACKGROUND", (0, 0), (-1, 0), _TABLE_HEADER_BG),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE", (0, 0), (-1, 0), 10),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _TABLE_ROW_STRIPE]),
    ("GRID", (0, 0), (-1, -1), 0.5, _TABLE_GRID),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
]


def _period_for_frequency(frequency: ReportFrequency) -> tuple[datetime, datetime]:
    now = datetime.now(UTC)
    if frequency == ReportFrequency.DAILY:
        return now - timedelta(days=1), now
    if frequency == ReportFrequency.WEEKLY:
        return now - timedelta(weeks=1), now
    return now - timedelta(days=30), now


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            parent=base["Title"],
            fontSize=20,
            spaceAfter=6,
            textColor=_TITLE_COLOR,
        ),
        "heading": ParagraphStyle(
            "SectionHeading",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=6,
            textColor=_HEADING_COLOR,
        ),
        "meta": ParagraphStyle(
            "Meta",
            parent=base["BodyText"],
            fontSize=9,
            textColor=_META_COLOR,
            spaceAfter=4,
        ),
    }


def _make_table(data: list[list[str]], col_widths: list[float]) -> Table:
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle(_DEFAULT_TABLE_STYLE))
    return t


def _build_pdf(
    *,
    output_path: str,
    report_name: str,
    dashboard_name: str,
    frequency: ReportFrequency,
    period_start: datetime,
    period_end: datetime,
    total_events: int,
    error_events: int,
    events_by_day: list[tuple],
    events_by_type: list[tuple],
) -> None:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=inch,
        bottomMargin=0.75 * inch,
    )
    styles = _build_styles()
    half_page = (letter[0] - 1.5 * inch) / 2

    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph(report_name, styles["title"]))
    story.append(Paragraph(f"Dashboard: {dashboard_name}", styles["heading"]))
    story.append(Paragraph(f"Frequency: {frequency.value.title()}", styles["meta"]))
    story.append(
        Paragraph(
            f"Period: {period_start.strftime('%Y-%m-%d %H:%M UTC')} "
            f"→ {period_end.strftime('%Y-%m-%d %H:%M UTC')}",
            styles["meta"],
        )
    )
    story.append(
        Paragraph(
            f"Generated: {period_end.strftime('%Y-%m-%d %H:%M UTC')}",
            styles["meta"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=_TABLE_GRID))
    story.append(Spacer(1, 0.2 * inch))

    # ── KPI Summary ───────────────────────────────────────────────────────────
    story.append(Paragraph("KPI Summary", styles["heading"]))
    error_rate = f"{error_events / total_events * 100:.1f}%" if total_events else "0.0%"
    kpi_data = [
        ["Metric", "Value"],
        ["Total Events", str(total_events)],
        ["Error Events", str(error_events)],
        ["Error Rate", error_rate],
    ]
    story.append(_make_table(kpi_data, [half_page, half_page]))
    story.append(Spacer(1, 0.2 * inch))

    # ── Events by Day ─────────────────────────────────────────────────────────
    story.append(Paragraph("Events by Day", styles["heading"]))
    if events_by_day:
        day_data = [["Date", "Event Count"]] + [[str(d), str(c)] for d, c in events_by_day]
    else:
        day_data = [["Date", "Event Count"], ["No data for this period", "—"]]
    story.append(_make_table(day_data, [half_page, half_page]))
    story.append(Spacer(1, 0.2 * inch))

    # ── Top Event Types ───────────────────────────────────────────────────────
    story.append(Paragraph("Top Event Types", styles["heading"]))
    top_types = events_by_type[:10]
    if top_types:
        type_data = [["Event Type", "Count"]] + [[name, str(count)] for name, count in top_types]
    else:
        type_data = [["Event Type", "Count"], ["No data for this period", "—"]]
    type_table = Table(
        type_data,
        colWidths=[letter[0] - 1.5 * inch - 2.5 * inch, 2.5 * inch],
    )
    type_table.setStyle(TableStyle(_DEFAULT_TABLE_STYLE + [("ALIGN", (1, 0), (1, -1), "CENTER")]))
    story.append(type_table)

    doc.build(story)


@celery_app.task(
    bind=True,
    name="generate_report",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def generate_report(self, report_id: str) -> None:
    logger.info(
        "Generating report PDF.",
        extra={"report_id": report_id, "task_id": self.request.id},
    )
    asyncio.run(_generate_report(UUID(report_id)))
    logger.info("Report PDF generation complete.", extra={"report_id": report_id})


async def _generate_report(report_id: UUID) -> None:
    async with AsyncSessionLocal() as session:
        report_repo = ReportRepository(session)
        dashboard_repo = DashboardRepository(session)
        analytics_repo = AnalyticsRepository(session)

        report = await report_repo.get_by_id(report_id)
        if report is None:
            logger.error("Report not found, skipping.", extra={"report_id": str(report_id)})
            return

        dashboard = await dashboard_repo.get_by_id(report.dashboard_id)
        dashboard_name = dashboard.name if dashboard else "Unknown Dashboard"

        period_start, period_end = _period_for_frequency(report.frequency)

        total_events = await analytics_repo.get_event_count(
            organization_id=report.organization_id,
            start_date=period_start,
            end_date=period_end,
        )

        from sqlalchemy import func, select

        from src.models.event import Event

        error_stmt = (
            select(func.count())
            .select_from(Event)
            .where(
                Event.organization_id == report.organization_id,
                Event.event_timestamp >= period_start,
                Event.event_timestamp <= period_end,
                Event.event_name.ilike("%error%"),
            )
        )
        error_events: int = (await session.execute(error_stmt)).scalar_one()

        events_by_day = await analytics_repo.get_events_by_day(
            organization_id=report.organization_id,
            start_date=period_start,
            end_date=period_end,
        )
        events_by_type = await analytics_repo.get_events_by_type(
            organization_id=report.organization_id,
            start_date=period_start,
            end_date=period_end,
        )

        reports_dir = Path(settings.reports_dir) / str(report.organization_id)
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = period_end.strftime("%Y%m%d_%H%M%S")
        output_path = str(reports_dir / f"{report_id}_{timestamp}.pdf")

        _build_pdf(
            output_path=output_path,
            report_name=report.name,
            dashboard_name=dashboard_name,
            frequency=report.frequency,
            period_start=period_start,
            period_end=period_end,
            total_events=total_events,
            error_events=error_events,
            events_by_day=events_by_day,
            events_by_type=events_by_type,
        )

        await report_repo.update_generation_result(
            report_id=report_id,
            file_path=output_path,
            last_generated_at=period_end,
        )
        await session.commit()

        logger.info(
            "Report saved.",
            extra={"report_id": str(report_id), "path": output_path},
        )


@celery_app.task(
    bind=True,
    name="dispatch_scheduled_reports",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def dispatch_scheduled_reports(self, frequency: str) -> None:
    logger.info(
        "Dispatching scheduled reports.",
        extra={"frequency": frequency, "task_id": self.request.id},
    )
    asyncio.run(_dispatch_scheduled_reports(ReportFrequency(frequency)))


async def _dispatch_scheduled_reports(frequency: ReportFrequency) -> None:
    async with AsyncSessionLocal() as session:
        report_repo = ReportRepository(session)
        reports = await report_repo.list_by_frequency(frequency)
        logger.info(
            "Reports dispatched.",
            extra={"frequency": frequency.value, "count": len(reports)},
        )
        for report in reports:
            generate_report.delay(str(report.id))
