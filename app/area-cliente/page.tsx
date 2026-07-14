import Link from "next/link";
import Image from "next/image";

export default function AreaCliente() {
  return (
    <main className="min-h-screen bg-noite flex flex-col items-center justify-center px-6">
      <div className="w-full max-w-sm flex flex-col items-center gap-8">
        <Link href="/">
          <Image
            src="/images/logo-trilho.png"
            alt="Trilho Consultoria"
            width={180}
            height={90}
            className="h-10 w-auto brightness-0 invert"
          />
        </Link>

        <div className="w-full bg-grafite/40 border border-branco/10 rounded-2xl p-8 flex flex-col gap-5">
          <h1 className="font-display text-2xl text-branco text-center">
            Área do Cliente
          </h1>

          <div className="flex flex-col gap-3">
            <label className="text-sm text-branco/60">E-mail</label>
            <input
              type="email"
              placeholder="seu@email.com"
              className="bg-transparent border border-branco/20 rounded-lg px-4 py-3 text-branco placeholder:text-branco/30 focus:border-dourado-claro outline-none transition-colors"
            />
          </div>

          <div className="flex flex-col gap-3">
            <label className="text-sm text-branco/60">Senha</label>
            <input
              type="password"
              placeholder="••••••••"
              className="bg-transparent border border-branco/20 rounded-lg px-4 py-3 text-branco placeholder:text-branco/30 focus:border-dourado-claro outline-none transition-colors"
            />
          </div>

          <button
            className="w-full bg-dourado-claro text-noite font-medium py-3 rounded-full hover:bg-dourado transition-colors mt-1"
          >
            Entrar
          </button>

          <p className="text-center text-xs text-branco/30">
            Acesso restrito a clientes da Trilho Consultoria.
            <br />
            Problemas? Entre em contato pelo{" "}
            <a
              href="https://wa.me/5534991270137"
              className="text-dourado-claro hover:underline"
            >
              WhatsApp
            </a>
            .
          </p>
        </div>

        <Link
          href="/"
          className="text-sm text-branco/40 hover:text-branco/70 transition-colors"
        >
          ← Voltar ao site
        </Link>
      </div>
    </main>
  );
}
