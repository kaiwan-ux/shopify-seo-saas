"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { api, authApi, shopifyApi } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";

export function StoreBootstrap() {
  const queryClient = useQueryClient();
  const setUser = useAppStore((state) => state.setUser);
  const setCurrentStore = useAppStore((state) => state.setCurrentStore);
  const setStoreHydrated = useAppStore((state) => state.setStoreHydrated);
  const resetWorkspace = useAppStore((state) => state.resetWorkspace);
  const previousUserId = useRef<string | null>(null);

  const enabled = typeof window !== "undefined" && api.hasAccessToken();

  const user = useQuery({
    queryKey: ["me"],
    queryFn: authApi.me,
    enabled,
    staleTime: 0,
    retry: false,
  });

  const store = useQuery({
    queryKey: ["store", user.data?.id],
    queryFn: shopifyApi.store,
    enabled: enabled && !!user.data,
    staleTime: 0,
    retry: false,
  });

  useEffect(() => {
    if (!enabled) {
      setUser(null);
      resetWorkspace();
      queryClient.removeQueries({ queryKey: ["store"] });
      return;
    }
    setCurrentStore(null);
    setStoreHydrated(false);
  }, [enabled, queryClient, resetWorkspace, setCurrentStore, setStoreHydrated, setUser]);

  useEffect(() => {
    if (!user.data) return;
    if (previousUserId.current && previousUserId.current !== user.data.id) {
      resetWorkspace();
      queryClient.removeQueries({ queryKey: ["store"] });
      queryClient.removeQueries({ queryKey: ["products"] });
      queryClient.removeQueries({ queryKey: ["collections"] });
      queryClient.removeQueries({ queryKey: ["pages"] });
    }
    previousUserId.current = user.data.id;
    setUser(user.data);
  }, [queryClient, resetWorkspace, setUser, user.data]);

  useEffect(() => {
    if (!enabled || !user.data) return;
    if (store.data) {
      setCurrentStore(store.data);
      setStoreHydrated(true);
      return;
    }
    if (store.error) {
      setCurrentStore(null);
      setStoreHydrated(true);
    }
  }, [enabled, setCurrentStore, setStoreHydrated, store.data, store.error, user.data]);

  return null;
}
