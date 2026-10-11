# Typefaces

These are the typeface files the planner prints with. They live in the repo, so
a fresh clone builds every look and every typeface set with no download step.
They were added to the repo on 2026-10-10.

- 83 families, 251 `.woff2` files, covering all 52 built-in typeface sets.
- Every file came from Google Fonts, unchanged. `python planner.py fonts --all`
  fetched them.
- Licences: 77 families use the SIL Open Font License 1.1 and 6 use the
  Apache License 2.0. No family here uses the Ubuntu Font Licence. All of these
  licences allow the fonts to be copied, bundled and redistributed, including
  in PDFs you sell.
- Each family's own licence text is in [`licenses/`](licenses/). An OFL file
  starts with that family's copyright line. Apache 2.0 licence files carry no
  copyright line, so those holders are listed at the end of this page.

## Refresh or re-download

The files are already here. To refresh them from Google Fonts (for example
after a family is revised, or to add a family for a custom set):

```
python planner.py fonts --all      # every built-in set, skips files already here
python planner.py fonts --looks    # only the sets the thirteen looks use
python planner.py fonts --all --force   # re-download every file
```

If you add a new family, add its licence file to `licenses/` and a row to the
table below before you commit it.

## Families

| Family | Licence | Licence file | Source | Files |
|--------|---------|--------------|--------|-------|
| Abril Fatface | SIL OFL 1.1 | [abril-fatface-OFL.txt](licenses/abril-fatface-OFL.txt) | [google/fonts `ofl/abrilfatface`](https://github.com/google/fonts/tree/main/ofl/abrilfatface) | `abril-fatface-400.woff2`, `abril-fatface-600.woff2`, `abril-fatface-700.woff2` |
| Alex Brush | SIL OFL 1.1 | [alex-brush-OFL.txt](licenses/alex-brush-OFL.txt) | [google/fonts `ofl/alexbrush`](https://github.com/google/fonts/tree/main/ofl/alexbrush) | `alex-brush-400.woff2` |
| Alfa Slab One | SIL OFL 1.1 | [alfa-slab-one-OFL.txt](licenses/alfa-slab-one-OFL.txt) | [google/fonts `ofl/alfaslabone`](https://github.com/google/fonts/tree/main/ofl/alfaslabone) | `alfa-slab-one-400.woff2`, `alfa-slab-one-600.woff2`, `alfa-slab-one-700.woff2` |
| Allura | SIL OFL 1.1 | [allura-OFL.txt](licenses/allura-OFL.txt) | [google/fonts `ofl/allura`](https://github.com/google/fonts/tree/main/ofl/allura) | `allura-400.woff2` |
| Amatic SC | SIL OFL 1.1 | [amatic-sc-OFL.txt](licenses/amatic-sc-OFL.txt) | [google/fonts `ofl/amaticsc`](https://github.com/google/fonts/tree/main/ofl/amaticsc) | `amatic-sc-400.woff2`, `amatic-sc-600.woff2`, `amatic-sc-700.woff2` |
| Andika | SIL OFL 1.1 | [andika-OFL.txt](licenses/andika-OFL.txt) | [google/fonts `ofl/andika`](https://github.com/google/fonts/tree/main/ofl/andika) | `andika-400.woff2`, `andika-400i.woff2`, `andika-700.woff2`, `andika-800.woff2` |
| Anton | SIL OFL 1.1 | [anton-OFL.txt](licenses/anton-OFL.txt) | [google/fonts `ofl/anton`](https://github.com/google/fonts/tree/main/ofl/anton) | `anton-400.woff2`, `anton-600.woff2`, `anton-700.woff2` |
| Archivo | SIL OFL 1.1 | [archivo-OFL.txt](licenses/archivo-OFL.txt) | [google/fonts `ofl/archivo`](https://github.com/google/fonts/tree/main/ofl/archivo) | `archivo-400.woff2`, `archivo-400i.woff2`, `archivo-600.woff2`, `archivo-700.woff2`, `archivo-800.woff2` |
| Baloo 2 | SIL OFL 1.1 | [baloo-2-OFL.txt](licenses/baloo-2-OFL.txt) | [google/fonts `ofl/baloo2`](https://github.com/google/fonts/tree/main/ofl/baloo2) | `baloo-2-400.woff2`, `baloo-2-600.woff2`, `baloo-2-700.woff2` |
| Barlow | SIL OFL 1.1 | [barlow-OFL.txt](licenses/barlow-OFL.txt) | [google/fonts `ofl/barlow`](https://github.com/google/fonts/tree/main/ofl/barlow) | `barlow-400.woff2`, `barlow-400i.woff2`, `barlow-700.woff2`, `barlow-800.woff2` |
| Barlow Condensed | SIL OFL 1.1 | [barlow-condensed-OFL.txt](licenses/barlow-condensed-OFL.txt) | [google/fonts `ofl/barlowcondensed`](https://github.com/google/fonts/tree/main/ofl/barlowcondensed) | `barlow-condensed-400.woff2`, `barlow-condensed-400i.woff2`, `barlow-condensed-600.woff2`, `barlow-condensed-700.woff2` |
| Big Shoulders Display | SIL OFL 1.1 | [big-shoulders-display-OFL.txt](licenses/big-shoulders-display-OFL.txt) | [google/fonts `ofl/bigshouldersdisplay`](https://github.com/google/fonts/tree/main/ofl/bigshouldersdisplay) | `big-shoulders-display-400.woff2`, `big-shoulders-display-600.woff2`, `big-shoulders-display-700.woff2` |
| Bodoni Moda | SIL OFL 1.1 | [bodoni-moda-OFL.txt](licenses/bodoni-moda-OFL.txt) | [google/fonts `ofl/bodonimoda`](https://github.com/google/fonts/tree/main/ofl/bodonimoda) | `bodoni-moda-400.woff2`, `bodoni-moda-400i.woff2`, `bodoni-moda-600.woff2`, `bodoni-moda-700.woff2` |
| Bricolage Grotesque | SIL OFL 1.1 | [bricolage-grotesque-OFL.txt](licenses/bricolage-grotesque-OFL.txt) | [google/fonts `ofl/bricolagegrotesque`](https://github.com/google/fonts/tree/main/ofl/bricolagegrotesque) | `bricolage-grotesque-400.woff2`, `bricolage-grotesque-600.woff2`, `bricolage-grotesque-700.woff2`, `bricolage-grotesque-800.woff2` |
| Cabin | SIL OFL 1.1 | [cabin-OFL.txt](licenses/cabin-OFL.txt) | [google/fonts `ofl/cabin`](https://github.com/google/fonts/tree/main/ofl/cabin) | `cabin-400.woff2`, `cabin-400i.woff2`, `cabin-700.woff2`, `cabin-800.woff2` |
| Caveat | SIL OFL 1.1 | [caveat-OFL.txt](licenses/caveat-OFL.txt) | [google/fonts `ofl/caveat`](https://github.com/google/fonts/tree/main/ofl/caveat) | `caveat-400.woff2` |
| Caveat Brush | SIL OFL 1.1 | [caveat-brush-OFL.txt](licenses/caveat-brush-OFL.txt) | [google/fonts `ofl/caveatbrush`](https://github.com/google/fonts/tree/main/ofl/caveatbrush) | `caveat-brush-400.woff2` |
| Chewy | Apache 2.0 | [chewy-Apache-2.0.txt](licenses/chewy-Apache-2.0.txt) | [google/fonts `apache/chewy`](https://github.com/google/fonts/tree/main/apache/chewy) | `chewy-400.woff2`, `chewy-600.woff2`, `chewy-700.woff2` |
| Cinzel | SIL OFL 1.1 | [cinzel-OFL.txt](licenses/cinzel-OFL.txt) | [google/fonts `ofl/cinzel`](https://github.com/google/fonts/tree/main/ofl/cinzel) | `cinzel-400.woff2`, `cinzel-600.woff2`, `cinzel-700.woff2` |
| Cormorant | SIL OFL 1.1 | [cormorant-OFL.txt](licenses/cormorant-OFL.txt) | [google/fonts `ofl/cormorant`](https://github.com/google/fonts/tree/main/ofl/cormorant) | `cormorant-400.woff2`, `cormorant-400i.woff2`, `cormorant-600.woff2`, `cormorant-700.woff2` |
| Cormorant Garamond | SIL OFL 1.1 | [cormorant-garamond-OFL.txt](licenses/cormorant-garamond-OFL.txt) | [google/fonts `ofl/cormorantgaramond`](https://github.com/google/fonts/tree/main/ofl/cormorantgaramond) | `cormorant-garamond-400.woff2`, `cormorant-garamond-400i.woff2`, `cormorant-garamond-600.woff2`, `cormorant-garamond-700.woff2` |
| Courgette | SIL OFL 1.1 | [courgette-OFL.txt](licenses/courgette-OFL.txt) | [google/fonts `ofl/courgette`](https://github.com/google/fonts/tree/main/ofl/courgette) | `courgette-400.woff2`, `courgette-600.woff2`, `courgette-700.woff2`, `courgette-800.woff2` |
| Covered By Your Grace | SIL OFL 1.1 | [covered-by-your-grace-OFL.txt](licenses/covered-by-your-grace-OFL.txt) | [google/fonts `ofl/coveredbyyourgrace`](https://github.com/google/fonts/tree/main/ofl/coveredbyyourgrace) | `covered-by-your-grace-400.woff2` |
| Crimson Pro | SIL OFL 1.1 | [crimson-pro-OFL.txt](licenses/crimson-pro-OFL.txt) | [google/fonts `ofl/crimsonpro`](https://github.com/google/fonts/tree/main/ofl/crimsonpro) | `crimson-pro-400.woff2`, `crimson-pro-400i.woff2`, `crimson-pro-600.woff2`, `crimson-pro-700.woff2` |
| DM Sans | SIL OFL 1.1 | [dm-sans-OFL.txt](licenses/dm-sans-OFL.txt) | [google/fonts `ofl/dmsans`](https://github.com/google/fonts/tree/main/ofl/dmsans) | `dm-sans-400.woff2`, `dm-sans-400i.woff2`, `dm-sans-700.woff2`, `dm-sans-800.woff2` |
| DM Serif Display | SIL OFL 1.1 | [dm-serif-display-OFL.txt](licenses/dm-serif-display-OFL.txt) | [google/fonts `ofl/dmserifdisplay`](https://github.com/google/fonts/tree/main/ofl/dmserifdisplay) | `dm-serif-display-400.woff2`, `dm-serif-display-400i.woff2`, `dm-serif-display-600.woff2`, `dm-serif-display-700.woff2` |
| Dancing Script | SIL OFL 1.1 | [dancing-script-OFL.txt](licenses/dancing-script-OFL.txt) | [google/fonts `ofl/dancingscript`](https://github.com/google/fonts/tree/main/ofl/dancingscript) | `dancing-script-400.woff2` |
| EB Garamond | SIL OFL 1.1 | [eb-garamond-OFL.txt](licenses/eb-garamond-OFL.txt) | [google/fonts `ofl/ebgaramond`](https://github.com/google/fonts/tree/main/ofl/ebgaramond) | `eb-garamond-400.woff2`, `eb-garamond-400i.woff2`, `eb-garamond-600.woff2`, `eb-garamond-700.woff2`, `eb-garamond-800.woff2` |
| Fredoka | SIL OFL 1.1 | [fredoka-OFL.txt](licenses/fredoka-OFL.txt) | [google/fonts `ofl/fredoka`](https://github.com/google/fonts/tree/main/ofl/fredoka) | `fredoka-400.woff2`, `fredoka-600.woff2`, `fredoka-700.woff2` |
| Gochi Hand | SIL OFL 1.1 | [gochi-hand-OFL.txt](licenses/gochi-hand-OFL.txt) | [google/fonts `ofl/gochihand`](https://github.com/google/fonts/tree/main/ofl/gochihand) | `gochi-hand-400.woff2` |
| Great Vibes | SIL OFL 1.1 | [great-vibes-OFL.txt](licenses/great-vibes-OFL.txt) | [google/fonts `ofl/greatvibes`](https://github.com/google/fonts/tree/main/ofl/greatvibes) | `great-vibes-400.woff2` |
| Homemade Apple | Apache 2.0 | [homemade-apple-Apache-2.0.txt](licenses/homemade-apple-Apache-2.0.txt) | [google/fonts `apache/homemadeapple`](https://github.com/google/fonts/tree/main/apache/homemadeapple) | `homemade-apple-400.woff2` |
| IBM Plex Sans | SIL OFL 1.1 | [ibm-plex-sans-OFL.txt](licenses/ibm-plex-sans-OFL.txt) | [google/fonts `ofl/ibmplexsans`](https://github.com/google/fonts/tree/main/ofl/ibmplexsans) | `ibm-plex-sans-400.woff2`, `ibm-plex-sans-400i.woff2`, `ibm-plex-sans-700.woff2`, `ibm-plex-sans-800.woff2` |
| IBM Plex Sans Condensed | SIL OFL 1.1 | [ibm-plex-sans-condensed-OFL.txt](licenses/ibm-plex-sans-condensed-OFL.txt) | [google/fonts `ofl/ibmplexsanscondensed`](https://github.com/google/fonts/tree/main/ofl/ibmplexsanscondensed) | `ibm-plex-sans-condensed-400.woff2`, `ibm-plex-sans-condensed-400i.woff2`, `ibm-plex-sans-condensed-600.woff2`, `ibm-plex-sans-condensed-700.woff2` |
| Indie Flower | SIL OFL 1.1 | [indie-flower-OFL.txt](licenses/indie-flower-OFL.txt) | [google/fonts `ofl/indieflower`](https://github.com/google/fonts/tree/main/ofl/indieflower) | `indie-flower-400.woff2` |
| Instrument Sans | SIL OFL 1.1 | [instrument-sans-OFL.txt](licenses/instrument-sans-OFL.txt) | [google/fonts `ofl/instrumentsans`](https://github.com/google/fonts/tree/main/ofl/instrumentsans) | `instrument-sans-400.woff2`, `instrument-sans-400i.woff2`, `instrument-sans-700.woff2`, `instrument-sans-800.woff2` |
| Instrument Serif | SIL OFL 1.1 | [instrument-serif-OFL.txt](licenses/instrument-serif-OFL.txt) | [google/fonts `ofl/instrumentserif`](https://github.com/google/fonts/tree/main/ofl/instrumentserif) | `instrument-serif-400.woff2`, `instrument-serif-400i.woff2`, `instrument-serif-600.woff2`, `instrument-serif-700.woff2` |
| Italiana | SIL OFL 1.1 | [italiana-OFL.txt](licenses/italiana-OFL.txt) | [google/fonts `ofl/italiana`](https://github.com/google/fonts/tree/main/ofl/italiana) | `italiana-400.woff2`, `italiana-600.woff2`, `italiana-700.woff2` |
| Josefin Sans | SIL OFL 1.1 | [josefin-sans-OFL.txt](licenses/josefin-sans-OFL.txt) | [google/fonts `ofl/josefinsans`](https://github.com/google/fonts/tree/main/ofl/josefinsans) | `josefin-sans-400.woff2`, `josefin-sans-400i.woff2`, `josefin-sans-600.woff2`, `josefin-sans-700.woff2`, `josefin-sans-800.woff2` |
| Jost | SIL OFL 1.1 | [jost-OFL.txt](licenses/jost-OFL.txt) | [google/fonts `ofl/jost`](https://github.com/google/fonts/tree/main/ofl/jost) | `jost-400.woff2`, `jost-400i.woff2`, `jost-600.woff2`, `jost-700.woff2`, `jost-800.woff2` |
| Kalam | SIL OFL 1.1 | [kalam-OFL.txt](licenses/kalam-OFL.txt) | [google/fonts `ofl/kalam`](https://github.com/google/fonts/tree/main/ofl/kalam) | `kalam-400.woff2` |
| Karla | SIL OFL 1.1 | [karla-OFL.txt](licenses/karla-OFL.txt) | [google/fonts `ofl/karla`](https://github.com/google/fonts/tree/main/ofl/karla) | `karla-400.woff2`, `karla-400i.woff2`, `karla-700.woff2`, `karla-800.woff2` |
| La Belle Aurore | SIL OFL 1.1 | [la-belle-aurore-OFL.txt](licenses/la-belle-aurore-OFL.txt) | [google/fonts `ofl/labelleaurore`](https://github.com/google/fonts/tree/main/ofl/labelleaurore) | `la-belle-aurore-400.woff2` |
| Lato | SIL OFL 1.1 | [lato-OFL.txt](licenses/lato-OFL.txt) | [google/fonts `ofl/lato`](https://github.com/google/fonts/tree/main/ofl/lato) | `lato-400.woff2`, `lato-400i.woff2`, `lato-700.woff2`, `lato-800.woff2` |
| Libre Baskerville | SIL OFL 1.1 | [libre-baskerville-OFL.txt](licenses/libre-baskerville-OFL.txt) | [google/fonts `ofl/librebaskerville`](https://github.com/google/fonts/tree/main/ofl/librebaskerville) | `libre-baskerville-400.woff2`, `libre-baskerville-400i.woff2`, `libre-baskerville-600.woff2`, `libre-baskerville-700.woff2` |
| Libre Franklin | SIL OFL 1.1 | [libre-franklin-OFL.txt](licenses/libre-franklin-OFL.txt) | [google/fonts `ofl/librefranklin`](https://github.com/google/fonts/tree/main/ofl/librefranklin) | `libre-franklin-400.woff2`, `libre-franklin-400i.woff2`, `libre-franklin-700.woff2`, `libre-franklin-800.woff2` |
| Lora | SIL OFL 1.1 | [lora-OFL.txt](licenses/lora-OFL.txt) | [google/fonts `ofl/lora`](https://github.com/google/fonts/tree/main/ofl/lora) | `lora-400.woff2`, `lora-400i.woff2`, `lora-600.woff2`, `lora-700.woff2` |
| Manrope | SIL OFL 1.1 | [manrope-OFL.txt](licenses/manrope-OFL.txt) | [google/fonts `ofl/manrope`](https://github.com/google/fonts/tree/main/ofl/manrope) | `manrope-400.woff2`, `manrope-600.woff2`, `manrope-700.woff2`, `manrope-800.woff2` |
| Montserrat | SIL OFL 1.1 | [montserrat-OFL.txt](licenses/montserrat-OFL.txt) | [google/fonts `ofl/montserrat`](https://github.com/google/fonts/tree/main/ofl/montserrat) | `montserrat-400.woff2`, `montserrat-400i.woff2`, `montserrat-600.woff2`, `montserrat-700.woff2` |
| Mrs Saint Delafield | SIL OFL 1.1 | [mrs-saint-delafield-OFL.txt](licenses/mrs-saint-delafield-OFL.txt) | [google/fonts `ofl/mrssaintdelafield`](https://github.com/google/fonts/tree/main/ofl/mrssaintdelafield) | `mrs-saint-delafield-400.woff2` |
| Mulish | SIL OFL 1.1 | [mulish-OFL.txt](licenses/mulish-OFL.txt) | [google/fonts `ofl/mulish`](https://github.com/google/fonts/tree/main/ofl/mulish) | `mulish-400.woff2`, `mulish-400i.woff2`, `mulish-700.woff2`, `mulish-800.woff2` |
| Nothing You Could Do | SIL OFL 1.1 | [nothing-you-could-do-OFL.txt](licenses/nothing-you-could-do-OFL.txt) | [google/fonts `ofl/nothingyoucoulddo`](https://github.com/google/fonts/tree/main/ofl/nothingyoucoulddo) | `nothing-you-could-do-400.woff2` |
| Nunito | SIL OFL 1.1 | [nunito-OFL.txt](licenses/nunito-OFL.txt) | [google/fonts `ofl/nunito`](https://github.com/google/fonts/tree/main/ofl/nunito) | `nunito-400.woff2`, `nunito-400i.woff2`, `nunito-700.woff2`, `nunito-800.woff2` |
| Nunito Sans | SIL OFL 1.1 | [nunito-sans-OFL.txt](licenses/nunito-sans-OFL.txt) | [google/fonts `ofl/nunitosans`](https://github.com/google/fonts/tree/main/ofl/nunitosans) | `nunito-sans-400.woff2`, `nunito-sans-400i.woff2`, `nunito-sans-700.woff2`, `nunito-sans-800.woff2` |
| Old Standard TT | SIL OFL 1.1 | [old-standard-tt-OFL.txt](licenses/old-standard-tt-OFL.txt) | [google/fonts `ofl/oldstandardtt`](https://github.com/google/fonts/tree/main/ofl/oldstandardtt) | `old-standard-tt-400.woff2`, `old-standard-tt-400i.woff2`, `old-standard-tt-700.woff2`, `old-standard-tt-800.woff2` |
| Open Sans | SIL OFL 1.1 | [open-sans-OFL.txt](licenses/open-sans-OFL.txt) | [google/fonts `ofl/opensans`](https://github.com/google/fonts/tree/main/ofl/opensans) | `open-sans-400.woff2`, `open-sans-400i.woff2`, `open-sans-600.woff2`, `open-sans-700.woff2`, `open-sans-800.woff2` |
| Oswald | SIL OFL 1.1 | [oswald-OFL.txt](licenses/oswald-OFL.txt) | [google/fonts `ofl/oswald`](https://github.com/google/fonts/tree/main/ofl/oswald) | `oswald-400.woff2`, `oswald-600.woff2`, `oswald-700.woff2` |
| Outfit | SIL OFL 1.1 | [outfit-OFL.txt](licenses/outfit-OFL.txt) | [google/fonts `ofl/outfit`](https://github.com/google/fonts/tree/main/ofl/outfit) | `outfit-400.woff2`, `outfit-600.woff2`, `outfit-700.woff2`, `outfit-800.woff2` |
| Oxygen | SIL OFL 1.1 | [oxygen-OFL.txt](licenses/oxygen-OFL.txt) | [google/fonts `ofl/oxygen`](https://github.com/google/fonts/tree/main/ofl/oxygen) | `oxygen-400.woff2`, `oxygen-600.woff2`, `oxygen-700.woff2`, `oxygen-800.woff2` |
| Pacifico | SIL OFL 1.1 | [pacifico-OFL.txt](licenses/pacifico-OFL.txt) | [google/fonts `ofl/pacifico`](https://github.com/google/fonts/tree/main/ofl/pacifico) | `pacifico-400.woff2` |
| Parisienne | SIL OFL 1.1 | [parisienne-OFL.txt](licenses/parisienne-OFL.txt) | [google/fonts `ofl/parisienne`](https://github.com/google/fonts/tree/main/ofl/parisienne) | `parisienne-400.woff2` |
| Permanent Marker | Apache 2.0 | [permanent-marker-Apache-2.0.txt](licenses/permanent-marker-Apache-2.0.txt) | [google/fonts `apache/permanentmarker`](https://github.com/google/fonts/tree/main/apache/permanentmarker) | `permanent-marker-400.woff2`, `permanent-marker-600.woff2`, `permanent-marker-700.woff2` |
| Pinyon Script | SIL OFL 1.1 | [pinyon-script-OFL.txt](licenses/pinyon-script-OFL.txt) | [google/fonts `ofl/pinyonscript`](https://github.com/google/fonts/tree/main/ofl/pinyonscript) | `pinyon-script-400.woff2` |
| Playfair Display | SIL OFL 1.1 | [playfair-display-OFL.txt](licenses/playfair-display-OFL.txt) | [google/fonts `ofl/playfairdisplay`](https://github.com/google/fonts/tree/main/ofl/playfairdisplay) | `playfair-display-400.woff2`, `playfair-display-400i.woff2`, `playfair-display-600.woff2`, `playfair-display-700.woff2` |
| Public Sans | SIL OFL 1.1 | [public-sans-OFL.txt](licenses/public-sans-OFL.txt) | [google/fonts `ofl/publicsans`](https://github.com/google/fonts/tree/main/ofl/publicsans) | `public-sans-400.woff2`, `public-sans-400i.woff2`, `public-sans-700.woff2`, `public-sans-800.woff2` |
| Quicksand | SIL OFL 1.1 | [quicksand-OFL.txt](licenses/quicksand-OFL.txt) | [google/fonts `ofl/quicksand`](https://github.com/google/fonts/tree/main/ofl/quicksand) | `quicksand-400.woff2`, `quicksand-600.woff2`, `quicksand-700.woff2`, `quicksand-800.woff2` |
| Reenie Beanie | SIL OFL 1.1 | [reenie-beanie-OFL.txt](licenses/reenie-beanie-OFL.txt) | [google/fonts `ofl/reeniebeanie`](https://github.com/google/fonts/tree/main/ofl/reeniebeanie) | `reenie-beanie-400.woff2` |
| Rock Salt | Apache 2.0 | [rock-salt-Apache-2.0.txt](licenses/rock-salt-Apache-2.0.txt) | [google/fonts `apache/rocksalt`](https://github.com/google/fonts/tree/main/apache/rocksalt) | `rock-salt-400.woff2` |
| Rubik | SIL OFL 1.1 | [rubik-OFL.txt](licenses/rubik-OFL.txt) | [google/fonts `ofl/rubik`](https://github.com/google/fonts/tree/main/ofl/rubik) | `rubik-400.woff2`, `rubik-400i.woff2`, `rubik-600.woff2`, `rubik-700.woff2`, `rubik-800.woff2` |
| Sacramento | SIL OFL 1.1 | [sacramento-OFL.txt](licenses/sacramento-OFL.txt) | [google/fonts `ofl/sacramento`](https://github.com/google/fonts/tree/main/ofl/sacramento) | `sacramento-400.woff2` |
| Satisfy | Apache 2.0 | [satisfy-Apache-2.0.txt](licenses/satisfy-Apache-2.0.txt) | [google/fonts `apache/satisfy`](https://github.com/google/fonts/tree/main/apache/satisfy) | `satisfy-400.woff2` |
| Shadows Into Light | SIL OFL 1.1 | [shadows-into-light-OFL.txt](licenses/shadows-into-light-OFL.txt) | [google/fonts `ofl/shadowsintolight`](https://github.com/google/fonts/tree/main/ofl/shadowsintolight) | `shadows-into-light-400.woff2` |
| Shrikhand | SIL OFL 1.1 | [shrikhand-OFL.txt](licenses/shrikhand-OFL.txt) | [google/fonts `ofl/shrikhand`](https://github.com/google/fonts/tree/main/ofl/shrikhand) | `shrikhand-400.woff2`, `shrikhand-600.woff2`, `shrikhand-700.woff2` |
| Source Sans 3 | SIL OFL 1.1 | [source-sans-3-OFL.txt](licenses/source-sans-3-OFL.txt) | [google/fonts `ofl/sourcesans3`](https://github.com/google/fonts/tree/main/ofl/sourcesans3) | `source-sans-3-400.woff2`, `source-sans-3-400i.woff2`, `source-sans-3-700.woff2`, `source-sans-3-800.woff2` |
| Space Grotesk | SIL OFL 1.1 | [space-grotesk-OFL.txt](licenses/space-grotesk-OFL.txt) | [google/fonts `ofl/spacegrotesk`](https://github.com/google/fonts/tree/main/ofl/spacegrotesk) | `space-grotesk-400.woff2`, `space-grotesk-600.woff2`, `space-grotesk-700.woff2`, `space-grotesk-800.woff2` |
| Space Mono | SIL OFL 1.1 | [space-mono-OFL.txt](licenses/space-mono-OFL.txt) | [google/fonts `ofl/spacemono`](https://github.com/google/fonts/tree/main/ofl/spacemono) | `space-mono-400.woff2`, `space-mono-400i.woff2`, `space-mono-700.woff2`, `space-mono-800.woff2` |
| Tenor Sans | SIL OFL 1.1 | [tenor-sans-OFL.txt](licenses/tenor-sans-OFL.txt) | [google/fonts `ofl/tenorsans`](https://github.com/google/fonts/tree/main/ofl/tenorsans) | `tenor-sans-400.woff2`, `tenor-sans-600.woff2`, `tenor-sans-700.woff2` |
| UnifrakturMaguntia | SIL OFL 1.1 | [unifrakturmaguntia-OFL.txt](licenses/unifrakturmaguntia-OFL.txt) | [google/fonts `ofl/unifrakturmaguntia`](https://github.com/google/fonts/tree/main/ofl/unifrakturmaguntia) | `unifrakturmaguntia-400.woff2` |
| Work Sans | SIL OFL 1.1 | [work-sans-OFL.txt](licenses/work-sans-OFL.txt) | [google/fonts `ofl/worksans`](https://github.com/google/fonts/tree/main/ofl/worksans) | `work-sans-400.woff2`, `work-sans-400i.woff2`, `work-sans-700.woff2`, `work-sans-800.woff2` |
| Yellowtail | Apache 2.0 | [yellowtail-Apache-2.0.txt](licenses/yellowtail-Apache-2.0.txt) | [google/fonts `apache/yellowtail`](https://github.com/google/fonts/tree/main/apache/yellowtail) | `yellowtail-400.woff2` |
| Yeseva One | SIL OFL 1.1 | [yeseva-one-OFL.txt](licenses/yeseva-one-OFL.txt) | [google/fonts `ofl/yesevaone`](https://github.com/google/fonts/tree/main/ofl/yesevaone) | `yeseva-one-400.woff2`, `yeseva-one-600.woff2`, `yeseva-one-700.woff2` |
| Young Serif | SIL OFL 1.1 | [young-serif-OFL.txt](licenses/young-serif-OFL.txt) | [google/fonts `ofl/youngserif`](https://github.com/google/fonts/tree/main/ofl/youngserif) | `young-serif-400.woff2`, `young-serif-600.woff2`, `young-serif-700.woff2` |
| Zilla Slab | SIL OFL 1.1 | [zilla-slab-OFL.txt](licenses/zilla-slab-OFL.txt) | [google/fonts `ofl/zillaslab`](https://github.com/google/fonts/tree/main/ofl/zillaslab) | `zilla-slab-400.woff2`, `zilla-slab-400i.woff2`, `zilla-slab-600.woff2`, `zilla-slab-700.woff2`, `zilla-slab-800.woff2` |

## Apache 2.0 copyright holders

- Chewy: Copyright (c) 2010 by Font Diner, Inc DBA Sideshow. All rights reserved.
- Homemade Apple: Copyright (c) 2010 by Font Diner, Inc. All rights reserved.
- Permanent Marker: Copyright (c) 2010 by Font Diner, Inc. All rights reserved.
- Rock Salt: Copyright (c) 2010 by Font Diner, Inc DBA Sideshow. All rights reserved.
- Satisfy: Copyright (c) 2011 by Font Diner, Inc. All rights reserved.
- Yellowtail: Copyright (c) 2011 by Brian J. Bonislawsky DBA Astigmatic (AOETI). All rights reserved.
