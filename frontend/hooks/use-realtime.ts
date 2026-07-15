"use client";

import { useEffect } from "react";
import { useAppStore } from "@/stores/app-store";
import type { RealtimeEvent } from "@/lib/types";

export function useRealtime() {
  const addNotification = useAppStore((state) => state.addNotification);

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_REALTIME_URL;
    if (!url) return;
    const stream = new EventSource(url, { withCredentials: true });
    stream.onmessage = (message) => {
      try {
        addNotification(JSON.parse(message.data) as RealtimeEvent);
      } catch {
        // Ignore malformed external events.
      }
    };
    return () => stream.close();
  }, [addNotification]);
}
