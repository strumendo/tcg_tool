export const ENERGY_TYPES = [
  "fire",
  "water",
  "grass",
  "lightning",
  "psychic",
  "fighting",
  "darkness",
  "metal",
  "fairy",
  "dragon",
  "colorless",
] as const;

export const ENERGY_COLORS: Record<string, string> = {
  fire: "#F08030",
  water: "#6890F0",
  grass: "#78C850",
  lightning: "#F8D030",
  psychic: "#F85888",
  fighting: "#C03028",
  darkness: "#705848",
  metal: "#B8B8D0",
  fairy: "#EE99AC",
  dragon: "#7038F8",
  colorless: "#A8A878",
};

export const REGULATION_MARKS = {
  G: { label: "Rotating Mar 2026", color: "#EF4444" },
  H: { label: "Legal (Safe)", color: "#22C55E" },
  I: { label: "Legal (New)", color: "#3B82F6" },
} as const;

export const SEVERITY_COLORS = {
  NONE: "#22C55E",
  LOW: "#84CC16",
  MODERATE: "#EAB308",
  HIGH: "#F97316",
  CRITICAL: "#EF4444",
} as const;

export const MAX_DECK_SIZE = 60;
export const MAX_CARD_COPIES = 4;
