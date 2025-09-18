from typing import List, Optional, Literal, Union
from pydantic import BaseModel, Field

TableCell = Union[str, int, float, bool, None]

class KVPoint(BaseModel):
    label: str
    value: float

class XYPoint(BaseModel):
    x: float
    y: float
    label: Optional[str] = None

class PieResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["pie"]
    data: List[KVPoint]
    text_summary: str

class BarResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["bar"]
    data: List[KVPoint]
    text_summary: str

class LineResult(BaseModel):
    type: Literal["chart"]
    chartType: Literal["line"]
    data: List[KVPoint]
    text_summary: str

class TableResult(BaseModel):
    type: Literal["table"]
    headers: List[str]
    rows: List[List[TableCell]]
    text_summary: str


ChartOrTableResult = Union[PieResult, BarResult, LineResult, TableResult]

class VisualizationRouter(BaseModel):
    visualization: ChartOrTableResult = Field(..., description="The single chart or table object to be rendered.")
