<template>
  <div>
    <ClientOnly>
      <PreloaderOverlay />
    </ClientOnly>
    <div id="app-content">
      <slot />
    </div>
  </div>
</template>
