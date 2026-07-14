"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, Phone, MapPin } from "lucide-react";

export default function Contato() {
  const [enviado, setEnviado] = useState(false);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setEnviado(true);
  }

  return (
    <section id="contato" className="bg-noite text-branco py-28 lg:py-36">
      <div className="mx-auto max-w-7xl px-6 lg:px-10 grid lg:grid-cols-12 gap-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="lg:col-span-5"
        >
          <span className="text-dourado-claro text-sm tracking-[0.2em] uppercase">
            Contato
          </span>
          <h2 className="font-display font-medium text-3xl sm:text-4xl mt-4 mb-10 leading-tight">
            Vamos encontrar o profissional certo para sua empresa.
          </h2>

          <div className="flex flex-col gap-5 text-branco/75">
            <a
              href="mailto:alexandre.faleiros@trilhoconsultoria.com.br"
              className="flex items-center gap-3 hover:text-dourado-claro transition-colors"
            >
              <Mail size={18} />
              alexandre.faleiros@trilhoconsultoria.com.br
            </a>
            <a
              href="tel:+5534991270137"
              className="flex items-center gap-3 hover:text-dourado-claro transition-colors"
            >
              <Phone size={18} />
              (34) 99127-0137
            </a>
            <div className="flex items-center gap-3">
              <MapPin size={18} />
              Uberlândia, MG
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="lg:col-span-6 lg:col-start-7"
        >
          {enviado ? (
            <div className="border border-dourado-claro/40 rounded-2xl p-8 text-branco/85">
              Mensagem enviada. Em breve a equipe da Trilho entrará em contato.
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <div className="grid sm:grid-cols-2 gap-5">
                <input
                  required
                  type="text"
                  placeholder="Nome"
                  className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
                />
                <input
                  required
                  type="email"
                  placeholder="E-mail"
                  className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
                />
              </div>
              <input
                type="text"
                placeholder="Empresa"
                className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
              />
              <textarea
                required
                rows={4}
                placeholder="Como podemos ajudar?"
                className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors resize-none"
              />
              <button
                type="submit"
                className="self-start bg-dourado-claro text-noite font-medium px-7 py-3.5 rounded-full hover:bg-dourado transition-colors"
              >
                Enviar mensagem
              </button>
            </form>
          )}
        </motion.div>
      </div>
    </section>
  );
}
