import logging
import traceback

from fastapi import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.models.users import Feedback, Log


class StatisticService:
    @staticmethod
    def show_feedbacks(db_session: Session):
        """
        Выбирает из БД модели всех отзывов
        :param db_session: сессия БД
        :return:
        """
        try:
            avg_mark = db_session.query(func.avg(Feedback.mark)).scalar()

            feedback_list = []
            feedbacks = db_session.query(Feedback).order_by(desc(Feedback.created_at)).all()
            for feedback in feedbacks:
                feedback_list.append(feedback)
            return feedback_list, avg_mark
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def delete_feedback(id: str, db_session: Session, ip: str, user_id: str) -> None:
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
            feedback = db_session.query(Feedback).filter_by(id=id).one()
            db_session.delete(feedback)

            log = Log(created_ip=ip,
                      level=5,
                      action='Удалил отзыв',
                      information=feedback.email + " " + str(feedback.mark) + " " + feedback.about,
                      user_id=user_id)
            db_session.add(log)

            db_session.commit()
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
