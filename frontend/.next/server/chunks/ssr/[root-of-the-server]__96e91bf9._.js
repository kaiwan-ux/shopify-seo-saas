module.exports = [
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[project]/lib/api/client.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "aiApi",
    ()=>aiApi,
    "api",
    ()=>api,
    "authApi",
    ()=>authApi,
    "seoApi",
    ()=>seoApi,
    "shopifyApi",
    ()=>shopifyApi
]);
const API_URL = ("TURBOPACK compile-time value", "https://academy-gold-consumers-barnes.trycloudflare.com/api/v1") ?? "http://localhost:8000/api/v1";
class ApiClient {
    accessToken = null;
    refreshPromise = null;
    constructor(){
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
    }
    hasAccessToken() {
        if (this.accessToken) return true;
        if ("TURBOPACK compile-time truthy", 1) return false;
        //TURBOPACK unreachable
        ;
    }
    setAccessToken(token) {
        this.accessToken = token;
        if ("TURBOPACK compile-time truthy", 1) return;
        //TURBOPACK unreachable
        ;
    }
    clearSession() {
        this.setAccessToken(null);
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
    }
    async request(path, init = {}) {
        const headers = new Headers(init.headers);
        if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
        if (this.hasAccessToken()) headers.set("Authorization", `Bearer ${this.accessToken}`);
        let response = await fetch(`${API_URL}${path}`, {
            ...init,
            headers,
            credentials: "include"
        });
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        if (!response.ok) {
            const data = await response.json().catch(()=>({
                    detail: "Request failed"
                }));
            const fieldErrors = Array.isArray(data.errors) ? data.errors.map((item)=>item.message || item.field).filter(Boolean).join(". ") : "";
            throw new Error(fieldErrors || data.detail || data.message || "Request failed");
        }
        if (response.status === 204) return undefined;
        return response.json();
    }
    async refresh() {
        if (this.refreshPromise) return this.refreshPromise;
        const refreshToken = ("TURBOPACK compile-time falsy", 0) ? "TURBOPACK unreachable" : null;
        if ("TURBOPACK compile-time truthy", 1) return null;
        //TURBOPACK unreachable
        ;
    }
}
const api = new ApiClient();
const authApi = {
    login: (email, password)=>api.request("/auth/login", {
            method: "POST",
            body: JSON.stringify({
                email,
                password
            })
        }),
    register: (data)=>api.request("/auth/register", {
            method: "POST",
            body: JSON.stringify(data)
        }),
    me: ()=>api.request("/users/me")
};
const shopifyApi = {
    store: ()=>api.request("/shopify/store"),
    connect: (shop_domain)=>api.request("/shopify/connect", {
            method: "POST",
            body: JSON.stringify({
                shop_domain
            })
        }),
    sync: (sync_type = "full")=>api.request("/shopify/sync", {
            method: "POST",
            body: JSON.stringify({
                sync_type
            })
        }),
    products: (limit = 100)=>api.request(`/shopify/products?limit=${limit}`),
    collections: (limit = 100)=>api.request(`/shopify/collections?limit=${limit}`),
    pages: (limit = 100)=>api.request(`/shopify/pages?limit=${limit}`)
};
const seoApi = {
    audit: (store_id, resources)=>api.request("/seo/audit", {
            method: "POST",
            body: JSON.stringify({
                store_id,
                resources
            })
        }),
    technical: (payload)=>api.request("/seo/technical", {
            method: "POST",
            body: JSON.stringify(payload)
        }),
    score: (payload)=>api.request("/seo/score", {
            method: "POST",
            body: JSON.stringify(payload)
        }),
    report: (id)=>api.request(`/seo/report/${id}`)
};
const aiApi = {
    agents: ()=>api.request("/ai/agents"),
    workflow: (workflowId)=>api.request(`/ai/workflow/${workflowId}`),
    runWorkflow: (task, storeId)=>api.request("/ai/workflow/start", {
            method: "POST",
            body: JSON.stringify({
                task,
                store_id: storeId
            })
        }),
    runAgent: (agent_name, task, storeId)=>api.request("/ai/agents/run", {
            method: "POST",
            body: JSON.stringify({
                agent_name,
                task,
                store_id: storeId
            })
        }),
    applyApprovals: (fixes, storeId)=>api.request("/ai/approvals/apply", {
            method: "POST",
            body: JSON.stringify({
                fixes,
                store_id: storeId
            })
        })
};
}),
"[project]/stores/app-store.ts [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAppStore",
    ()=>useAppStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/middleware.mjs [app-ssr] (ecmascript)");
;
;
const idleWorkflow = {
    status: "idle",
    logs: []
};
const idleAudit = {
    status: "idle",
    resourcesAnalyzed: 0,
    findings: []
};
const useAppStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["persist"])((set)=>({
        user: null,
        currentStore: null,
        storeHydrated: false,
        notifications: [],
        sidebarOpen: false,
        compactMode: false,
        workflow: idleWorkflow,
        audit: idleAudit,
        setUser: (user)=>set({
                user
            }),
        setCurrentStore: (currentStore)=>set({
                currentStore
            }),
        setStoreHydrated: (storeHydrated)=>set({
                storeHydrated
            }),
        addNotification: (event)=>set((state)=>({
                    notifications: [
                        event,
                        ...state.notifications
                    ].slice(0, 100)
                })),
        markAllRead: ()=>set({
                notifications: []
            }),
        toggleSidebar: ()=>set((state)=>({
                    sidebarOpen: !state.sidebarOpen
                })),
        setCompactMode: (compactMode)=>set({
                compactMode
            }),
        setWorkflow: (workflow)=>set((state)=>({
                    workflow: {
                        ...state.workflow,
                        ...workflow
                    }
                })),
        appendWorkflowLog: (line)=>set((state)=>({
                    workflow: {
                        ...state.workflow,
                        logs: [
                            line,
                            ...state.workflow.logs
                        ].slice(0, 30)
                    }
                })),
        resetWorkflow: ()=>set({
                workflow: idleWorkflow
            }),
        setAudit: (audit)=>set((state)=>({
                    audit: {
                        ...state.audit,
                        ...audit
                    }
                })),
        resetAudit: ()=>set({
                audit: idleAudit
            }),
        resetWorkspace: ()=>set({
                currentStore: null,
                storeHydrated: false,
                notifications: [],
                workflow: idleWorkflow,
                audit: idleAudit
            })
    }), {
    name: "seo-console",
    partialize: ({ compactMode })=>({
            compactMode
        }),
    merge: (persisted, current)=>({
            ...current,
            compactMode: typeof persisted === "object" && persisted !== null && "compactMode" in persisted ? Boolean(persisted.compactMode) : current.compactMode
        })
}));
}),
"[project]/components/store-bootstrap.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "StoreBootstrap",
    ()=>StoreBootstrap
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/useQuery.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/stores/app-store.ts [app-ssr] (ecmascript)");
"use client";
;
;
;
;
function StoreBootstrap() {
    const queryClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQueryClient"])();
    const setUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppStore"])((state)=>state.setUser);
    const setCurrentStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppStore"])((state)=>state.setCurrentStore);
    const setStoreHydrated = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppStore"])((state)=>state.setStoreHydrated);
    const resetWorkspace = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useAppStore"])((state)=>state.resetWorkspace);
    const previousUserId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useRef"])(null);
    const enabled = "undefined" !== "undefined" && __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["api"].hasAccessToken();
    const user = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "me"
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["authApi"].me,
        enabled,
        staleTime: 0,
        retry: false
    });
    const store = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "store",
            user.data?.id
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["shopifyApi"].store,
        enabled: enabled && !!user.data,
        staleTime: 0,
        retry: false
    });
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if ("TURBOPACK compile-time truthy", 1) {
            setUser(null);
            resetWorkspace();
            queryClient.removeQueries({
                queryKey: [
                    "store"
                ]
            });
            return;
        }
        //TURBOPACK unreachable
        ;
    }, [
        enabled,
        queryClient,
        resetWorkspace,
        setCurrentStore,
        setStoreHydrated,
        setUser
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if (!user.data) return;
        if (previousUserId.current && previousUserId.current !== user.data.id) {
            resetWorkspace();
            queryClient.removeQueries({
                queryKey: [
                    "store"
                ]
            });
            queryClient.removeQueries({
                queryKey: [
                    "products"
                ]
            });
            queryClient.removeQueries({
                queryKey: [
                    "collections"
                ]
            });
            queryClient.removeQueries({
                queryKey: [
                    "pages"
                ]
            });
        }
        previousUserId.current = user.data.id;
        setUser(user.data);
    }, [
        queryClient,
        resetWorkspace,
        setUser,
        user.data
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useEffect"])(()=>{
        if ("TURBOPACK compile-time truthy", 1) return;
        //TURBOPACK unreachable
        ;
    }, [
        enabled,
        setCurrentStore,
        setStoreHydrated,
        store.data,
        store.error,
        user.data
    ]);
    return null;
}
}),
"[project]/components/providers.tsx [app-ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Providers",
    ()=>Providers
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react-jsx-dev-runtime.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/query-core/build/modern/queryClient.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2d$themes$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next-themes/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/server/route-modules/app-page/vendored/ssr/react.js [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/sonner/dist/index.mjs [app-ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$store$2d$bootstrap$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/store-bootstrap.tsx [app-ssr] (ecmascript)");
"use client";
;
;
;
;
;
;
function Providers({ children }) {
    const [queryClient] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["useState"])(()=>new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["QueryClient"]({
            defaultOptions: {
                queries: {
                    staleTime: 60_000,
                    gcTime: 10 * 60_000,
                    retry: 1,
                    refetchOnWindowFocus: false
                },
                mutations: {
                    retry: 0
                }
            }
        }));
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2d$themes$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["ThemeProvider"], {
        attribute: "class",
        defaultTheme: "dark",
        enableSystem: true,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["QueryClientProvider"], {
            client: queryClient,
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$store$2d$bootstrap$2e$tsx__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["StoreBootstrap"], {}, void 0, false, {
                    fileName: "[project]/components/providers.tsx",
                    lineNumber: 22,
                    columnNumber: 9
                }, this),
                children,
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$server$2f$route$2d$modules$2f$app$2d$page$2f$vendored$2f$ssr$2f$react$2d$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$ssr$5d$__$28$ecmascript$29$__["Toaster"], {
                    theme: "system",
                    richColors: true,
                    position: "bottom-right"
                }, void 0, false, {
                    fileName: "[project]/components/providers.tsx",
                    lineNumber: 24,
                    columnNumber: 9
                }, this)
            ]
        }, void 0, true, {
            fileName: "[project]/components/providers.tsx",
            lineNumber: 21,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/components/providers.tsx",
        lineNumber: 20,
        columnNumber: 5
    }, this);
}
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/dynamic-access-async-storage.external.js [external] (next/dist/server/app-render/dynamic-access-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/dynamic-access-async-storage.external.js", () => require("next/dist/server/app-render/dynamic-access-async-storage.external.js"));

module.exports = mod;
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__96e91bf9._.js.map