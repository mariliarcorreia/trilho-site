"use client";

import { motion } from "framer-motion";

const ETAPAS = [
  {
    n: "01",
    titulo: "Diagnóstico do Perfil",
    texto: "Entendemos a cultura organizacional, os desafios da posição e as competências técnicas e comportamentais necessárias para a vaga. Utilizamos ferramentas modernas, inteligência artificial e metodologias de avaliação para definir o perfil ideal.",
  },
  {
    n: "02",
    titulo: "Mapeamento de Mercado",
    texto: "Realizamos uma busca estratégica de talentos por meio de networking qualificado, LinkedIn, bancos de currículos especializados e técnicas de hunting, com foco nos segmentos de agronegócio, indústria e celulose.",
  },
  {
    n: "03",
    titulo: "Seleção Criteriosa",
    texto: "Conduzimos triagens, entrevistas e avaliações com apoio de plataformas especializadas, garantindo maior aderência técnica e comportamental dos profissionais apresentados para validação do cliente.",
  },
  {
    n: "04",
    titulo: "Acompanhamento Pré-Admissional",
    texto: "Oferecemos suporte completo durante todo o processo de contratação, auxiliando na gestão documental, exames admissionais e alinhamentos necessários até a integração do profissional à empresa.",
  },
  {
    n: "05",
    titulo: "Atendimento Especializado",
    texto: "Nossa equipe possui experiência prática nos setores agro, indústria e celulose, proporcionando assertividade na identificação de talentos. Trabalhamos com foco em SLA, agilidade, qualidade de entrega e garantia de reposição, assegurando maior segurança para a contratação.",
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
          <span className="text-dourado text-sm tracking-[0.2em] uppercase font-bold">
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
              className="grid grid-cols-[auto_1fr] gap-6 sm:gap-10 py-8 border-t border-linha last:border-b items-start group hover:bg-branco/50 rounded-xl px-4 transition-colors duration-200"
            >
              <span className="font-display text-dourado text-2xl sm:text-3xl font-medium">
                {e.n}
              </span>
              <div>
                <h3 className="font-display text-xl sm:text-2xl font-medium mb-2 group-hover:text-dourado transition-colors">
                  {e.titulo}
                </h3>
                <p className="text-grafite leading-relaxed max-w-xl text-justify">
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