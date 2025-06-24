import React from "react";
import { IconButton } from "@mui/material";
import ArrowBackIosNewIcon from "@mui/icons-material/ArrowBackIosNew";
import ArrowForwardIosIcon from "@mui/icons-material/ArrowForwardIos";
import "../index.css";

const guardrailOptions = [
  { label: "Guardrail On", emoji: "🛡️" },
  { label: "Guardrail Off", emoji: "🌀" },
];

interface HeroProps {
  guardrailsOn: boolean;
  setGuardrailsOn: (on: boolean) => void;
  guardrailConfig: Record<string, any>;
}

const Hero: React.FC<HeroProps> = ({
  guardrailsOn,
  setGuardrailsOn,
  guardrailConfig,
}) => {
  const currentIndex = guardrailsOn ? 0 : 1;

  const handlePrev = () => {
    setGuardrailsOn(!guardrailsOn);
  };

  const handleNext = () => {
    setGuardrailsOn(!guardrailsOn);
  };

  return (
    <section className="hero-section">
      <div className="hero-bg" />
      <div className="hero-content">
        <div className="hero-modern-text">
          <span className="highlight">Explore</span>
          {" "}
          how diverse perspectives of individuals worldwide can shape AI behavior by embedding their values into guardrails.
        </div>
        <div className="hero-select-row hero-select-hero" style={{ width: "100%", justifyContent: "center" }}>
          <IconButton
            aria-label="Previous option"
            onClick={handlePrev}
            size="large"
            className="hero-arrow"
          >
            <ArrowBackIosNewIcon fontSize="inherit" />
          </IconButton>
          <div className="hero-stepper-label">
            <span className="hero-select-emoji" style={{ fontSize: "2.5rem", marginRight: 16 }}>
              {guardrailOptions[currentIndex].emoji}
            </span>
            <span className="hero-stepper-continent">{guardrailOptions[currentIndex].label}</span>
          </div>
          <IconButton
            aria-label="Next option"
            onClick={handleNext}
            size="large"
            className="hero-arrow"
          >
            <ArrowForwardIosIcon fontSize="inherit" />
          </IconButton>
        </div>
      </div>
    </section>
  );
};

export default Hero;