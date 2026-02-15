"use client";

import { useState } from "react";
import Image from "next/image";
import type { Card } from "@/lib/types";
import { REGULATION_MARKS } from "@/lib/constants";

interface CardDetailPanelProps {
  card: Card | null;
  onClose: () => void;
}

export function CardDetailPanel({ card, onClose }: CardDetailPanelProps) {
  const [imageError, setImageError] = useState(false);

  if (!card) return null;

  const regMark = card.regulation_mark as keyof typeof REGULATION_MARKS | null;
  const regInfo = regMark ? REGULATION_MARKS[regMark] : null;
  const isRotating = card.regulation_mark === "G";

  const imageUrl = card.image_url_hires || card.image_url;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="relative w-full max-w-md bg-white shadow-xl overflow-y-auto animate-slide-in-right">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-lg font-semibold text-gray-900 truncate">
            {card.name_pt || card.name_en}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Card image */}
          <div className="flex justify-center">
            <Image
              src={imageError || !imageUrl ? "/images/card-back.png" : imageUrl}
              alt={card.name_en}
              width={250}
              height={350}
              className="rounded-xl shadow-lg"
              onError={() => setImageError(true)}
            />
          </div>

          {/* Names */}
          <div className="space-y-1">
            <p className="text-xl font-bold text-gray-900">{card.name_en}</p>
            {card.name_pt && card.name_pt !== card.name_en && (
              <p className="text-sm text-gray-500">{card.name_pt}</p>
            )}
          </div>

          {/* Basic info grid */}
          <div className="grid grid-cols-2 gap-3">
            {/* Set info */}
            <InfoItem
              label="Set"
              value={card.set?.name_en || `Set #${card.set_id}`}
            />
            <InfoItem label="Numero" value={card.set_number} />

            {/* Card type */}
            <InfoItem
              label="Tipo"
              value={formatCardType(card.card_type, card.trainer_subtype)}
            />

            {/* HP */}
            {card.hp && <InfoItem label="HP" value={String(card.hp)} />}

            {/* Energy type */}
            {card.energy_type && (
              <InfoItem label="Tipo de Energia" value={capitalizeFirst(card.energy_type)} />
            )}

            {/* Stage */}
            {card.stage && (
              <InfoItem label="Estagio" value={capitalizeFirst(card.stage)} />
            )}
          </div>

          {/* Regulation mark */}
          {card.regulation_mark && (
            <div className="flex items-center gap-3 p-3 rounded-lg bg-gray-50">
              <span
                className="text-sm font-bold px-2.5 py-1 rounded text-white"
                style={{ backgroundColor: regInfo?.color || "#6B7280" }}
              >
                {card.regulation_mark}
              </span>
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Marca de Regulacao {card.regulation_mark}
                </p>
                <p className={`text-xs ${isRotating ? "text-red-600" : "text-green-600"}`}>
                  {isRotating ? "Rotacionando em Marco 2026" : regInfo?.label || "Legal"}
                </p>
              </div>
            </div>
          )}

          {/* EX badge */}
          {card.is_ex && (
            <span className="inline-block bg-yellow-100 text-yellow-800 text-xs font-semibold px-2.5 py-1 rounded-full">
              Pokemon ex
            </span>
          )}

          {/* Abilities */}
          {card.abilities && card.abilities.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
                Habilidades
              </h3>
              <div className="space-y-3">
                {card.abilities.map((ability) => (
                  <div
                    key={ability.id}
                    className="bg-purple-50 rounded-lg p-3 border border-purple-100"
                  >
                    <p className="font-medium text-purple-900">
                      {ability.name_pt || ability.name_en}
                    </p>
                    {ability.category && (
                      <span className="inline-block text-xs bg-purple-200 text-purple-800 px-2 py-0.5 rounded mt-1">
                        {ability.category}
                      </span>
                    )}
                    {(ability.effect_pt || ability.effect_en) && (
                      <p className="text-sm text-gray-600 mt-1">
                        {ability.effect_pt || ability.effect_en}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Attacks */}
          {card.attacks && card.attacks.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
                Ataques
              </h3>
              <div className="space-y-3">
                {card.attacks.map((attack) => (
                  <div
                    key={attack.id}
                    className="bg-blue-50 rounded-lg p-3 border border-blue-100"
                  >
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-blue-900">
                        {attack.name_pt || attack.name_en}
                      </p>
                      {attack.damage && (
                        <span className="text-lg font-bold text-blue-700">
                          {attack.damage}
                        </span>
                      )}
                    </div>
                    {attack.energy_cost && attack.energy_cost.length > 0 && (
                      <div className="flex gap-1 mt-1">
                        {attack.energy_cost.map((cost, idx) => (
                          <span
                            key={idx}
                            className="text-xs bg-blue-200 text-blue-800 px-1.5 py-0.5 rounded"
                          >
                            {cost}
                          </span>
                        ))}
                      </div>
                    )}
                    {(attack.effect_pt || attack.effect_en) && (
                      <p className="text-sm text-gray-600 mt-2">
                        {attack.effect_pt || attack.effect_en}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Functions */}
          {card.functions && card.functions.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">
                Funcoes
              </h3>
              <div className="flex flex-wrap gap-2">
                {card.functions.map((fn) => (
                  <span
                    key={fn}
                    className="bg-gray-100 text-gray-700 text-xs px-2.5 py-1 rounded-full font-medium"
                  >
                    {formatFunction(fn)}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Find alternatives link */}
          <div className="pt-2 border-t border-gray-200">
            <a
              href={`/cards?alternative_for=${card.id}`}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Buscar alternativas para esta carta
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-50 rounded-lg p-2.5">
      <p className="text-xs text-gray-500 uppercase tracking-wider">{label}</p>
      <p className="text-sm font-medium text-gray-900 truncate">{value}</p>
    </div>
  );
}

function formatCardType(type: string, subtype: string | null): string {
  const typeMap: Record<string, string> = {
    pokemon: "Pokemon",
    trainer: "Treinador",
    energy: "Energia",
  };
  const subtypeMap: Record<string, string> = {
    supporter: "Apoiador",
    item: "Item",
    stadium: "Estadio",
    tool: "Ferramenta",
  };
  const base = typeMap[type] || type;
  if (subtype && subtypeMap[subtype]) {
    return `${base} - ${subtypeMap[subtype]}`;
  }
  return base;
}

function capitalizeFirst(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatFunction(fn: string): string {
  const map: Record<string, string> = {
    draw: "Compra",
    search: "Busca",
    recovery: "Recuperacao",
    removal: "Remocao",
    switching: "Troca",
    energy_accel: "Aceleracao de Energia",
    damage: "Dano",
    healing: "Cura",
    disruption: "Disrupcao",
    setup: "Setup",
    protection: "Protecao",
    other: "Outro",
  };
  return map[fn] || fn;
}
