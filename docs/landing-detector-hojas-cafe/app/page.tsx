import { Hero } from '@/components/landing/hero'
import { HowItWorks } from '@/components/landing/how-it-works'
import { Install } from '@/components/landing/install'
import { Performance } from '@/components/landing/performance'
import { Limitations } from '@/components/landing/limitations'
import { Privacy } from '@/components/landing/privacy'
import { Footer } from '@/components/landing/footer'

export default function Page() {
  return (
    <>
      <main className="mx-auto flex w-full max-w-5xl flex-col gap-16 px-5 pt-8 pb-16 sm:px-8 sm:pt-12 lg:gap-24 lg:pt-16 lg:pb-24">
        <Hero />
        <HowItWorks />
        <div className="grid items-start gap-16 lg:grid-cols-2 lg:gap-x-10 lg:gap-y-20">
          <Install />
          <Performance />
          <Limitations />
          <Privacy />
        </div>
      </main>
      <Footer />
    </>
  )
}
