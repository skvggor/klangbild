<template>
  <div class="min-h-screen bg-[#0a0a0f]">
    <HeroSection />
    <FeaturesSection />
    <ExamplesSection />
    <QuickStartSection />
    <FooterSection />
  </div>
</template>

<script setup lang="ts">
useHead({
  title: "klangbild - 4K Audio Visualizer for YouTube",
  meta: [
    {
      name: "description",
      content:
        "Generate stunning 4K audio visualizer videos and cover images for YouTube from any MP3 file",
    },
  ],
});
</script>
