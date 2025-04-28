import logging
import traceback
from datetime import datetime
from typing import List, Tuple

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.models.logistic import Section, Route, Stop, Tpu, Chart, Timetable
from src.schemas.coord import Coord
from src.schemas.navigation import RouteSimple, RouteReport


class NavigationService:
    @staticmethod
    async def create_routes(from_id: int, to_id: int, current_time: datetime, session: AsyncSession) -> RouteReport:
        """
        Построение всех маршрутах по заданным начальным и конечным остановкам
        :param from_id: айди 1 остановки
        :param to_id: айди последней остановки
        :param session: сессия БД
        :return:
        """
        try:
            stop_from = await session.get(Stop, from_id)
            tpu_from = await session.get(Tpu, stop_from.tpu_id)
            stops_from = []
            if tpu_from:
                stmt = select(Stop).where(Stop.tpu_id == tpu_from.id)
                results = await session.execute(stmt)
                for row in results:
                    stops_from.append(row[0].id)
            else:
                stops_from.append(from_id)

            stop_to = await session.get(Stop, to_id)
            tpu_to = await session.get(Tpu, stop_to.tpu_id)
            stops_to = []
            if tpu_to:
                stmt = select(Stop).where(Stop.tpu_id == tpu_to.id)
                results = await session.execute(stmt)
                for row in results:
                    stops_to.append(row[0].id)
            else:
                stops_to.append(to_id)

            fact_time = current_time.hour * 60 + current_time.minute

            simple_routes = await NavigationService().create_simple_routes(stops_from, stops_to, fact_time, session)
            count = len(simple_routes)
            if count:
                result = 200
            else:
                result = 0
            route_report = RouteReport(result=result, count=count, simple_routes=simple_routes)
            return route_report
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def create_simple_routes(stops_from: List[int], stops_to: List[int], fact_time: int,
                                   session: AsyncSession) -> List[RouteSimple]:
        """
        Построение беспересадочных маршрутов
        :param from_id: айди 1 остановки
        :param to_id: айди последней остановки
        :param session: сессия БД
        :return:
        """
        s1 = aliased(Section)
        s2 = aliased(Section)
        stop_table = aliased(Stop)
        chart_table = aliased(Chart)

        stmt = select(s1, s2).join(s2, s1.route_id == s2.route_id).where(
            s1.stop_id.in_(stops_from), s2.stop_id.in_(stops_to), s1.order < s2.order).order_by(s1.route_id)

        result = await session.execute(stmt)
        results = result.fetchall()

        routes_df = pd.DataFrame(
            {'route': [], 'home': [], 'end': [], 'load': [], 'time_label': [], 'time_begin': [], 'time_road': [],
             'full_time': []})

        for row in results:
            section1, section2 = row
            route = await session.get(Route, section1.route_id)
            routes_df.loc[len(routes_df)] = [route, section1.order, section2.order, None, 'Нет отправлений', '-', '-',
                                             None]

        for i, row_df in routes_df.iterrows():
            route, home, end, load, t1, t2, t3, t4 = row_df
            max_load, time_coef = await NavigationService().analize_sections(route.id, home, end, session)
            routes_df.iloc[i, 3] = max_load
            full_time_coef = await NavigationService().full_time_coeff(route.id, session)
            before_time_coef = await NavigationService().before_time_coeff(route.id, home, session)
            stmt = select(Timetable).where(Timetable.route_id == route.id).order_by(Timetable.start)
            result = await session.execute(stmt)
            results = result.fetchall()
            timetable_start, timetable_trip, timetable_full = None, None, None
            for row in results:
                timetable = row[0]
                start = timetable.start.hour * 60 + timetable.start.minute
                lap = timetable.lap.hour * 60 + timetable.lap.minute
                begin = start + lap * before_time_coef / full_time_coef
                if (begin >= fact_time):
                    timetable_start = begin
                    timetable_trip = lap * time_coef / full_time_coef
                    timetable_full = begin - fact_time + timetable_trip
                    break
            vehicles_start, vehicles_trip, vehicles_full = None, None, None

            if timetable_full is None and vehicles_full is None:
                pass
            if timetable_full is not None and vehicles_full is None:
                routes_df.iloc[i, 4] = 'По графику'
                routes_df.iloc[i, 5] = f'в {int(timetable_start // 60):02}:{int(timetable_start % 60):02}'
                routes_df.iloc[i, 6] = f'{int(timetable_trip // 60):02}:{int(timetable_trip % 60):02}'
                routes_df.iloc[i, 7] = timetable_full
            if timetable_full is None and vehicles_full is not None:
                pass
            if timetable_full is not None and vehicles_full is not None:
                pass

        #print(routes_df)
        routes_df = routes_df.sort_values(by='load')

        simple_routes = []
        for _, row_df in routes_df.iterrows():
            route, home, end, load, time_label, time_begin, time_road, t4 = row_df
            stmt = (select(s1, stop_table, chart_table)
                    .join(stop_table, stop_table.id == s1.stop_id)
                    .join(chart_table, chart_table.id == s1.chart_id, isouter=True)
                    .where(s1.order >= home, s1.order <= end, s1.route_id == route.id)
                    .order_by(s1.order))
            result = await session.execute(stmt)
            results = result.fetchall()
            stops = []
            for row in results:
                section, stop, chart = row
                stops.append(Coord(lat=stop.lat, lon=stop.lon))
                if chart and section.order < end:
                    for i in range(min(len(chart.lats), len(chart.lons))):
                        stops.append(Coord(lat=chart.lats[i], lon=chart.lons[i]))
            simple_routes.append(
                RouteSimple(label=route.label, number=route.number, long='25 мин', load=load, stops=stops,
                            time_label=time_label, time_begin=time_begin, time_road=time_road))
            # route = await session.get(Route, section.route_id)
            # routes.append(route)
        return simple_routes

    @staticmethod
    async def analize_sections(route_id: int, home: int, end: int, session: AsyncSession) -> Tuple[int, float]:
        """
        Вычисление загруженности промежутка маршрута
        :param route_id: айди маршрутка
        :param home: 1 остановка по ходу движения
        :param end: последння остановка по ходу движения
        :param session: сессия БД
        :return:
        """
        stmt = select(
            func.max(Section.load).label('max_load'),
            func.sum(Section.coef).label('time_coef'),
        ).where(Section.route_id == route_id, Section.order >= home, Section.order < end)
        result = await session.execute(stmt)
        values = result.one()
        max_load = values[0]
        time_coef = values[1]
        return max_load, time_coef

    @staticmethod
    async def full_time_coeff(route_id: int, session: AsyncSession) -> float:
        """
        Вычисление загруженности промежутка маршрута
        :param route_id: айди маршрутка
        :param home: 1 остановка по ходу движения
        :param end: последння остановка по ходу движения
        :param session: сессия БД
        :return:
        """
        stmt = select(
            func.sum(Section.coef).label('full_time'),
        ).where(Section.route_id == route_id)
        result = await session.execute(stmt)
        values = result.one()
        full_time = values[0]
        return full_time

    @staticmethod
    async def before_time_coeff(route_id: int, home: int, session: AsyncSession) -> float:
        """
        Вычисление загруженности промежутка маршрута
        :param route_id: айди маршрутка
        :param home: 1 остановка по ходу движения
        :param end: последння остановка по ходу движения
        :param session: сессия БД
        :return:
        """
        stmt = select(
            func.sum(Section.coef).label('time_coef'),
        ).where(Section.route_id == route_id, Section.order < home)
        result = await session.execute(stmt)
        values = result.one()
        time_coef = values[0]
        if time_coef is None:
            return 0.0
        return time_coef
