"use client";

import { motion } from "framer-motion";
import { Linkedin } from "lucide-react";

const SOCIOS = [
  {
    nome: "Alexandre Faleiros",
    cargo: "Sócio & Diretor de Talent",
    linkedin: "https://www.linkedin.com/in/alexandre-faleiros",
    bio: "Administrador de Empresas pela Universidade Federal de Uberlândia (UFU), pós-graduado pela Fundação Getulio Vargas (FGV), especialista em Talent Acquisition e Gestão Estratégica de Pessoas. Possui mais de 10 anos de experiência em Recursos Humanos, atuando em empresas nacionais e multinacionais, com forte atuação em recrutamento estratégico para posições operacionais, técnicas, especialistas, liderança e executivos. Ao longo de sua carreira, liderou projetos de Employer Branding, Programas de Estágio e Trainee, atração de talentos, hunting, People Analytics e iniciativas de Diversidade, Equidade e Inclusão. É certificado nas metodologias comportamentais Predictive Index (PI) e PDA International.",
  },
  {
    nome: "William Sales",
    cargo: "Sócio & Diretor Executivo",
    linkedin: "https://www.linkedin.com/in/will-sales",
    bio: "Administrador, pós-graduado pela Fundação Getúlio Vargas (FGV), executivo com mais de 20 anos de experiência em gestão empresarial, gerenciamento de riscos, desenvolvimento de negócios e liderança de equipes multidisciplinares e multiculturais. Construiu sua carreira em empresas de grande porte, tanto nacionais como multinacionais, passando por todas as etapas organizacionais, liderando operações, projetos de transformação organizacional, estratégia corporativa e desenvolvimento de pessoas. Sua atuação combina visão de negócios, capacidade analítica e foco em resultados sustentáveis.",
  },
];

export default function Equipe() {
  return (
    <section id="equipe" className="bg-pedra py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mb-16"
        >
          <span className="text-dourado text-sm tracking-[0.2em] uppercase font-bold">Nossa Equipe</span>
          <h2 className="font-display font-medium text-3xl sm:text-5xl mt-4 leading-tight">
            Dois sócios. <span className="text-dourado">Diferentes trajetórias.</span> Um mesmo propósito.
          </h2>
          <p className="mt-6 text-grafite text-lg leading-relaxed max-w-3xl text-justify">
            A Trilho Consultoria foi fundada por profissionais com sólida trajetória em Recursos Humanos, Estratégia e Gestão Empresarial, reunindo experiência em empresas nacionais e multinacionais dos segmentos de Agronegócio, Indústria e Celulose.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.6 }}
          className="w-full rounded-2xl overflow-hidden mb-12 relative"
          style={{ minHeight: "300px" }}
        >
          <img
            src="/images/equipe.png?v=2"
            alt="Alexandre Faleiros e William Sales"
            style={{ width: "100%", maxHeight: "520px", objectFit: "cover", objectPosition: "top", display: "block", borderRadius: "1rem" }}
          />
          <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: "4px", backgroundColor: "#9A7B3A", borderRadius: "0 0 1rem 1rem" }} />
        </motion.div>

        <motion.blockquote
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5 }}
          className="border-l-4 border-dourado pl-6 mb-14 max-w-3xl"
        >
          <p className="text-grafite text-base italic leading-relaxed text-justify">
            "Mais do que conduzir processos seletivos, desenvolvemos carreiras liderando projetos estratégicos, formando equipes de alta performance e apoiando organizações na construção de resultados sustentáveis por meio da gestão e recrutamento de pessoas."
          </p>
          <footer className="mt-3 text-dourado font-medium text-sm">
            — Alexandre Faleiros, Sócio & Diretor de Talent
          </footer>
        </motion.blockquote>

        <div className="grid sm:grid-cols-2 gap-8">
          {SOCIOS.map((s, i) => (
            <motion.div
              key={s.nome}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.12 }}
              className="bg-branco rounded-2xl p-8 flex flex-col gap-4 border border-linha shadow-sm"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="font-display text-xl font-medium text-noite">{s.nome}</h3>
                  <p className="text-dourado text-sm font-medium mt-1">{s.cargo}</p>
                </div>
                <a href={s.linkedin} target="_blank" rel="noopener noreferrer" className="text-dourado hover:text-dourado-claro transition-colors shrink-0 mt-1">
                  <Linkedin size={22} />
                </a>
              </div>
              <div className="h-px bg-linha" />
              <p className="text-grafite text-sm leading-relaxed text-justify">{s.bio}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}