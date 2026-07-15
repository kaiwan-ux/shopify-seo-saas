(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/lib/api/client.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$swc$2f$helpers$2f$esm$2f$_define_property$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@swc/helpers/esm/_define_property.js [app-client] (ecmascript)");
;
var _process_env_NEXT_PUBLIC_API_URL;
const API_URL = (_process_env_NEXT_PUBLIC_API_URL = ("TURBOPACK compile-time value", "https://academy-gold-consumers-barnes.trycloudflare.com/api/v1")) !== null && _process_env_NEXT_PUBLIC_API_URL !== void 0 ? _process_env_NEXT_PUBLIC_API_URL : "http://localhost:8000/api/v1";
class ApiClient {
    hasAccessToken() {
        if (this.accessToken) return true;
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        this.accessToken = localStorage.getItem("access_token");
        return Boolean(this.accessToken);
    }
    setAccessToken(token) {
        this.accessToken = token;
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        if (token) localStorage.setItem("access_token", token);
        else localStorage.removeItem("access_token");
    }
    clearSession() {
        this.setAccessToken(null);
        if ("TURBOPACK compile-time truthy", 1) {
            localStorage.removeItem("refresh_token");
            document.cookie = "seo_session=; path=/; max-age=0; SameSite=Lax";
        }
    }
    async request(path) {
        let init = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {};
        const headers = new Headers(init.headers);
        if (!(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
        if (this.hasAccessToken()) headers.set("Authorization", "Bearer ".concat(this.accessToken));
        let response = await fetch("".concat(API_URL).concat(path), {
            ...init,
            headers,
            credentials: "include"
        });
        if (response.status === 401 && "object" !== "undefined") {
            const token = await this.refresh();
            if (token) {
                headers.set("Authorization", "Bearer ".concat(token));
                response = await fetch("".concat(API_URL).concat(path), {
                    ...init,
                    headers,
                    credentials: "include"
                });
            }
        }
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
        const refreshToken = ("TURBOPACK compile-time truthy", 1) ? localStorage.getItem("refresh_token") : "TURBOPACK unreachable";
        if (!refreshToken) return null;
        this.refreshPromise = fetch("".concat(API_URL, "/auth/refresh"), {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                refresh_token: refreshToken
            })
        }).then(async (response)=>{
            if (!response.ok) {
                this.clearSession();
                return null;
            }
            const tokens = await response.json();
            this.setAccessToken(tokens.access_token);
            localStorage.setItem("refresh_token", tokens.refresh_token);
            return tokens.access_token;
        }).finally(()=>{
            this.refreshPromise = null;
        });
        return this.refreshPromise;
    }
    constructor(){
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$swc$2f$helpers$2f$esm$2f$_define_property$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["_"])(this, "accessToken", null);
        (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$swc$2f$helpers$2f$esm$2f$_define_property$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["_"])(this, "refreshPromise", null);
        if ("TURBOPACK compile-time truthy", 1) this.accessToken = localStorage.getItem("access_token");
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
    sync: function() {
        let sync_type = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "full";
        return api.request("/shopify/sync", {
            method: "POST",
            body: JSON.stringify({
                sync_type
            })
        });
    },
    products: function() {
        let limit = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 100;
        return api.request("/shopify/products?limit=".concat(limit));
    },
    collections: function() {
        let limit = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 100;
        return api.request("/shopify/collections?limit=".concat(limit));
    },
    pages: function() {
        let limit = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : 100;
        return api.request("/shopify/pages?limit=".concat(limit));
    }
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
    report: (id)=>api.request("/seo/report/".concat(id))
};
const aiApi = {
    agents: ()=>api.request("/ai/agents"),
    workflow: (workflowId)=>api.request("/ai/workflow/".concat(workflowId)),
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/stores/app-store.ts [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAppStore",
    ()=>useAppStore
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/react.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/zustand/esm/middleware.mjs [app-client] (ecmascript)");
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
const useAppStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$react$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["create"])()((0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$zustand$2f$esm$2f$middleware$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["persist"])((set)=>({
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
    partialize: (param)=>{
        let { compactMode } = param;
        return {
            compactMode
        };
    },
    merge: (persisted, current)=>({
            ...current,
            compactMode: typeof persisted === "object" && persisted !== null && "compactMode" in persisted ? Boolean(persisted.compactMode) : current.compactMode
        })
}));
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/store-bootstrap.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "StoreBootstrap",
    ()=>StoreBootstrap
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/useQuery.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/lib/api/client.ts [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/stores/app-store.ts [app-client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
function StoreBootstrap() {
    var _user_data;
    _s();
    const queryClient = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQueryClient"])();
    const setUser = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"])({
        "StoreBootstrap.useAppStore[setUser]": (state)=>state.setUser
    }["StoreBootstrap.useAppStore[setUser]"]);
    const setCurrentStore = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"])({
        "StoreBootstrap.useAppStore[setCurrentStore]": (state)=>state.setCurrentStore
    }["StoreBootstrap.useAppStore[setCurrentStore]"]);
    const setStoreHydrated = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"])({
        "StoreBootstrap.useAppStore[setStoreHydrated]": (state)=>state.setStoreHydrated
    }["StoreBootstrap.useAppStore[setStoreHydrated]"]);
    const resetWorkspace = (0, __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"])({
        "StoreBootstrap.useAppStore[resetWorkspace]": (state)=>state.resetWorkspace
    }["StoreBootstrap.useAppStore[resetWorkspace]"]);
    const previousUserId = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const enabled = "object" !== "undefined" && __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["api"].hasAccessToken();
    const user = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "me"
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["authApi"].me,
        enabled,
        staleTime: 0,
        retry: false
    });
    const store = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"])({
        queryKey: [
            "store",
            (_user_data = user.data) === null || _user_data === void 0 ? void 0 : _user_data.id
        ],
        queryFn: __TURBOPACK__imported__module__$5b$project$5d2f$lib$2f$api$2f$client$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["shopifyApi"].store,
        enabled: enabled && !!user.data,
        staleTime: 0,
        retry: false
    });
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "StoreBootstrap.useEffect": ()=>{
            if (!enabled) {
                setUser(null);
                resetWorkspace();
                queryClient.removeQueries({
                    queryKey: [
                        "store"
                    ]
                });
                return;
            }
            setCurrentStore(null);
            setStoreHydrated(false);
        }
    }["StoreBootstrap.useEffect"], [
        enabled,
        queryClient,
        resetWorkspace,
        setCurrentStore,
        setStoreHydrated,
        setUser
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "StoreBootstrap.useEffect": ()=>{
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
        }
    }["StoreBootstrap.useEffect"], [
        queryClient,
        resetWorkspace,
        setUser,
        user.data
    ]);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "StoreBootstrap.useEffect": ()=>{
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
        }
    }["StoreBootstrap.useEffect"], [
        enabled,
        setCurrentStore,
        setStoreHydrated,
        store.data,
        store.error,
        user.data
    ]);
    return null;
}
_s(StoreBootstrap, "rSEtxS+GtCSXzot4NwYasuuipjg=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQueryClient"],
        __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$stores$2f$app$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useAppStore"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"],
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$useQuery$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useQuery"]
    ];
});
_c = StoreBootstrap;
var _c;
__turbopack_context__.k.register(_c, "StoreBootstrap");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/providers.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "Providers",
    ()=>Providers
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/query-core/build/modern/queryClient.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/@tanstack/react-query/build/modern/QueryClientProvider.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2d$themes$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next-themes/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/sonner/dist/index.mjs [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$store$2d$bootstrap$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/store-bootstrap.tsx [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
;
;
function Providers(param) {
    let { children } = param;
    _s();
    const [queryClient] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])({
        "Providers.useState": ()=>new __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$query$2d$core$2f$build$2f$modern$2f$queryClient$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["QueryClient"]({
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
            })
    }["Providers.useState"]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2d$themes$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["ThemeProvider"], {
        attribute: "class",
        defaultTheme: "dark",
        enableSystem: true,
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f40$tanstack$2f$react$2d$query$2f$build$2f$modern$2f$QueryClientProvider$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["QueryClientProvider"], {
            client: queryClient,
            children: [
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$store$2d$bootstrap$2e$tsx__$5b$app$2d$client$5d$__$28$ecmascript$29$__["StoreBootstrap"], {}, void 0, false, {
                    fileName: "[project]/components/providers.tsx",
                    lineNumber: 22,
                    columnNumber: 9
                }, this),
                children,
                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$sonner$2f$dist$2f$index$2e$mjs__$5b$app$2d$client$5d$__$28$ecmascript$29$__["Toaster"], {
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
_s(Providers, "b2mJLvFzsv1ynYM37Mr/heXe1FM=");
_c = Providers;
var _c;
__turbopack_context__.k.register(_c, "Providers");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
]);

//# sourceMappingURL=_7fe9d036._.js.map