from datetime import timedelta, datetime

from fastapi import APIRouter
from geopy.distance import distance
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.core.db import db_async_client
from src.models.logistic import Route, Section, Stop, Chart, Timetable

codd_router = APIRouter(prefix="/codd", tags=["CODD"])


def time_to_timedelta(t):
    return timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)


@codd_router.get("/transport")
async def transport(route_id: int, session: AsyncSession = db_async_client):
    real_time = datetime.now()
    real_time = datetime(2026, 6, 2, 12, 00, 0, 0)
    fact_time = time_to_timedelta(real_time.time())

    s1 = aliased(Section)
    t1 = aliased(Timetable)
    stop_table = aliased(Stop)
    chart_table = aliased(Chart)

    route = await session.get(Route, route_id)
    full_length = 0.0

    stmt = (select(s1, stop_table, chart_table)
            .join(stop_table, stop_table.id == s1.stop_id)
            .join(chart_table, chart_table.id == s1.chart_id, isouter=True)
            .where(s1.route_id == route_id)
            .order_by(s1.order))
    result = await session.execute(stmt)
    results = result.fetchall()

    points = []
    # Массив точек маршрута: [0_Широта, 1_Долгота, 2_Навзвание остановки, 3_Длина участка, 4_Пройденный путь]
    lat1, lon1 = None, None

    for row in results:
        section, stop, chart = row
        lat2, lon2 = stop.lat, stop.lon
        if lat1 is None:
            lat1, lon1 = lat2, lon2
        distation = distance((lat1, lon1), (lat2, lon2)).meters
        full_length += distation
        points.append((lat2, lon2, stop.name, distation, full_length))
        lat1, lon1 = lat2, lon2
        if chart:
            for i in range(min(len(chart.lats), len(chart.lons))):
                lat2, lon2 = chart.lats[i], chart.lons[i]
                distation = distance((lat1, lon1), (lat2, lon2)).meters
                full_length += distation
                points.append((lat2, lon2, stop.name, distation, full_length))
                lat1, lon1 = lat2, lon2



    print(points)

    stmt = (select(t1).where(t1.route_id == route_id).order_by(t1.start))
    result = await session.execute(stmt)
    results = result.fetchall()
    vehicles = []

    for row in results:
        timetable = row[0]
        if time_to_timedelta(timetable.start) < fact_time < time_to_timedelta(timetable.start) + time_to_timedelta(
                timetable.lap):
            coef = (fact_time - time_to_timedelta(timetable.start)) / time_to_timedelta(timetable.lap)
            real_length = full_length * coef
            for i in range(len(points) - 1):
                if points[i][4] < real_length < points[i + 1][4]:
                    coef2 = (real_length - points[i][4]) / points[i + 1][3]
                    lat = points[i][0] + coef2 * (points[i + 1][0] - points[i][0])
                    lon = points[i][1] + coef2 * (points[i + 1][1] - points[i][1])
                    stop = points[i][2]
                    data = [
                        lat,
                        lon,
                        0,
                        real_time.isoformat(),
                        "B236PH236",
                        0,
                        0,
                        route.number,
                        0,
                        real_time.isoformat(),
                        stop,
                        None
                    ]
                    vehicles.append(data)
    return vehicles
