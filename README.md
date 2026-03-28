---
title: SupportEnv
emoji: 🚀
colorFrom: purple
colorTo: gray
sdk: docker
app_port: 7860
---

# 🚀 SupportEnv — AI Customer Support Simulation Environment

SupportEnv is a real-world simulation environment designed for training and evaluating AI agents on customer support tasks.

---

## 🎯 Problem

Customer support is a complex, real-world task involving:
- Understanding user intent
- Handling emotions (neutral / angry users)
- Taking correct actions (reply, escalate)
- Providing accurate solutions

This environment simulates those challenges in a structured, testable way.

---

## 🧠 Features

- ✅ Real-world task simulation (customer support tickets)
- ✅ OpenEnv-style step/reset/state API
- ✅ Multi-difficulty tasks:
  - Easy → Password reset
  - Medium → Billing/refund issue
  - Hard → Technical crash issue
- ✅ Reward shaping (partial progress signals)
- ✅ Deterministic grading system (0.0–1.0 score)
- ✅ Baseline AI agent with realistic performance variance
- ✅ Interactive UI dashboard for manual testing

---

## ⚙️ API Endpoints

| Endpoint | Description |
|--------|------------|
| `/reset` | Start new task |
| `/step` | Perform action |
| `/state` | Get current state |
| `/tasks` | List all tasks |
| `/grader` | Evaluate performance |
| `/baseline` | Run baseline agent |
| `/ui` | Interactive dashboard |

---

## 🎮 Action Space

```json
{
  "response": "string",
  "action_type": "reply | escalate | close"
}


## 👁️ Observation Space
{
  "message": "string",
  "sentiment": "neutral | angry",
  "difficulty": "easy | medium | hard"
}