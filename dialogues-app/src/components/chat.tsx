import React from "react";
import { TextField, Button, Typography, Paper } from "@mui/material";
import VoiceInput from "./VoiceInput";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatProps {
  input: string;
  setInput: (value: string) => void;
  handleSend: () => void;
  messages: Message[];
}

const Chat: React.FC<ChatProps> = ({ input, setInput, handleSend, messages }) => {
  const displayMessages = messages.slice(-2);

  // Track when a voice input should trigger send after input updates
  const [pendingVoiceSend, setPendingVoiceSend] = React.useState(false);

  React.useEffect(() => {
    if (pendingVoiceSend) {
      handleSend();
      setPendingVoiceSend(false);
    }
  }, [pendingVoiceSend, input, handleSend]);

  return (
    <section className="chat-section">
      <Paper elevation={2} className="chat-window">
        {displayMessages.map((msg, idx) => (
          <div key={idx} className={`chat-message-row ${msg.role}`}>
            <div className={`chat-message-bubble ${msg.role}`}>
              {msg.content}
            </div>
          </div>
        ))}
      </Paper>

      <div className="input-row">
        {/* Keyboard input still works */}
        <TextField
          fullWidth
          variant="outlined"
          size="small"
          label="Send a message to Mira .."
          placeholder="Would you choose to save a cat or a dog?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSend();
          }}
        />

        {/* Voice input: set state, then trigger send via effect */}
        <VoiceInput
          onTranscriptFinal={(finalText: string) => {
            if (!finalText.trim()) return;
            setInput(finalText);
            setPendingVoiceSend(true);
          }}
        />

        <Button variant="contained" color="primary" onClick={handleSend} />
      </div>

      <Typography className="disclaimer">
        🚨 This AI system is for informational and educational purposes only and
        may not always provide accurate responses. It doesn’t remember past
        messages, so it can’t hold a conversation like a person would.
      </Typography>
    </section>
  );
};

export default Chat;
