"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ArrowRight, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { api, authApi } from "@/lib/api/client";
import { useAppStore } from "@/stores/app-store";

const schema = z.object({ email: z.string().email("Enter a valid email"), password: z.string().min(8, "Use at least 8 characters") });
type LoginForm = z.infer<typeof schema>;

export default function LoginPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const setUser = useAppStore((state) => state.setUser);
  const setCurrentStore = useAppStore((state) => state.setCurrentStore);
  const setStoreHydrated = useAppStore((state) => state.setStoreHydrated);
  const resetWorkspace = useAppStore((state) => state.resetWorkspace);
  const form = useForm<LoginForm>({ resolver: zodResolver(schema) });
  const login = useMutation({
    mutationFn: async (values: LoginForm) => {
      const tokens = await authApi.login(values.email, values.password);
      api.setAccessToken(tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      const user = await authApi.me();
      return user;
    },
    onSuccess: async (user) => {
      queryClient.clear();
      resetWorkspace();
      setUser(user);
      setCurrentStore(null);
      setStoreHydrated(false);
      document.cookie = "seo_session=active; path=/; SameSite=Lax";
      toast.success("Signed in");
      router.push("/dashboard");
    },
    onError: (error) => toast.error(error.message),
  });

  return (
    <AuthShell title="Welcome back" description="Continue to your SEO command center." footer={<>New here? <Link className="text-foreground underline underline-offset-4" href="/register">Create an account</Link></>}>
      <form className="space-y-5" onSubmit={form.handleSubmit((values) => login.mutate(values))}>
        <label className="block space-y-2 text-sm font-medium"><span>Email</span><Input placeholder="you@company.com" autoComplete="email" {...form.register("email")} />{form.formState.errors.email && <span className="text-xs text-red-500">{form.formState.errors.email.message}</span>}</label>
        <label className="block space-y-2 text-sm font-medium"><span className="flex justify-between">Password<Link href="/forgot-password" className="font-normal text-muted-foreground hover:text-foreground">Forgot password?</Link></span><Input type="password" autoComplete="current-password" {...form.register("password")} />{form.formState.errors.password && <span className="text-xs text-red-500">{form.formState.errors.password.message}</span>}</label>
        <Button className="w-full" size="lg" disabled={login.isPending}>{login.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <>Sign in <ArrowRight className="h-4 w-4" /></>}</Button>
      </form>
    </AuthShell>
  );
}


