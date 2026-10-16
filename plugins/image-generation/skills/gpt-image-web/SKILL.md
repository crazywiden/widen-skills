---
name: gpt-image-web
description: Generate images by driving the ChatGPT Images web UI (https://chatgpt.com/images) through the browser, optionally with reference images, and save the results to a user-specified path. Use this skill whenever the user asks to generate, create, draw, render, or make an image, picture, illustration, logo, icon, mockup, or artwork, or to produce a variation of an image they provide — even if they don't mention ChatGPT or say "generate" explicitly.
---

# gpt-image-web

Generate images with ChatGPT Images by controlling the browser, then save the output locally. This skill uses the user's own ChatGPT session in Chrome, so it needs their consent before it runs and it never touches credentials directly.

## Before starting

1. **Ask for consent.** Because this drives the user's logged-in ChatGPT account, ask once per conversation: *"Do you want me to generate this with ChatGPT Images (chatgpt.com/images)?"* If they decline, stop and do not use this skill for the rest of the conversation unless they bring it up again.
2. **Check for a browser tool.** This skill requires a Chrome automation tool (e.g. Claude in Chrome / a browser MCP). If none is available, tell the user and stop rather than trying to fake the result.
3. **Confirm the output location.** Default to `./generated-images/` in the current working directory unless the user names a path. Create the directory if it doesn't exist.

## Workflow

### 1. Understand the request

Work out, from the user's message and any attached files:

- How many distinct images they want (one request may imply several, e.g. "a logo in three styles").
- The subject, style, mood, composition, aspect ratio, and any text that must appear in the image.
- Which local files are reference images and what role each plays (style reference, subject to edit, background, etc.).
- The desired filename(s), if the user specified any.

If the request is ambiguous in a way that materially changes the output (e.g. photo vs. illustration, portrait vs. landscape), ask one short clarifying question. Otherwise make a sensible choice and note it when reporting back.

### 2. Run one agent per image

First, start the local image receiver once, in the background, pointed at the output directory (see step 6):

```bash
python3 -I ${CLAUDE_SKILL_DIR}/receiver.py <output dir> [port]   # port defaults to 8765
```

If the port is taken, pick another and use it everywhere below. Stop the receiver after all agents finish.

Launch one subagent per image so generations can proceed in parallel and a failure in one doesn't block the others. Give each agent everything it needs: the final prompt, the list of reference image paths, the receiver port, and the filename to use. Each agent runs steps 3–6 below.

### 3. Open ChatGPT Images

Navigate to `https://chatgpt.com/images` in Chrome. If the page shows a login screen, stop and ask the user to sign in themselves — never enter credentials on their behalf. Wait for the page to be interactive before continuing.

### 4. Upload reference images (if any)

Use the page's attach/upload control to add each reference image. Verify each thumbnail appears before moving on; a silently failed upload produces a wrong result that looks like a prompt problem.

### 5. Write and submit the prompt

Turn the user's request into a single clear prompt. Good prompts state, in order:

- **Subject** — what is in the image and what it's doing
- **Style / medium** — e.g. flat vector, watercolor, studio photograph, 3D render
- **Composition** — framing, aspect ratio, background, lighting
- **Constraints** — exact text to render, colors to use or avoid, things to exclude
- **How to use each reference** — "match the color palette of the attached image", "keep the person's face unchanged, replace the background with..."

Keep the user's own wording where it is specific; expand it where it is vague. Don't add stylistic flourishes the user didn't ask for. Submit the prompt and wait for the generation to complete — this can take a minute or more, so poll patiently rather than timing out early.

### 6. Save the image locally

Do not use the page's download button or an `<a download>` click. Chrome's download flow can stall on a Save dialog or leave only a hidden `.com.google.Chrome.*` temp file in `~/Downloads`. Instead, the tab POSTs the image bytes straight to `receiver.py` on `127.0.0.1`. This works because ChatGPT's Content-Security-Policy has no `form-action` rule, so a form POST to localhost isn't blocked. No dialogs open, and the exact bytes are saved.

Name the file in kebab-case (e.g. `logo-minimal-blue`), using the user's filename if they gave one. The receiver accepts only `^[a-z0-9][a-z0-9-]*\.(png|jpg|webp)$` names whose bytes match the extension. It adds `-2`, `-3` instead of overwriting an existing file.

Run this with the browser tool's JavaScript executor in the tab that holds the result. Set `base` and `port` first:

```js
await (async () => {
  const base = 'logo-minimal-blue', port = 8765;
  const imgs = [...document.querySelectorAll('img')].filter(i => /^Generated image/.test(i.alt) && i.naturalWidth > 500 && i.complete);
  const img = imgs[imgs.length - 1];
  const b = await fetch(img.src).then(r => r.blob());
  const ext = {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp'}[b.type];
  const f = document.createElement('form');
  f.method = 'POST'; f.enctype = 'multipart/form-data'; f.action = `http://127.0.0.1:${port}/upload`;
  const inp = document.createElement('input'); inp.type = 'file'; inp.name = 'file';
  const dt = new DataTransfer(); dt.items.add(new File([b], `${base}.${ext}`, {type: b.type}));
  inp.files = dt.files; f.appendChild(inp); document.body.appendChild(f);
  setTimeout(() => f.submit(), 50);
  return {name: `${base}.${ext}`, type: b.type, size: b.size, back: location.href};
})()
```

- `Generated image N` is the alt text ChatGPT used as of 2026-10. If nothing matches, find the result image by screenshot and adjust the filter.
- The submit loads the receiver's reply page in the tab: `SAVED <file> <bytes>` on success, or an error. Read it, check that the byte count equals the returned `size`, and confirm the file is on disk with `ls -la`.
- Navigate back to the returned `back` URL if you need that conversation again.

## Handling problems

- **Content refusal or empty result:** report the refusal message verbatim and ask the user how they'd like to adjust the prompt. Don't silently rewrite the prompt to work around a refusal.
- **Rate limit or quota message:** stop and tell the user; don't retry in a loop.
- **Page layout differs from expectations:** take a screenshot, locate the controls by their visible labels, and adapt. Don't hard-code selectors.
- **Receiver POST fails** (the tab shows a CSP or connection error, or the receiver logs nothing): check that the receiver is running on that port. If ChatGPT's CSP now blocks `form-action`, fall back to an `<a download>` click on the blob URL, then copy the file from `~/Downloads`, including any hidden `.com.google.Chrome.*` temp file. Tell the user the default path broke.
- **Result clearly doesn't match the request:** regenerate at most once with a tightened prompt, then show the user what you got and let them decide.

## Reporting back

When all agents finish, give the user one concise summary: the path of each saved file, the prompt used for it, and any decisions you made on their behalf (assumed aspect ratio, chosen style, etc.). Offer to iterate on any image they'd like changed.
