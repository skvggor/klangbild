<template>
  <section id="quickstart" class="py-24 bg-[#0a0a0f]">
    <div class="max-w-4xl mx-auto px-6 sm:px-8 lg:px-12">
      <div class="mb-16">
        <h2 class="text-3xl md:text-4xl lg:text-5xl text-white mb-4 tracking-tight">
          Quick Start
        </h2>
        <p class="text-lg md:text-xl lg:text-2xl text-gray-400">
          Get started in seconds with these simple commands
        </p>
      </div>
      
      <div class="flex flex-col gap-16">
        <div class="code-block">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm md:text-base lg:text-lg text-gray-500">Basic Usage</span>
            <button
              class="text-xs text-[#7C3AED] hover:text-[#06B6D4] transition-colors flex items-center gap-1"
              @click="copyToClipboard(basicCommandRaw, 'basic')"
            >
              <UIcon :name="copied === 'basic' ? 'ph:check' : 'ph:copy'" class="w-3 h-3" />
              <span>{{ copied === 'basic' ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
          <div class="bg-[#0f0f1a]/80 p-5 rounded-lg overflow-x-auto border border-[#7C3AED]/10">
            <pre class="text-sm text-gray-300 leading-relaxed" style="white-space: pre;"><code><span class="text-[#7C3AED] font-medium">uv</span> <span class="text-[#7C3AED] font-medium">run</span> <span class="text-[#7C3AED] font-medium">klangbild</span> \
    <span class="text-[#06B6D4] font-medium">--audio</span> <span class="text-[#4ade80]">"song.mp3"</span> \
    <span class="text-[#06B6D4] font-medium">--background</span> <span class="text-[#4ade80]">"cover.jpg"</span> \
    <span class="text-[#06B6D4] font-medium">--title</span> <span class="text-[#4ade80]">"Song Title"</span> \
    <span class="text-[#06B6D4] font-medium">--artist</span> <span class="text-[#4ade80]">"Artist Name"</span> \
    <span class="text-[#06B6D4] font-medium">--album</span> <span class="text-[#4ade80]">"Album Name"</span> \
    <span class="text-[#06B6D4] font-medium">--output</span> <span class="text-[#4ade80]">"visualizer.mp4"</span></code></pre>
          </div>
        </div>
        
        <div class="code-block">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm md:text-base lg:text-lg text-gray-500">With Gradients</span>
            <button
              class="text-xs text-[#7C3AED] hover:text-[#06B6D4] transition-colors flex items-center gap-1"
              @click="copyToClipboard(gradientCommandRaw, 'gradient')"
            >
              <UIcon :name="copied === 'gradient' ? 'ph:check' : 'ph:copy'" class="w-3 h-3" />
              <span>{{ copied === 'gradient' ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
          <div class="bg-[#0f0f1a]/80 p-5 rounded-lg overflow-x-auto border border-[#7C3AED]/10">
            <pre class="text-sm text-gray-300 leading-relaxed" style="white-space: pre;"><code><span class="text-[#7C3AED] font-medium">uv</span> <span class="text-[#7C3AED] font-medium">run</span> <span class="text-[#7C3AED] font-medium">klangbild</span> \
    <span class="text-[#06B6D4] font-medium">--audio</span> <span class="text-[#4ade80]">"song.mp3"</span> \
    <span class="text-[#06B6D4] font-medium">--background</span> <span class="text-[#4ade80]">"cover.jpg"</span> \
    <span class="text-[#06B6D4] font-medium">--layout</span> spotlight \
    <span class="text-[#06B6D4] font-medium">--wave-style</span> circular \
    <span class="text-[#06B6D4] font-medium">--text-gradient</span> <span class="text-[#4ade80]">"#FF8C42,#FF5A5F"</span> \
    <span class="text-[#06B6D4] font-medium">--wave-gradient</span> <span class="text-[#4ade80]">"#FF5A5F,#FF8C42"</span> \
    <span class="text-[#06B6D4] font-medium">--output</span> <span class="text-[#4ade80]">"visualizer.mp4"</span></code></pre>
          </div>
        </div>
        
        <div class="code-block">
          <div class="flex items-center justify-between mb-4">
            <span class="text-sm md:text-base lg:text-lg text-gray-500">Batch Mode</span>
            <button
              class="text-xs text-[#7C3AED] hover:text-[#06B6D4] transition-colors flex items-center gap-1"
              @click="copyToClipboard(batchCommandRaw, 'batch')"
            >
              <UIcon :name="copied === 'batch' ? 'ph:check' : 'ph:copy'" class="w-3 h-3" />
              <span>{{ copied === 'batch' ? 'Copied' : 'Copy' }}</span>
            </button>
          </div>
          <div class="bg-[#0f0f1a]/80 p-5 rounded-lg overflow-x-auto border border-[#7C3AED]/10">
            <pre class="text-sm text-gray-300 leading-relaxed" style="white-space: pre;"><code><span class="text-[#7C3AED] font-medium">uv</span> <span class="text-[#7C3AED] font-medium">run</span> <span class="text-[#7C3AED] font-medium">klangbild</span> \
    <span class="text-[#06B6D4] font-medium">--input-dir</span> <span class="text-[#4ade80]">"/path/to/mp3s"</span> \
    <span class="text-[#06B6D4] font-medium">--background</span> <span class="text-[#4ade80]">"cover.jpg"</span> \
    <span class="text-[#06B6D4] font-medium">--gpu</span> nvenc \
    <span class="text-[#06B6D4] font-medium">--workers</span> <span class="text-[#a855f7]">30</span></code></pre>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const copied = ref<string | null>(null);

const basicCommandRaw = `uv run klangbild \\
    --audio "song.mp3" \\
    --background "cover.jpg" \\
    --title "Song Title" \\
    --artist "Artist Name" \\
    --album "Album Name" \\
    --output "visualizer.mp4"`;

const gradientCommandRaw = `uv run klangbild \\
    --audio "song.mp3" \\
    --background "cover.jpg" \\
    --layout spotlight \\
    --wave-style circular \\
    --text-gradient "#FF8C42,#FF5A5F" \\
    --wave-gradient "#FF5A5F,#FF8C42" \\
    --output "visualizer.mp4"`;

const batchCommandRaw = `uv run klangbild \\
    --input-dir "/path/to/mp3s" \\
    --background "cover.jpg" \\
    --gpu nvenc \\
    --workers 30`;

const copyToClipboard = async (text: string, type: string) => {
  try {
    await navigator.clipboard.writeText(text);
    copied.value = type;
    setTimeout(() => (copied.value = null), 2000);
  } catch (err) {
    console.error("Failed to copy:", err);
  }
};

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

  document.querySelectorAll(".code-block").forEach((el) => {
    observer.observe(el);
  });
});
</script>

<style scoped>
pre {
  margin: 0;
  white-space: pre;
  font-family: 'Fira Code', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-variant-ligatures: none;
}

code {
  font-family: 'Fira Code', 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 400;
  font-variant-ligatures: none;
}

.code-block {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.code-block.is-visible {
  opacity: 1;
  transform: translateY(0);
}

.code-block:nth-child(1) { transition-delay: 0ms; }
.code-block:nth-child(2) { transition-delay: 150ms; }
.code-block:nth-child(3) { transition-delay: 300ms; }

.code-block:not(:last-child) {
  margin-bottom: 4rem;
}
</style>
