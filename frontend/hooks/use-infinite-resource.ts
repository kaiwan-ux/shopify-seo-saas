import { useInfiniteQuery } from "@tanstack/react-query";
import { api } from "@/lib/api/client";

interface Page<T> {
  items: T[];
  next_page: number | null;
}

export function useInfiniteResource<T>(key: string, path: string) {
  return useInfiniteQuery({
    queryKey: [key],
    queryFn: ({ pageParam }) => api.request<Page<T>>(`${path}?page=${pageParam}`),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => lastPage.next_page ?? undefined,
  });
}
