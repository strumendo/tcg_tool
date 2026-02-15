import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Deck, DeckCreate, DeckImport } from "@/lib/types";

export function useDecks() {
  return useQuery<Deck[]>({
    queryKey: ["decks"],
    queryFn: async () => {
      const { data } = await api.get("/decks");
      return data;
    },
  });
}

export function useDeck(id: number) {
  return useQuery<Deck>({
    queryKey: ["decks", id],
    queryFn: async () => {
      const { data } = await api.get(`/decks/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCreateDeck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (deck: DeckCreate) => {
      const { data } = await api.post("/decks", deck);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useImportDeck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (importData: DeckImport) => {
      const { data } = await api.post("/decks/import", importData);
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useDeleteDeck() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: number) => {
      await api.delete(`/decks/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["decks"] });
    },
  });
}

export function useExportDeck(id: number) {
  return useQuery<string>({
    queryKey: ["decks", id, "export"],
    queryFn: async () => {
      const { data } = await api.get(`/decks/${id}/export`);
      return data;
    },
    enabled: false,
  });
}

export function useDeckMissingCards(id: number) {
  return useQuery({
    queryKey: ["decks", id, "missing"],
    queryFn: async () => {
      const { data } = await api.get(`/decks/${id}/missing-cards`);
      return data;
    },
    enabled: !!id,
  });
}
