import logging
import traceback
from typing import Type, List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.logistic import Route, Section
from src.models.users import Log
from src.schemas.route import RouteModel, RouteInput, SectionsInput


class RouteService:
    @staticmethod
    def show_routes(db_session: Session) -> List[Type[Route]]:
        """
        Выбирает из БД модели всех маршрутов
        :param db_session: сессия БД
        :return:
        """
        try:
            routes = db_session.query(Route).order_by(Route.id).all()
            return routes
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def update_route(data: RouteModel, db_session: Session, ip: str, user_id: str) -> None:
        """
        Обновляет модель маршрута в базе данных
        :param data: модель маршрута
        :param db_session: сессия БД
        :param ip: айпи редактора
        :param user_id: айди редактора
        """
        try:
            route = db_session.query(Route).filter_by(id=data.id).first()
            route.number = data.number
            route.label = data.label
            route.title = data.title
            route.info = data.info
            route.stage = data.stage
            route.care = data.care
            route.atp_id = data.atp_id
            log = Log(created_ip=ip,
                      level=5,
                      action='Обновил маршрут',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def add_route(data: RouteInput, db_session: Session, ip: str, user_id: str) -> RouteModel:
        """
        Добавляет модель маршрута в базу данных
        :param data: модель маршрута
        :param db_session: сессия БД
        :param ip: айпи редактора
        :param user_id: айди редактора
        """
        try:
            route = Route(number=data.number,
                          label=data.label,
                          title=data.title,
                          info=data.info,
                          stage=data.stage,
                          care=data.care,
                          atp_id=data.atp_id
                          )
            log = Log(created_ip=ip,
                      level=5,
                      action='Добавил маршрут',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.add(route)
            db_session.commit()
            return RouteModel(**route.__dict__)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def edit_route(route_id: int, data: SectionsInput, db_session: Session, ip: str, user_id: str) -> None:
        """
        Редактирует остановки маршрута
        :param route_id: айди маршрута
        :param data: информация о маршруте
        :param db_session: сессия БД
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            sections_old = db_session.query(Section).filter_by(route_id=route_id).all()
            for old_section in sections_old:
                db_session.delete(old_section)

            sections = data.sections
            sections_to_input = []
            for i in range(len(sections)):
                sections_to_input.append(Section(stop_id=sections[i].stop_id,
                                                 route_id=route_id,
                                                 order=i,
                                                 coef=sections[i].coef,
                                                 stage=1,
                                                 load=sections[i].load,
                                                 chart_id=(sections[i].chart_id if sections[i].chart_id else None)))
            db_session.add_all(sections_to_input)
            log = Log(created_ip=ip,
                      level=3,
                      action='Отредактировал маршрут',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
