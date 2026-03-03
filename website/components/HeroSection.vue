<template>
  <section id="hero" class="relative min-h-screen w-full bg-[#0a0a0f] overflow-hidden">
    <ClientOnly fallback-tag="div" fallback-class="absolute inset-0 bg-[#0f0f1a]">
      <WaveBackground class="absolute inset-0 z-[1]" />
    </ClientOnly>
    <div class="absolute inset-0 bg-gradient-to-b from-[#0a0a0f]/40 via-transparent to-[#0a0a0f]/60 z-[2]"></div>

    <div class="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 sm:px-8 lg:px-12 py-6">
      <div class="flex flex-col items-center justify-center w-full max-w-4xl mx-auto text-center">
        <div class="mb-6 animate-fade-in-down">
          <div class="mb-6">
            <img 
              src="/icon.svg" 
              alt="klangbild" 
              class="w-16 h-16 md:w-20 md:h-20 mx-auto"
            />
          </div>
          <h1 class="text-4xl md:text-6xl lg:text-7xl xl:text-8xl text-white mb-4 tracking-tight bg-gradient-to-r from-[#7C3AED] via-[#06B6D4] to-[#7C3AED] bg-clip-text text-transparent">
            klangbild
          </h1>
          <p class="text-lg md:text-2xl lg:text-3xl text-gray-400 max-w-2xl mx-auto">
            Generate stunning 4K audio visualizer videos for YouTube
          </p>
          <p class="text-sm md:text-base text-gray-500 mt-2">
            Linux-only command-line tool
          </p>
        </div>
        
        <div class="w-full max-w-3xl mx-auto mb-10 animate-fade-in-up">
          <div
            class="relative w-full bg-transparent rounded-lg overflow-hidden border border-[#7C3AED]/20 shadow-2xl shadow-[#7C3AED]/10"
            style="aspect-ratio: 16/9;"
          >
            <iframe
              v-if="isPlaying"
              class="absolute inset-0 w-full h-full"
              :src="videoUrl"
              title="klangbild demo"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
            
            <div
              v-show="!isPlaying"
              class="absolute inset-0 flex items-center justify-center bg-[#0a0a0f]/30 backdrop-blur-xl cursor-pointer group"
              @click="playVideo"
            >
              <div class="absolute inset-0 overflow-hidden">
                <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full">
                  <div class="absolute w-2 h-2 rounded-full bg-[#7C3AED]/20 animate-pulse" style="top: 20%; left: 10%;"></div>
                  <div class="absolute w-1 h-1 rounded-full bg-[#06B6D4]/30 animate-pulse" style="top: 60%; left: 20%; animation-delay: 0.5s;"></div>
                  <div class="absolute w-1.5 h-1.5 rounded-full bg-[#7C3AED]/25 animate-pulse" style="top: 30%; left: 80%; animation-delay: 1s;"></div>
                  <div class="absolute w-1 h-1 rounded-full bg-[#06B6D4]/20 animate-pulse" style="top: 70%; left: 85%; animation-delay: 1.5s;"></div>
                  <div class="absolute w-2 h-2 rounded-full bg-[#7C3AED]/15 animate-pulse" style="top: 15%; left: 70%; animation-delay: 2s;"></div>
                </div>
              </div>
              
              <div class="relative w-20 h-20 md:w-24 md:h-24 rounded-full bg-gradient-to-r from-[#7C3AED] to-[#06B6D4] flex items-center justify-center opacity-90 group-hover:opacity-100 transition-all duration-300 group-hover:scale-110 shadow-xl shadow-[#7C3AED]/40">
                <UIcon name="ph:play-fill" class="w-8 h-8 md:w-10 md:h-10 text-white ml-1" />
              </div>
              
              <div class="absolute bottom-6 left-0 right-0 text-center">
                <span class="text-gray-500 text-sm">Click to watch demo</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="flex flex-col sm:flex-row items-center justify-center gap-6 mt-4 animate-fade-in">
          <NuxtLink
            to="#features"
            class="group flex items-center gap-2 text-[#7C3AED] hover:text-[#06B6D4] transition-colors"
          >
            <span>Get Started</span>
            <UIcon name="ph:arrow-right" class="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </NuxtLink>
          <span class="hidden sm:block text-gray-600">|</span>
          <NuxtLink
            to="https://github.com/skvggor/klangbild"
            class="group flex items-center gap-2 px-4 py-2 rounded-lg bg-[#1a1a2e] hover:bg-[#1a1a2e]/80 border border-[#7C3AED]/30 hover:border-[#7C3AED]/50 transition-all duration-200"
            external
            target="_blank"
          >
            <UIcon name="ph:star-fill" class="w-4 h-4 text-yellow-500" />
            <span class="text-gray-300">Star on GitHub</span>
          </NuxtLink>
        </div>
        
        <div class="flex justify-center mt-10 animate-fade-in">
          <NuxtLink
            to="#features"
            class="group flex flex-col items-center gap-1 text-gray-500 hover:text-[#7C3AED] transition-colors cursor-pointer"
          >
            <span class="text-xs mb-1 opacity-0 group-hover:opacity-100 transition-opacity">Scroll down</span>
            <div class="animate-bounce">
              <UIcon name="ph:caret-down" class="w-6 h-6" />
            </div>
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const isPlaying = ref(false);
const videoId = "zSJnd_S_jVk";

const videoUrl = computed(() => {
  return `https://www.youtube.com/embed/${videoId}?autoplay=1&controls=0&disablekb=1&fs=0&iv_load_policy=3&modestbranding=1&rel=0&showinfo=0`;
});

const playVideo = () => {
  isPlaying.value = true;
};
</script>
