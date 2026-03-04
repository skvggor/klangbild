<template>
  <Transition name="preloader-fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-[9999] flex items-center justify-center bg-[#0a0a0f]"
    >
      <canvas
        ref="canvas"
        class="w-64 h-32 md:w-80 md:h-40"
        style="display: block;"
      />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import * as THREE from "three";

const visible = ref(true);
const canvas = ref<HTMLCanvasElement | null>(null);

onMounted(() => {
  if (!canvas.value) return;

  const width = canvas.value.clientWidth;
  const height = canvas.value.clientHeight;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
  camera.position.z = 20;

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas.value,
    alpha: true,
    antialias: true,
  });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);

  const fov = 50;
  const distance = 20;
  const visibleHeight = 2 * Math.tan((fov * Math.PI) / 180 / 2) * distance;
  const visibleWidth = visibleHeight * (width / height);
  const waveWidth = visibleWidth * 0.9;
  const halfWidth = waveWidth / 2;
  const segments = 60;

  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array((segments + 1) * 3);
  for (let i = 0; i <= segments; i++) {
    positions[i * 3] = (i / segments) * waveWidth - halfWidth;
    positions[i * 3 + 1] = 0;
    positions[i * 3 + 2] = 0;
  }
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

  const material = new THREE.LineBasicMaterial({
    color: 0xc084fc,
    transparent: true,
    opacity: 1,
  });
  const line = new THREE.Line(geometry, material);
  scene.add(line);

  const mirrorGeometry = new THREE.BufferGeometry();
  const mirrorPositions = new Float32Array((segments + 1) * 3);
  for (let i = 0; i <= segments; i++) {
    mirrorPositions[i * 3] = (i / segments) * waveWidth - halfWidth;
    mirrorPositions[i * 3 + 1] = 0;
    mirrorPositions[i * 3 + 2] = 0;
  }
  mirrorGeometry.setAttribute(
    "position",
    new THREE.BufferAttribute(mirrorPositions, 3),
  );

  const mirrorMaterial = new THREE.LineBasicMaterial({
    color: 0x67e8f9,
    transparent: true,
    opacity: 1,
  });
  const mirrorLine = new THREE.Line(mirrorGeometry, mirrorMaterial);
  scene.add(mirrorLine);

  let time = 0;
  let animationId: number;

  const animate = () => {
    animationId = requestAnimationFrame(animate);
    time += 0.015;

    const pos = geometry.attributes.position.array as Float32Array;
    const mirrorPos = mirrorGeometry.attributes.position.array as Float32Array;

    for (let i = 0; i <= segments; i++) {
      const t = i / segments;
      const centerDist = Math.abs(t - 0.5) * 2;
      const fade = 1 - centerDist ** 2;

      const wave1 = Math.sin(t * Math.PI * 6 + time * 2) * 2;
      const wave2 = Math.sin(t * Math.PI * 12 + time * 3) * 1;
      const wave3 = Math.cos(t * Math.PI * 3 + time * 1.5) * 1.2;

      const y = (wave1 + wave2 + wave3) * fade;
      pos[i * 3 + 1] = y;
      mirrorPos[i * 3 + 1] = -y;
    }

    geometry.attributes.position.needsUpdate = true;
    mirrorGeometry.attributes.position.needsUpdate = true;
    renderer.render(scene, camera);
  };

  animate();

  const cleanup = () => {
    cancelAnimationFrame(animationId);
    geometry.dispose();
    mirrorGeometry.dispose();
    material.dispose();
    mirrorMaterial.dispose();
    renderer.dispose();
  };

  const dismiss = () => {
    setTimeout(() => {
      visible.value = false;
      document.getElementById("app-content")?.classList.add("is-ready");
      setTimeout(cleanup, 600);
    }, 800);
  };

  if (document.readyState === "complete") {
    dismiss();
  } else {
    window.addEventListener("load", dismiss, { once: true });
  }

  onBeforeUnmount(cleanup);
});
</script>

<style>
.preloader-fade-leave-active {
  transition: opacity 0.5s ease-out;
}

.preloader-fade-leave-to {
  opacity: 0;
}
</style>
