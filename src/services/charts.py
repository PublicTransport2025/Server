import logging
import traceback

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.logistic import Chart
from src.models.users import Log
from src.schemas.charts import ChartInput, ChartUpd


class ChartService:

    @staticmethod
    def add_chart(data: ChartInput, db_session: Session, ip: str, user_id: str) -> None:
        """
        Вставляет новую схему движения в БД
        :param data: модель новой схемы движения
        :param db_session: сессия базы данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        """
        try:
            label = data.title_str

            lats_str = data.lats_str.split()
            lats = []
            for lat in lats_str:
                lats.append(float(lat))

            lons_str = data.lons_str.split()
            lons = []
            for lon in lons_str:
                lons.append(float(lon))

            chart = Chart(label=label, lats=lats, lons=lons)
            db_session.add(chart)

            log = Log(created_ip=ip,
                      level=5,
                      action='Добавил схему движения',
                      information=str(data),
                      user_id=user_id)

            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def update_chart(data: ChartUpd, db_session: Session, ip: str, user_id: str) -> None:
        """
        Обновляет схему движения в БД
        :param data: модель новой схемы движения
        :param db_session: сессия базы данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        """
        try:
            label = data.title_str

            lats_str = data.lats_str.split()
            lats = []
            for lat in lats_str:
                lats.append(float(lat))

            lons_str = data.lons_str.split()
            lons = []
            for lon in lons_str:
                lons.append(float(lon))

            chart = db_session.query(Chart).filter_by(id=data.id).first()
            chart.label = label
            chart.lats = lats
            chart.lons = lons

            log = Log(created_ip=ip,
                      level=5,
                      action='Обновил схему движения',
                      information=str(data.id) + " " + str(data),
                      user_id=user_id)

            db_session.add(log)
            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_chart(id: int, db_session: Session, ip: str, user_id: str) -> None:
        """
        Удаляет модель схемы движения из базы данных.
        При этом его маршруты становятся неактивынми, но не удаляются
        :param id: айди удаляемого АТП
        :param db_session: сессия баз данных
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return:
        """
        try:
            chart = db_session.query(Chart).filter_by(id=id).one()
            db_session.delete(chart)

            log = Log(created_ip=ip,
                      level=5,
                      action='Удалил схему движения',
                      information=str(id),
                      user_id=user_id)
            db_session.add(log)

            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
