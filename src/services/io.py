import io
import logging
import traceback
import uuid

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.models.users import Log


class IOService:
    """
    Сервис обработки импорта и экспорта данных
    """
    @staticmethod
    def upload_table(contents: bytes, source: str, db_session: Session, ip: str, user_id: str) -> int:
        """
        Записывает загруженный ксв-файл в базу данных
        :param contents: биты загруженного файла
        :param source: название таблицы
        :param db_session: сессия БД
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return: количество записанных строк
        """
        try:
            number = source + str(uuid.uuid4()) + '.csv'
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')), sep=';')
            df.to_csv('io/' + number, sep=';', quoting=1, index=False)
            log = Log(created_ip=ip,
                      level=10,
                      action='Загрузил таблицу',
                      information=str(number),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
            db_session.execute(text(f'TRUNCATE TABLE {source} RESTART IDENTITY CASCADE'))
            db_session.commit()
            with db_session.connection() as conn:
                df.to_sql(source, conn, if_exists="append", method='multi', chunksize=1000, index=False)
                if source != 'sections':
                    conn.execute(text(f"SELECT setval('{source}_seq', (SELECT COALESCE(MAX(id), 0) FROM {source}));"))
                conn.commit()
            return len(df)
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))

    @staticmethod
    def download_table(source: str, db_session: Session, ip: str, user_id: str) -> StreamingResponse:
        """
        Возвращает поток с ксв-файлом из БД
        :param source: название таблицы
        :param db_session: сессия БД
        :param ip: айпи редактора
        :param user_id: айди редактора
        :return: Поток
        """
        try:
            log = Log(created_ip=ip,
                      level=3,
                      action='Скачал таблицу',
                      information=str(source),
                      user_id=user_id)
            db_session.add(log)
            db_session.commit()
            with db_session.connection() as conn:
                df = pd.read_sql(source, conn)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, sep=';', quoting=1, index=False)
            csv_buffer.seek(0)
            return StreamingResponse(io.BytesIO(csv_buffer.getvalue().encode()), media_type="text/csv",
                                     headers={"Content-Disposition": f"attachment; filename={source}.csv"})
        except Exception as exc:
            msg = '\n'.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            logging.error(msg)
            raise HTTPException(500, str(exc))
