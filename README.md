# Trilho Consultoria — Site Institucional

Site institucional desenvolvido em Next.js 16 (App Router) com TypeScript, Tailwind CSS v4 e Framer Motion.

## Como rodar localmente

```bash
npm install
npm run dev
```

Acesse http://localhost:3000

Para testar em outro dispositivo na mesma rede (celular, tablet):
```bash
npm run dev -- -H 0.0.0.0
```
Depois acesse pelo IP local da máquina, por exemplo http://192.168.x.x:3000

## Estrutura

- `app/layout.tsx` — fontes (Fraunces + Inter), metadata e estrutura HTML base
- `app/page.tsx` — composição da página principal
- `app/globals.css` — tokens de cor e configuração do Tailwind v4 (tema definido via `@theme`)
- `components/` — cada seção do site como componente isolado

## Pontos para finalizar com o cliente

- Link da plataforma de vagas (Agrosearch) — atualmente como placeholder em `components/Header.tsx` (`VAGAS_URL`)
- Fotos da equipe — `components/Equipe.tsx`
- Logos de clientes e parceiros — `components/Clientes.tsx`
- Links de redes sociais (LinkedIn, YouTube, WhatsApp) — `components/Footer.tsx`
- Integração do formulário de contato com serviço de envio de e-mail — `components/Contato.tsx`
- Link da Área do Cliente — `components/Footer.tsx`

## Paleta de cores

| Token            | Hex       | Uso                          |
|-------------------|-----------|-------------------------------|
| `noite`            | `#0D0D0D` | Fundos escuros, header        |
| `grafite`          | `#2B2B29` | Texto secundário              |
| `dourado`          | `#9A7B3A` | Acento principal              |
| `dourado-claro`    | `#C9A86A` | Hover, detalhes sobre fundo escuro |
| `pedra`            | `#F5F3EE` | Fundos claros alternados      |
| `branco`           | `#FFFFFF` | Fundo base, texto sobre escuro|
| `linha`            | `#E4E0D6` | Divisores e bordas sutis      |
