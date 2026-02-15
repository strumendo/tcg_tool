import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Card, CardUsageStats } from "@/lib/types";

export function useCardSearch(query: string, filters?: Record<string, string>) {
  return useQuery<Card[]>({
    queryKey: ["cards", "search", query, filters],
    queryFn: async () => {
      const params = { q: query, ...filters };
      const { data } = await api.get("/cards", { params });
      return data;
    },
    enabled: query.length >= 2,
  });
}

export function useCard(id: number) {
  return useQuery<Card>({
    queryKey: ["cards", id],
    queryFn: async () => {
      const { data } = await api.get(`/cards/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCardAlternatives(id: number) {
  return useQuery<Card[]>({
    queryKey: ["cards", id, "alternatives"],
    queryFn: async () => {
      const { data } = await api.get(`/cards/${id}/alternatives`);
      return data;
    },
    enabled: !!id,
  });
}

export function useCardUsage(id: number) {
  return useQuery<CardUsageStats>({
    queryKey: ["cards", id, "usage"],
    queryFn: async () => {
      const { data } = await api.get(`/cards/${id}/usage`);
      return data;
    },
    enabled: !!id,
  });
}

export function useAbilityCategories() {
  return useQuery<string[]>({
    queryKey: ["cards", "abilities"],
    queryFn: async () => {
      const { data } = await api.get("/cards/abilities");
      return data;
    },
  });
}
