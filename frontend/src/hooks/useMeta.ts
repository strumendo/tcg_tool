import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { MetaDeck, MetaMatchup } from "@/lib/types";

export function useMetaDecks() {
  return useQuery<MetaDeck[]>({
    queryKey: ["meta", "decks"],
    queryFn: async () => {
      const { data } = await api.get("/meta/decks");
      return data;
    },
  });
}

export function useMetaDeck(id: string) {
  return useQuery<MetaDeck>({
    queryKey: ["meta", "decks", id],
    queryFn: async () => {
      const { data } = await api.get(`/meta/decks/${id}`);
      return data;
    },
    enabled: !!id,
  });
}

export function useMetaMatchups() {
  return useQuery<MetaMatchup[]>({
    queryKey: ["meta", "matchups"],
    queryFn: async () => {
      const { data } = await api.get("/meta/matchups");
      return data;
    },
  });
}

export function useMetaTiers() {
  return useQuery({
    queryKey: ["meta", "tiers"],
    queryFn: async () => {
      const { data } = await api.get("/meta/tiers");
      return data;
    },
  });
}
