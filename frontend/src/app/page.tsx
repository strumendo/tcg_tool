"use client";

import Link from "next/link";

const features = [
  {
    title: "Meus Decks",
    description: "Gerencie e visualize seus decks com imagens das cartas",
    href: "/decks",
    icon: "🃏",
  },
  {
    title: "Meta Decks",
    description: "Top decks competitivos com matchups e tier list",
    href: "/meta",
    icon: "🏆",
  },
  {
    title: "Buscar Cartas",
    description: "Busque cartas por nome, habilidade ou tipo",
    href: "/cards",
    icon: "🔍",
  },
  {
    title: "Importar Deck",
    description: "Importe decks do TCG Live ou arquivo .txt",
    href: "/decks/import",
    icon: "📥",
  },
  {
    title: "Batalhas",
    description: "Registre batalhas e analise suas estrategias",
    href: "/battles",
    icon: "⚔️",
  },
  {
    title: "Estatisticas",
    description: "Relatorios estatisticos dos seus resultados",
    href: "/stats",
    icon: "📊",
  },
  {
    title: "Chat IA",
    description: "Pergunte sobre estrategias e cartas ao assistente IA",
    href: "/chat",
    icon: "🤖",
  },
  {
    title: "Colecao",
    description: "Marque cartas que voce possui e veja o que falta",
    href: "/collection",
    icon: "📦",
  },
  {
    title: "Simulacao",
    description: "Simule sequencias de jogadas contra decks meta",
    href: "/simulation",
    icon: "🎯",
  },
];

export default function HomePage() {
  return (
    <div>
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          TCG Tool
        </h1>
        <p className="text-lg text-gray-600">
          Plataforma de analise de decks Pokemon TCG com insights de IA
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <Link
            key={feature.href}
            href={feature.href}
            className="block p-6 bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md hover:border-primary-300 transition-all"
          >
            <div className="text-3xl mb-3">{feature.icon}</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {feature.title}
            </h2>
            <p className="text-gray-600">{feature.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
