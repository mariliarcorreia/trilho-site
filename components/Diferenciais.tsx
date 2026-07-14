"use client";

import { motion } from "framer-motion";

const ETAPAS = [
  {
    n: "01",
    titulo: "Diagnóstico do perfil",
    texto:
      "Entendemos a cultura da empresa e o perfil técnico e comportamental exigido pela vaga.",
  },
  {
    n: "02",
    titulo: "Mapeamento de mercado",
    texto:
      "Buscamos candidatos ativos e passivos com conhecimento real do setor agro e de celulose.",
  },
  {
    n: "03",
    titulo: "Seleção criteriosa",
    texto:
      "Entrevistas, dinâmicas e validações técnicas filtram apenas os perfis mais alinhados.",
  },
  {
    n: "04",
    titulo: "Acompanhamento pós-contratação",
    texto:
      "Damos suporte na integração do profissional para garantir adaptação e permanência.",
  },
];

export default function Diferenciais() {
  return (
    <section id="diferenciais" className="bg-pedra py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl mb-16"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase">
            Diferenciais
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 leading-tight">
            Um processo construído etapa por etapa.
          </h2>
        </motion.div>

        <div className="flex flex-col">
          {ETAPAS.map((e, i) => (
            <motion.div
              key={e.n}
              initial={{ opacity: 0, x: -16 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="grid grid-cols-[auto_1fr] gap-6 sm:gap-10 py-8 border-t border-linha last:border-b items-start"
            >
              <span className="font-display text-dourado text-2xl sm:text-3xl">
                {e.n}
              </span>
              <div>
                <h3 className="font-display text-xl sm:text-2xl font-medium mb-2">
                  {e.titulo}
                </h3>
                <p className="text-grafite leading-relaxed max-w-xl">
                  {e.texto}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
