from fastapi import HTTPException

def testErrorResponse():
  """Return an HTTPException for manual testing endpoint error responses"""
  return HTTPException(
    status_code=500, 
    detail="Test error response"
  )
