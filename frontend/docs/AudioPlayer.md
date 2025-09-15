# Audio Player Component

The application has several places where audio playback is needed - sentence display, source file audio, and flashcards. This document outlines our shared `AudioPlayer` component that provides consistent audio functionality across the application.

## Design Goals

- **Consistency**: Provide a unified audio experience throughout the application
- **Reusability**: Reduce code duplication across components
- **Flexibility**: Support different use cases while maintaining a core set of features
- **Simplicity**: Focus on essential audio functionality without overcomplicating

## Usage

```svelte
<script>
  import { AudioPlayer } from '$lib';
  
  // Basic usage
  let audioPlayer;
</script>

<!-- Basic usage -->
<AudioPlayer 
  bind:this={audioPlayer}
  src="https://example.com/audio.mp3"
  downloadUrl="https://example.com/download/audio.mp3"
  showDownload={true}
  autoplay={false}
/>

<!-- Programmatic control -->
<button on:click={() => audioPlayer.play()}>Play</button>
<button on:click={() => audioPlayer.pause()}>Pause</button>
<button on:click={() => audioPlayer.setPlaybackRate(0.9)}>Slow Down</button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `src` | string | required | URL of the audio file to play |
| `downloadUrl` | string | `src` | URL for the download link (defaults to `src` if not provided) |
| `autoplay` | boolean | `false` | Whether to automatically play audio on mount |
| `showControls` | boolean | `true` | Whether to show the native audio controls |
| `showSpeedControls` | boolean | `true` | Whether to show playback speed controls |
| `showDownload` | boolean | `true` | Whether to show the download button |
| `className` | string | `''` | Additional CSS classes for the container |
| `containerStyle` | string | `''` | Additional inline styles for the container |

## Methods/Properties

The component exposes several methods and properties for controlling audio playback programmatically:

| Method/Property | Description |
|----------------|-------------|
| `play()` | Start playing the audio |
| `pause()` | Pause the audio |
| `setPlaybackRate(rate)` | Set the playback rate (0.8, 0.85, 0.9, 0.95, 1.0, or 1.2) |
| `isPlaying()` | Returns a boolean indicating if audio is currently playing |

## Events

| Event | Description |
|-------|-------------|
| `on:play` | Fired when audio starts playing |
| `on:pause` | Fired when audio is paused |
| `on:ended` | Fired when audio playback completes |
| `on:error` | Fired when an error occurs during playback |
| `on:loadstart` | Fired when loading starts |
| `on:canplay` | Fired when audio can start playing |
| `on:autoplayBlocked` | Fired when the browser blocks autoplay |
| `on:speedChanged` | Fired when playback speed is changed via UI |

## Example Implementations

### Basic Audio Player

```svelte
<AudioPlayer 
  src={audioUrl} 
  downloadUrl={downloadUrl}
/>
```

### Flashcard Audio Player (Autoplay)

```svelte
<AudioPlayer 
  bind:this={audioPlayer}
  src={data.audio_url}
  autoplay={true}
  showDownload={false}
/>

<!-- External controls -->
<button on:click={() => audioPlayer.play()}>Replay Audio</button>
```

### Minimal Audio Player

```svelte
<AudioPlayer 
  src={audioUrl}
  showControls={true}
  showSpeedControls={false}
  showDownload={false}
/>
```

## Implementation Details

- Consistent UI styling using Bootstrap and project CSS variables
- Audio playback speed options: 0.8x, 0.85x, 0.9x, 0.95x, 1.0x, and 1.2x
- Error message display on playback failure
- Loading state using `LoadingSpinner` component
- Standardized approach using Svelte binding for audio element referencing

## CSS/Styling

The component uses the application's theme variables for styling consistency:

- Buttons use standard Bootstrap classes with our custom theme colors
- Container uses `audio-view` class with flexbox layout
- Speed control buttons use Bootstrap's button styling with state indication
- Download button uses the accent sky blue color (`--hz-color-accent-sky-blue`)

## Loading & Error States

- While audio is loading, the component displays a `LoadingSpinner` component
- The loading spinner will disappear automatically after 5 seconds if audio fails to load
- On error, a helpful message is displayed to the user
- The component specially handles autoplay restrictions (no error shown)
- Autoplay will often fail due to browser security when users haven't interacted with the page yet
- The component does not implement retries or fallbacks

## Accessibility

- Native audio controls provide built-in accessibility features
- Additional buttons include appropriate ARIA labels
- Keyboard navigation supported for all controls

## See also

- `../../docs/reference/AUDIO.md` – System-wide audio architecture and lemma variant design

