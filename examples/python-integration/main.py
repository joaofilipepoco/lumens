from fastapi import FastAPI

from lumens_observability import configure_application_observability, instrument_fastapi

app = FastAPI()
operations = configure_application_observability("1.0.0")
instrument_fastapi(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/integrate")
async def integrate() -> dict[str, str]:
    # The FastAPI server span is supplied by the official instrumentor, not Lumens.
    return await operations.observe_async("integration.enrich", lambda _: _integrate())


async def _integrate() -> dict[str, str]:
    return {"outcome": "success"}
