import React, { useEffect, useRef } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import { IconButton, Tooltip } from "@mui/material";
import MicIcon from "@mui/icons-material/Mic";
import MicOffIcon from "@mui/icons-material/MicOff";

interface VoiceInputProps {
  onTranscriptFinal: (text: string) => void; // called when speech ends
}

const VoiceInput: React.FC<VoiceInputProps> = ({ onTranscriptFinal }) => {
  const { transcript, listening, resetTranscript, browserSupportsSpeechRecognition } =
    useSpeechRecognition();
  const prevListening = useRef(listening);

  useEffect(() => {
    const prev = prevListening.current;
    const hasText = transcript && transcript.trim().length > 0;

    // Case 1: just stopped & already have transcript
    if (prev && !listening && hasText) {
      onTranscriptFinal(transcript.trim());
      resetTranscript();
    }

    // Case 2: already stopped, transcript arrived after stop
    if (!listening && !prev && hasText) {
      onTranscriptFinal(transcript.trim());
      resetTranscript();
    }

    prevListening.current = listening;
  }, [listening, transcript, onTranscriptFinal, resetTranscript]);

  if (!browserSupportsSpeechRecognition) {
    return <span>Your browser doesn’t support speech recognition.</span>;
  }

  const toggleListening = () => {
    if (listening) {
      SpeechRecognition.stopListening();
    } else {
      resetTranscript();
      SpeechRecognition.startListening({
        continuous: false,
        interimResults: false,
        lang: "en-US", // force language each time
      });
    }
  };

  return (
    <Tooltip title={listening ? "Stop listening" : "Start voice input"}>
      <IconButton
        color={listening ? "secondary" : "default"}
        onClick={toggleListening}
        size="large"
      >
        {listening ? <MicOffIcon /> : <MicIcon />}
      </IconButton>
    </Tooltip>
  );
};

export default VoiceInput;
