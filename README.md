# FitBuddy Backend

> **Django micro‑service that powers the AI and data look‑ups for the FitBuddy mobile app**

This repo exposes a handful of JSON endpoints that proxy third‑party APIs and hide all secret keys from the Flutter client. It is deployed at:
```
https://fitbuddy-backend-ruby.vercel.app/
```

---

## 📑 Endpoints

| Route | Method | Purpose | Upstream API |
| ----- | ------ | ------- | ------------ |
| `/generate_workout/` | POST | Return a personalised workout plan | **OpenAI** `gpt‑3.5‑turbo` |
| `/generate_diet/` | POST | Return a diet plan matched to body type & goal | **OpenAI** `gpt‑3.5‑turbo` |
| `/nutritionix/` | POST | *Two‑in‑one*<br>• `query` ⇒ food autocomplete<br>• `food` ⇒ macro breakdown | **Nutritionix** |
| `/exercise_suggest/` | POST | Autocomplete exercise names | **ExerciseDB** (RapidAPI) |
| `/exercise_tutorial/` | POST | AI‑generated step‑by‑step tutorial | **ExerciseDB** + **OpenAI** |

All routes expect **form‑encoded** parameters and respond with `application/json`.

---

## 🛡️ Security Notes
- All secrets remain on the server; the mobile app never sees them.
- `csrf_exempt` is used because the endpoints are API‑only.

---

## 📜 License

MIT — see `LICENSE`.
