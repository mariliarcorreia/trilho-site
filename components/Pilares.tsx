"use client";

import { motion } from "framer-motion";
import { Target, Eye, Compass } from "lucide-react";

const PILARES = [
  {
    icon: Target,
    titulo: "Missão",
    texto:
      "Proporcionar os melhores talentos e soluções para que as empresas atinjam seus objetivos e gerenciem seus negócios e recursos, além de buscar as melhores oportunidades para os profissionais que procuram um novo desafio em suas carreiras.",
  },
  {
    icon: Eye,
    titulo: "Visão",
    texto:
      "Ser referência no mercado de Recrutamento & Seleção em agronegócio, indústria e no segmento de papel e celulose.",
  },
  {
    icon: Compass,
    titulo: "Valores",
    texto: "Integridade · Respeito · Qualidade · Conexão · Resultado",
  },
];

export default function Pilares() {
  return (
    <section className="bg-pedra py-24 lg:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <div className="grid md:grid-cols-3 gap-px bg-linha rounded-2xl overflow-hidden">
          {PILARES.map((p, i) => (
            <motion.div
              key={p.titulo}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="bg-pedra p-10 flex flex-col gap-5"
            >
              <p.icon className="text-dourado" size={28} strokeWidth={1.5} />
              <h3 className="font-display text-2xl font-medium">{p.titulo}</h3>
              <p className="text-grafite leading-relaxed">{p.texto}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
