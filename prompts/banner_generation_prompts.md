# AI CDMX — Banner Generation Prompts

Reusable prompts for the API-based banner generator (OpenAI GPT Image / Google Gemini
"Nano Banana"). These are the design briefs fed to the image model(s).

The event-specific fields (Title, Subtitle, Date, Time, Speaker name, Speaker role,
Location/format, Partner logos) are injected at generation time.

---

## Prompt 1 — 6 Banner Concepts (1200 × 675, 16:9 horizontal)

Create 6 distinct, high-quality promotional banner concepts for AI CDMX.

### Format
- 1200 × 675 px (16:9), horizontal
- Keep all key content inside a safe zone roughly 15–20% from the edges
- Backgrounds and large visual elements may extend to the edges for a more immersive,
  high-energy feel
- The banner must remain readable at small sizes

### Event info (provided by the user)
- Title
- Subtitle (if available)
- Date
- Time
- Speaker name
- Speaker role
- Location / format (if relevant)
- Partner logos (if provided or shown in the template)

### Primary goal
Make each concept punchy, intentional, visually striking, emotionally compelling, and
easy to scan. The result should feel share-worthy and memorable—the opposite of a generic
event flyer. Aim for an instant emotional reaction such as excitement, curiosity, delight,
chills, urgency, necessity, or FOMO.

### Tone
Smart, creative, playful, modern, bold, slightly experimental, story-forward, and not
corporate.

### Priority order (top = most repeated and most important)

**1) Information hierarchy and clarity**
- The title must be the dominant hook
- Information must be easy to find quickly
- Maintain a clear hierarchy using typography, contrast, scale, and spacing
- Keep the design uncluttered
- Ensure readability at small sizes
- Use icons to help viewers quickly identify practical information such as date, time,
  and location

**2) Speaker image treatment**
- The speaker photo must be prominent, feel important, and be clearly tied to the event
- Use the exact provided speaker photo only; do not replace the person
- You may crop aggressively for impact, show the person partially or fully, remove the
  background, blend edges, or stylize the framing, but keep the person unchanged
- Speaker name and role should appear close to the speaker image and be easy to read
- Avoid template speaker photos
- Avoid outdated oval speaker frames unless strongly justified

**3) Composition and visual impact**
- Avoid generic centered layouts
- Use asymmetry, layering, depth, and intentional negative space
- Let some visual elements reach the edges for energy and immersion
- Backgrounds and thematic elements must support the content, not compete with it
- Favor bold, impactful shapes and focal moments over overly intricate decoration
- If detail is used, it should guide the viewer's eye, not distract from the main
  information

**4) Theme expression**
- Derive the visual direction from the event title, subtitle, and description
- Each concept must clearly express the event theme through composition, typography,
  background, and visual motifs
- Thematic elements should feel bold, intentional, and story-forward
- Thematic elements should contain no text
- They should enhance depth and atmosphere without competing with the title or event
  details

**5) Typography**
- The title should feel bespoke, expressive, premium, and specific to the banner/theme
- Typography should feel custom, not generic
- Mix type styles if useful (for example, tech + human or serif + sans)
- Use typography and contrast to reinforce hierarchy and emotional impact

**6) AI CDMX branding**
- The AI CDMX logo must be present but secondary
- Do not let the logo compete with the title or speaker
- Logo placement can be flexible, including side placement or compact / square lockups
- If the logo appears on one line, its elements should align to the same height

**7) Language and supporting elements**
- Important text should appear in English and Spanish unless the event is clearly
  single-language or a template specifies otherwise
- Partner logos, if provided, should appear cleanly near the bottom and remain within the
  content safe zone

### Color system
- Dark mode aesthetic preferred
- Deep purple / near-black base
- Neon cyan primary accent
- Magenta / pink secondary accent
- Optional subtle green or violet accents
- Use gradients, glow, contrast, and depth
- Stay within this palette family, though small supporting elements may use other colors
  if they still fit the overall aesthetic and theme

### Background rules
- No background text or decorative writing
- Backgrounds should visually support the key information and guide attention toward it
- Circuit patterns are optional and should appear in no more than 30% of the concepts

### Avoid
- Generic meetup flyers
- Overly safe corporate layouts
- Clutter
- Background text or decorative writing
- Visual elements that fight with the title or event info
- Outdated oval speaker frames unless strongly justified

---

## Prompt 2 — Square Versions (from chosen banner images)

After you have the images you want, create square versions in different sizes.

Recompose layout for square:
- Increase title size
- Simplify elements
- Prioritize visual impact
- Remove low-priority elements

### Design goal
The final result should:
- Feel like a unique, one-off poster — DO NOT simply crop the banner
- Be scroll-stopping on social
- Still clearly belong to AI CDMX as a series
