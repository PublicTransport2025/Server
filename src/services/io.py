import io

import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session


class IOService:
    """
    Сервис обработки импорта и экспорта данных
    """
    @staticmethod
    def upload_table(contents: bytes, source: str, db_session: Session) -> int:
        """
        Записывает загруженный ксв-файл в базу данных
        :param contents: биты загруженного файла
        :param source: название таблицы
        :param db_session: сессия БД
        :return: количество записанных строк
        """
        try:
            df = pd.read_csv(io.StringIO(contents.decode('utf-8')), sep=';')
            with db_session.connection() as conn:
                df.to_sql(source, conn, if_exists="replace", method='multi', chunksize=1000, index=False)
                conn.commit()
            return len(df)
        except Exception as exc:
            raise HTTPException(500, str(exc))

    @staticmethod
    def download_table(source: str, db_session: Session) -> StreamingResponse:
        """
        Возвращает поток с ксв-файлом из БД
        :param source: название таблицы
        :param db_session: сессия БД
        :return: Поток
        """
        try:
            with db_session.connection() as conn:
                df = pd.read_sql(source, conn)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, sep=';', quoting=1, index=False)
            csv_buffer.seek(0)
            return StreamingResponse(io.BytesIO(csv_buffer.getvalue().encode()), media_type="text/csv",
                                     headers={"Content-Disposition": f"attachment; filename={source}.csv"})
        except Exception as exc:
            raise HTTPException(500, str(exc))
