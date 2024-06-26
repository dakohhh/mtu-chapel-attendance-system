
from fastapi.responses import JSONResponse




class CustomResponse(JSONResponse):
    def __init__(self, msg, status=200, success=True, data=None) -> None:

        response = {
        "status":status,
        "message": msg,
        "success": success,
        "data": data 
        }

        super().__init__(status_code=status, content=response)



