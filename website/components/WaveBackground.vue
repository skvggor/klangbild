<template>
  <div
    ref="container"
    class="absolute inset-0 w-full h-full pointer-events-none"
    style="background: transparent;"
  >
    <canvas
      ref="canvas"
      class="w-full h-full"
      style="display: block; background: transparent;"
    />
  </div>
</template>

<script setup lang="ts">
import * as THREE from "three";

const container = ref<HTMLDivElement | null>(null);
const canvas = ref<HTMLCanvasElement | null>(null);

onMounted(() => {
  if (!container.value || !canvas.value) {
    console.error("[WaveBackground] Missing refs");
    return;
  }

  const width = container.value.clientWidth || window.innerWidth;
  const height = container.value.clientHeight || window.innerHeight;

  const scene = new THREE.Scene();

  const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 1000);
  camera.position.z = 40;

  const renderer = new THREE.WebGLRenderer({
    canvas: canvas.value,
    alpha: true,
    antialias: true,
  });
  renderer.setSize(width, height);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x000000, 0);

  // Calculate visible width at camera distance to make waves fill 100% of screen
  const fov = 50;
  const distance = 40;
  const visibleHeight = 2 * Math.tan((fov * Math.PI) / 180 / 2) * distance;
  const visibleWidth = visibleHeight * (width / height);
  const waveWidth = visibleWidth * 1.1; // Add 10% padding to ensure full coverage
  const halfWidth = waveWidth / 2;

  const segments = 80;

  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array((segments + 1) * 3);
  for (let i = 0; i <= segments; i++) {
    const x = (i / segments) * waveWidth - halfWidth;
    positions[i * 3] = x;
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
    const x = (i / segments) * waveWidth - halfWidth;
    mirrorPositions[i * 3] = x;
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

      const wave1 = Math.sin(t * Math.PI * 6 + time * 2) * 4;
      const wave2 = Math.sin(t * Math.PI * 12 + time * 3) * 2;
      const wave3 = Math.cos(t * Math.PI * 3 + time * 1.5) * 2.5;

      const y = (wave1 + wave2 + wave3) * fade;

      pos[i * 3 + 1] = y;
      mirrorPos[i * 3 + 1] = -y;
    }

    geometry.attributes.position.needsUpdate = true;
    mirrorGeometry.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
  };

  animate();

  const handleResize = () => {
    if (!container.value) return;
    const newWidth = container.value.clientWidth || window.innerWidth;
    const newHeight = container.value.clientHeight || window.innerHeight;
    camera.aspect = newWidth / newHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(newWidth, newHeight);

    // Recalculate wave width for new screen size
    const fov = 50;
    const distance = 40;
    const visibleHeight = 2 * Math.tan((fov * Math.PI) / 180 / 2) * distance;
    const visibleWidth = visibleHeight * (newWidth / newHeight);
    const waveWidth = visibleWidth * 1.1;
    const halfWidth = waveWidth / 2;

    // Update wave geometry positions
    const pos = geometry.attributes.position.array as Float32Array;
    const mirrorPos = mirrorGeometry.attributes.position.array as Float32Array;
    for (let i = 0; i <= segments; i++) {
      const x = (i / segments) * waveWidth - halfWidth;
      pos[i * 3] = x;
      mirrorPos[i * 3] = x;
    }
    geometry.attributes.position.needsUpdate = true;
    mirrorGeometry.attributes.position.needsUpdate = true;
  };

  window.addEventListener("resize", handleResize);

  onBeforeUnmount(() => {
    cancelAnimationFrame(animationId);
    window.removeEventListener("resize", handleResize);
    geometry.dispose();
    mirrorGeometry.dispose();
    material.dispose();
    mirrorMaterial.dispose();
    renderer.dispose();
  });
});
</script>
