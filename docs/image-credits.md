# Image credits

Every image used on a reading page, with its source and rights. Nothing goes on
the site unless it is public domain or was already in the source document and is
clearly free to use.

`scripts/fetch_public_domain_image.py` is what fetches the Wikimedia Commons ones.
It reads the licence metadata from the Commons API and **refuses to download
anything that is not public domain** — a CC BY or CC BY-SA file is rejected, not
downloaded with attribution, because it is simpler to keep the whole library
rights-free than to track conditions per file. Two candidates were refused this
way while assembling this list: a photograph of a statue of Hatshepsut (CC BY-SA
3.0) and the Wellcome Collection's scan of the same Karnak lithograph (CC BY 4.0).

## From Wikimedia Commons (public domain)

| Page | Image | Artist | Date |
|---|---|---|---|
| `b1/maringa` | Chicago in Flames | Currier & Ives | 1871 |
| `b2/egypt` | Hall of columns at Karnak | David Roberts, lith. Louis Haghe | 1846 |
| `b2/john-snow` | Map of cholera deaths in Soho | John Snow | 1854 |
| `b2/soma-nomaoi` | Samurai leading a horse | Utagawa Kuniyoshi | first half of the 19th c. |
| `c1/america-in-1776` | Declaration of Independence | John Trumbull | 1819 |
| `c1/rs-japan` | Fine Wind, Clear Morning | Katsushika Hokusai | c. 1830 |
| `c1/trials` | Les Gens de Justice, plate 1 | Honoré Daumier | 1845–48 |

The Karnak plate is cropped out of a Library of Congress scan — the original file
includes the colour calibration bars and the card mount, which are not part of the
lithograph.

## Carried over from the source documents

| Page | Image | Note |
|---|---|---|
| `b1/christmas-krampus-grinch` | St Nicholas fresco; a Krampuskarte | Both old enough to be free of rights |
| `b1/robot-birds` | Peregrine falcon plate | 19th-century ornithological illustration |
| `b2/aesop` (3 pages share the set) | Doré, Crane, Bewick, Winter | All public domain |
| `b2/john-snow` | "Monster Soup", William Heath | 1828 caricature of Thames water |

## Deliberately not used

The source documents hold about 50 images in all. Most are modern stock
photographs — Karnak, the Romanian Carpathians, the Golden Gate at dusk — which
are both the wrong register for these pages and of uncertain licence, so they
were left out and replaced with period artwork where an image was wanted.

Four were excluded for specific reasons:

- A 1966 Grinch television still, and a Bugs Bunny frame — both in copyright.
- A photograph of the Hachiko statue carrying a third party's watermark.
- A pen-and-ink portrait that is a recognisable likeness of a living-memory
  actor, offered as a fictional character in a detective exercise.
