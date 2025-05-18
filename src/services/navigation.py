import logging
import traceback
from datetime import datetime
from typing import List, Tuple, Dict

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from src.models.logistic import Section, Route, Stop, Tpu, Chart, Timetable
from src.schemas.coord import Coord
from src.schemas.navigation import RouteSimple, RouteReport, RouteDouble


class NavigationService:
    @staticmethod
    async def create_routes(from_id: int, to_id: int, care: bool, change: bool, priority: int, current_time: datetime,
                            session: AsyncSession) -> RouteReport:
        """
        Построение всех маршрутах по заданным начальным и конечным остановкам
        :param from_id: начальная остановка
        :param to_id: конечная остановка
        :param care: только низкопольный пс?
        :param change: делать ли пересадки?
        :param priority: приоритет: 0 - загруженность, 1 - время, 2 - баланс
        :param current_time: время отправления от начальной остановки
        :param session: сессия БД
        :return: json-модель маршрута
        """
        try:
            # Определение списка соседних остановок от точки отправления
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

            # Определение списка соседних остановок от точки прибытия
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

            # Перевод времени отправления в минуты
            fact_time = current_time.hour * 60 + current_time.minute

            # Построение беспересадочных маршрутов
            simple_routes, rb = await NavigationService().create_simple_routes(stops_from, stops_to, care, priority,
                                                                               fact_time, session)

            # Построение маршрутов с пересадками
            double_routes = []
            if not change:
                double_routes = await NavigationService().create_double_routes(stops_from, stops_to, care, priority,
                                                                               rb, fact_time, session)

            # Формирование отчета
            count = len(simple_routes) + len(double_routes)
            count_simple = len(simple_routes)
            if count:
                result = 200
            else:
                result = 0
            route_report = RouteReport(result=result, count=count, count_simple=count_simple,
                                       simple_routes=simple_routes, double_routes=double_routes)
            return route_report
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def check_timetables(route_id: int, fact_time: int, before_time_coef: float, time_coef: float,
                               full_time_coef: float, session: AsyncSession) -> Tuple[int, int, int]:
        stmt = select(Timetable).where(Timetable.route_id == route_id).order_by(Timetable.start)
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
        return timetable_start, timetable_trip, timetable_full

    @staticmethod
    async def create_simple_routes(stops_from: List[int], stops_to: List[int], care: bool, priority: int,
                                   fact_time: int, session: AsyncSession) -> Tuple[List[RouteSimple], Dict[Route, int]]:
        """
        Построение беспересадочных маршрутов
        :param from_id: айди 1 остановки
        :param to_id: айди последней остановки
        :param session: сессия БД
        :return:
        """

        # Создание псевдонимов таблиц
        s1 = aliased(Section)
        s2 = aliased(Section)
        stop_table = aliased(Stop)
        chart_table = aliased(Chart)

        # Запрос выбора маршрута из БД
        stmt = (select(s1, s2)
                .join(s2, s1.route_id == s2.route_id)
                .where(s1.stop_id.in_(stops_from), s2.stop_id.in_(stops_to), s1.order < s2.order)
                .order_by(s1.route_id))
        result = await session.execute(stmt)
        results = result.fetchall()

        # Датасет маршрутов
        routes_df = pd.DataFrame(
            {'route': [], 'home': [], 'end': [], 'long': [], 'load': [], 'time_label': [], 'time_begin': [],
             'time_road': [],
             'full_time': [], 'weight_time': []})

        # Выбор маршрутов из БД
        for row in results:
            section1, section2 = row
            route = await session.get(Route, section1.route_id)
            if route.stage != 1:
                continue
            if care and not route.care:
                continue
            routes_df.loc[len(routes_df)] = [route, section1.order, section2.order, section2.order - section1.order, 9,
                                             'Нет отправлений', '-', '-',
                                             9999, 9999]

        # Уточнение маршрутов
        for i, row_df in routes_df.iterrows():
            route, home, end, long, load, t1, t2, t3, t4, t5 = row_df

            # Оценка загруженности
            max_load, time_coef = await NavigationService().analize_sections(route.id, home, end, session)
            routes_df.iloc[i, 4] = max_load

            # Оценка времени
            full_time_coef = await NavigationService().full_time_coeff(route.id, session)
            before_time_coef = await NavigationService().before_time_coeff(route.id, home, session)

            # Оценка времени по графику
            timetable_start, timetable_trip, timetable_full \
                = await NavigationService().check_timetables(route.id, fact_time, before_time_coef, time_coef,
                                                             full_time_coef, session)
            vehicles_start, vehicles_trip, vehicles_full = None, None, None

            # Поиск наиболее быстрого выремени
            if timetable_full and vehicles_full:
                pass
            elif timetable_full:
                routes_df.iloc[i, 5] = 'По графику'
                routes_df.iloc[i, 6] = f'в {int(timetable_start // 60):02}:{int(timetable_start % 60):02}'
                routes_df.iloc[i, 7] = f'{int(timetable_trip // 60):02}:{int(timetable_trip % 60):02}'
                routes_df.iloc[i, 8] = int(timetable_full)
                routes_df.iloc[i, 9] = int(timetable_full - timetable_trip + (1 + 1 * max_load) * timetable_trip)
            elif vehicles_full:
                pass

        # Сортировка датасета маршрутов
        if priority == 0:  # По загруженности
            routes_df = routes_df.sort_values(by=['load', 'full_time', 'long'])
        elif priority == 1:  # По времени
            routes_df = routes_df.sort_values(by=['full_time', 'load', 'long'])
        else:  # По взвешенному времени (баланс)
            routes_df = routes_df.sort_values(by=['weight_time', 'load', 'long'])

        # Ограничение поиска
        routes_df.drop_duplicates(subset=['route'], keep='first', inplace=True, ignore_index=True)
        # routes_df = routes_df.head(5)

        routes_df['route_id'] = [routes_df.iloc[i, 0].id for i in range(len(routes_df))]
        # Определение брифа беспересадочных маршрутов
        routes_brief = routes_df.set_index('route_id')['long']
        print(routes_brief)

        # Подготовка json-ответа
        simple_routes = []
        for _, row_df in routes_df.iterrows():
            route, home, end, long, load, time_label, time_begin, time_road, t4, t5, rid = row_df
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
                RouteSimple(label=route.label, number=route.number, load=load, stops=stops,
                            time_label=time_label, time_begin=time_begin, time_road=time_road))
            # route = await session.get(Route, section.route_id)
            # routes.append(route)
        return simple_routes, routes_brief

    @staticmethod
    async def create_double_routes(stops_from: List[int], stops_to: List[int], care: bool, priority: int,
                                   rb, fact_time: int, session: AsyncSession) -> List[RouteDouble]:
        s1 = aliased(Section)
        s2 = aliased(Section)

        s3 = aliased(Section)
        s4 = aliased(Section)

        stop1 = aliased(Stop)
        stop2 = aliased(Stop)

        stop_table = aliased(Stop)
        chart_table = aliased(Chart)

        # 140 943 Брно-73

        stmt = (select(s1, s2, stop1, stop2, s3, s4)
                .join(s2, s1.route_id == s2.route_id)
                .join(stop1, s2.stop_id == stop1.id)
                .join(stop2, stop1.tpu_id == stop2.tpu_id)
                .join(s3, stop2.id == s3.stop_id)
                .join(s4, s3.route_id == s4.route_id)
                .where(s1.stop_id.in_(stops_from), s4.stop_id.in_(stops_to), s2.route_id != s3.route_id,
                       s1.order < s2.order, s3.order < s4.order)
                .order_by(s1.route_id, s3.route_id))

        result = await session.execute(stmt)
        results = result.fetchall()

        double_routes_df = pd.DataFrame(
            {'route1': [], 'home1': [], 'end1': [], 'long1': [], 'load1': [],
             'time_label1': [], 'time_begin1': [], 'time_road1': [], 'stop1': [],
             'route2': [], 'home2': [], 'end2': [], 'long2': [], 'load2': [],
             'time_label2': [], 'time_begin2': [], 'time_road2': [], 'stop2': [],
             'full_time': [], 'weight_time': [], 'max_load': []})

        for row in results:
            section1, section2, stop_1, stop_2, section3, section4 = row
            route1 = await session.get(Route, section1.route_id)
            route2 = await session.get(Route, section3.route_id)
            if route1.stage != 1 or route2.stage != 1:
                continue
            if care and (not route1.care or not route2.care):
                continue
            double_routes_df.loc[len(double_routes_df)] = \
                [route1, section1.order, section2.order, section2.order - section1.order, 9, 'Нет отправлений', 'None',
                 'None', stop_1.name,
                 route2, section3.order, section4.order, section4.order - section3.order, 9, 'Нет отправлений', 'None',
                 'None', stop_2.name,
                 99999, 9999, 9]

        for i, row_df in double_routes_df.iterrows():
            route1, home1, end1, long1, load1, time_label1, time_begin1, time_road1, stop1, \
                route2, home2, end2, long2, load2, time_label2, time_begin2, time_road2, stop2, tt, ll, ww = row_df

            # Оценка загруженности 1 и 2 маршртуа
            max_load1, time_coef1 = \
                await NavigationService().analize_sections(route1.id, home1, end1, session)
            double_routes_df.iloc[i, 4] = max_load1
            max_load2, time_coef2 = \
                await NavigationService().analize_sections(route2.id, home2, end2, session)
            double_routes_df.iloc[i, 13] = max_load2
            double_routes_df.iloc[i, 20] = max(max_load1, max_load2)

            # Оценка времени 1 маршртуа
            full_time_coef1 = await NavigationService().full_time_coeff(route1.id, session)
            before_time_coef1 = await NavigationService().before_time_coeff(route1.id, home1, session)

            # Оценка времени по графику 1 маршрута
            timetable_start1, timetable_trip1, timetable_full1 \
                = await NavigationService().check_timetables(route1.id, fact_time, before_time_coef1, time_coef1,
                                                             full_time_coef1, session)
            vehicles_start1, vehicles_trip1, vehicles_full1, real1 = None, None, None, None

            # Поиск наиболее быстрого выремени 1 маршрута
            if timetable_full1 and vehicles_full1:
                pass
            elif timetable_full1:
                double_routes_df.iloc[i, 5] = 'По графику'
                double_routes_df.iloc[i, 6] = f'в {int(timetable_start1 // 60):02}:{int(timetable_start1 % 60):02}'
                double_routes_df.iloc[i, 7] = f'{int(timetable_trip1 // 60):02}:{int(timetable_trip1 % 60):02}'
                real1 = timetable_full1
            elif vehicles_full1:
                pass

            if real1:
                # Оценка времени 2 маршртуа
                full_time_coef2 = await NavigationService().full_time_coeff(route2.id, session)
                before_time_coef2 = await NavigationService().before_time_coeff(route2.id, home2, session)

                # Оценка времени по графику 2 маршрута
                timetable_start2, timetable_trip2, timetable_full2 \
                    = await NavigationService().check_timetables(route2.id, fact_time + real1 + 5, before_time_coef2, time_coef2,
                                                                 full_time_coef2, session)
                vehicles_start2, vehicles_trip2, vehicles_full2 = None, None, None

                # Поиск наиболее быстрого выремени 2 маршрута
                if timetable_full2 and vehicles_full2:
                    pass
                elif timetable_full2:
                    double_routes_df.iloc[i, 14] = 'По графику'
                    double_routes_df.iloc[i, 15] = f'в {int(timetable_start2 // 60):02}:{int(timetable_start2 % 60):02}'
                    double_routes_df.iloc[i, 16] = f'{int(timetable_trip2 // 60):02}:{int(timetable_trip2 % 60):02}'
                    double_routes_df.iloc[i, 18] = int(timetable_full2)
                    double_routes_df.iloc[i, 19] = int(timetable_full2 - timetable_trip2 + (1 + 1 * max_load2) * timetable_trip2)
                elif vehicles_full2:
                    pass


        # Сортировка датасета маршрутов
        if priority == 0:  # По загруженности
            double_routes_df = double_routes_df.sort_values(
                by=['max_load', 'load1', 'load2', 'long1', 'long2', 'full_time'])
        elif priority == 1:  # По времени
            double_routes_df = double_routes_df.sort_values(
                by=['full_time', 'max_load', 'load1', 'load2', 'long1', 'long2'])
        else:  # По взвешенному времени (баланс)
            double_routes_df = double_routes_df.sort_values(
                by=['weight_time', 'max_load', 'load1', 'load2', 'long1', 'long2'])

        # Ограничение поиска
        double_routes_df.drop_duplicates(subset=['route1', 'route2'], keep='first', inplace=True, ignore_index=True)

        def should_drop(row):
            key = row['route1'].id
            val_b = row['long1']
            if key in rb:
                val_a = rb[key]
                if val_b > val_a:
                    return True
            key = row['route2'].id
            val_b = row['long2']
            if key in rb:
                val_a = rb[key]
                if val_b > val_a:
                    return True
            return False

        double_routes_df = double_routes_df[~double_routes_df.apply(should_drop, axis=1)].reset_index(drop=True)

        double_routes_df = double_routes_df.head(5)

        double_routes = []
        for i, row_df in double_routes_df.iterrows():
            route1, home1, end1, long1, load1, time_label1, time_begin1, time_road1, stop1, \
                route2, home2, end2, long2, load2, time_label2, time_begin2, time_road2, stop2, tt, ll, ww = row_df

            stmt = (select(s1, stop_table, chart_table)
                    .join(stop_table, stop_table.id == s1.stop_id)
                    .join(chart_table, chart_table.id == s1.chart_id, isouter=True)
                    .where(s1.order >= home1, s1.order <= end1, s1.route_id == route1.id)
                    .order_by(s1.order))
            result = await session.execute(stmt)
            results = result.fetchall()
            stops1 = []
            for row in results:
                section, stop, chart = row
                stops1.append(Coord(lat=stop.lat, lon=stop.lon))
                if chart and section.order < end1:
                    for i in range(min(len(chart.lats), len(chart.lons))):
                        stops1.append(Coord(lat=chart.lats[i], lon=chart.lons[i]))

            stmt = (select(s1, stop_table, chart_table)
                    .join(stop_table, stop_table.id == s1.stop_id)
                    .join(chart_table, chart_table.id == s1.chart_id, isouter=True)
                    .where(s1.order >= home2, s1.order <= end2, s1.route_id == route2.id)
                    .order_by(s1.order))
            result = await session.execute(stmt)
            results = result.fetchall()
            stops2 = []
            for row in results:
                section, stop, chart = row
                stops2.append(Coord(lat=stop.lat, lon=stop.lon))
                if chart and section.order < end2:
                    for i in range(min(len(chart.lats), len(chart.lons))):
                        stops2.append(Coord(lat=chart.lats[i], lon=chart.lons[i]))

            double_routes.append(
                RouteDouble(label1=route1.label, number1=route1.number, load1=load1, stops1=stops1, stop1=stop1,
                            time_label1=time_label1, time_begin1=time_begin1, time_road1=time_road1,
                            label2=route2.label, number2=route2.number, load2=load2, stops2=stops2, stop2=stop2,
                            time_label2=time_label2, time_begin2=time_begin2, time_road2=time_road2
                            ))
            # route = await session.get(Route, section.route_id)
            # routes.append(route)
        return double_routes

    @staticmethod
    async def analize_sections(route_id: int, home: int, end: int, session: AsyncSession) -> Tuple[int, float]:
        """
        Вычисление загруженности промежутка маршрута
        :param route_id: айди маршрута
        :param home: первая остановка по ходу маршрута
        :param end: последння остановка по ходу маршрута
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
