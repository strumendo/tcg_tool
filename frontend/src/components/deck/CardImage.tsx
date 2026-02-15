"use client";

import Image from "next/image";
import { useState } from "react";
import type { Card } from "@/lib/types";

interface CardImageProps {
  card: Card;
  width?: number;
  height?: number;
  showOverlay?: boolean;
  isOwned?: boolean;
  onClick?: () => void;
}

export function CardImage({
  card,
  width = 120,
  height = 168,
  showOverlay = false,
  isOwned,
  onClick,
}: CardImageProps) {
  const [error, setError] = useState(false);

  const imageUrl = card.image_url || card.image_url_hires;
  const fallbackUrl = `/images/card-back.png`;

  return (
    <div
      className={`relative inline-block cursor-pointer transition-transform hover:scale-105 ${
        onClick ? "cursor-pointer" : ""
      }`}
      onClick={onClick}
    >
      <Image
        src={error || !imageUrl ? fallbackUrl : imageUrl}
        alt={card.name_en}
        width={width}
        height={height}
        className="rounded-lg shadow-md"
        onError={() => setError(true)}
      />

      {/* Regulation mark badge */}
      {card.regulation_mark && (
        <span
          className={`absolute top-1 right-1 text-xs font-bold px-1.5 py-0.5 rounded ${
            card.regulation_mark === "G"
              ? "bg-red-500 text-white"
              : card.regulation_mark === "H"
                ? "bg-green-500 text-white"
                : "bg-blue-500 text-white"
          }`}
        >
          {card.regulation_mark}
        </span>
      )}

      {/* Missing card overlay */}
      {showOverlay && isOwned === false && (
        <div className="absolute inset-0 bg-red-500/20 rounded-lg flex items-end justify-center pb-2">
          <span className="bg-red-600 text-white text-xs px-2 py-0.5 rounded-full font-medium">
            Faltando
          </span>
        </div>
      )}
    </div>
  );
}
