interface YouTubePlayer {
  playVideo: () => void;
  pauseVideo: () => void;
  seekTo: (seconds: number, allowSeekAhead: boolean) => void;
  getPlayerState: () => number;
  mute: () => void;
  unMute: () => void;
  isMuted: () => boolean;
  destroy: () => void;
}

declare global {
  interface Window {
    YT: {
      Player: new (
        elementId: string,
        options: {
          videoId: string;
          playerVars: Record<string, number | string>;
          events: {
            onReady?: (event: { target: YouTubePlayer }) => void;
            onStateChange?: (event: {
              data: number;
              target: YouTubePlayer;
            }) => void;
            onError?: (event: { data: number }) => void;
          };
        },
      ) => YouTubePlayer;
      PlayerState: {
        PLAYING: number;
        PAUSED: number;
        ENDED: number;
      };
    };
    onYouTubeIframeAPIReady?: () => void;
  }
}

export const useYouTubePlayer = () => {
  const player = ref<YouTubePlayer | null>(null);
  const isReady = ref(false);
  const isPlaying = ref(false);
  const currentTime = ref(0);
  const duration = ref(267);

  const VIDEO_ID = "zSJnd_S_jVk";

  const initPlayer = (elementId: string = "yt-player") => {
    if (!window.YT) {
      console.warn("YouTube API not loaded yet");
      return;
    }

    player.value = new window.YT.Player(elementId, {
      videoId: VIDEO_ID,
      playerVars: {
        autoplay: 1,
        controls: 0,
        disablekb: 1,
        fs: 0,
        iv_load_policy: 3,
        loop: 1,
        modestbranding: 1,
        mute: 1,
        playsinline: 1,
        rel: 0,
        showinfo: 0,
        start: 0,
        playlist: VIDEO_ID,
      },
      events: {
        onReady: (event) => {
          isReady.value = true;
          event.target.playVideo();
          event.target.mute();
          console.log("YouTube player ready");
        },
        onStateChange: (event) => {
          isPlaying.value = event.data === window.YT.PlayerState.PLAYING;

          if (event.data === window.YT.PlayerState.ENDED) {
            event.target.seekTo(0, true);
            event.target.playVideo();
          }
        },
        onError: (event) => {
          console.error("YouTube player error:", event.data);
        },
      },
    });
  };

  const destroy = () => {
    if (player.value) {
      player.value.destroy();
      player.value = null;
      isReady.value = false;
      isPlaying.value = false;
    }
  };

  onMounted(() => {
    if (window.YT?.Player) {
      initPlayer();
    } else {
      const checkAPI = setInterval(() => {
        if (window.YT?.Player) {
          clearInterval(checkAPI);
          initPlayer();
        }
      }, 100);

      setTimeout(() => clearInterval(checkAPI), 10000);
    }
  });

  onUnmounted(() => {
    destroy();
  });

  return {
    player,
    isReady,
    isPlaying,
    currentTime,
    duration,
    initPlayer,
    destroy,
  };
};
