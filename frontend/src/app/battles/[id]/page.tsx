"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import {
  useBattle,
  useBattleAnalysis,
  useDeleteBattle,
} from "@/hooks/useBattles";

export default function BattleDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const battleId = parseInt(id);
  const router = useRouter();
  const { data: battle, isLoading } = useBattle(battleId);
  const analysisMutation = useBattleAnalysis(battleId);
  const deleteMutation = useDeleteBattle();
  const [analysis, setAnalysis] = useState<string | null>(null);

  if (isLoading)
    return <div className="text-center py-10">Carregando...</div>;
  if (!battle)
    return (
      <div className="text-center py-10">Batalha nao encontrada</div>
    );

  const resultColors: Record<string, string> = {
    win: "bg-green-100 text-green-700 border-green-300",
    loss: "bg-red-100 text-red-700 border-red-300",
    draw: "bg-yellow-100 text-yellow-700 border-yellow-300",
  };
  const resultLabels: Record<string, string> = {
    win: "Vitoria",
    loss: "Derrota",
    draw: "Empate",
  };

  const handleAnalyze = () => {
    analysisMutation.mutate(undefined, {
      onSuccess: (data) => setAnalysis(data.analysis),
    });
  };

  const handleDelete = () => {
    deleteMutation.mutate(battleId, {
      onSuccess: () => router.push("/battles"),
    });
  };

  return (
    <div className="max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            vs {battle.opponent_deck_name || "Oponente desconhecido"}
          </h1>
          <p className="text-sm text-gray-500">
            {new Date(battle.played_at).toLocaleDateString("pt-BR", {
              day: "2-digit",
              month: "long",
              year: "numeric",
            })}
          </p>
        </div>
        <span
          className={`px-4 py-2 rounded-full text-lg font-bold border-2 ${resultColors[battle.result]}`}
        >
          {resultLabels[battle.result]}
        </span>
      </div>

      {/* Info cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {battle.total_turns && (
          <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {battle.total_turns}
            </p>
            <p className="text-xs text-gray-500">Turnos</p>
          </div>
        )}
        {battle.went_first !== null && (
          <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
            <p className="text-2xl font-bold text-gray-900">
              {battle.went_first ? "1o" : "2o"}
            </p>
            <p className="text-xs text-gray-500">Comecou</p>
          </div>
        )}
        <div className="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p className="text-2xl font-bold text-gray-900 capitalize">
            {battle.source}
          </p>
          <p className="text-xs text-gray-500">Fonte</p>
        </div>
      </div>

      {/* Notes */}
      {battle.notes && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-2">Notas</h2>
          <p className="text-gray-600 whitespace-pre-wrap">{battle.notes}</p>
        </div>
      )}

      {/* Battle Timeline */}
      {battle.actions.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
          <h2 className="font-semibold text-gray-900 mb-4">Timeline</h2>
          <div className="space-y-3">
            {battle.actions.map((action, i) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-sm font-bold">
                    {action.turn}
                  </div>
                  {i < battle.actions.length - 1 && (
                    <div className="w-0.5 h-full bg-gray-200 mt-1" />
                  )}
                </div>
                <div className="pb-3">
                  <p className="font-medium text-gray-900">
                    {action.player}: {action.action_type}
                  </p>
                  {action.card_name && (
                    <p className="text-sm text-gray-600">
                      Carta: {action.card_name}
                    </p>
                  )}
                  {action.details && (
                    <p className="text-sm text-gray-500">{action.details}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* AI Analysis */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-semibold text-gray-900">Analise IA</h2>
          <button
            onClick={handleAnalyze}
            disabled={analysisMutation.isPending}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 text-sm transition-colors"
          >
            {analysisMutation.isPending ? "Analisando..." : "Analisar com IA"}
          </button>
        </div>
        {analysis ? (
          <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
            {analysis}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">
            Clique em &quot;Analisar com IA&quot; para obter insights sobre esta
            partida.
          </p>
        )}
      </div>

      {/* Delete */}
      <div className="flex justify-end">
        <button
          onClick={handleDelete}
          disabled={deleteMutation.isPending}
          className="px-4 py-2 text-red-600 border border-red-300 rounded-lg hover:bg-red-50 text-sm transition-colors"
        >
          {deleteMutation.isPending ? "Excluindo..." : "Excluir Batalha"}
        </button>
      </div>
    </div>
  );
}
