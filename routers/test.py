from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def test():
  return 'Welcome!'

@router.get('/test')
async def test():
  return 'Success!'
