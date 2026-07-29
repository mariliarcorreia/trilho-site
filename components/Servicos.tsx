"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Users, GraduationCap, ChevronLeft, ChevronRight } from "lucide-react";

const SERVICOS = [
  {
    icon: Users,
    titulo: "Recrutamento & Seleção",
    descricao: "Processos seletivos completos, do alinhamento de perfil ideal à integração do profissional aprovado. Conheça nossas soluções para R&S:",
    subservicos: [
      { icone: "🌱", texto: "Trilho Estágio — Recrutamento especializado para programas de estágio, com processos personalizados à cultura, aos desafios e ao perfil de talento que cada empresa busca. Da atração à seleção, encontramos jovens com potencial para crescer junto com o seu negócio." },
      { icone: "⭐", texto: "Trilho Talent — Posições técnicas, operacionais e administrativas até nível Sênior" },
      { icone: "⭐", texto: "Trilho Strategy — Atração e seleção para posições de gerência, especialistas e coordenação" },
      { icone: "⭐", texto: "Trilho Executive — Posições estratégicas C-Level, Vice-Presidência e Diretoria" },
    ],
    imagem: "/images/recrutamento.png",
    posicao: "object-center",
  },
  {
    icon: GraduationCap,
    titulo: "Treinamentos & Conteúdo Especializado",
    descricao: "Desenvolvemos programas de capacitação corporativa personalizados, presenciais e online, alinhados aos desafios e objetivos reais de cada equipe. Produzimos conteúdos estratégicos em diversos formatos — treinamentos, workshops, podcasts, vídeos e materiais técnicos — que aceleram o desenvolvimento profissional e fortalecem a tomada de decisão.",
    subservicos: [],
    imagem: "/images/treinamento.png",
    posicao: "object-[center_20%]",
  },
];

export default function Servicos() {
  const [ativo, setAtivo] = useState(0);

  // 15 segundos de intervalo
  useEffect(() => {
    const timer = setInterval(() => {
      setAtivo((prev) => (prev + 1) % SERVICOS.length);
    }, 25000);
    return () => clearInterval(timer);
  }, []);

  const anterior = () => setAtivo((prev) => (prev - 1 + SERVICOS.length) % SERVICOS.length);
  const proximo  = () => setAtivo((prev) => (prev + 1) % SERVICOS.length);
  const s = SERVICOS[ativo];

  return (
    <section id="servicos" className="bg-noite text-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <span className="text-dourado-claro text-sm tracking-[0.2em] uppercase font-bold mb-8 block">
          Serviços
        </span>

        <div className="flex gap-3 mb-12 flex-wrap">
          {SERVICOS.map((sv, i) => (
            <button
              key={sv.titulo}
              onClick={() => setAtivo(i)}
              className={`px-7 py-3.5 rounded-full text-base font-semibold transition-all duration-300 ${
                i === ativo
                  ? "bg-dourado-claro text-noite scale-105"
                  : "border-2 border-branco/30 text-branco/70 hover:border-dourado-claro hover:text-dourado-claro"
              }`}
            >
              {sv.titulo}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={ativo}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="grid lg:grid-cols-2 gap-12 items-center"
          >
            <div className="flex flex-col gap-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-full bg-dourado flex items-center justify-center shrink-0">
                  <s.icon size={28} strokeWidth={1.5} color="#FFFFFF" />
                </div>
                <h2 className="font-display font-medium text-3xl sm:text-4xl leading-tight">{s.titulo}</h2>
              </div>
              <p className="text-branco/80 text-lg leading-relaxed">{s.descricao}</p>
              {s.subservicos.length > 0 && (
                <ul className="flex flex-col gap-4">
                  {s.subservicos.map((sub, i) => (
                    <li key={i} className="flex items-start gap-3 text-branco/80 text-sm leading-relaxed">
                      <span className="text-dourado-claro text-base shrink-0 mt-0.5">{sub.icone}</span>
                      {sub.texto}
                    </li>
                  ))}
                </ul>
              )}
              <a href="#contato" className="self-start mt-2 bg-dourado-claro text-noite font-bold px-7 py-3.5 rounded-full hover:bg-dourado transition-colors uppercase tracking-wide text-sm">
                Fale com a Trilho
              </a>
            </div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="rounded-2xl overflow-hidden"
            >
              <img src={s.imagem} alt={s.titulo} className="w-full h-auto object-contain rounded-2xl" />
            </motion.div>
          </motion.div>
        </AnimatePresence>

        <div className="flex items-center gap-4 mt-12">
          <button onClick={anterior} className="w-10 h-10 rounded-full border border-branco/30 flex items-center justify-center hover:border-dourado-claro hover:text-dourado-claro transition-colors">
            <ChevronLeft size={20} />
          </button>
          <div className="flex gap-2">
            {SERVICOS.map((_, i) => (
              <button key={i} onClick={() => setAtivo(i)} className={`h-1.5 rounded-full transition-all duration-300 ${i === ativo ? "w-8 bg-dourado-claro" : "w-3 bg-branco/30"}`} />
            ))}
          </div>
          <button onClick={proximo} className="w-10 h-10 rounded-full border border-branco/30 flex items-center justify-center hover:border-dourado-claro hover:text-dourado-claro transition-colors">
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </section>
  );
}
