from fastapi import APIRouter
from src.decision.explanation_builder import explain_result
router=APIRouter(prefix='/decisions',tags=['decisions'])
@router.post('/explain')
def explain(payload: dict): return {'explanation': 'Structured decision explanation', 'input': payload}
