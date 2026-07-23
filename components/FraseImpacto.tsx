"use client";

import { motion } from "framer-motion";

export default function FraseImpacto() {
  return (
    <section className="bg-dourado py-20 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-10 flex flex-col items-center text-center gap-6">
        <motion.div
          initial={{ opacity: 0, scaleX: 0 }}
          whileInView={{ opacity: 1, scaleX: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="w-16 h-1 bg-noite rounded-full"
        />
        <motion.h2
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="font-display font-semibold text-4xl sm:text-5xl lg:text-6xl text-noite leading-tight max-w-4xl uppercase tracking-wide"
        >
          Conectando Talentos ao Destino Certo
        </motion.h2>
        <motion.div
          initial={{ opacity: 0, scaleX: 0 }}
          whileInView={{ opacity: 1, scaleX: 1 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="w-16 h-1 bg-noite rounded-full"
        />
      </div>
    </section>
  );
}
