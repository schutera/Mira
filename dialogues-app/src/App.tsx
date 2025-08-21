import React, { useState } from "react";
import guardrailConfig from "./guardrails_config.json";
import Sidebar from "./components/sidebar";
import Hero from "./components/hero";
import "./index.css";
import Chat from "./components/chat";


const WELCOME_MESSAGE: Message = {
  role: "assistant",
  content: "👋 Hey, I'm Mira! My behavior is custom tailored around and derived from a global survey on human expectation and perspectives on AI systems. Try me.",
};

type Message = { role: "user" | "assistant"; content: string };

function App() {
  // Use a boolean for guardrails
  const [guardrailsOn, setGuardrailsOn] = useState(true);
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Use the config as needed, or just pick one
  const guardrailValues = guardrailConfig[guardrailsOn ? "Guardrail On" : "Guardrail Off"];

  const handleSend = async () => {
    if (!input.trim()) {
      return;
    }

    // 1) Add the user’s message
    setMessages((msgs) => [
      ...msgs,
      { role: "user", content: input },
    ]);

    const prompt = input;
    setInput("");

    try {
      // 2) Hit your backend
      const res = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, guardrails: guardrailsOn }),
      });
      const data = await res.json();

      // 3) Prepare Mira’s reply object
      const assistantMessage = {
        role: "assistant" as const,
        content: data.response,
      };

      // 4) Append Mira’s reply
      setMessages((msgs) => [...msgs, assistantMessage]);

      // 🗑 Removed Step 5: Speech synthesis
    } catch (e) {
      console.error("Error occurred while sending message:", e);

      // 5) Fallback reply
      setMessages((msgs) => [
        ...msgs,
        {
          role: "assistant" as const,
          content: "Sorry, the AI system is taking a bio break 🌱",
        },
      ]);
    }
  };


  return (
    <div className="app-root">
      <Sidebar
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        guardrailValues={guardrailValues}
      />
      <main className="main-content">
        <Hero
          guardrailsOn={guardrailsOn}
          setGuardrailsOn={setGuardrailsOn}
          guardrailConfig={guardrailConfig}
        />
        <Chat
          input={input}
          setInput={setInput}
          handleSend={handleSend}
          messages={messages}
        />
      </main>
    </div>
  );
}

export default App;
