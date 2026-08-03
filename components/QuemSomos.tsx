"use client";

import { motion } from "framer-motion";

export default function QuemSomos() {
  return (
    <section id="quem-somos" className="bg-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <span className="text-dourado font-light tracking-[0.3em] uppercase block text-2xl sm:text-3xl lg:text-4xl mb-8">
            Quem Somos
          </span>
          <h2 className="font-display font-medium text-5xl sm:text-6xl lg:text-7xl leading-tight max-w-4xl">
            Especialistas em conectar{" "}
            <span className="text-dourado">pessoas certas</span> a desafios certos.
          </h2>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="rounded-2xl overflow-hidden w-full"
          >
            <img
              src="/images/quem-somos.png"
              alt="Trilho Consultoria"
              className="w-full h-auto object-cover rounded-2xl"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex flex-col gap-5 text-grafite text-base leading-relaxed"
          >
            <p className="font-bold text-noite text-lg text-justify">
              A Trilho Consultoria nasceu da união de profissionais com sólida experiência em Recursos Humanos, Gestão de Negócios e Desenvolvimento Organizacional.
            </p>
            <p className="text-justify">
              Nosso propósito é conectar pessoas e empresas por meio de soluções personalizadas que apoiam a atração, seleção, desenvolvimento e retenção de talentos. Trabalhamos para fortalecer organizações, formar equipes de alta performance e contribuir para ambientes mais inclusivos, inovadores e preparados para os desafios do futuro.
            </p>
            <p className="font-bold text-noite text-justify">
              Contamos com uma equipe de recrutadores especializados em diferentes mercados, com forte atuação nos setores de agronegócio, indústria e celulose.
            </p>
            <p className="text-justify">
              Na Trilho Consultoria, acreditamos que cada empresa possui uma história, uma cultura e desafios únicos. Por isso, combinamos inteligência de mercado, metodologia, tecnologia e uma abordagem genuinamente humana para construir soluções que geram resultados sustentáveis.
            </p>
            <p className="font-medium text-noite text-justify">
              Mais do que uma consultoria de Recrutamento e Seleção, somos parceiros estratégicos na construção de caminhos que impulsionam pessoas, fortalecem organizações e transformam o futuro dos negócios.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}