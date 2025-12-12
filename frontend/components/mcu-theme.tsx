"use client";

// MCU Theme Configuration - Cinematic Color Palette & Animations
export const MCUTheme = {
  colors: {
    ironMan: {
      primary: "#C41E3A", // Iron Man Red
      secondary: "#FFD700", // Gold
      glow: "#FF6B6B",
      gradient: "from-red-600 via-red-500 to-yellow-500",
    },
    captainAmerica: {
      primary: "#003A70", // Captain America Blue
      secondary: "#C41E3A", // Red
      glow: "#4A90E2",
      gradient: "from-blue-700 via-blue-600 to-red-600",
    },
    thor: {
      primary: "#FFD700", // Gold
      secondary: "#FF8C00", // Orange
      glow: "#FFD700",
      gradient: "from-yellow-400 via-yellow-500 to-orange-500",
    },
    vision: {
      primary: "#90EE90", // Green
      secondary: "#FFD700", // Yellow
      glow: "#90EE90",
      gradient: "from-green-400 via-green-300 to-yellow-300",
    },
    blackWidow: {
      primary: "#1C1C1C", // Black
      secondary: "#C41E3A", // Red
      glow: "#FF4444",
      gradient: "from-gray-900 via-gray-800 to-red-600",
    },
    doctorStrange: {
      primary: "#4B0082", // Indigo
      secondary: "#9370DB", // Purple
      glow: "#9370DB",
      gradient: "from-indigo-700 via-purple-600 to-purple-500",
    },
    shield: {
      primary: "#1E3A8A", // Shield Blue
      secondary: "#DC2626", // Shield Red
      glow: "#3B82F6",
    },
  },
  animations: {
    cinematic: {
      fadeInUp: {
        initial: { opacity: 0, y: 60, scale: 0.95 },
        animate: { opacity: 1, y: 0, scale: 1 },
        transition: { duration: 0.8, ease: [0.25, 0.46, 0.45, 0.94] },
      },
      slideInLeft: {
        initial: { opacity: 0, x: -100 },
        animate: { opacity: 1, x: 0 },
        transition: { duration: 0.7, ease: "easeOut" },
      },
      slideInRight: {
        initial: { opacity: 0, x: 100 },
        animate: { opacity: 1, x: 0 },
        transition: { duration: 0.7, ease: "easeOut" },
      },
      scaleIn: {
        initial: { opacity: 0, scale: 0.8 },
        animate: { opacity: 1, scale: 1 },
        transition: { duration: 0.6, ease: "easeOut" },
      },
      heroEntrance: {
        initial: { opacity: 0, y: 100, scale: 0.9 },
        animate: { opacity: 1, y: 0, scale: 1 },
        transition: { 
          duration: 1.2, 
          ease: [0.25, 0.46, 0.45, 0.94],
          staggerChildren: 0.1,
        },
      },
    },
    effects: {
      glow: {
        animate: {
          boxShadow: [
            "0 0 20px rgba(255, 107, 107, 0.5)",
            "0 0 40px rgba(255, 107, 107, 0.8)",
            "0 0 20px rgba(255, 107, 107, 0.5)",
          ],
        },
        transition: { duration: 2, repeat: Infinity },
      },
      pulse: {
        animate: {
          scale: [1, 1.05, 1],
          opacity: [0.8, 1, 0.8],
        },
        transition: { duration: 2, repeat: Infinity },
      },
      shimmer: {
        background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)",
        backgroundSize: "200% 100%",
        animation: "shimmer 2s infinite",
      },
    },
  },
  typography: {
    hero: "font-bold tracking-tight",
    subtitle: "font-semibold tracking-wide",
    body: "font-normal",
  },
};

// MCU Story Phases
export const MCUPhases = {
  phase1: {
    title: "Phase 1: Assembly",
    description: "The heroes gather, each bringing unique powers to the team",
    color: MCUTheme.colors.shield.primary,
  },
  phase2: {
    title: "Phase 2: Evolution",
    description: "The team grows stronger, facing new challenges together",
    color: MCUTheme.colors.ironMan.primary,
  },
  phase3: {
    title: "Phase 3: Infinity",
    description: "The ultimate battle - where all powers combine",
    color: MCUTheme.colors.doctorStrange.primary,
  },
};

