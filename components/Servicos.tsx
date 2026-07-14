"use client";

import { motion } from "framer-motion";

const SERVICOS = [
  {
    titulo: "Recrutamento & Seleção",
    texto:
      "Processos seletivos completos, do mapeamento do perfil ideal à integração do profissional aprovado.",
  },
  {
    titulo: "Hunting Executivo",
    texto:
      "Busca ativa de lideranças e especialistas para posições estratégicas, com abordagem direta e discreta.",
  },
  {
    titulo: "Treinamentos",
    texto:
      "Capacitação corporativa online e presencial, desenvolvida para as demandas reais de cada equipe.",
  },
  {
    titulo: "Consultoria",
    texto:
      "Apoio estratégico em gestão de pessoas, estruturação de processos seletivos e diagnóstico de RH.",
  },
];

export default function Servicos() {
  return (
    <section id="servicos" className="bg-noite text-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl mb-16"
        >
          <span className="text-dourado-claro text-sm tracking-[0.2em] uppercase">
            Serviços
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 leading-tight">
            Soluções completas em gestão de talentos.
          </h2>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-x-10">
          {SERVICOS.map((s, i) => (
            <motion.div
              key={s.titulo}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="py-9 border-t border-branco/15 first:border-t-0 sm:first:border-t sm:nth-[2]:border-t-0"
            >
              <h3 className="font-display text-xl sm:text-2xl font-medium mb-3">
                {s.titulo}
              </h3>
              <p className="text-branco/65 leading-relaxed">{s.texto}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
