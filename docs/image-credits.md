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

98 images, imported with `scripts/import_local_artwork.py` from the local
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
| `b1/a-day-in-the-house` | `01.jpg` | A Sleeping Dog | `gerrit-dou-a-sleeping-dog.jpeg` |
| `b1/a-day-in-the-office` | `01.jpg` | Presentation of the Pandects to the Emperor Justinian | `hermann-knackfuss-presentation-of-the-pandects-to-the-emperor-justinian.jpeg` |
| `b1/a-freelance-accounting-assignment` | `01.jpg` | The Cartographers' Circle | `fritz-wagner-the-cartographers-circle.jpeg` |
| `b1/animal-solutions` | `01.jpg` | Cattle and Sheep on Canterbury Meadows | `thomas-sidney-cooper-cattle-and-sheep-on-canterbury-meadows-1803-1902.jpg` |
| `b1/animal-solutions` | `02.jpg` | Shepherd with Cows | `rudolf-koller-shepherd-with-cows-1828-1905.jpeg` |
| `b1/arriving-in-johannesburg` | `01.jpg` | Cape Mountain Landscape | `gabriel-cornelis-de-jongh-cape-mountain-landscape.jpeg` |
| `b1/arriving-in-johannesburg` | `02.jpg` | View Through an Archway | `bartholomeus-johannes-van-hove-view-through-an-archway-1790-1880.jpeg` |
| `b1/beers` | `01.jpg` | In the Monastery Cellar | `eduard-von-grutzner-in-the-monastery-cellar-1878.jpeg` |
| `b1/cachacas` | `01.jpg` | Bringing in the Grapes | `williams-penry-bringing-in-the-grapes.jpg` |
| `b1/cachacas` | `02.jpg` | Interior of a Hammersmith | `hugo-charlemont-interior-of-a-hammersmith-1883.jpg` |
| `b1/cars` | `01.jpg` | The Horse Fair | `rosa-bonheur-the-horse-fair-c-1855.jpeg` |
| `b1/cars` | `02.jpg` | The Montgolfier brothers' balloon | `claude-louis-desrais-montgolfier-brothers-hot-air-balloon.jpg` |
| `b1/climbing` | `01.jpg` | Glacier Plateau | `edward-theodore-compton-glacier-plateau-1906.jpg` |
| `b1/climbing` | `02.jpg` | Grindelwald Glacier in the Alps | `joseph-anton-koch-grindelwald-glacier-in-the-alps-1823.jpeg` |
| `b1/common-chores` | `01.jpg` | Moscow Courtyard | `vasily-polenov-moscow-courtyard-1878.jpeg` |
| `b1/cybersecurity` | `01.jpg` | The Siege: Defense of a Church Courtyard During the Thirty Years' War | `karl-friedrich-lessing-the-siege-defense-of-a-church-courtyard-during-the-thirty-years-war-1848.jpeg` |
| `b1/cybersecurity` | `02.jpg` | Knight's Castle | `karl-friedrich-lessing-knights-castle.jpeg` |
| `b1/detective-story` | `01.jpg` | Moonlight Landscape | `joseph-wright-of-derby-moonlight-landscape.jpg` |
| `b1/do-make-livestock-farming` | `01.jpg` | In the Farm | `julien-dupre-1851-1910-french-naturalist-painter-in-the-farm.jpeg` |
| `b1/do-make-livestock-farming` | `02.jpg` | The Gleaners | `jean-francois-millet-the-gleaners-1857.jpeg` |
| `b1/glamping` | `01.jpg` | Camping for the Night on Mansfield Mountain | `sanford-robinson-gifford-camping-for-the-night-on-mansfield-mountain.jpeg` |
| `b1/golden-gate-bridge-present-perfect` | `01.jpg` | The Opening of Tower Bridge | `wyllie-william-lionel-the-opening-of-tower-bridge.jpg` |
| `b1/golden-gate-bridge-present-perfect` | `02.jpg` | Landseer modelling one of the lions for Nelson's Column | `john-ballantyne-1815-1897-scottish-portrait-and-history-painter-edwin-henry-landseer-1802-1873-english-painter-and-sculptor-modelling-one-of-the-lions-for-the-base-of-nelsons-column-in-trafalgar-square.jpeg` |
| `b1/hachiko` | `01.jpg` | The Spiral Hall at the Temple of Five Hundred Arhats | `kitao-shigemas-the-spiral-hall-at-the-temple-of-five-hundred-arhats-in-honjo-fifth-ward.jpeg` |
| `b1/hachiko` | `02.jpg` | The Faithful Servant | `john-sargent-noble-the-faithful-servant.jpeg` |
| `b1/investigation-story` | `01.jpg` | A Game of Piquet | `ernest-meissonier-a-game-of-piquet-1861.jpeg` |
| `b1/investigation-story` | `02.jpg` | A Moonlit Night | `august-piepenhagen-a-moonlit-night.jpg` |
| `b1/investigation-story` | `03.jpg` | Lost Honour | `eduard-schulz-briesen-lost-honour.jpeg` |
| `b1/kitchen-chaos` | `01.jpg` | The Dinner at the Ball | `adolph-von-menzel-the-dinner-at-the-ball-1878.jpg` |
| `b1/milan-restaurants` | `01.jpg` | Oregon Trail Campfire | `albert-bierstadt-oregon-trail-campfire-1863.jpeg` |
| `b1/milan-restaurants` | `02.jpg` | Fishermen | `hans-gude-adolph-tidemand-fishermen-1851.jpeg` |
| `b1/my-day-in-vienna-to-by-for` | `01.jpg` | St Stephen's Cathedral in Vienna | `rudolf-von-alt-st-stephens-cathedral-in-vienna-1832.jpg` |
| `b1/my-day-in-vienna-to-by-for` | `02.jpg` | The Roman Ruins at Schönbrunn | `ferdinand-georg-waldmuller-the-roman-ruins-at-schonbrunn-1832.jpeg` |
| `b1/my-life-and-plans` | `01.jpg` | Distracted from His Studies | `jules-girardet-1856-1938-distracted-from-his-studies.jpeg` |
| `b1/nfl` | `01.jpg` | Pindar Exalts a Victor in the Olympic Games | `giuseppe-sciuti-pindar-exalts-a-victor-in-the-olympic-games.jpeg` |
| `b1/ny-visitation` | `01.jpg` | Park Landscape with a Fountain | `edvard-petersen-park-landscape-with-a-fountain.jpeg` |
| `b1/ny-visitation` | `02.jpg` | The Victoria Embankment from Hungerford Bridge | `george-hyde-pownall-the-victoria-embankment-from-hungerford-bridge-1876-1932.jpeg` |
| `b1/physical-education` | `01.jpg` | The Nursery | `albert-anker-the-nursery-1890.jpeg` |
| `b1/physical-education` | `02.jpg` | Children in a Punt, Fishing an Old Shoe | `marie-wunsch-1862-1898-children-in-a-punt-fishing-an-old-shoe.jpeg` |
| `b1/rio-de-janeiro-exercises` | `01.jpg` | The Heart of the Andes | `frederic-edwin-church-the-heart-of-the-andes.jpg` |
| `b1/rio-de-janeiro-exercises` | `02.jpg` | Tropical Landscape with a Hanging Bridge | `frederic-edwin-church-tropical-landscape-with-a-hanging-bridge.jpg` |
| `b1/santa-catarina` | `01.jpg` | Storm at Sea off the Norwegian Coast | `andreas-achenbach-storm-at-sea-off-the-norwegian-coast-1815-1910.jpeg` |
| `b1/santa-catarina` | `02.jpg` | Retreating Storm on the Italian Coast | `oswald-achenbach-retreating-storm-on-the-italian-coast.jpeg` |
| `b1/say-speak-talk-tell-02` | `01.jpg` | Market Square, Seville | `richard-ansdell-market-square-seville-1860.jpeg` |
| `b1/snowy-days` | `01.jpg` | First Snow | `ivan-shishkin-first-snow.jpeg` |
| `b1/snowy-days` | `02.jpg` | Winter Landscape | `caspar-david-friedrich-winter-landscape.jpg` |
| `b1/southeast-asia-adventure` | `01.jpg` | The Main Temple of Tassiding Monastery, Sikkim | `vasily-vereshchagin-the-main-temple-of-tassiding-monastery-sikkim-1875.jpg` |
| `b1/southeast-asia-adventure` | `02.jpg` | Evening on a Lake | `vasily-vereshchagin-evening-on-a-lake-a-pavilion-on-the-marble-embankment-in-rajnagar-udaipur-principality-1874.jpg` |
| `b1/state-fair-food` | `01.jpg` | Village Fair by Night | `hendrik-gerrit-ten-cate-village-fair-by-night-1803-1856.jpeg` |
| `b1/state-fair-food` | `02.jpg` | Fair in the Oude Beurs, Antwerp | `pierre-jean-van-der-ouderaa-fair-in-the-oude-beurs-in-antwerp-1892.jpeg` |
| `b1/travel-dialogues-02` | `01.jpg` | A Scene of Everyday Life at the Nuremberg Town Hall | `heinrich-hansen-a-scene-of-everyday-life-at-the-nuremberg-town-hall.jpeg` |
| `b1/usa-restaurants` | `01.jpg` | Muddy Alligators | `john-singer-sargent-muddy-alligators.jpeg` |
| `b1/usa-restaurants` | `02.jpg` | Jamaica | `frederic-edwin-church-jamaica-1871.jpeg` |

<!-- gallery:end -->
