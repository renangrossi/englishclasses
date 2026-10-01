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

## From the local art gallery

<!-- gallery:start -->

45 images, imported with `scripts/import_local_artwork.py` from the local
gallery of painting and print scans. Each one is a work old enough to be free of
rights; the gallery also holds living and recent artists, and none of that is used.

| Page | File | Work | Gallery source |
|---|---|---|---|
| `a1/at-the-store` | `01.jpg` | Venetian Fruit Sellers | `stefano-novo-venetian-fruit-sellers-1898.jpeg` |
| `a1/going-to-the-airport` | `01.jpg` | London Bridge, Half Tide | `john-atkinson-grimshaw-london-bridge-half-tide.jpeg` |
| `a1/greetings-and-names` | `01.jpg` | The Fan Shop | `utagawa-toyokuni-the-fan-shop-ca-1800.jpeg` |
| `a1/i-dont-feel-good` | `01.jpg` | The Quack | `albert-anker-the-quack-1897.jpeg` |
| `a1/jack-works-from-home` | `01.jpg` | Sir Lawrence Alma-Tadema's Library in Townshend House, London | `anna-alma-tadema-sir-lawrence-alma-tademas-library-in-townshend-house-london-1884.jpeg` |
| `a1/making-dinner` | `01.jpg` | Baking Bread | `anders-leonard-zorn-horneando-pan-1860-1920.jpeg` |
| `a1/my-day` | `01.jpg` | The Happy Family | `eugenio-eduardo-zampighi-the-happy-family-1859-1944.jpeg` |
| `a1/my-family` | `01.jpg` | Le gioie di casa* (The Joys of Home) | `pietro-saltini-le-gioie-di-casa.jpeg` |
| `a1/my-job` | `01.jpg` | Inside a Bakery | `gustaf-olof-cederstrom-inside-a-bakery-1845-1933.jpeg` |
| `a1/my-room` | `01.jpg` | Winter Garden | `eduard-hau-winter-garden.jpeg` |
| `a1/numbers-and-time` | `01.jpg` | Piazza San Marco in Venice by Moonlight | `ippolito-caffi-piazza-san-marco-in-venice-by-moonlight.jpg` |
| `a1/ordering-food` | `01.jpg` | Refreshments at a Wayside Inn | `cesare-augusto-detti-refreshments-at-a-wayside-inn.jpeg` |
| `a1/rain-and-snow` | `01.jpg` | A Woman Under an Umbrella on a Flowering Meadow | `ivan-shishkin-a-woman-under-an-umbrella-on-a-flowering-meadow-1881.jpg` |
| `a1/rain-and-snow` | `02.jpg` | Falling Leaves | `olga-wisinger-florian-falling-leaves-1899.jpeg` |
| `a1/saturday-morning` | `01.jpg` | A Spring Day in Sæby Forest | `peder-mork-monsted-a-spring-day-in-saeby-forest-a-glimmer-of-sunlight-through-trees-1916.jpg` |
| `a1/taking-the-train` | `01.jpg` | Steamboat Pier in Nærøyfjorden | `anders-askevold-steamboat-pier-in-naeroyfjorden-1894.jpg` |
| `a2/a-weekend-at-the-lake` | `01.jpg` | The Picnic | `emile-claus-el-picnic-1887.jpeg` |
| `a2/at-the-hotel` | `01.jpg` | A Game of L'hombre in Brøndum's Hotel | `anna-palm-de-rosa-a-game-of-lhombre-in-brondums-hotel-1885.jpg` |
| `a2/at-the-hotel` | `02.jpg` | Outside the Fish Inn | `frank-moss-bennett-outside-the-fish-inn.jpeg` |
| `a2/bus-to-the-mountains` | `01.jpg` | Drovers on a Bridge in an Alpine Landscape | `carl-schweich-drovers-on-a-bridge-in-an-alpine-landscape-1854.jpeg` |
| `a2/bus-to-the-mountains` | `02.jpg` | Mountain Landscape with River | `zankovsky-ilya-nikolaevich-mountain-landscape-with-river-3.jpg` |
| `a2/coffee-brewing` | `01.jpg` | Le Verre de Vin | `leon-augustin-lhermitte-le-verre-de-vin.jpeg` |
| `a2/dream-bistro` | `01.jpg` | A Market Scene in Naples | `vincenzo-caprile-a-market-scene-in-naples.jpeg` |
| `a2/everyday-service-english` | `01.jpg` | The Principal Market in Münster | `cornelis-springer-1840-1891-the-principal-market-in-munster.jpeg` |
| `a2/everyday-service-english` | `02.jpg` | Photographed at the Acropolis | `genthe-arnold-kanellos-dance-group-performing-at-acropolis-photographed-1929.jpeg` |
| `a2/finding-an-apartment` | `01.jpg` | Houses on the Herengracht, Amsterdam | `jan-van-der-heyden-amsterdam-city-view-with-houses-on-the-herengracht-and-the-old-haarlemmersluis-ca-1670.jpeg` |
| `a2/flying-to-the-us` | `01.jpg` | A Ship Receiving a Pilot | `wyllie-william-lionel-a-ship-recieving-a-pilot-through-busy-thames-waters.jpg` |
| `a2/flying-to-the-us` | `02.jpg` | Auf hoher See* (On the High Seas) | `michael-zeno-diemer-auf-hoher-see-ca-1902.jpg` |
| `a2/flying-to-the-us` | `03.jpg` | Sentinel at the Entrance to the Temple Mount, Jerusalem | `gustav-bauernfeind-1848-1904-german-painter-illustrator-and-architect-sentinel-at-the-entrance-to-the-temple-mount-jerusalem.jpeg` |
| `a2/grocery-shopping` | `01.jpg` | Still Life: Three Salmon Steaks | `francisco-goya-still-life-three-salmon-steaks-painted-1746-1828.jpeg` |
| `a2/hiking-in-the-mountains` | `01.jpg` | The Mountain Pass | `sidney-richard-percy-the-mountain-pass.jpg` |
| `a2/hiking-in-the-mountains` | `02.jpg` | Landscape at the Lake of Lucerne | `robert-zund-landscape-at-lake-of-lucerne-1827-1909.jpg` |
| `a2/restaurant-dialogue` | `01.jpg` | At the Inn | `alexandre-louis-leloir-at-the-inn-1868.jpeg` |
| `a2/saying-and-telling` | `01.jpg` | New Acquaintance | `karl-lemoch-new-acquaintance.jpg` |
| `a2/something-wrong-with-the-order` | `01.jpg` | It's Touch and Go to Laugh or No | `sophie-gengembre-anderson-its-touch-and-go-to-laugh-or-no-1857.jpeg` |
| `a2/st-patricks-day` | `01.jpg` | Procession to St Paul's Cathedral | `nicholas-chevalier-procession-to-st-pauls-cathedral-1872.jpeg` |
| `a2/st-patricks-day` | `02.jpg` | Riders of the Sidhe | `john-duncan-riders-of-the-sidhe-1911.jpg` |
| `a2/thanksgiving` | `01.jpg` | Harvest | `vladimir-orlovsky-harvest-in-the-ukraine-1880.jpeg` |
| `a2/thanksgiving` | `02.jpg` | The Roast Beef of Old England | `frank-moss-bennett-the-roast-beef-of-old-england.jpeg` |
| `a2/the-day-at-the-market` | `01.jpg` | The Nieuwezijds Voorburgwal with the Flower Market, Amsterdam | `gerrit-berckheyde-the-nieuwezijds-voorburgswal-with-the-flower-market-amsterdam-1686.jpg` |
| `a2/the-day-at-the-market` | `02.jpg` | A Good Roast | `eduard-von-grutzner-a-good-roast-1889.jpeg` |
| `a2/two-small-errands` | `01.jpg` | On the Terrace | `paul-fischer-on-the-terrace-1912.jpeg` |
| `a2/two-small-errands` | `02.jpg` | A Town Scene with a Farrier | `jacques-carabain-a-town-scene-with-a-farrier.jpeg` |
| `a2/two-very-different-trips` | `01.jpg` | People on a Beach | `amaldus-nielsen-people-on-a-beach-1894.jpg` |
| `a2/two-very-different-trips` | `02.jpg` | Buddhist Temple in Darjeeling, Sikkim | `vasily-vereshchagin-buddhist-temple-in-darjiling-sikkim-1874.jpg` |

<!-- gallery:end -->
