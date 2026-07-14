"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Linkedin } from "lucide-react";

const SOCIOS = [
  {
    nome: "Alexandre Faleiros",
    linkedin: "https://www.linkedin.com/in/alexandre-faleiros",
    bio: "Mais de 10 anos de experiência em Recursos Humanos, com atuação em recrutamento estratégico, atração e seleção de talentos, employer branding, programas de estágio e trainee, além de iniciativas voltadas à Diversidade, Equidade e Inclusão. Sua trajetória é marcada pela construção de processos seletivos humanizados, estratégicos e alinhados às necessidades do negócio.",
  },
  {
    nome: "William Sales",
    linkedin: "https://www.linkedin.com/in/will-sales",
    bio: "Sólida carreira de mais de 20 anos como executivo e administrador, reunindo ampla experiência em gestão, desenvolvimento de negócios, estratégia, transformação organizacional e liderança de equipes. Sua visão de negócios contribui para conectar pessoas, resultados e crescimento sustentável.",
  },
];

export default function Equipe() {
  return (
    <section id="equipe" className="bg-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl mb-16"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase">
            Equipe
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 leading-tight">
            Dois sócios. Diferentes trajetórias. Um mesmo propósito.
          </h2>
          <p className="mt-4 text-grafite leading-relaxed">
            Conectar talentos e empresas com excelência.
          </p>
        </motion.div>

        {/* Foto dos dois juntos */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.6 }}
          className="w-full rounded-2xl overflow-hidden mb-10"
        >
          <Image
            src="/images/equipe.PNG"
            alt="Alexandre Faleiros e William Sales — Sócios da Trilho Consultoria"
            width={1456}
            height={816}
            className="w-full object-cover object-top max-h-[520px]"
          />
        </motion.div>

        {/* Texto introdutório */}
        <motion.p
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5 }}
          className="text-grafite text-base leading-relaxed max-w-3xl mb-14"
        >
          É com muita satisfação que apresentamos os sócios da Trilho Consultoria, especializada em Recrutamento & Seleção para os segmentos de Agronegócio, Indústria e Celulose. Com ampla experiência em mercados nacionais e multinacionais, unem suas expertises para inovação, performance e resultado.
        </motion.p>

        {/* Cards individuais */}
        <div className="grid sm:grid-cols-2 gap-8">
          {SOCIOS.map((s, i) => (
            <motion.div
              key={s.nome}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="bg-pedra rounded-2xl p-8 flex flex-col gap-4 border border-linha"
            >
              <div className="flex items-center justify-between">
                <h3 className="font-display text-xl font-medium">{s.nome}</h3>
                <a
                  href={s.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={`LinkedIn de ${s.nome}`}
                  className="text-dourado hover:text-dourado-claro transition-colors"
                >
                  <Linkedin size={20} />
                </a>
              </div>
              <p className="text-grafite text-sm leading-relaxed">{s.bio}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
