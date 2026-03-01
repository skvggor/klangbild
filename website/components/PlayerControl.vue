<template>
  <div class="fixed bottom-6 left-4 right-4 md:left-6 md:right-6 lg:left-8 lg:right-8 z-50">
    <div
      class="bg-[#0a0a0f]/30 backdrop-blur-xl rounded-2xl border-2 transition-all duration-300 shadow-2xl shadow-[#0a0a0f]/80"
      :class="isComplete ? 'border-[#7C3AED] animate-pulse-glow' : 'border-[#7C3AED]/20'"
    >
      <div class="max-w-5xl mx-auto px-6 py-4 md:px-8 md:py-5">
        <div class="flex items-center gap-4 md:gap-6">
          <button
            class="flex-shrink-0 w-11 h-11 md:w-12 md:h-12 rounded-full bg-[#7C3AED]/20 hover:bg-[#7C3AED]/30 flex items-center justify-center transition-all duration-300 hover:scale-105"
            @click="toggleAutoScroll"
          >
            <UIcon
              :name="isAutoScrolling ? 'ph:pause-fill' : 'ph:play-fill'"
              class="w-5 h-5 md:w-6 md:h-6 text-[#7C3AED]"
            />
          </button>

          <div
            ref="seekBarRef"
            class="flex-1 relative h-2 md:h-2.5 bg-[#1a1a2e] rounded-full cursor-grab active:cursor-grabbing hover:bg-[#1a1a2e]/80 transition-colors select-none"
            @mousedown="startDrag"
            @mousemove="onDrag"
            @mouseup="endDrag"
            @mouseleave="endDrag"
            @touchstart.prevent="startDragTouch"
            @touchmove.prevent="onDragTouch"
            @touchend="endDrag"
          >
            <div
              class="absolute top-0 left-0 h-full bg-gradient-to-r from-[#7C3AED] to-[#06B6D4] rounded-full transition-all duration-100 z-10 pointer-events-none"
              :style="{ width: progressPercent + '%' }"
            />
            <div
              class="absolute top-1/2 -translate-y-1/2 w-4 h-4 md:w-5 md:h-5 bg-white rounded-full shadow-lg z-20 transition-transform duration-100 pointer-events-none"
              :class="{ 'scale-110': isDragging }"
              :style="{ left: 'calc(' + progressPercent + '% - 8px)' }"
            />
          </div>

          <span class="flex-shrink-0 text-sm md:text-base text-gray-400 font-light w-12 text-right">
            {{ progressPercent }}%
          </span>

          <div class="flex-shrink-0 text-xs md:text-sm text-gray-500 font-light hidden sm:block">
            <span class="text-[#7C3AED]">{{ currentTime }}</span>
            <span class="mx-1 text-gray-600">/</span>
            <span>{{ totalTime }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const progressPercent = ref(0);
const isAutoScrolling = ref(false);
const isComplete = ref(false);
const currentTime = ref("0:00");
const totalTime = ref("0:00");
const isDragging = ref(false);
const seekBarRef = ref<HTMLElement | null>(null);

let animationFrameId: number | null = null;
let userInteracted = false;

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
};

const sections = [
  { id: "hero", hash: "" },
  { id: "features", hash: "features" },
  { id: "examples", hash: "examples" },
  { id: "quickstart", hash: "quickstart" },
  { id: "footer", hash: "footer" },
];

let currentSectionHash = "";

const updateUrlHash = () => {
  const scrollPosition = window.scrollY + window.innerHeight / 3;

  for (let i = sections.length - 1; i >= 0; i--) {
    const section = document.getElementById(sections[i].id);
    if (section) {
      const sectionTop = section.offsetTop;
      if (scrollPosition >= sectionTop) {
        const newHash = sections[i].hash;
        if (newHash !== currentSectionHash) {
          currentSectionHash = newHash;
          const url = newHash ? `#${newHash}` : window.location.pathname;
          window.history.replaceState(null, "", url);
        }
        break;
      }
    }
  }
};

const getScrollMetrics = () => {
  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress =
    docHeight > 0
      ? Math.min(100, Math.max(0, (scrollTop / docHeight) * 100))
      : 0;
  return { scrollTop, docHeight, progress };
};

const updateDisplay = () => {
  const { scrollTop, docHeight, progress } = getScrollMetrics();
  progressPercent.value = Math.floor(progress);
  isComplete.value = progress >= 99.5;

  const totalSeconds = docHeight / 50;
  totalTime.value = formatTime(totalSeconds);
  currentTime.value = formatTime((scrollTop / docHeight) * totalSeconds);

  updateUrlHash();
};

const performScroll = () => {
  if (!isAutoScrolling.value || isDragging.value || userInteracted) {
    animationFrameId = null;
    return;
  }

  const { scrollTop, docHeight } = getScrollMetrics();
  const maxScroll = docHeight;

  if (scrollTop >= maxScroll - 1) {
    isAutoScrolling.value = false;
    isComplete.value = true;
    animationFrameId = null;
    return;
  }

  const step = 0.8;
  window.scrollTo({ top: scrollTop + step, behavior: "auto" });
  updateDisplay();

  animationFrameId = requestAnimationFrame(performScroll);
};

const toggleAutoScroll = () => {
  if (isAutoScrolling.value) {
    isAutoScrolling.value = false;
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  } else {
    userInteracted = false;
    isAutoScrolling.value = true;
    if (!animationFrameId) {
      animationFrameId = requestAnimationFrame(performScroll);
    }
  }
};

const stopAutoScroll = () => {
  if (isAutoScrolling.value) {
    isAutoScrolling.value = false;
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  }
};

const calculatePercentFromEvent = (clientX: number): number => {
  if (!seekBarRef.value) return progressPercent.value;
  const rect = seekBarRef.value.getBoundingClientRect();
  const percent = Math.min(
    100,
    Math.max(0, ((clientX - rect.left) / rect.width) * 100),
  );
  return Math.floor(percent);
};

const applyScrollFromPercent = (percent: number) => {
  const { docHeight } = getScrollMetrics();
  const targetScroll = (percent / 100) * docHeight;
  window.scrollTo({ top: targetScroll, behavior: "auto" });
};

const startDrag = (event: MouseEvent) => {
  isDragging.value = true;
  userInteracted = true;
  stopAutoScroll();
  const percent = calculatePercentFromEvent(event.clientX);
  progressPercent.value = percent;
  applyScrollFromPercent(percent);
};

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return;
  event.preventDefault();
  const percent = calculatePercentFromEvent(event.clientX);
  progressPercent.value = percent;
  applyScrollFromPercent(percent);
};

const startDragTouch = (event: TouchEvent) => {
  isDragging.value = true;
  userInteracted = true;
  stopAutoScroll();
  const touch = event.touches[0];
  const percent = calculatePercentFromEvent(touch.clientX);
  progressPercent.value = percent;
  applyScrollFromPercent(percent);
};

const onDragTouch = (event: TouchEvent) => {
  if (!isDragging.value) return;
  const touch = event.touches[0];
  const percent = calculatePercentFromEvent(touch.clientX);
  progressPercent.value = percent;
  applyScrollFromPercent(percent);
};

const endDrag = () => {
  if (isDragging.value) {
    isDragging.value = false;
    setTimeout(() => {
      userInteracted = false;
    }, 100);
  }
};

let rafId: number;
const updateLoop = () => {
  if (!isDragging.value) {
    updateDisplay();
  }
  rafId = requestAnimationFrame(updateLoop);
};

const handleUserScroll = () => {
  if (!isDragging.value && !isAutoScrolling.value) {
    userInteracted = true;
    updateDisplay();
    clearTimeout((handleUserScroll as unknown as { timer?: number }).timer);
    (handleUserScroll as unknown as { timer?: number }).timer =
      window.setTimeout(() => {
        userInteracted = false;
      }, 150);
  }
};

onMounted(() => {
  updateDisplay();
  window.addEventListener("scroll", handleUserScroll, { passive: true });
  rafId = requestAnimationFrame(updateLoop);
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", handleUserScroll);
  cancelAnimationFrame(rafId);
  stopAutoScroll();
});
</script>

<style scoped>
@keyframes pulse-glow {
  0%,
  100% {
    box-shadow: 0 0 5px rgba(124, 58, 237, 0.5), 0 0 20px rgba(124, 58, 237, 0.3);
    border-color: rgba(124, 58, 237, 0.8);
  }
  50% {
    box-shadow: 0 0 15px rgba(124, 58, 237, 0.8), 0 0 30px rgba(124, 58, 237, 0.5),
      0 0 45px rgba(6, 182, 212, 0.3);
    border-color: rgba(6, 182, 212, 0.9);
  }
}

.animate-pulse-glow {
  animation: pulse-glow 1.5s ease-in-out infinite;
}
</style>
