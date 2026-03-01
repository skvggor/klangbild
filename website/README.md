# Klangbild Landing Page

Nuxt 3 website for klangbild - 4K Audio Visualizer

## Development

```bash
cd website
npm install
npm run dev
```

## Build

```bash
npm run build
```

## CMS (Content Management)

Edit YAML files in `content/` folder to update website content without touching code:

- `hero.yml` - Hero section text and CTAs
- `features.yml` - Feature list
- `examples.yml` - Layout examples
- `quickstart.yml` - Code examples
- `footer.yml` - Footer links and info

## Deploy

Push to `main` branch triggers automatic deployment via GitHub Actions.

## Structure

```
website/
├── components/       # Vue components
├── composables/      # Vue composables
├── content/          # YAML content files (CMS)
├── pages/            # Nuxt pages
├── assets/           # CSS, images
├── public/           # Static files
├── Dockerfile        # Production build
└── compose.yml       # Docker Compose config
```
