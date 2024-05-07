from fastapi.requests import HTTPConnection


async def connection_report(request: HTTPConnection):
    print("\n>>> connection_report", request.url.path, request.headers)
    yield
    print("<<< connection_report")
