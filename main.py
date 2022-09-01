from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Authentication.router import authRouter
from Shop.router import shopRouter


app = FastAPI(
    title="Shopping API",
    description="Shopping API"
)

origins = []


@app.get("/", tags=["index"])
async def index():
    return {
        "welcome": "to Shop"
    }


# Authentication API
app.include_router(authRouter)
# Shop API
app.include_router(shopRouter)
# Image Uploader API with Arvan Cloud
# app.include_router(uploadRouter)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
