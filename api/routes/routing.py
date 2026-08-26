from fastapi import APIRouter
router=APIRouter(prefix='/routing',tags=['routing'])
@router.get('/strategies')
def strategies(): return {'strategies':['dijkstra','astar','greedy','two_opt','three_opt','hybrid']}
