declare module "react-speech-recognition" {
  export interface SpeechRecognitionOptions {
    continuous?: boolean;
    interimResults?: boolean;
    lang?: string;
  }

  export interface UseSpeechRecognitionResult {
    transcript: string;
    interimTranscript: string;
    finalTranscript: string;
    listening: boolean;
    resetTranscript: () => void;
    browserSupportsSpeechRecognition: boolean;
  }

  export function useSpeechRecognition(
    options?: SpeechRecognitionOptions
  ): UseSpeechRecognitionResult;

  export function startListening(
    options?: SpeechRecognitionOptions
  ): void;

  export function stopListening(): void;

  export function abortListening(): void;

  export function resetTranscript(): void;

  const SpeechRecognition: {
    startListening: typeof startListening;
    stopListening: typeof stopListening;
    abortListening: typeof abortListening;
    resetTranscript: typeof resetTranscript;
  };

  export default SpeechRecognition;
}
