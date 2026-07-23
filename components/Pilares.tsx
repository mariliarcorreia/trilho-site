"use client";

import { motion } from "framer-motion";
import { Target, Eye, Gem } from "lucide-react";

const PILARES = [
  {
    icon: Target,
    titulo: "Missão",
    texto:
      "Proporcionar os melhores talentos e soluções para que as empresas atinjam seus objetivos e gerenciem seus negócios e recursos, além de buscar as melhores oportunidades para os profissionais que procuram um novo desafio em suas carreiras.",
    bg: "#0D0D0D",
    iconBg: "#9A7B3A",
    iconColor: "#0D0D0D",
    textColor: "#FFFFFF",
  },
  {
    icon: Eye,
    titulo: "Visão",
    texto:
      "Ser referência no mercado de Recrutamento & Seleção em agronegócio, indústria e no segmento de papel e celulose.",
    bg: "#9A7B3A",
    iconBg: "#0D0D0D",
    iconColor: "#C9A86A",
    textColor: "#FFFFFF",
  },
  {
    icon: Gem,
    titulo: "Valores",
    texto: "Integridade · Respeito · Qualidade · Conexão · Resultado",
    bg: "#F5F3EE",
    iconBg: "#9A7B3A",
    iconColor: "#FFFFFF",
    textColor: "#0D0D0D",
  },
];

export default function Pilares() {
  return (
    <section className="bg-pedra py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mb-16 text-center"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase font-bold">
            Nossa Essência
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 leading-tight">
            O que nos guia todos os dias.
          </h2>
        </motion.div>

        {/* Força 3 colunas sempre no desktop */}
        <div className="grid grid-cols-1 sm:grid-cols-3 rounded-2xl overflow-hidden shadow-xl">
          {PILARES.map((p, i) => (
            <motion.div
              key={p.titulo}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.15 }}
              whileHover={{ y: -8 }}
              style={{ backgroundColor: p.bg }}
              className="relative flex flex-col items-center text-center gap-7 px-10 py-14 cursor-default transition-all duration-300 hover:shadow-2xl"
            >
              <motion.div
                whileHover={{ rotate: 12, scale: 1.2 }}
                transition={{ type: "spring", stiffness: 280 }}
                style={{ backgroundColor: p.iconBg }}
                className="w-28 h-28 rounded-full flex items-center justify-center shrink-0"
              >
                <p.icon size={56} strokeWidth={1.2} color={p.iconColor} />
              </motion.div>

              <h3
                style={{ color: p.textColor }}
                className="font-display text-2xl font-semibold uppercase tracking-[0.2em]"
              >
                {p.titulo}
              </h3>

              <div
                style={{ backgroundColor: p.iconBg }}
                className="w-14 h-[3px] rounded-full"
              />

              <p style={{ color: p.textColor }} className="text-sm leading-relaxed opacity-85">
                {p.texto}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
