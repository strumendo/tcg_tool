"use client";

import { ENERGY_COLORS } from "@/lib/constants";

interface EnergyBadgeProps {
  type: string;
  size?: "sm" | "md";
}

const ENERGY_LABELS: Record<string, string> = {
  fire: "Fogo",
  water: "Agua",
  grass: "Planta",
  lightning: "Eletrico",
  psychic: "Psiquico",
  fighting: "Lutador",
  darkness: "Noturno",
  metal: "Metal",
  fairy: "Fada",
  dragon: "Dragao",
  colorless: "Incolor",
};

export function EnergyBadge({ type, size = "sm" }: EnergyBadgeProps) {
  const normalizedType = type.toLowerCase();
  const color = ENERGY_COLORS[normalizedType] || "#A8A878";
  const label = ENERGY_LABELS[normalizedType] || type;

  const dotSize = size === "sm" ? "w-2.5 h-2.5" : "w-3.5 h-3.5";
  const textSize = size === "sm" ? "text-xs" : "text-sm";
  const padding = size === "sm" ? "px-2 py-0.5" : "px-2.5 py-1";

  return (
    <span
      className={`inline-flex items-center gap-1.5 ${padding} rounded-full bg-gray-100 ${textSize} font-medium text-gray-700`}
    >
      <span
        className={`${dotSize} rounded-full flex-shrink-0`}
        style={{ backgroundColor: color }}
      />
      {label}
    </span>
  );
}
