# widen-skills

Agent skills for Claude, packaged as a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces). Each plugin groups related skills so you can install only what you need.

## Catalog

| Plugin | Skill | Description |
|---|---|---|
| `image-generation` | `gpt-image-web` | Generate images through the ChatGPT Images web UI in Chrome, with optional reference images, and save them locally. |
| `shopify-merchandising` | `get-image-text-section` | Turn one Shopify product into 3 conversion-focused image-with-text sections and add them to a theme copy. |

`shopify-merchandising` depends on `image-generation`; installing it installs `image-generation` too.

## Install in Claude Code

Add the marketplace, then install a plugin:

```
/plugin marketplace add crazywiden/widen-skills
/plugin install image-generation@widen-skills
/plugin install shopify-merchandising@widen-skills
```

Or from your shell:

```bash
claude plugin marketplace add crazywiden/widen-skills
claude plugin install shopify-merchandising@widen-skills
```

Plugin skills are namespaced by plugin, for example `/image-generation:gpt-image-web` and `/shopify-merchandising:get-image-text-section`. Claude also invokes them automatically when a request matches their description.

To get updates later:

```
/plugin marketplace update widen-skills
```

## Manual install

**Claude Code without the marketplace:** copy a skill folder into your personal skills directory.

```bash
git clone https://github.com/crazywiden/widen-skills.git
cp -R widen-skills/plugins/image-generation/skills/gpt-image-web ~/.claude/skills/
cp -R widen-skills/plugins/shopify-merchandising/skills/get-image-text-section ~/.claude/skills/
```

Copy `gpt-image-web` whenever you copy `get-image-text-section`, since the latter uses it to generate images. Manually installed skills are not namespaced, so they run as `/gpt-image-web` and `/get-image-text-section`.

**Claude.ai:** zip a skill folder (the folder that contains `SKILL.md`) and upload it in the Skills section of Claude.ai settings. Note that both skills currently rely on Claude Code capabilities (Chrome browser automation, a local Python receiver, subagents, and Shopify Admin API access), so they will not work fully on Claude.ai.

## Requirements

- **`image-generation`**: a Chrome automation tool such as Claude in Chrome, a ChatGPT account signed in to Chrome, and `python3` for the bundled `receiver.py`, which saves images to disk on `127.0.0.1`.
- **`shopify-merchandising`**: Shopify Admin API access through a connected Shopify tool, with the `write_files`, `write_themes`, and `write_products` scopes. The skill edits a duplicate of your live theme and leaves publishing to you.

## Disclaimer

`gpt-image-web` drives your own signed-in ChatGPT session in the browser. It asks for consent before running and never enters credentials, but you are responsible for making sure this use complies with OpenAI's terms of service. ChatGPT's page layout can change at any time and may break the skill.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
