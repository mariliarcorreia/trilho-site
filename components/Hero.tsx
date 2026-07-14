"use client";

import { motion } from "framer-motion";
import Image from "next/image";

const VAGAS_URL = "#";

export default function Hero() {
  return (
    <section
      id="topo"
      className="relative min-h-screen flex flex-col justify-center bg-noite text-branco overflow-hidden"
    >
      <div className="absolute inset-0">
        <Image
          src="/images/home-final.png"
          alt="Trilho Consultoria"
          fill
          className="object-cover object-center"
          priority
        />
        <div className="absolute inset-0 bg-noite/60" />
      </div>

      <div className="relative mx-auto max-w-7xl w-full px-6 lg:px-10 pt-32 pb-24">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-dourado-claro text-sm tracking-[0.2em] uppercase mb-6"
        >
          Recrutamento & Seleção · Agronegócio & Celulose
        </motion.p>

        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
          className="font-display font-medium text-[2.6rem] leading-[1.08] sm:text-6xl lg:text-7xl max-w-4xl"
        >
          O caminho certo entre talentos e oportunidades.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.22 }}
          className="mt-7 text-branco/70 text-lg max-w-xl leading-relaxed"
        >
          Consultoria especializada em recrutamento, seleção e hunting
          executivo para empresas do agronegócio e da indústria de celulose.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.34 }}
          className="mt-10 flex flex-wrap gap-4"
        >
          <a
            href={VAGAS_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-dourado-claro text-noite font-medium px-7 py-3.5 rounded-full hover:bg-dourado transition-colors"
          >
            Ver vagas abertas
          </a>
          <a
            href="#contato"
            className="border border-branco/25 text-branco px-7 py-3.5 rounded-full hover:border-dourado-claro hover:text-dourado-claro transition-colors"
          >
            Fale com a Trilho
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.46 }}
          className="mt-16 pt-10 border-t border-branco/10 grid sm:grid-cols-2 gap-6 max-w-2xl"
        >
          <div>
            <p className="text-dourado-claro text-xs tracking-[0.18em] uppercase mb-2">Para empresas</p>
            <p className="text-branco/60 text-sm leading-relaxed">Encontre o profissional certo para cada posição do seu negócio.</p>
            <a href="#contato" className="inline-block mt-3 text-sm text-branco/80 hover:text-dourado-claro transition-colors underline underline-offset-4">Solicitar consultoria</a>
          </div>
          <div>
            <p className="text-dourado-claro text-xs tracking-[0.18em] uppercase mb-2">Para candidatos</p>
            <p className="text-branco/60 text-sm leading-relaxed">Acesse as vagas disponíveis e candidate-se à sua próxima oportunidade.</p>
            <a href={VAGAS_URL} target="_blank" rel="noopener noreferrer" className="inline-block mt-3 text-sm text-branco/80 hover:text-dourado-claro transition-colors underline underline-offset-4">Ver vagas abertas</a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
