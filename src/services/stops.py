import logging
import traceback
from typing import List, Type, Optional

from fastapi import HTTPException
from geopy.distance import geodesic
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.models.logistic import Stop, Tpu
from src.models.users import Log, UserStopLikes
from src.schemas.coord import Coord
from src.schemas.stop import StopModel, StopUpd, StopInput
from src.utils.security import decode_token


class StopService:
    @staticmethod
    async def get_all_stops(session: AsyncSession, token: Optional[str]) -> List[StopModel]:
        """
        Выбирает из БД все остановки в виде JSON-схем
        :param token: авторизационный токен пользователя
        :param session: сессия БД
        :return: список остановок
        """
        try:
            user_id = None
            if token:
                try:
                    payload = decode_token(token)
                    user_id = payload["sub"]
                except Exception as exc:
                    msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
                    print(msg)

            liked = set()
            if user_id:
                result = await session.execute(select(UserStopLikes).where(UserStopLikes.user_id == user_id))
                for stop in result.scalars().all():
                    liked.add(stop.stop_id)
            stops = []
            result = await session.execute(select(Stop).where(Stop.stage > 0))
            for stop in result.scalars().all():
                stops.append(
                    StopModel(id=stop.id, name=stop.name, about=stop.about,
                              coord=Coord(lat=stop.lat, lon=stop.lon), like=stop.id in liked))
            return stops
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def like_stop(session: AsyncSession, token: str, stop_id: int) -> StopModel:
        """
        Добавляет остановку в избранное
        :param stop: айди остановки
        :param token: Авторизационный токен пользователя
        :param session: Сессия БД
        :return: Модель обновленной остановки
        """
        try:
            payload = decode_token(token)
            user_id = payload["sub"]
            await session.execute(insert(UserStopLikes).values(user_id=user_id, stop_id=stop_id))
            await session.commit()
            stop = await session.get(Stop, stop_id)
            return StopModel(id=stop.id, name=stop.name, about=stop.about,
                             coord=Coord(lat=stop.lat, lon=stop.lon), like=True)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def dislike_stop(session: AsyncSession, token: str, stop_id: int) -> StopModel:
        """
        Удаляет остановку из избранного
        :param stop: айди остановки
        :param token: Авторизационный токен пользователя
        :param session: Сессия БД
        :return: Модель обновленной остановки
        """
        try:
            payload = decode_token(token)
            user_id = payload["sub"]
            await session.execute(delete(UserStopLikes).where(UserStopLikes.user_id==user_id,
            UserStopLikes.stop_id==stop_id))
            await session.commit()
            stop = await session.get(Stop, stop_id)
            return StopModel(id=stop.id, name=stop.name, about=stop.about,
                             coord=Coord(lat=stop.lat, lon=stop.lon), like=False)
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


    @staticmethod
    def delete_stop(id: int, db_session: Session, ip: str, user_id: str) -> None:
        """
        Удаляет модель АТП из базы данных.
        При этом его маршруты становятся неактивынми, но не удаляются
        :param id: айди удаляемого АТП
        :param db_session: сессия баз данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            stop = db_session.query(Stop).filter_by(id=id).one()
            db_session.delete(stop)

            log = Log(created_ip=ip,
                      level=5,
                      action='Удалил ООТ',
                      information=str(id),
                      user_id=user_id)
            db_session.add(log)

            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))