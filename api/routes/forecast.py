from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.demand.baseline import SeasonalMean
router=APIRouter(prefix='/forecast',tags=['forecast'])
class ForecastRequest(BaseModel): values:list[float]; horizon:int=1
def forecast(request: ForecastRequest):
    model=SeasonalMean().fit(request.values)
    return {'model':'seasonal_mean','values':model.predict(request.horizon)}
router.add_api_route('/demand', forecast, methods=['POST'])
