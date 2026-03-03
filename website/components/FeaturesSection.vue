<template>
  <section id="features" class="py-24 bg-[#0a0a0f]">
    <div class="max-w-5xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="section-header mb-16">
        <h2 class="text-3xl md:text-4xl lg:text-5xl text-white mb-4 tracking-tight">
          {{ features?.title || 'Features' }}
        </h2>
        <p class="text-lg md:text-xl lg:text-2xl text-gray-400">
          {{ features?.description || 'Everything you need to create professional audio visualizations' }}
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 md:gap-8 lg:gap-12">
        <div
          v-for="(feature, index) in features?.features"
          :key="feature.title"
          class="feature-item flex items-start gap-4 p-4 rounded-lg hover:bg-[#0f0f1a]/50 transition-colors"
        >
          <div class="flex-shrink-0 mt-1">
            <div class="w-10 h-10 rounded-lg bg-[#7C3AED]/10 flex items-center justify-center">
              <UIcon :name="feature.icon" class="w-5 h-5 text-[#7C3AED]" />
            </div>
          </div>
          <div class="flex flex-col">
            <h3 class="text-base md:text-lg lg:text-xl font-normal text-white mb-2">
              {{ feature.title }}
            </h3>
            <p class="text-gray-400 text-sm md:text-base lg:text-lg leading-relaxed flex-grow">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { data: features } = await useAsyncData("features", () =>
  queryContent("features").findOne(),
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
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" },
  );

  document.querySelectorAll(".section-header, .feature-item").forEach((el) => {
    observer.observe(el);
  });
});
</script>

<style>
.section-header,
.feature-item {
  opacity: 1;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.section-header.is-visible,
.feature-item.is-visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
