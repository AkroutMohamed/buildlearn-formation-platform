import Categories from "@/components/home/Categories";
import CTA from "@/components/home/CTA";
import Hero from "@/components/home/Hero";
import FeaturedFormations from "@/components/home/FeaturedFormations";
import HowItWorks from "@/components/home/HowItWorks";
import SearchSection from "@/components/home/SearchSection";
import WhyChooseUs from "@/components/home/WhyChooseUs";

export default function Home() {
  return (
    <main className="flex flex-col bg-zinc-50 text-slate-900">
      <Hero />
      <Categories />
      <SearchSection />
      <FeaturedFormations />
      <WhyChooseUs />
      <HowItWorks />
      <CTA />
    </main>
  );
} 
