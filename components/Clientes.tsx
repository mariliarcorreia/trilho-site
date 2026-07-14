"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const CLIENTES = [
  { nome: "LD Celulose", logo: "/images/ld-celulose.png" },
  { nome: "MAZI Consultoria e Contabilidade", logo: "/images/mazi-consultoria.png" },
];

export default function Clientes() {
  return (
    <section id="clientes" className="bg-pedra py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase">
            Clientes & Parceiros
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 leading-tight">
            Empresas que confiam na Trilho.
          </h2>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-8">
          {CLIENTES.map((c, i) => (
            <motion.div
              key={c.nome}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="bg-branco rounded-2xl border border-linha flex flex-col items-center justify-center gap-4 p-10 min-h-[240px]"
            >
              <img
                src={c.logo}
                alt={c.nome}
                style={{ width: "100%", height: "160px", objectFit: "contain" }}
              />
              <p className="text-grafite font-medium text-base text-center">{c.nome}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
