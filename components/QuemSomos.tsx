"use client";

import { motion } from "framer-motion";
import Image from "next/image";

export default function QuemSomos() {
  return (
    <section id="quem-somos" className="bg-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">

        {/* Título chamativo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase">
            Quem Somos
          </span>
          <h2 className="font-display font-medium text-4xl sm:text-5xl lg:text-6xl mt-4 leading-tight max-w-3xl">
            Especialistas em conectar{" "}
            <span className="text-dourado">pessoas certas</span> a desafios certos.
          </h2>
        </motion.div>

        {/* Grid imagem + texto */}
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-start">
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="rounded-2xl overflow-hidden"
          >
            <Image
              src="/images/quem-somos.png"
              alt="Trilho Consultoria"
              width={800}
              height={900}
              className="w-full h-full object-cover"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="flex flex-col gap-5 text-grafite text-base leading-relaxed"
          >
            <p>
              A Trilho Consultoria nasceu da união de profissionais com sólida experiência em Recursos Humanos, Gestão de Negócios e Desenvolvimento Organizacional. Reunimos vivência prática em empresas nacionais e multinacionais de diferentes portes e segmentos, oferecendo uma visão estratégica, moderna e orientada a resultados.
            </p>
            <p>
              Nossos sócios fundadores unem competências complementares. Alexandre Sales possui mais de 10 anos de experiência em Recrutamento e Seleção, com atuação especializada em atração de talentos, recrutamento estratégico e iniciativas de Diversidade, Equidade e Inclusão. William Sales traz uma trajetória de mais de 20 anos como executivo e administrador, com ampla experiência em gestão, desenvolvimento de negócios e transformação organizacional.
            </p>
            <p>
              Além da liderança dos sócios, contamos com uma equipe de recrutadores especializados em diferentes mercados, com forte atuação nos setores de agronegócio, indústria e celulose, o que nos permite compreender as particularidades de cada segmento e entregar processos seletivos mais assertivos.
            </p>
            <p>
              Nosso propósito é conectar pessoas e empresas por meio de soluções personalizadas que apoiam a atração, seleção, desenvolvimento e retenção de talentos. Trabalhamos para fortalecer organizações, formar equipes de alta performance e contribuir para ambientes mais inclusivos, inovadores e preparados para os desafios do futuro.
            </p>
            <p className="font-medium text-noite">
              Mais do que uma consultoria de Recrutamento e Seleção, somos parceiros estratégicos na construção de caminhos que impulsionam pessoas, fortalecem organizações e transformam o futuro dos negócios.
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
