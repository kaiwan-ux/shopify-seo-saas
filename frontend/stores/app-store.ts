import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Issue, RealtimeEvent, Store, User } from "@/lib/types";

export type OperationStatus = "idle" | "running" | "completed" | "failed" | "waiting_approval";

export interface WorkflowOperation {
  id?: string;
  task?: string;
  status: OperationStatus;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  logs: string[];
  result?: unknown;
}

export interface AuditOperation {
  status: OperationStatus;
  startedAt?: string;
  completedAt?: string;
  error?: string;
  resourcesAnalyzed: number;
  findings: Issue[];
  summary?: string;
}

const idleWorkflow: WorkflowOperation = { status: "idle", logs: [] };
const idleAudit: AuditOperation = { status: "idle", resourcesAnalyzed: 0, findings: [] };

interface AppState {
  user: User | null;
  currentStore: Store | null;
  storeHydrated: boolean;
  notifications: RealtimeEvent[];
  sidebarOpen: boolean;
  compactMode: boolean;
  workflow: WorkflowOperation;
  audit: AuditOperation;
  setUser: (user: User | null) => void;
  setCurrentStore: (store: Store | null) => void;
  setStoreHydrated: (hydrated: boolean) => void;
  addNotification: (event: RealtimeEvent) => void;
  markAllRead: () => void;
  toggleSidebar: () => void;
  setCompactMode: (compact: boolean) => void;
  setWorkflow: (workflow: Partial<WorkflowOperation>) => void;
  appendWorkflowLog: (line: string) => void;
  resetWorkflow: () => void;
  setAudit: (audit: Partial<AuditOperation>) => void;
  resetAudit: () => void;
  resetWorkspace: () => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      currentStore: null,
      storeHydrated: false,
      notifications: [],
      sidebarOpen: false,
      compactMode: false,
      workflow: idleWorkflow,
      audit: idleAudit,
      setUser: (user) => set({ user }),
      setCurrentStore: (currentStore) => set({ currentStore }),
      setStoreHydrated: (storeHydrated) => set({ storeHydrated }),
      addNotification: (event) =>
        set((state) => ({ notifications: [event, ...state.notifications].slice(0, 100) })),
      markAllRead: () => set({ notifications: [] }),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setCompactMode: (compactMode) => set({ compactMode }),
      setWorkflow: (workflow) => set((state) => ({ workflow: { ...state.workflow, ...workflow } })),
      appendWorkflowLog: (line) =>
        set((state) => ({ workflow: { ...state.workflow, logs: [line, ...state.workflow.logs].slice(0, 30) } })),
      resetWorkflow: () => set({ workflow: idleWorkflow }),
      setAudit: (audit) => set((state) => ({ audit: { ...state.audit, ...audit } })),
      resetAudit: () => set({ audit: idleAudit }),
      resetWorkspace: () => set({ currentStore: null, storeHydrated: false, notifications: [], workflow: idleWorkflow, audit: idleAudit }),
    }),
    {
      name: "seo-console",
      partialize: ({ compactMode }) => ({ compactMode }),
      merge: (persisted, current) => ({
        ...current,
        compactMode: typeof persisted === "object" && persisted !== null && "compactMode" in persisted ? Boolean((persisted as { compactMode?: boolean }).compactMode) : current.compactMode,
      }),
    },
  ),
);




