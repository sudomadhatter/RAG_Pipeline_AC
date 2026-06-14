---
description: Convert green screen MP4 videos to WebM with true alpha transparency for floating UI elements.
---

# WebM Alpha Conversion Workflow

**Goal:** Process raw green screen `.mp4` video files into web-optimized `.webm` files with native alpha channel transparency using FFmpeg.

**Context:** This workflow is used specifically for creating "floating" video assets (like the AI Agent Avatars) that need to overlay on top of complex UI backgrounds (like glassmorphism) without a bounding box. MP4 codecs do not support alpha channels; this workflow bypasses that limitation. 

## Prerequisites

1. FFmpeg must be installed on the system.
   - Run `ffmpeg -version` to verify.
   - If not installed (Windows), run: `winget install --id Gyan.FFmpeg -e --source winget`

## Required Inputs

You need three things before running this workflow:
1.  **Input File Path:** The absolute or relative path to the `.mp4` file.
2.  **Output File Path:** Where the `.webm` file should be saved (usually `frontend/public/assets/`).
3.  **Exact Hex Color:** The specific color code of the green screen (e.g., `#27BB36`).

## Step 1: Execute the FFmpeg Chromakey Conversion

Use the following `run_command` replacing the variables in brackets. 

**Critical Parameters:**
- `chromakey=0x[HEX_CODE]:0.15:0.02`: The first number is the similarity threshold (how aggressive the cut is). `0.15` is a tight key. The second number is the blend/feathering (how sharp the edge is). `0.02` is slightly soft. If the character is getting erased, lower the similarity to `0.10`.
- `format=yuva420p`: This is the crucial flag that adds the `a` (alpha channel) structure so the transparency is retained.
- `-c:v libvpx-vp9`: Forces the VP9 codec, which is required for transparent WebM to render in Chrome/Safari.

// turbo
```powershell
$input_file = "[path\to\input.mp4]"
$output_file = "[path\to\output.webm]"
$hex = "[HEX_CODE]" # Do not include the # symbol

ffmpeg -i $input_file -vf "chromakey=0x${hex}:0.15:0.02,format=yuva420p" -c:v libvpx-vp9 -auto-alt-ref 0 -b:v 0 -crf 28 -y $output_file 2>&1 | Select-Object -Last 10
```

> **Note on Exit Codes:** The VP9 encoder often throws an `Exit code: 1` when the muxer closes the file, even if the conversion was 100% successful. Always verify the file size of the output `.webm` — if it's > 500KB, it likely succeeded.

## Step 2: Verify File Output

Ensure the output file was created and has a reasonable file size.

// turbo
```powershell
Get-Item -Path $output_file | Select-Object Name, Length
```

## Step 3: Implement the Frontend Target

When updating the React/Next.js frontend, enforce the following standard for the `<video>` element to ensure it plays silently and automatically without user interaction.

```tsx
<video
    src="/assets/[your_file].webm"
    poster="/assets/[your_fallback_image].png"
    autoPlay
    muted
    loop
    playsInline
    className="opacity-80 object-contain drop-shadow-2xl"
/>
```

**Implementation Rules:**
- `muted` and `playsInline` are strictly required, otherwise modern browsers will block the `autoPlay`.
- Always provide a `poster` image (the static PNG equivalent) so the UI doesn't look broken while the video asset loads.
- Adjust `opacity` based on the background to make the asset feel cohesive rather than "pasted on."