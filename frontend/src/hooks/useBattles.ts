import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Battle, BattleCreate } from "@/lib/types";

export function useBattles() {
  return useQuery<Battle[]>({
    queryKey: ["battles"],
    queryFn: async () => {
      const { data } = await api.get("/battles");
      return data;
    },
  });
}

export function useBattle(id: number) {
  return useQuery<Battle>({
    queryKey: ["battles", id],
    queryFn: async () => {
      const { data } = await api.get(`/battles/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateBattle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (battle: BattleCreate) => {
      const { data } = await api.post("/battles", battle);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["battles"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}

export function useDeleteBattle() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/battles/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["battles"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}

export function useBattleAnalysis(battleId: number) {
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post(`/battles/${battleId}/analyze`);
      return data as { battle_id: number; analysis: string };
    },
  });
}

export function useBattleStats() {
  return useQuery({
    queryKey: ["stats", "battles"],
    queryFn: async () => {
      const { data } = await api.get("/stats/battles");
      return data;
    },
  });
}
