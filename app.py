from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random

app = FastAPI()

# -------- MODELS --------
class Action(BaseModel):
    response: str
    action_type: str  # reply / escalate / close


# -------- TICKETS --------
tickets = [
    {
        "id": 1,
        "message": "How do I reset my password?",
        "sentiment": "neutral",
        "difficulty": "easy"
    },
    {
        "id": 2,
        "message": "I was charged twice for my subscription!",
        "sentiment": "angry",
        "difficulty": "medium"
    },
    {
        "id": 3,
        "message": "Your app crashes when I upload files. Fix this ASAP.",
        "sentiment": "angry",
        "difficulty": "hard"
    }
]

current_ticket = None
last_action = None


# -------- UI ROUTE --------
from fastapi.responses import HTMLResponse

@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <head>
        <title>SupportEnv UI</title>
    </head>
    <body style="background:black; color:white; text-align:center; font-family:Arial;">

    <h1>🚀 SupportEnv Dashboard</h1>

    <button onclick="reset()">New Ticket</button>
    <p id="ticket"></p>

    <input id="response" placeholder="Type response here" style="width:300px;" />
    <br><br>

    <button onclick="send('reply')">Reply</button>
    <button onclick="send('escalate')">Escalate</button>

    <p id="result"></p>

    <script>
    async function reset() {
        const res = await fetch('/reset');
        const data = await res.json();
        document.getElementById("ticket").innerText = data.message + " (" + data.difficulty + ")";
    }

    async function send(type) {
        const res = await fetch('/step', {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                response: document.getElementById("response").value,
                action_type: type
            })
        });

        const data = await res.json();

        const grade = await fetch('/grader').then(r => r.json());

        document.getElementById("result").innerText =
            "Reward: " + data.reward + " | Score: " + grade.score;
    }
    </script>

    </body>
    </html>
    """
# -------- HOME --------
@app.get("/")
def home():
    return {"status": "SupportEnv running 🚀"}


# -------- RESET --------
@app.get("/reset")
def reset():
    global current_ticket, last_action
    current_ticket = random.choice(tickets)
    last_action = None
    return current_ticket


# -------- STEP --------
@app.post("/step")
def step(action: Action):
    global current_ticket, last_action

    if current_ticket is None:
        return {"error": "Call /reset first"}

    last_action = action

    reward = 0.0
    response = action.response.lower()

    if current_ticket["difficulty"] == "easy":
        if "reset" in response:
            reward += 1.0
        else:
            reward -= 0.5

    elif current_ticket["difficulty"] == "medium":
        if "refund" in response:
            reward += 0.5
        if "sorry" in response:
            reward += 0.3
        if action.action_type == "escalate":
            reward += 0.2

    elif current_ticket["difficulty"] == "hard":
        if "fix" in response or "issue" in response:
            reward += 0.4
        if "sorry" in response:
            reward += 0.2
        if action.action_type == "escalate":
            reward += 0.4

    done = reward >= 0.8

    return {
        "ticket": current_ticket,
        "reward": round(reward, 2),
        "done": done
    }


# -------- STATE --------
@app.get("/state")
def state():
    return current_ticket


# -------- TASKS --------
@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "id": 1,
                "difficulty": "easy",
                "description": "Help user reset password"
            },
            {
                "id": 2,
                "difficulty": "medium",
                "description": "Handle billing issue and refund"
            },
            {
                "id": 3,
                "difficulty": "hard",
                "description": "Handle technical crash issue"
            }
        ],
        "action_schema": {
            "response": "string",
            "action_type": "reply | escalate | close"
        }
    }


# -------- GRADER --------
@app.get("/grader")
def grader():
    global current_ticket, last_action

    if current_ticket is None or last_action is None:
        return {"error": "No episode to grade"}

    response = last_action.response.lower()
    score = 0.0

    if current_ticket["difficulty"] == "easy":
        if "reset" in response:
            score = 1.0

    elif current_ticket["difficulty"] == "medium":
        if "refund" in response:
            score += 0.5
        if "sorry" in response:
            score += 0.3
        if last_action.action_type == "escalate":
            score += 0.2

    elif current_ticket["difficulty"] == "hard":
        if "fix" in response or "issue" in response:
            score += 0.4
        if "sorry" in response:
            score += 0.2
        if last_action.action_type == "escalate":
            score += 0.4

    return {
        "task_id": current_ticket["id"],
        "difficulty": current_ticket["difficulty"],
        "score": round(min(score, 1.0), 2)
    }


# -------- BASELINE --------
@app.get("/baseline")
def baseline():
    results = []

    for task in tickets:
        global current_ticket, last_action

        current_ticket = task
        last_action = None

        if task["difficulty"] == "easy":
            action = Action(
                response="You can reset your password using the reset link",
                action_type="reply"
            )

        elif task["difficulty"] == "medium":
            responses = [
                "Sorry for the inconvenience, we will process your refund",
                "We will look into this issue",
                "Please contact support"
            ]
            action = Action(
                response=random.choice(responses),
                action_type=random.choice(["reply", "escalate"])
            )

        elif task["difficulty"] == "hard":
            responses = [
                "We are working to fix the issue",
                "Please reinstall the app",
                "Sorry for the inconvenience"
            ]
            action = Action(
                response=random.choice(responses),
                action_type=random.choice(["reply", "escalate"])
            )

        last_action = action

        response = action.response.lower()
        score = 0.0

        if task["difficulty"] == "easy":
            if "reset" in response:
                score = 1.0

        elif task["difficulty"] == "medium":
            if "refund" in response:
                score += 0.5
            if "sorry" in response:
                score += 0.3
            if action.action_type == "escalate":
                score += 0.2

        elif task["difficulty"] == "hard":
            if "fix" in response or "issue" in response:
                score += 0.4
            if "sorry" in response:
                score += 0.2
            if action.action_type == "escalate":
                score += 0.4

        results.append({
            "task_id": task["id"],
            "difficulty": task["difficulty"],
            "score": round(min(score, 1.0), 2)
        })

    avg_score = sum(r["score"] for r in results) / len(results)

    return {
        "results": results,
        "average_score": round(avg_score, 2)
    }