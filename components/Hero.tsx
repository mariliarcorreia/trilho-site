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

      <div className="relative mx-auto max-w-7xl w-full px-6 lg:px-10 pt-36 pb-24">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-dourado-claro text-base tracking-[0.2em] uppercase mb-6 font-bold"
        >
          Recrutamento & Seleção · Agronegócio & Indústria
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
          className="mt-7 text-branco/80 text-lg max-w-xl leading-relaxed"
        >
          Consultoria especializada em recrutamento e seleção, treinamentos e conteúdos estratégicos para empresas do agronegócio e da indústria.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mt-14 pt-10 border-t border-branco/10 grid sm:grid-cols-3 gap-8 max-w-4xl"
        >
          <div className="flex flex-col gap-3">
            <p className="text-dourado-claro text-xs tracking-[0.18em] uppercase font-bold">Para Empresas</p>
            <p className="text-branco/60 text-sm leading-relaxed">Encontre o profissional certo para cada posição do seu negócio.</p>
            <a href="#contato" className="self-start bg-dourado-claro text-noite font-bold px-6 py-3 rounded-full hover:bg-dourado transition-colors text-sm uppercase tracking-wide">
              Fale com a Trilho
            </a>
          </div>
          <div className="flex flex-col gap-3">
            <p className="text-dourado-claro text-xs tracking-[0.18em] uppercase font-bold">Para Candidatos</p>
            <p className="text-branco/60 text-sm leading-relaxed">Acesse as vagas disponíveis e candidate-se à sua próxima oportunidade.</p>
            <a href={VAGAS_URL} target="_blank" rel="noopener noreferrer" className="self-start bg-dourado-claro text-noite font-bold px-6 py-3 rounded-full hover:bg-dourado transition-colors text-sm uppercase tracking-wide">
              Ver Vagas
            </a>
          </div>
          <div className="flex flex-col gap-3">
            <p className="text-dourado-claro text-xs tracking-[0.18em] uppercase font-bold">Para Consultorias</p>
            <p className="text-branco/60 text-sm leading-relaxed">Consultoria de Carreira para profissionais.</p>
            <a href="#contato" className="self-start bg-dourado-claro text-noite font-bold px-6 py-3 rounded-full hover:bg-dourado transition-colors text-sm uppercase tracking-wide">
              Solicitar Consultoria
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
