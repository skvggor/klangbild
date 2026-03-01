<template>
  <section id="examples" class="py-24 bg-[#0f0f1a]">
    <div class="max-w-5xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="section-header mb-16">
        <h2 class="text-3xl md:text-4xl lg:text-5xl font-light text-white mb-4 tracking-tight">
          {{ examples?.title || 'Examples' }}
        </h2>
        <p class="text-lg md:text-xl lg:text-2xl text-gray-400 font-light">
          {{ examples?.description || 'See what you can create with klangbild' }}
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-12 md:gap-8 lg:gap-10">
        <div
          v-for="(layout, index) in examples?.layouts"
          :key="layout.name"
          class="example-item group flex flex-col"
        >
          <div class="mb-3">
            <h3 class="text-lg md:text-xl lg:text-2xl font-normal text-white mb-1 h-8 flex items-center">
              {{ layout.name }}
            </h3>
            <p class="text-gray-400 text-sm md:text-base lg:text-lg font-light min-h-[3rem] leading-relaxed">
              {{ layout.description }}
            </p>
          </div>
          <div class="overflow-hidden rounded-lg border border-[#7C3AED]/10 group-hover:border-[#7C3AED]/30 transition-colors mt-auto bg-[#0a0a0f]">
            <img
              :src="layout.image"
              :alt="layout.name"
              class="w-full h-auto object-cover opacity-90 group-hover:opacity-100 transition-opacity duration-500"
              loading="lazy"
            />
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { data: examples } = await useAsyncData("examples", () =>
  queryContent("examples").findOne(),
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

  document.querySelectorAll(".section-header, .example-item").forEach((el) => {
    observer.observe(el);
  });
});
</script>

<style>
.section-header,
.example-item {
  opacity: 1;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.section-header.is-visible,
.example-item.is-visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
