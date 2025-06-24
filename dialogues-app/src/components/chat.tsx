import React from "react";
import { TextField, Button, Typography, Paper } from "@mui/material";

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
    // Remove the welcome message as you would any other message by slicing
    const displayMessages = messages.slice(-2);

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
                <TextField
                    fullWidth
                    variant="outlined"
                    size="small"
                    label="Send a message to Mira .."
                    placeholder="Would you choose to save a cat or a dog?"
                    value={input}                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleSend();
                    }}
                />
                <Button variant="contained" color="primary" onClick={handleSend} />
            </div>
            <Typography className="disclaimer">
                🚨 This AI system is for informational and educational purposes
                only and may not always provide accurate responses. It doesn’t remember past messages, so it can’t hold a conversation like a person would.
            </Typography>
        </section>
    );
};

export default Chat;