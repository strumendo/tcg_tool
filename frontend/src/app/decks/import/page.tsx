"use client";

import { useRouter } from "next/navigation";
import { DeckImportForm } from "@/components/deck/DeckImportForm";

export default function ImportDeckPage() {
  const router = useRouter();

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">
        Importar Deck
      </h1>
      <DeckImportForm
        onImportSuccess={(deckId) => router.push(`/decks/${deckId}`)}
      />
    </div>
  );
}
