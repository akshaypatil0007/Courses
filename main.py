from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from motor import motor_asyncio
from app.db import mongo_config
api = FastAPI()
# from app.cotrollers import courses
from app.routes import courses_routes
# Make a connection to MongoDB when the FastAPI app starts
@api.on_event("startup")
async def startup_db_client():
    print("Connecting to database...")

    try:
        api.mongodb_client = motor_asyncio.AsyncIOMotorClient(
            mongo_config._db_settings.DB_URL
        )
        api.mongodb = api.mongodb_client[mongo_config._db_settings.DB_NAME]

        print(api.mongodb_client)
        print("Connection to database successful...")

        # await mongo_config.create_all__collections(api.mongodb)
    except Exception as e:
        print(e)
        print(
            "Connection to database failed: Verify if database server in running..."
        )


origins = ["*"]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api.include_router(courses_routes.router,tags=['Course'])

if __name__ == "__main__":
    uvicorn.run(api, host="127.0.0.1", port=8000)
    print("Running Server...")
