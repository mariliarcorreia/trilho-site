import Image from "next/image";
import Link from "next/link";
import { Linkedin, Instagram, Facebook } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-noite text-branco/60 border-t border-branco/10">
      <div className="mx-auto max-w-7xl px-6 lg:px-10 py-14 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-8">
        <Image
          src="/images/logo-branca.png"
          alt="Trilho Consultoria"
          width={280}
          height={140}
          className="h-16 w-auto"
        />

        <div className="flex flex-wrap items-center gap-7">
          <a
            href="#"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Facebook"
            className="hover:text-dourado-claro transition-colors"
          >
            <Facebook size={32} />
          </a>
          <a
            href="#"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Instagram"
            className="hover:text-dourado-claro transition-colors"
          >
            <Instagram size={32} />
          </a>
          <a
            href="https://www.linkedin.com/company/trilhoconsultoria"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="LinkedIn"
            className="hover:text-dourado-claro transition-colors"
          >
            <Linkedin size={32} />
          </a>
          <Link
            href="/area-cliente"
            className="text-sm border border-branco/20 rounded-full px-5 py-2.5 hover:border-dourado-claro hover:text-dourado-claro transition-colors"
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
