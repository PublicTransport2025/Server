import logging
import traceback
from datetime import date
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import insert, select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.models.users import Event, Log
from src.schemas.event import EventUpd, EventInput
from src.schemas.eventwrited import EventWrited
from src.utils.security import decode_token


class EventsService:
    @staticmethod
    async def write_event(session: AsyncSession, token: str, data: EventWrited):
        """
        Записывает в базу данных новый пользовательский отзыв
        :param data: содержание отзыва
        :param token: Авторизационный токен пользователя
        :param session: Сессия БД
        """
        payload = decode_token(token)
        user_id = payload["sub"]
        stmt = select(
            func.count(Event.id).label('user_count'),
        ).where(Event.user_id == user_id, Event.moderated == 0)
        result = await session.execute(stmt)
        values = result.one()
        user_count = values[0]
        if user_count > 3:
            raise HTTPException(400, detail="Не флудите")
        try:
            result = await session.execute(insert(Event).values(
                user_id=user_id,
                type=data.type,
                line=data.line,
                lat=data.lat,
                lon=data.lon).returning(Event.lat, Event.lon, Event.type, Event.line, Event.moderated, Event.user_id,
                                        Event.id))
            await session.commit()
            event = result.one()
            # print(event)
            return {'lat': event[0], 'lon': event[1], 'type': event[2], 'line': event[3],
                    'moderated': event[4], 'my': bool(str(event[5]) == user_id), 'id': event[6]}
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def show_events(db_session: Session):
        """
        Выбирает из БД модели всех остановок
        :param db_session: сессия БД
        :return:
        """
        try:
            events = db_session.query(Event).order_by(desc(Event.created_at)).all()
            return events
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def update_event(data: EventUpd, db_session: Session, ip: str, user_id: str) -> None:
        """
        Редактирует дорожное событие в базе данных
        :param data: модель ООТ
        :param db_session: сессия БД
        :param ip: айпи редактора
        :paran user_id: айди редактора
        """
        try:
            event = db_session.query(Event).filter_by(id=data.id).first()
            event.type = data.type
            event.line = data.line
            event.lat = data.lat
            event.lon = data.lon
            event.moderated = data.moderated
            log = Log(created_ip=ip,
                      level=5,
                      action='Отредактировал дорожное событие',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_event(id: str, db_session: Session, ip: str, user_id: str) -> None:
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
            event = db_session.query(Event).filter_by(id=id).one()
            db_session.delete(event)

            log = Log(created_ip=ip,
                      level=5,
                      action='Удалил орожное событие',
                      information=str(id),
                      user_id=user_id)
            db_session.add(log)

            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def add_event(data: EventInput, db_session: Session, ip: str, user_id: str) -> EventUpd:
        """
        Добавляет модель ООТ в базу данных
        :param data: модель ООТ
        :param db_session: сессия БД
        :param ip: айпи редактора
        :paran user_id: айди редактора
        """
        try:
            event = Event(user_id=user_id,
                          type=data.type,
                          line=data.line,
                          lat=data.lat,
                          lon=data.lon,
                          moderated=data.moderated)
            log = Log(created_ip=ip,
                      level=5,
                      action='Добавил дорожное событие',
                      information=str(data),
                      user_id=user_id)
            db_session.add(log)
            db_session.add(event)
            db_session.commit()
            return {"id": str(event.id), "type": event.type, "line": event.line, "lat": event.lat, "lon": event.lon}
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def get_all_events(session: AsyncSession, token: Optional[str]):
        """
        Выбирает из БД все дорожные события в виде JSON-схем
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

            events = []
            today = date.today()
            if user_id:
                result = await session.execute(
                    select(Event).filter(
                        (Event.moderated == 4)
                        | ((Event.moderated == 0) & (func.date(Event.created_at) == today) & (Event.user_id == user_id))
                        | ((Event.moderated == 2) & (func.date(Event.created_at) == today) & (Event.user_id == user_id))
                        | ((Event.moderated == 1) & (func.date(Event.created_at) == today))
                        | ((Event.moderated == 5) & (func.date(Event.created_at) == today))))
                for event in result.scalars().all():
                    events.append(
                        {'id': event.id, 'lat': event.lat, 'lon': event.lon, 'type': event.type, 'line': event.line,
                         'moderated': event.moderated, 'my': bool(str(event.user_id) == user_id)})
            else:
                result = await session.execute(
                    select(Event).filter(
                        (Event.moderated == 4)
                        | ((Event.moderated == 1) & (func.date(Event.created_at) == today))
                        | ((Event.moderated == 5) & (func.date(Event.created_at) == today))))
                for event in result.scalars().all():
                    events.append(
                        {'id': event.id, 'lat': event.lat, 'lon': event.lon, 'type': event.type, 'line': event.line,
                         'moderated': event.moderated, 'my': False})
            return events
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def clear_event(session: AsyncSession, token: str, event_id: str):
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
            event = await session.get(Event, event_id)
            if (str(event.user_id) == user_id and event.moderated < 2):
                event.moderated = 3
            await session.commit()
            return {'id': event.id, 'lat': event.lat, 'lon': event.lon, 'type': event.type, 'line': event.line,
                    'moderated': event.moderated, 'my': bool(str(event.user_id) == user_id)}
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    async def fix_event(session: AsyncSession, token: str, event_id: str):
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
            event = await session.get(Event, event_id)
            if (str(event.user_id) == user_id and event.moderated == 1):
                event.moderated = 5
            await session.commit()
            return {'id': event.id, 'lat': event.lat, 'lon': event.lon, 'type': event.type, 'line': event.line,
                    'moderated': event.moderated, 'my': bool(str(event.user_id) == user_id)}
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
