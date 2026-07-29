"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mail, MapPin } from "lucide-react";

export default function Contato() {
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setEnviando(true);

    const form = e.currentTarget;
    const data = new FormData(form);

    try {
      const response = await fetch("https://formspree.io/f/xpqvkebg", {
        method: "POST",
        body: data,
        headers: { Accept: "application/json" },
      });

      if (response.ok) {
        setEnviado(true);
        form.reset();
      }
    } catch (error) {
      console.error("Erro ao enviar formulário:", error);
    } finally {
      setEnviando(false);
    }
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
          <span className="text-dourado-claro text-sm tracking-[0.2em] uppercase font-bold">
            Contato
          </span>
          <div className="flex flex-col gap-5 text-branco/75 mt-8">
            <a
              href="mailto:recrutamento@trilhoconsultoria.com.br"
              className="flex items-center gap-3 hover:text-dourado-claro transition-colors"
            >
              <Mail size={18} />
              recrutamento@trilhoconsultoria.com.br
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
              Mensagem enviada com sucesso! Em breve a equipe da Trilho entrará em contato.
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <div className="grid sm:grid-cols-2 gap-5">
                <input
                  required
                  type="text"
                  name="nome"
                  placeholder="Nome"
                  className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
                />
                <input
                  required
                  type="email"
                  name="email"
                  placeholder="E-mail"
                  className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
                />
              </div>
              <input
                type="tel"
                name="telefone"
                placeholder="Telefone"
                className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors"
              />
              <textarea
                required
                rows={4}
                name="mensagem"
                placeholder="Como podemos ajudar?"
                className="bg-transparent border border-branco/25 rounded-lg px-4 py-3 placeholder:text-branco/40 focus:border-dourado-claro outline-none transition-colors resize-none"
              />
              <button
                type="submit"
                disabled={enviando}
                className="self-start bg-dourado-claro text-noite font-medium px-7 py-3.5 rounded-full hover:bg-dourado transition-colors disabled:opacity-60"
              >
                {enviando ? "Enviando..." : "Enviar mensagem"}
              </button>
            </form>
          )}
        </motion.div>
      </div>
    </section>
  );
}
