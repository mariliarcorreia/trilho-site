import Image from "next/image";
import Link from "next/link";
import { Linkedin, Youtube, MessageCircle } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-noite text-branco/60 border-t border-branco/10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10 py-12 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-8">
        <Image
          src="/images/logo-branca.png"
          alt="Trilho Consultoria"
          width={200}
          height={100}
          className="h-12 w-auto"
        />

        <div className="flex flex-wrap items-center gap-5">
          <a
            href="https://www.linkedin.com/in/alexandre-faleiros"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn Alexandre Faleiros"
            className="hover:text-dourado-claro transition-colors"
          >
            <Linkedin size={22} />
          </a>
          <a
            href="https://www.linkedin.com/in/will-sales"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn William Sales"
            className="hover:text-dourado-claro transition-colors"
          >
            <Linkedin size={22} />
          </a>
          <a
            href="https://www.youtube.com/@trilhoconsultoria"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="YouTube"
            className="hover:text-dourado-claro transition-colors"
          >
            <Youtube size={22} />
          </a>
          <a
            href="https://wa.me/5534991270137"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="WhatsApp"
            className="hover:text-dourado-claro transition-colors"
          >
            <MessageCircle size={22} />
          </a>
          <Link
            href="/area-cliente"
            className="text-sm border border-branco/20 rounded-full px-4 py-2 hover:border-dourado-claro hover:text-dourado-claro transition-colors"
          >
            Área do Cliente
          </Link>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-6 lg:px-10 pb-8 text-xs text-branco/35">
        © {new Date().getFullYear()} Trilho Consultoria em Recrutamento &
        Seleção. CNPJ 66.585.378/0001-02.
      </div>
    </footer>
  );
}
