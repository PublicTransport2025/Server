import logging
import traceback
from typing import List

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.models.logistic import Section, Route, Stop, Tpu
from src.schemas.coord import Coord
from src.schemas.navigation import RouteSimple, RouteReport


class NavigationService:
    @staticmethod
    async def create_routes(from_id: int, to_id: int, session: AsyncSession) -> RouteReport:
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



            simple_routes = await NavigationService().create_simple_routes(stops_from, stops_to, session)
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
    async def create_simple_routes(stops_from: List[int], stops_to: List[int], session: AsyncSession) -> List[RouteSimple]:
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

        stmt = select(s1, s2).join(s2, s1.route_id == s2.route_id).where(
            s1.stop_id.in_(stops_from), s2.stop_id.in_(stops_to), s1.order < s2.order).order_by(s1.route_id)

        result = await session.execute(stmt)
        results = result.fetchall()

        routes_df = pd.DataFrame({'route': [], 'home': [], 'end': [], 'load': []})

        for row in results:
            section1, section2 = row
            route = await session.get(Route, section1.route_id)
            routes_df.loc[len(routes_df)] = [route, section1.order, section2.order, None]

        for i, row_df in routes_df.iterrows():
            route, home, end, load = row_df
            max_load = await NavigationService().calc_load(route.id, home, end, session)
            routes_df.iloc[i, 3] = max_load

        print(routes_df)
        routes_df = routes_df.sort_values(by='load')

        simple_routes = []
        for _, row_df in routes_df.iterrows():
            route, home, end, load = row_df
            stmt = select(s1, stop_table).join(stop_table, stop_table.id == s1.stop_id).where(
                s1.order >= home, s1.order <= end, s1.route_id == route.id).order_by(s1.order)
            result = await session.execute(stmt)
            results = result.fetchall()
            stops = []
            for row in results:
                section, stop = row
                stops.append(Coord(lat=stop.lat, lon=stop.lon))
            simple_routes.append(
                RouteSimple(label=route.label, number=route.number, long='25 мин', load=load, stops=stops))
            # route = await session.get(Route, section.route_id)
            # routes.append(route)
        return simple_routes

    @staticmethod
    async def calc_load(route_id: int, home: int, end: int, session: AsyncSession) -> int:
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
        ).where(Section.route_id == route_id, Section.order >= home, Section.order < end)
        result = await session.execute(stmt)
        max_load = result.one()[0]
        return max_load
