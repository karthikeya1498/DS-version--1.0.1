from fastapi import APIRouter
from pydantic import BaseModel
from src.ml.eta.baseline import MeanEta
router=APIRouter(prefix='/eta',tags=['eta'])
class EtaRequest(BaseModel): values:list[float]; count:int=1
def eta(request: EtaRequest): return {'model':'mean_eta','values':MeanEta().fit(request.values).predict(request.count)}
router.add_api_route('/predict', eta, methods=['POST'])
