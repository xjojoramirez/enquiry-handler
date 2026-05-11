from fastapi import FastAPI
from app.routers.enquiries import router

app = FastAPI(title="AI Enquiry Handler", version="1.0.0")
app.include_router(router)
