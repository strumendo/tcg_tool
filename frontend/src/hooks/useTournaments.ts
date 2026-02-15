import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Tournament, NewsArticle } from "@/lib/types";

export function useTournaments(format: string = "Standard") {
  return useQuery<Tournament[]>({
    queryKey: ["tournaments", format],
    queryFn: async () => {
      const { data } = await api.get("/tournaments", { params: { format, limit: 50 } });
      return data;
    },
  });
}

export function useNews(limit: number = 20) {
  return useQuery<NewsArticle[]>({
    queryKey: ["news", limit],
    queryFn: async () => {
      const { data } = await api.get("/tournaments/news", { params: { limit } });
      return data;
    },
  });
}
