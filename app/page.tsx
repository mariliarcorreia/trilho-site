import Header from "@/components/Header";
import Hero from "@/components/Hero";
import QuemSomos from "@/components/QuemSomos";
import FraseImpacto from "@/components/FraseImpacto";
import Pilares from "@/components/Pilares";
import Servicos from "@/components/Servicos";
import Diferenciais from "@/components/Diferenciais";
import Equipe from "@/components/Equipe";
import Clientes from "@/components/Clientes";
import Youtube from "@/components/Youtube";
import Contato from "@/components/Contato";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <QuemSomos />
        <FraseImpacto />
        <Pilares />
        <Servicos />
        <Diferenciais />
        <Equipe />
        <Clientes />
        <Youtube />
        <Contato />
      </main>
      <Footer />
    </>
  );
}
