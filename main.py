from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import List
from calendar_utils import get_free_slots, create_event
from booking_agent import agent_executor
import traceback

app = FastAPI()


# ----------------------------  Chat Model ----------------------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat_agent(req: ChatRequest):
    try:
        result = agent_executor.invoke({
            "messages": [req.message],
            "agent_scratchpad": [],
            "input": req.message
        }) 
        print("🧾 Full result from agent_executor.invoke():", result)


        print("🔎 Agent result:", result)

        # Handle different possible keys safely
        response_text = result.get("messages", ["No output"])[-1] if "messages" in result else result.get("output", " No valid agent output")

        return {"response": response_text}

    except Exception as e:
        print("Agent error:", e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))

# ----------------------------  Time Slot Logic ----------------------------
class TimeSlotRequest(BaseModel):
    date: str  # Format: 'YYYY-MM-DD'
    duration: int  # in minutes

@app.post("/available-slots")
def available_slots(req: TimeSlotRequest):
    try:
        slots = get_free_slots(req.date, req.duration)
        return {"available_slots": slots}
    except Exception as e:
        print(" Slot Error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# ----------------------------  Booking Logic ----------------------------
class BookRequest(BaseModel):
    summary: str
    description: str
    start: str  # Format: 'YYYY-MM-DDTHH:MM:SS'
    end: str    # Format: 'YYYY-MM-DDTHH:MM:SS'

@app.post("/book-appointment")
def book_slot(req: BookRequest):
    try:
        event = create_event(req.summary, req.description, req.start, req.end)
        return {"status": "success", "event_link": event.get("htmlLink")}
    except Exception as e:
        print(" Booking Error:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error: " + str(e))


# ----------------------------  Health Check ----------------------------
@app.get("/")
def home():
    return {"message": "Calendar Booking API is live "}


# ----------------------------  For Local Run ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
