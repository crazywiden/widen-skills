---
name: get-image-text-section
description: Create and publish 3 conversion-focused image-with-text sections for a Shopify product page. Analyzes one product (variants, pricing, description, images), picks its 3 strongest selling points, writes a headline and short copy for each, generates on-brand product images, reviews and revises them, then adds the sections to the store's theme. Use this skill whenever the user shares a Shopify product link or product ID and wants to improve, enrich, or "make more converting" the product page, add feature/benefit blocks, image-and-text sections, lifestyle images, or selling-point content — even if they don't say "image-text section" explicitly.
---

# get-image-text-section

Turn one Shopify product into 3 polished image-with-text sections that explain why a shopper should buy it, and install them on the product page.

The goal is conversion: each section should answer a question a hesitant shopper has ("Why this one?", "Will it fit my life?", "Is it worth the price?"). Every step below serves that goal, so when in doubt, choose what helps a real customer decide.

## Inputs

- **Required:** a product reference, usually a Shopify admin URL such as `https://admin.shopify.com/store/<store-handle>/products/<product-id>`. A storefront URL, product handle, or numeric ID also works.
- **Optional:** brand voice notes, target audience, preferred image style, or which theme to edit. If the user gave any of these, they override the defaults below.

## Workflow

### 1. Understand the product

Parse the store handle and product ID from the link, then fetch the product through the Shopify Admin API (or the connected Shopify tool). Collect:

1. Title, product type, vendor, and tags
2. Variants (options such as size, color, material) and their prices, including compare-at prices
3. Full description (strip HTML)
4. All product images and their URLs — these are the ground truth for what the product looks like and will be used as references in step 3
5. The product's current `templateSuffix`, if any. (needed in step 5)

If the product can't be fetched (bad link, missing permission), stop and tell the user what failed rather than guessing about the product.

**Pick 3 selling points.** Read everything above and choose the 3 points most likely to move a buyer. Good selling points are:

- **Benefits, not just specs.** "Stays cold for 24 hours" beats "double-wall steel."
- **Specific to this product.** Avoid points that apply to every product in the category ("high quality," "great value").
- **Distinct from each other.** Cover different angles, for example one about performance, one about design or materials, one about everyday use or who it's for.
- **Supported by the product data.** Never invent claims, certifications, or numbers that aren't in the description, variants, or images. Unsupported claims hurt trust and can create legal risk.

Write down, for each point, the evidence from the product data that backs it up. You'll use this in the review step.

### 2. Write the copy for each selling point

Image-with-text sections usually show a heading and a short paragraph, so write both:

- **Headline:** 3–8 words. Creative and memorable, but the meaning must be clear at a glance. Lead with the benefit.
- **Body:** 1–2 sentences (roughly 20–40 words) that make the headline concrete with a specific detail from the product data.
- **Optional button label:** only if there is a natural action (e.g. "Choose your color").

Match the brand's existing tone, which you can infer from the product description. Keep the 3 headlines consistent in style and length so the page feels designed, not assembled.

**Example**

> Selling point: vacuum insulation keeps drinks cold for 24 hours
> Headline: *Ice at Noon. Ice at Midnight.*
> Body: *Double-wall vacuum insulation keeps your drink cold for a full 24 hours, so the last sip tastes like the first.*

Avoid clichés like "Elevate your…", "Unleash…", or "Game-changer"; they read as generic and lower credibility.

### 3. Generate an image for each selling point

Use the `gpt-image-web` skill (`/image-generation:gpt-image-web`) to create one image per selling point. The most common failure here is an image that looks great but shows a product that isn't the real one, which misleads shoppers and leads to returns. So:

- **Always pass the real product image(s) as reference** and instruct the model to keep the product's shape, colors, materials, logo, and proportions unchanged.
- **Show the selling point visually.** The image should illustrate the headline (the product in use, a close-up of the feature, the result it delivers), not just the product on a blank background, which the main gallery already covers.
- **Keep a consistent look across all 3 images:** same lighting style, color palette, and level of polish, so the sections look like one campaign.
- **Leave room for the layout.** Image-with-text sections place text beside the image, so avoid text, watermarks, or logos baked into the image, and keep the product away from the edges so it survives cropping.
- **Format:** generate at the aspect ratio the theme section expects (check the section's settings; default to 1:1 or 4:3 if unknown), at least 1600 px on the long edge, saved as WebP or high-quality JPG.

**Prompt template**

```
Professional commercial product photograph of [product, described precisely from the reference image],
[scene that demonstrates the selling point],
[lighting: e.g. soft natural daylight / clean studio lighting], [mood],
premium e-commerce style, sharp focus on the product, realistic materials and textures,
no text, no watermarks. Keep the product identical to the reference image.
```

### 4. Review and revise

Run the review as a separate pass (a fresh subagent if available, otherwise a deliberately separate step) so the reviewer judges the result rather than the intention behind it. Score each image-text pair against:

| Criterion | Pass when |
|---|---|
| Image quality | Sharp, well lit, realistic; no warped shapes, extra parts, garbled text, or AI artifacts |
| Product fidelity | The product matches the real product images in shape, color, materials, and branding |
| Copy–product fit | The headline and body are accurate and supported by the evidence noted in step 1 |
| Copy–image fit | The image clearly illustrates the headline |
| Consistency | The 3 sections share a visual style and tone of voice |

For every criterion that fails, give feedback that is specific and actionable (for example "the lid is black but should be brushed steel; regenerate with the lid color stated explicitly in the prompt"), not general ("make it better"). Apply the fixes, then review again. Limit this to 2 revision rounds; if a pair still fails, flag it for the user instead of looping.

Before touching the theme, show the user the 3 final pairs (images, headlines, body copy) and get their go-ahead. This is the cheapest point to change direction.

### 5. Add the sections to the Shopify theme

Changes to a live storefront are visible to customers immediately, so work on a safe copy and let the user publish.

1. **Upload the images** to the store's Files (Admin API `stagedUploadsCreate` + `fileCreate`) and keep the returned file references.
2. **Pick the theme:** use the theme the user named; otherwise duplicate the live theme and edit the copy. Don't edit the live theme unless the user explicitly asks.
3. **Make the sections product-specific.** Adding sections to `templates/product.json` would show them on every product. Instead, create a new template (e.g. `templates/product.<product-handle>.json`) based on the current product template, and add 3 image-with-text sections (Dawn and most Online Store 2.0 themes call it `image-with-text`) after the main product section, filled with the uploaded images and copy. Then set the product's `templateSuffix` to the new template. If the product already uses a custom template, add the sections to that one instead.
4. **Verify:** open the theme preview link for the product page, confirm all 3 sections render on desktop and mobile, and share the preview link with the user.

**Permissions.** This step needs the `write_files`, `write_themes`, and `write_products` access scopes. If any call fails with an access or permission error, stop, tell the user exactly which action failed and which scope is likely missing, and hand over the finished images and copy so they can add the sections manually in the theme editor.

## Final output to the user

End with a short summary containing:

- The 3 selling points, each with its headline and body copy
- The 3 final images (or links to them)
- What changed in the store: theme name, template file, and whether the product's template was switched
- The preview link, and a reminder that the theme copy must be published to go live
- Any items flagged in review or any steps that failed
