"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X } from "lucide-react";

const NAV_LINKS = [
  { label: "QUEM SOMOS", href: "#quem-somos" },
  { label: "SERVIÇOS", href: "#servicos" },
  { label: "DIFERENCIAIS", href: "#diferenciais" },
  { label: "EQUIPE", href: "#equipe" },
  { label: "CLIENTES", href: "#clientes" },
  { label: "CONTATO", href: "#contato" },
];

const VAGAS_URL = "#";

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-noite">
      <div className="mx-auto max-w-7xl px-6 lg:px-10 flex items-center justify-between h-24">
        <a href="#topo" className="flex items-center shrink-0">
          <Image
            src="/images/logo-branca.png"
            alt="Trilho Consultoria"
            width={280}
            height={140}
            className="h-16 w-auto"
            priority
          />
        </a>

        <nav className="hidden lg:flex items-center gap-8">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-branco/80 hover:text-dourado-claro transition-colors tracking-wide"
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden lg:flex items-center gap-4">
          <a
            href="/area-cliente"
            className="text-sm text-branco/70 hover:text-dourado-claro transition-colors"
          >
            ÁREA DO CLIENTE
          </a>
          <a
            href={VAGAS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-noite bg-dourado-claro hover:bg-dourado px-5 py-2.5 rounded-full transition-colors"
          >
            VAGAS ABERTAS
          </a>
        </div>

        <button
          onClick={() => setMenuOpen(true)}
          className="lg:hidden text-branco p-2"
          aria-label="Abrir menu"
        >
          <Menu size={28} />
        </button>
      </div>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-noite lg:hidden"
          >
            <div className="flex items-center justify-between h-24 px-6">
              <Image
                src="/images/logo-branca.png"
                alt="Trilho Consultoria"
                width={240}
                height={120}
                className="h-14 w-auto"
              />
              <button
                onClick={() => setMenuOpen(false)}
                className="text-branco p-2"
                aria-label="Fechar menu"
              >
                <X size={28} />
              </button>
            </div>
            <nav className="flex flex-col px-8 pt-6 gap-1">
              {NAV_LINKS.map((link, i) => (
                <motion.a
                  key={link.href}
                  href={link.href}
                  onClick={() => setMenuOpen(false)}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.05 * i }}
                  className="text-branco text-2xl font-display py-3 border-b border-branco/10"
                >
                  {link.label}
                </motion.a>
              ))}
              <motion.a
                href={VAGAS_URL}
                onClick={() => setMenuOpen(false)}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * NAV_LINKS.length }}
                className="mt-6 text-center text-noite font-medium bg-dourado-claro px-5 py-3 rounded-full"
              >
                VAGAS ABERTAS
              </motion.a>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
