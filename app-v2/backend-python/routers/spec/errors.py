from typing import Generic, Literal, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# expected http error generic class

TErrorHttpStatus = TypeVar("TErrorHttpStatus", bound=int)
TErrorCode = TypeVar("TErrorCode", bound=str)

class HttpExpectedError(BaseModel, Generic[TErrorHttpStatus, TErrorCode]):
  """Custom error, can be passed both to openapi decorator responses and raised as HTTPException (XXX.toHttpException())"""
  httpStatus: TErrorHttpStatus = Field(title="Status", description="HTTP Status code (number) of the error")
  code: TErrorCode = Field(title="Code", description="Code of the error as FULL_CAPS case (e.g. RESOURCE_NOT_FOUND)")
  message: str = Field(title="Message", description="Message of the error")
  def toHttpException(self):
    """
    Convert to HTTPException ready to be raised inside fast api handlers.
    'fastApiHttpExceptionHandlerOverwrite' will catch it and convert it to JSON
    """
    return HTTPException(
      status_code=self.httpStatus,
      detail=self,
    )

# concrete http errors class for routers errrors definition and usage

class HttpExpectedError_500_InternalServerError(
  HttpExpectedError[
  Literal[500], 
  Literal["INTERNAL_SERVER_ERROR"],
  ]
):
  httpStatus: Literal[500] = 500
  code: Literal["INTERNAL_SERVER_ERROR"] = "INTERNAL_SERVER_ERROR"
  
class HttpExpectedError_404_NotFound(
  HttpExpectedError[
    Literal[404], 
    Literal["NOT_FOUND"],
  ]
):  
  httpStatus: Literal[404] = 404
  code: Literal["NOT_FOUND"] = "NOT_FOUND"
  
  
  
# fast api exception handler that we add to fastapi app to convert our custom errors to JSON

async def fastApiHttpExceptionHandlerOverwrite(request, exc):
  """
  Custom FastApi.HTTPException handler that overwrites the default one.
  Here we intrcept all HTTPException and if th details are our custom error class, 
  we send the corrct JSON response (that match the shape of the openapi spec, derived by fastapi from decorator responses)
  """
  # if is our custom error class...
  if isinstance(exc, StarletteHTTPException) and isinstance(exc.detail, HttpExpectedError):
    statusNum = exc.status_code
    detailJson = exc.detail.model_dump()
    return JSONResponse(
      status_code=statusNum,
      content=jsonable_encoder(detailJson),
    )
  # fallback to original fastapi handler
  return await http_exception_handler(request, exc)
