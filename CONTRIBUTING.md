# Contributing

## Repository layout

```
.claude-plugin/marketplace.json        # lists every plugin
plugins/<plugin-name>/
  .claude-plugin/plugin.json           # plugin manifest
  skills/<skill-name>/SKILL.md         # plus any scripts/, references/, assets/
```

## Add a skill to an existing plugin

1. Create `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`. Use a kebab-case folder name.
2. Start `SKILL.md` with YAML frontmatter. The opening `---` must be the first line:

   ```markdown
   ---
   name: my-skill
   description: What the skill does and when Claude should use it. Put the main use case first.
   ---

   # my-skill

   Instructions...
   ```

   - `name` must match the folder name.
   - Keep `description` specific and under 1,536 characters.
   - For Claude.ai compatibility, use only `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools` in the frontmatter.
3. Put bundled files next to `SKILL.md` (for example `scripts/`, `references/`, `assets/`) and reference them as `${CLAUDE_SKILL_DIR}/scripts/...` so the paths resolve wherever the plugin is installed.
4. To call a skill from another plugin, refer to it by its namespaced name (`/<plugin-name>:<skill-name>`) and add that plugin to `dependencies` in your plugin's `plugin.json`.
5. Bump `version` in the plugin's `.claude-plugin/plugin.json` (for example `1.0.0` to `1.1.0`). Users only receive the change after the version changes.
6. Add a row for the skill to the catalog table in `README.md`.

Skills in `skills/` are discovered automatically; you don't need to list them in `plugin.json`.

## Add a new plugin

1. Create `plugins/<plugin-name>/.claude-plugin/plugin.json`:

   ```json
   {
     "name": "<plugin-name>",
     "version": "1.0.0",
     "description": "One-line description",
     "author": { "name": "Your Name" },
     "license": "MIT"
   }
   ```

   Plugin names must be kebab-case and must not start with `claude-` or `anthropic-`.
2. Add skills under `plugins/<plugin-name>/skills/` as described above.
3. Register the plugin in `.claude-plugin/marketplace.json`. The entry `name` must equal the `name` in `plugin.json`, and `source` is relative to the repository root:

   ```json
   {
     "name": "<plugin-name>",
     "source": "./plugins/<plugin-name>",
     "description": "One-line description"
   }
   ```

   Keep `version` in `plugin.json` only.
4. Add the plugin and its skills to the catalog table in `README.md`.

## Test before opening a pull request

```bash
claude plugin validate .
claude plugin marketplace add ./
claude plugin install <plugin-name>@widen-skills
claude plugin details <plugin-name>
```

Then start a session and try the skill. When you are done, remove the local marketplace with `claude plugin marketplace remove widen-skills`.

Never commit API keys, tokens, store URLs, customer data, or personal paths. Use placeholders such as `<store-handle>` in examples.
