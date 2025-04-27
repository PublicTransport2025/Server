import logging
import traceback
from typing import List, Type

from fastapi import HTTPException
from geopy.distance import geodesic
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.models.logistic import Stop, Tpu
from src.models.users import Log
from src.schemas.coord import Coord
from src.schemas.stop import StopModel, StopUpd, StopInput


class StopService:
    @staticmethod
    async def get_all_stops(session: AsyncSession) -> List[StopModel]:
        """
        Выбирает из БД все остановки в виде JSON-схем
        :param session: сессия БД
        :return: список остановок
        """
        try:
            stops = []
            result = await session.execute(select(Stop).where(Stop.stage > 0))
            for stop in result.scalars().all():
                stops.append(
                    StopModel(id=stop.id, name=stop.name, about=stop.about, coord=Coord(lat=stop.lat, lon=stop.lon)))
            return stops
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def show_stops(db_session: Session) -> List[Type[Stop]]:
        """
        Выбирает из БД модели всех остановок
        :param db_session: сессия БД
        :return:
        """
        try:
            stops = db_session.query(Stop).order_by(Stop.id).all()
            return stops
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def update_stop(data: StopUpd, db_session: Session, ip: str, user_id: str) -> None:
        """
        Обновляет модель ООТ в базе данных
        :param data: модель ООТ
        :param db_session: сессия БД
        :param ip: айпи редактора
        :paran user_id: айди редактора
        """
        try:
            stop = db_session.query(Stop).filter_by(id=data.id).first()
            stop.name = data.name
            stop.about = data.about
            stop.lat = data.lat
            stop.lon = data.lon
            stop.stage = data.stage
            stop.tpu_id = data.tpu_id
            log = Log(created_ip=ip,
                      level=5,
                      action='Обновил ООТ',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def add_stop(data: StopInput, db_session: Session, ip: str, user_id: str) -> StopUpd:
        """
        Добавляет модель ООТ в базу данных
        :param data: модель ООТ
        :param db_session: сессия БД
        :param ip: айпи редактора
        :paran user_id: айди редактора
        """
        try:
            stop = Stop(name=data.name,
                        about=data.about,
                        lat=data.lat,
                        lon=data.lon,
                        stage=data.stage,
                        tpu_id=data.tpu_id)
            log = Log(created_ip=ip,
                      level=5,
                      action='Добавил ООТ',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.add(stop)
            db_session.commit()
            return StopUpd(**stop.__dict__)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def reset_tpu(db_session: Session, ip: str, user_id: str) -> None:
        """
        Перераспределяет остановки между ТПУ
        :param db_session:
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            stops = db_session.query(Stop).order_by(Stop.id).all()
            for stop in stops:
                stop.tpu_id = None
            db_session.commit()

            tpus = db_session.query(Tpu).order_by(Tpu.id).all()
            for tpu in tpus:
                db_session.delete(tpu)
            db_session.commit()


            stops = db_session.query(Stop).order_by(Stop.id).all()
            for i in range(len(stops)):
                if stops[i].tpu is None:
                    point1 = (stops[i].lat, stops[i].lon)
                    tpu = Tpu(id=stops[i].id, name=stops[i].name + str(stops[i].id))
                    stops[i].tpu = tpu
                    for j in range(i + 1, len(stops)):
                        if stops[j].tpu is None:
                            point2 = (stops[j].lat, stops[j].lon)
                            distance = geodesic(point1, point2).m
                            if distance < 200:
                                stops[j].tpu = tpu
            log = Log(created_ip=ip,
                      level=5,
                      action='Пересчитал ТПУ',
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
