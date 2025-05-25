from pydantic import BaseModel


class ChartInput(BaseModel):
    title_str: str
    lats_str: str
    lons_str: str

class ChartUpd(ChartInput):
    id: str