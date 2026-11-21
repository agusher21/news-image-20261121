// A working news-image-daily entry (Node 22, standard library only): its image is the entry.png beside this file, and
// the program copies it to /output/entry.png. A starting point, not a winner: replace the image. The gate takes a
// whole PNG or JPEG of at most 1 MiB and 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
//
// This version generates the image deterministically via Python PIL.

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';

// Generate the image deterministically using our Python script
const result = spawnSync('python3', ['generate_image.py'], { 
  cwd: import.meta.dirname,
  stdio: 'inherit'
});
if (result.status !== 0) {
  throw new Error(`Image generation failed with exit code ${result.status}`);
}

// Copy the generated image to the output directory
copyFileSync(join(import.meta.dirname, 'out', 'entry.png'), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
