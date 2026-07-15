"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { AuthShell } from "@/components/auth/auth-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { authApi } from "@/lib/api/client";

const schema = z.object({
  full_name: z.string().trim().min(2, "Enter your name"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(8, "Use at least 8 characters").regex(/[A-Z]/, "Add one uppercase letter").regex(/[a-z]/, "Add one lowercase letter").regex(/[0-9]/, "Add one number"),
});
type RegisterForm = z.infer<typeof schema>;

export default function RegisterPage() {
  const router = useRouter();
  const form = useForm<RegisterForm>({ resolver: zodResolver(schema) });
  const register = useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success("Account created");
      router.push("/login");
    },
    onError: (error) => toast.error(error.message),
  });

  return (
    <AuthShell
      title="Create your workspace"
      description="Connect a store and begin with a clear baseline."
      footer={<>Already have an account? <Link className="text-foreground underline underline-offset-4" href="/login">Sign in</Link></>}
    >
      <form className="space-y-4" onSubmit={form.handleSubmit((values) => register.mutate(values))}>
        {[
          ["full_name", "Full name", "Your name", "text"],
          ["email", "Work email", "you@company.com", "email"],
          ["password", "Password", "8+ chars, uppercase, lowercase, number", "password"],
        ].map(([name, label, placeholder, type]) => (
          <label key={name} className="block space-y-2 text-sm font-medium">
            <span>{label}</span>
            <Input type={type} placeholder={placeholder} {...form.register(name as keyof RegisterForm)} />
            {form.formState.errors[name as keyof RegisterForm] && (
              <span className="text-xs text-red-500">{form.formState.errors[name as keyof RegisterForm]?.message}</span>
            )}
          </label>
        ))}
        <Button className="mt-2 w-full" size="lg" disabled={register.isPending}>
          {register.isPending && <Loader2 className="h-4 w-4 animate-spin" />} Create account
        </Button>
        <p className="text-center text-[11px] leading-5 text-muted-foreground">By continuing, you agree to the product terms and privacy policy.</p>
      </form>
    </AuthShell>
  );
}

