"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CollectionEntry, MissingCard } from "@/lib/types";
import { useMemo } from "react";

export function useCollection() {
  return useQuery<CollectionEntry[]>({
    queryKey: ["collection"],
    queryFn: async () => {
      const { data } = await api.get("/collection");
      return data;
    },
  });
}

export function useCollectionMissing(deckId: number | null) {
  return useQuery<MissingCard[]>({
    queryKey: ["collection", "missing", deckId],
    queryFn: async () => {
      const { data } = await api.get(`/collection/missing/${deckId}`);
      return data;
    },
    enabled: deckId !== null && deckId > 0,
  });
}

export function useUpdateCollection() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      cardId,
      quantity,
    }: {
      cardId: number;
      quantity: number;
    }) => {
      const { data } = await api.put(`/collection/${cardId}`, {
        quantity_owned: quantity,
      });
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["collection"] });
    },
  });
}

export function useCollectionStats() {
  const { data: collection, isLoading } = useCollection();

  const stats = useMemo(() => {
    if (!collection) {
      return {
        totalUnique: 0,
        totalCopies: 0,
        missingCount: 0,
      };
    }

    const totalUnique = collection.length;
    const totalCopies = collection.reduce(
      (sum, entry) => sum + entry.quantity_owned,
      0
    );

    return {
      totalUnique,
      totalCopies,
      missingCount: 0,
    };
  }, [collection]);

  return { stats, isLoading };
}
