from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.stops import Stop
from src.schemas.coord import Coord
from src.schemas.stop import StopSchema


class StopService:
    @staticmethod
    async def get_all_stops(session: AsyncSession) -> List[StopSchema]:
        """
        Выбирает из БД все остановки
        :param session: сессия БД
        :return: список остановок
        """
        stops = []
        result = await session.execute(select(Stop))
        for stop in result.scalars().all():
            stops.append(StopSchema(id=stop.id, name=stop.name, coord=Coord(lat=stop.lat, lon=stop.lon)))
        return stops
