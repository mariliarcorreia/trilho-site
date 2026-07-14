"use client";

import { motion } from "framer-motion";
import { Play } from "lucide-react";

// substituir pelo ID real do vídeo do YouTube quando disponível
const YOUTUBE_VIDEO_ID = "";

export default function Youtube() {
  return (
    <section className="bg-noite py-24 lg:py-28">
      <div className="mx-auto max-w-7xl px-6 lg:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-10"
        >
          <div>
            <span className="text-dourado-claro text-sm tracking-[0.2em] uppercase">
              YouTube
            </span>
            <h2 className="font-display font-medium text-2xl sm:text-3xl text-branco mt-3">
              Conteúdo sobre mercado e carreira no agro.
            </h2>
          </div>
          <a
            href="https://www.youtube.com/@trilhoconsultoria"
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 text-sm border border-branco/20 text-branco/70 rounded-full px-5 py-2.5 hover:border-dourado-claro hover:text-dourado-claro transition-colors"
          >
            Ver canal completo
          </a>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="aspect-video w-full rounded-2xl overflow-hidden bg-grafite/40 border border-branco/10 flex items-center justify-center"
        >
          {YOUTUBE_VIDEO_ID ? (
            <iframe
              src={`https://www.youtube.com/embed/${YOUTUBE_VIDEO_ID}`}
              title="Trilho Consultoria no YouTube"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="w-full h-full"
            />
          ) : (
            <div className="flex flex-col items-center gap-4 text-branco/30">
              <Play size={48} strokeWidth={1} />
              <p className="text-sm">Vídeo em breve</p>
            </div>
          )}
        </motion.div>
      </div>
    </section>
  );
}
