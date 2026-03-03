<template>
  <footer id="footer" class="bg-[#0a0a0f] border-t border-[#7C3AED]/10">
    <div class="max-w-5xl mx-auto px-6 sm:px-8 lg:px-12 py-12">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div>
          <div class="flex items-center gap-3 mb-2">
            <img src="/icon.svg" alt="klangbild" class="w-6 h-6 opacity-80" />
            <span class="text-lg md:text-xl lg:text-2xl text-white tracking-tight">klangbild</span>
          </div>
          <p class="text-gray-500 text-xs md:text-sm lg:text-base">
            4K audio visualizer for YouTube
          </p>
        </div>
        
        <div class="flex items-center gap-6">
          <NuxtLink
            v-for="link in footer?.links"
            :key="link.name"
            :to="link.url"
            class="text-gray-400 hover:text-[#7C3AED] transition-colors text-sm md:text-base lg:text-lg"
            :external="link.url.startsWith('http')"
            :target="link.url.startsWith('http') ? '_blank' : undefined"
          >
            {{ link.name }}
          </NuxtLink>
        </div>
        
        <div class="text-gray-500 text-xs md:text-sm lg:text-base">
          by 
          <NuxtLink 
            :to="footer?.authorUrl || 'https://skvggor.dev'" 
            class="text-gray-400 hover:text-[#7C3AED] transition-colors"
            external
            target="_blank"
          >
            {{ footer?.authorName || 'Marcos Lima' }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
const { data: footer } = await useAsyncData("footer", () =>
  queryContent("footer").findOne(),
);

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.1 },
  );

  const footer = document.getElementById("footer");
  if (footer) {
    footer.style.opacity = "0";
    footer.style.transform = "translateY(20px)";
    footer.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
    observer.observe(footer);
  }
});
</script>

<style scoped>
#footer.is-visible {
  opacity: 1 !important;
  transform: translateY(0) !important;
}
</style>
