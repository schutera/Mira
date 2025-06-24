# Frontend

Welcome to the **Frontend**!  
This React app lets you interact with Mira, an AI assistant whose behavior can be dynamically shaped by human-derived values and guardrails.  
Toggle guardrails on or off and see how Mira's responses change in real time.

---

## Features

- Toggleable Guardrails:  
  Instantly switch between "Guardrails On" (AI guided by human values) and "Guardrails Off" (AI unconstrained).
- Conversational UI:  
  Clean, modern chat interface for seamless interaction with Mira.
- Educational Purpose:  
  Designed to showcase the impact of human values on AI behavior.
- Open Source:  
  Contribute, fork, or adapt for your own experiments!

---

## Getting Started

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

### Install Dependencies

```bash
npm install
```

### Start the Development Server

```bash
npm start
```

Open [http://localhost:3000](http://localhost:3000) in your browser to view the app.

---

## How It Works

- **Guardrails On:**  
  Mira is guided by actionable prompts derived from global survey data on human values and expectations for AI.
- **Guardrails Off:**  
  Mira responds without these constraints, and is encouraged to take a clear side in A/B-type decisions.
- **Switch Instantly:**  
  Use the toggle in the hero section to see the difference in real time.

---

## Project Structure

- `src/`
    - `components/`
        - `chat.tsx` — 💬 Chat window and input
        - `hero.tsx` — 🛡️ Guardrail toggle and intro
        - `sidebar.tsx` — 📚 Info and navigation sidebar
    - `App.tsx` — Main app logic and state
    - `index.css` — 🎨 Styling
    - `guardrails_config.json` — ⚙️ Guardrail configuration

---

## Available Scripts

In the project directory, you can run:

- **`npm start`**  
  Runs the app in development mode. The page reloads on edits and displays lint errors in the console.

- **`npm test`**  
  Launches the test runner in interactive watch mode.  
  See [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more info.

- **`npm run build`**  
  Builds the app for production to the `build` folder.  
  See [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more info.

- **`npm run eject`**  
  **Note:** This is a one-way operation. Once you eject, you can’t go back!  
  Ejecting gives you full control over the build configuration.

---

## Learn More

- [Create React App Documentation](https://facebook.github.io/create-react-app/docs/getting-started)
- [React Documentation](https://reactjs.org/)
- [Informed Dialogues Backend](../backend/README.md)

---

Feel free to customize and extend the Informed Dialogues Frontend to fit your needs!
