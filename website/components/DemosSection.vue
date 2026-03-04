<template>
  <section id="demos" class="py-24 bg-[#0f0f1a]">
    <div class="max-w-5xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="section-header-demos mb-12">
        <h2 class="text-3xl md:text-4xl lg:text-5xl text-white mb-4 tracking-tight">
          {{ demos?.title || 'Demos' }}
        </h2>
        <p class="text-lg md:text-xl lg:text-2xl text-gray-400 max-w-2xl">
          {{ demos?.description || 'See what klangbild can do.' }}
        </p>
      </div>

      <div v-if="demos?.link" class="demo-item">
        <NuxtLink
          :to="demos.link.url"
          external
          target="_blank"
          class="group flex items-center gap-4 p-6 rounded-lg border border-[#7C3AED]/20 hover:border-[#7C3AED]/50 bg-[#0a0a0f]/50 hover:bg-[#0a0a0f]/80 transition-all duration-300"
        >
          <div class="flex-shrink-0">
            <div class="w-14 h-14 rounded-lg bg-gradient-to-r from-[#7C3AED] to-[#06B6D4] flex items-center justify-center group-hover:scale-110 transition-transform duration-300 shadow-lg shadow-[#7C3AED]/20">
              <UIcon :name="demos.link.icon" class="w-7 h-7 text-white" />
            </div>
          </div>
          <div class="flex flex-col">
            <span class="text-lg md:text-xl text-white group-hover:text-[#06B6D4] transition-colors">
              {{ demos.link.label }}
            </span>
            <span class="text-sm md:text-base text-gray-500">
              {{ demos.link.description }}
            </span>
          </div>
          <UIcon name="ph:arrow-right" class="w-5 h-5 text-gray-500 group-hover:text-[#7C3AED] group-hover:translate-x-1 transition-all ml-auto flex-shrink-0" />
        </NuxtLink>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const { data: demos } = await useAsyncData("demos", () =>
  queryContent("demos").findOne(),
);

onMounted(() => {
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { threshold: 0.1, rootMargin: "0px 0px -50px 0px" },
  );

  document.querySelectorAll(".section-header-demos, .demo-item").forEach((el) => {
    observer.observe(el);
  });
});
</script>

<style>
.section-header-demos,
.demo-item {
  opacity: 1;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.section-header-demos.is-visible,
.demo-item.is-visible {
  opacity: 1;
  transform: translateY(0);
}
</style>
