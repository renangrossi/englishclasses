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

107 images, imported with `scripts/import_local_artwork.py` from the local
gallery of painting and print scans. Each one is a work old enough to be free of
rights; the gallery also holds living and recent artists, and none of that is used.

| Page | File | Work | Gallery source |
|---|---|---|---|
| `a1/at-the-store` | `01.jpg` | Venetian Fruit Sellers | `stefano-novo-venetian-fruit-sellers-1898.jpeg` |
| `a1/george-washington` | `01.jpg` | Washington Crossing the Delaware | `emanuel-leutze-washington-crossing-the-delaware.jpg` |
| `a1/i-dont-feel-good` | `01.jpg` | The Quack | `albert-anker-the-quack-1897.jpeg` |
| `a1/jack-works-from-home` | `01.jpg` | Sir Lawrence Alma-Tadema's Library in Townshend House, London | `anna-alma-tadema-sir-lawrence-alma-tademas-library-in-townshend-house-london-1884.jpeg` |
| `a1/making-dinner` | `01.jpg` | Baking Bread | `anders-leonard-zorn-horneando-pan-1860-1920.jpeg` |
| `a1/my-day` | `01.jpg` | The Happy Family | `eugenio-eduardo-zampighi-the-happy-family-1859-1944.jpeg` |
| `a1/my-family` | `01.jpg` | Le gioie di casa* (The Joys of Home) | `pietro-saltini-le-gioie-di-casa.jpeg` |
| `a1/my-job` | `01.jpg` | Inside a Bakery | `gustaf-olof-cederstrom-inside-a-bakery-1845-1933.jpeg` |
| `a1/numbers-and-time` | `01.jpg` | Piazza San Marco in Venice by Moonlight | `ippolito-caffi-piazza-san-marco-in-venice-by-moonlight.jpg` |
| `a1/ordering-food` | `01.jpg` | Refreshments at a Wayside Inn | `cesare-augusto-detti-refreshments-at-a-wayside-inn.jpeg` |
| `a1/rain-and-snow` | `01.jpg` | A Woman Under an Umbrella on a Flowering Meadow | `ivan-shishkin-a-woman-under-an-umbrella-on-a-flowering-meadow-1881.jpg` |
| `a1/rain-and-snow` | `02.jpg` | Falling Leaves | `olga-wisinger-florian-falling-leaves-1899.jpeg` |
| `a1/saturday-morning` | `01.jpg` | A Spring Day in Sæby Forest | `peder-mork-monsted-a-spring-day-in-saeby-forest-a-glimmer-of-sunlight-through-trees-1916.jpg` |
| `a2/a-weekend-at-the-lake` | `01.jpg` | The Picnic | `emile-claus-el-picnic-1887.jpeg` |
| `a2/at-the-hotel` | `01.jpg` | A Game of L'hombre in Brøndum's Hotel | `anna-palm-de-rosa-a-game-of-lhombre-in-brondums-hotel-1885.jpg` |
| `a2/at-the-hotel` | `02.jpg` | Outside the Fish Inn | `frank-moss-bennett-outside-the-fish-inn.jpeg` |
| `a2/bus-to-the-mountains` | `01.jpg` | Drovers on a Bridge in an Alpine Landscape | `carl-schweich-drovers-on-a-bridge-in-an-alpine-landscape-1854.jpeg` |
| `a2/bus-to-the-mountains` | `02.jpg` | Mountain Landscape with River | `zankovsky-ilya-nikolaevich-mountain-landscape-with-river-3.jpg` |
| `a2/declaration-of-independence` | `01.jpg` | Declaration of Independence | `john-trumbull-declaration-of-independence-1819.jpeg` |
| `a2/dream-bistro` | `01.jpg` | A Market Scene in Naples | `vincenzo-caprile-a-market-scene-in-naples.jpeg` |
| `a2/everyday-service-english` | `01.jpg` | The Principal Market in Münster | `cornelis-springer-1840-1891-the-principal-market-in-munster.jpeg` |
| `a2/finding-an-apartment` | `01.jpg` | Houses on the Herengracht, Amsterdam | `jan-van-der-heyden-amsterdam-city-view-with-houses-on-the-herengracht-and-the-old-haarlemmersluis-ca-1670.jpeg` |
| `a2/grocery-shopping` | `01.jpg` | Still Life: Three Salmon Steaks | `francisco-goya-still-life-three-salmon-steaks-painted-1746-1828.jpeg` |
| `a2/hiking-in-the-mountains` | `01.jpg` | The Mountain Pass | `sidney-richard-percy-the-mountain-pass.jpg` |
| `a2/hiking-in-the-mountains` | `02.jpg` | Landscape at the Lake of Lucerne | `robert-zund-landscape-at-lake-of-lucerne-1827-1909.jpg` |
| `a2/lewis-and-clark-west` | `01.jpg` | When the Land Belonged to God | `charles-marion-russell-when-the-land-belonged-to-god-1914.jpeg` |
| `a2/lewis-and-clark-west` | `02.jpg` | The Rocky Mountains, Lander's Peak | `albert-bierstadt-the-rocky-mountains-landers-peak.jpg` |
| `a2/oregon-trail` | `01.jpg` | Evening on the Prairie | `albert-bierstadt-evening-on-the-prairie-1870.jpeg` |
| `a2/restaurant-dialogue` | `01.jpg` | At the Inn | `alexandre-louis-leloir-at-the-inn-1868.jpeg` |
| `a2/st-patricks-day` | `01.jpg` | Procession to St Paul's Cathedral | `nicholas-chevalier-procession-to-st-pauls-cathedral-1872.jpeg` |
| `a2/st-patricks-day` | `02.jpg` | Riders of the Sidhe | `john-duncan-riders-of-the-sidhe-1911.jpg` |
| `a2/thanksgiving` | `01.jpg` | Harvest | `vladimir-orlovsky-harvest-in-the-ukraine-1880.jpeg` |
| `a2/thanksgiving` | `02.jpg` | The Roast Beef of Old England | `frank-moss-bennett-the-roast-beef-of-old-england.jpeg` |
| `a2/the-day-at-the-market` | `02.jpg` | A Good Roast | `eduard-von-grutzner-a-good-roast-1889.jpeg` |
| `a2/two-small-errands` | `02.jpg` | A Town Scene with a Farrier | `jacques-carabain-a-town-scene-with-a-farrier.jpeg` |
| `a2/two-very-different-trips` | `01.jpg` | People on a Beach | `amaldus-nielsen-people-on-a-beach-1894.jpg` |
| `a2/two-very-different-trips` | `02.jpg` | Buddhist Temple in Darjeeling, Sikkim | `vasily-vereshchagin-buddhist-temple-in-darjiling-sikkim-1874.jpg` |
| `b1/a-day-in-the-house` | `01.jpg` | A Sleeping Dog | `gerrit-dou-a-sleeping-dog.jpeg` |
| `b1/a-freelance-accounting-assignment` | `01.jpg` | The Cartographers' Circle | `fritz-wagner-the-cartographers-circle.jpeg` |
| `b1/animal-solutions` | `01.jpg` | Cattle and Sheep on Canterbury Meadows | `thomas-sidney-cooper-cattle-and-sheep-on-canterbury-meadows-1803-1902.jpg` |
| `b1/animal-solutions` | `02.jpg` | Shepherd with Cows | `rudolf-koller-shepherd-with-cows-1828-1905.jpeg` |
| `b1/arriving-in-johannesburg` | `01.jpg` | Cape Mountain Landscape | `gabriel-cornelis-de-jongh-cape-mountain-landscape.jpeg` |
| `b1/beers` | `01.jpg` | In the Monastery Cellar | `eduard-von-grutzner-in-the-monastery-cellar-1878.jpeg` |
| `b1/cachacas` | `02.jpg` | Interior of a Hammersmith | `hugo-charlemont-interior-of-a-hammersmith-1883.jpg` |
| `b1/cars` | `01.jpg` | The Horse Fair | `rosa-bonheur-the-horse-fair-c-1855.jpeg` |
| `b1/cars` | `02.jpg` | The Montgolfier brothers' balloon | `claude-louis-desrais-montgolfier-brothers-hot-air-balloon.jpg` |
| `b1/climbing` | `01.jpg` | Glacier Plateau | `edward-theodore-compton-glacier-plateau-1906.jpg` |
| `b1/climbing` | `02.jpg` | Grindelwald Glacier in the Alps | `joseph-anton-koch-grindelwald-glacier-in-the-alps-1823.jpeg` |
| `b1/detective-story` | `01.jpg` | Moonlight Landscape | `joseph-wright-of-derby-moonlight-landscape.jpg` |
| `b1/do-make-livestock-farming` | `01.jpg` | In the Farm | `julien-dupre-1851-1910-french-naturalist-painter-in-the-farm.jpeg` |
| `b1/do-make-livestock-farming` | `02.jpg` | The Gleaners | `jean-francois-millet-the-gleaners-1857.jpeg` |
| `b1/glamping` | `01.jpg` | Camping for the Night on Mansfield Mountain | `sanford-robinson-gifford-camping-for-the-night-on-mansfield-mountain.jpeg` |
| `b1/investigation-story` | `01.jpg` | A Game of Piquet | `ernest-meissonier-a-game-of-piquet-1861.jpeg` |
| `b1/investigation-story` | `02.jpg` | A Moonlit Night | `august-piepenhagen-a-moonlit-night.jpg` |
| `b1/investigation-story` | `03.jpg` | Lost Honor | `eduard-schulz-briesen-lost-honour.jpeg` |
| `b1/lewis-and-clark-unknown` | `01.jpg` | Among the Sierra Nevada Mountains | `albert-bierstadt-among-the-sierra-nevada-mountains-1868.jpg` |
| `b1/louisiana-purchase` | `01.jpg` | The Falls of St Anthony | `albert-bierstadt-the-falls-of-st-anthony-1887.jpg` |
| `b1/milan-restaurants` | `01.jpg` | Oregon Trail Campfire | `albert-bierstadt-oregon-trail-campfire-1863.jpeg` |
| `b1/milan-restaurants` | `02.jpg` | Fishermen | `hans-gude-adolph-tidemand-fishermen-1851.jpeg` |
| `b1/my-day-in-vienna-to-by-for` | `01.jpg` | St Stephen's Cathedral in Vienna | `rudolf-von-alt-st-stephens-cathedral-in-vienna-1832.jpg` |
| `b1/my-day-in-vienna-to-by-for` | `02.jpg` | The Roman Ruins at Schönbrunn | `ferdinand-georg-waldmuller-the-roman-ruins-at-schonbrunn-1832.jpeg` |
| `b1/my-life-and-plans` | `01.jpg` | Distracted from His Studies | `jules-girardet-1856-1938-distracted-from-his-studies.jpeg` |
| `b1/ny-visitation` | `01.jpg` | Park Landscape with a Fountain | `edvard-petersen-park-landscape-with-a-fountain.jpeg` |
| `b1/ny-visitation` | `02.jpg` | The Victoria Embankment from Hungerford Bridge | `george-hyde-pownall-the-victoria-embankment-from-hungerford-bridge-1876-1932.jpeg` |
| `b1/rio-de-janeiro-exercises` | `01.jpg` | The Heart of the Andes | `frederic-edwin-church-the-heart-of-the-andes.jpg` |
| `b1/rio-de-janeiro-exercises` | `02.jpg` | Tropical Landscape with a Hanging Bridge | `frederic-edwin-church-tropical-landscape-with-a-hanging-bridge.jpg` |
| `b1/santa-catarina` | `01.jpg` | Storm at Sea off the Norwegian Coast | `andreas-achenbach-storm-at-sea-off-the-norwegian-coast-1815-1910.jpeg` |
| `b1/santa-catarina` | `02.jpg` | Retreating Storm on the Italian Coast | `oswald-achenbach-retreating-storm-on-the-italian-coast.jpeg` |
| `b1/snowy-days` | `01.jpg` | First Snow | `ivan-shishkin-first-snow.jpeg` |
| `b1/snowy-days` | `02.jpg` | Winter Landscape | `caspar-david-friedrich-winter-landscape.jpg` |
| `b1/southeast-asia-adventure` | `01.jpg` | The Main Temple of Tassiding Monastery, Sikkim | `vasily-vereshchagin-the-main-temple-of-tassiding-monastery-sikkim-1875.jpg` |
| `b1/southeast-asia-adventure` | `02.jpg` | Evening on a Lake | `vasily-vereshchagin-evening-on-a-lake-a-pavilion-on-the-marble-embankment-in-rajnagar-udaipur-principality-1874.jpg` |
| `b1/state-fair-food` | `01.jpg` | Village Fair by Night | `hendrik-gerrit-ten-cate-village-fair-by-night-1803-1856.jpeg` |
| `b1/state-fair-food` | `02.jpg` | Fair in the Oude Beurs, Antwerp | `pierre-jean-van-der-ouderaa-fair-in-the-oude-beurs-in-antwerp-1892.jpeg` |
| `b1/transcontinental-railroad` | `01.jpg` | The Last of the Buffalo | `albert-bierstadt-the-last-of-the-buffalo-1888.jpg` |
| `b1/travel-dialogues-02` | `01.jpg` | A Scene of Everyday Life at the Nuremberg Town Hall | `heinrich-hansen-a-scene-of-everyday-life-at-the-nuremberg-town-hall.jpeg` |
| `b1/usa-restaurants` | `01.jpg` | Muddy Alligators | `john-singer-sargent-muddy-alligators.jpeg` |
| `b1/usa-restaurants` | `02.jpg` | Jamaica | `frederic-edwin-church-jamaica-1871.jpeg` |
| `b2/american-culture` | `01.jpg` | The Oxbow | `cole-thomas-the-oxbow-the-connecticut-river-near-northampton-1836.jpg` |
| `b2/american-culture` | `02.jpg` | Landscape with Buffalo on the Upper Missouri | `karl-bodmer-landscape-with-buffalo-on-the-upper-missouri-1833.jpg` |
| `b2/business-war-it` | `01.jpg` | Dreadnought and Victory: the Future and the Past at Their Moorings in Portsmouth | `wyllie-william-lionel-dreadnought-and-victory-the-future-and-the-past-at-their-moorings-in-portsmouth.jpg` |
| `b2/business-war-it` | `02.jpg` | HMS Nemesis Destroying Chinese Junks | `edward-duncan-hms-nemesis-destroying-chinese-junks-1st-opium-war-1843.jpeg` |
| `b2/capetown` | `01.jpg` | Mountain Gorge at Sunset | `tinus-de-jongh-mountain-gorge-at-sunset.jpeg` |
| `b2/capetown` | `02.jpg` | Near Burghersdorp | `tinus-de-jongh-near-burghersdorp-1885-1942.jpg` |
| `b2/describing-a-place` | `01.jpg` | The Night Fishermen | `sebastian-pether-the-night-fishermen-1793-1844.jpeg` |
| `b2/egypt-a-journey-through-history-and-culture` | `01.jpg` | The Citadel of Cairo | `cesare-biseo-the-citadel-of-cairo-1883.jpeg` |
| `b2/egypt-a-journey-through-history-and-culture` | `02.jpg` | Temple on the Nile | `david-roberts-temple-on-the-nile.jpeg` |
| `b2/formal-informal` | `01.jpg` | Pericles' Funeral Oration | `philipp-foltz-pericles-funeral-oration-1852.jpg` |
| `b2/formula-1` | `01.jpg` | The Chariot Race | `alexander-von-wagner-the-chariot-race.jpeg` |
| `b2/north-sentinel-island` | `01.jpg` | Dutch Vessels and Fishermen on a Rocky Coast | `adam-willaerts-dutch-vessels-and-fishermen-on-a-rocky-coast.jpeg` |
| `b2/romania` | `01.jpg` | Forest Landscape with Castle Ruins | `anton-hlavacek-forest-landscape-with-castle-ruins.jpeg` |
| `b2/romania` | `02.jpg` | Vlad the Impaler's Night Attack at Târgoviște | `theodor-aman-draculas-night-attack-at-targoviste.jpg` |
| `b2/the-marathon-and-the-wall` | `01.jpg` | The Heraean Games | `prospero-piatti-the-heraean-games-1901.jpg` |
| `c1/attention-economy` | `01.jpg` | Public Exhibition of a Picture | `joan-ferrer-miro-1850-1931-public-exhibition-of-a-picture.jpg` |
| `c1/real-estate` | `01.jpg` | Estes Park and Longs Peak | `albert-bierstadt-estes-park-and-longs-peak-c-1876.png` |
| `c1/shadows-in-the-server-room` | `01.jpg` | A Nocturnal Fire | `egbert-van-der-poel-a-nocturnal-fire-1621-1664.jpg` |
| `c1/technology-and-ethics` | `01.jpg` | The Death of Icarus | `alexandre-cabanel-the-death-of-icarus.jpeg` |
| `c1/the-meeting-problem` | `01.jpg` | After a Difficult Meeting | `eduard-von-grutzner-after-a-difficult-meeting-1892.jpeg` |
| `c1/the-night-shift` | `02.jpg` | Winter Morning | `joseph-farquharson-winter-morning.jpg` |
| `c2/reading-a-scientific-claim` | `01.jpg` | Total Eclipse of the Sun | `wilhelm-kranz-total-eclipse-of-the-sun-1897.jpeg` |
| `c2/reading-a-scientific-claim` | `02.jpg` | The Great Comet of 1861 | `edmund-weiss-great-comet-of-1861-1888.jpeg` |
| `c2/the-accent-you-keep` | `01.jpg` | A Reading from Homer | `lawrence-alma-tadema-a-reading-from-homer.jpg` |
| `c2/the-case-against-plain-english` | `01.jpg` | Diogenes | `jean-leon-gerome-diogene-1860.jpeg` |
| `c2/the-same-news-four-ways` | `01.jpg` | A Girl Reading a Newspaper | `wada-eisaku-a-girl-reading-newspaper-1897.jpeg` |
| `c2/the-second-language-self` | `01.jpg` | Flight and Pursuit | `william-rimmer-1816-1879-flight-and-pursuit.jpg` |
| `c2/the-west-was-not-empty` | `02.jpg` | Among the Sierra Nevada, California | `albert-bierstadt-among-the-sierra-nevada-mountains-1868.jpg` |
| `c2/what-doesnt-translate` | `01.jpg` | The Song of Phemius and the Sorrow of Penelope | `thomas-ralph-spence-the-song-of-phemius-and-the-sorrow-of-penelope-1897.jpg` |

### From Wikimedia Commons (public domain)

88 images the gallery could not answer -- flags, maps, photographs and
portraits of particular people. Fetched with `scripts/add_commons_image.py`, which
reads the Commons licence metadata and refuses anything that is not public domain.

| Page | File | Work | Commons file |
|---|---|---|---|
| `a1/abraham-lincoln` | `01.jpg` | Abraham Lincoln, photographed by Alexander Gardner, 1863. | `File:Abraham Lincoln O-80 by Gardner, 1863.jpg` |
| `a1/abraham-lincoln` | `02.jpg` | The Battle of Gettysburg | `File:Battle of Gettysburg, by Currier and Ives.png` |
| `a1/george-washington` | `02.jpg` | George Washington* (the Athenaeum portrait) | `File:Gilbert Stuart - George Washington (The Athenaeum Portrait) - Google Art Project.jpg` |
| `a1/going-to-the-airport` | `01.jpg` | Washington National Airport, 1941 | `File:Terminal waiting room Washington National Airport 1941 LOC fsa.8a36226.jpg` |
| `a1/greetings-and-names` | `01.jpg` | The soda fountain at People's Drug Store, Washington D.C. | `File:Interior of People's Drug Store, 11th and G Streets, Washington, D.C., with employees behind the counter of soda fountain and customers LCCN2001701747.jpg` |
| `a1/my-room` | `01.jpg` | A living room on Waverly Place, New York, 1942 | `File:Mrs. Marianna Costanzo in the living room of her apartment on Waverly Place8d11560v.jpg` |
| `a1/statue-of-liberty` | `01.jpg` | Unveiling the Statue of Liberty | `File:EdwardMoran-UnveilingTheStatueofLiberty1886Large.jpg` |
| `a1/statue-of-liberty` | `02.jpg` | Ellis Island, 1902. The island where ships from Europe stopped, a few hundred meters from the statue. | `File:Ellis island 1902.jpg` |
| `a1/the-american-flag` | `01.jpg` | The flag of 1777: thirteen stripes and thirteen stars, one for each of the first states. | `File:Flag of the United States (1777-1795).svg` |
| `a1/the-american-flag` | `02.jpg` | The flag today. Same thirteen stripes, fifty stars. | `File:Flag of the United States.svg` |
| `a2/boston-tea-party` | `01.jpg` | The Destruction of Tea at Boston Harbor | `File:Boston Tea Party Currier colored.jpg` |
| `a2/california-gold-rush` | `01.jpg` | Miners washing gravel with a “long tom”, California, around 1850. | `File:California gold miners with long tom.jpg` |
| `a2/california-gold-rush` | `02.jpg` | Yerba Buena Cove, San Francisco, 1849. The crews had walked off to the gold fields and left the ships where they lay. | `File:Ships-abandoned-in-Yerba-Buena-Cove-San-Francisco-during-the-California-gold-rush.-1849.jpg` |
| `a2/declaration-of-independence` | `02.jpg` | The document itself, now in Washington, D.C. The large signature at the top left of the names is John Hancock's. | `File:United States Declaration of Independence.jpg` |
| `a2/flying-to-the-us` | `01.jpg` | The first United Airlines service into Allentown, 1935. Flying was still something a town turned out to watch. | `File:1935 - United Airlines begins service to Allentown Airport.jpg` |
| `a2/oregon-trail` | `02.jpg` | Emigrants Crossing the Plains | `File:Emigrants Crossing the Plains, or The Oregon Trail (Albert Bierstadt), 1869.jpg` |
| `a2/sacagawea` | `01.jpg` | Lewis and Clark on the Lower Columbia | `File:Lewis and clark-expedition.jpg` |
| `a2/saying-and-telling` | `01.jpg` | A Piggly Wiggly store | `File:Interior view of a Piggly Wiggly self-service grocery store showing check out counter with cash registers LCCN92520726.jpg` |
| `b1/a-day-in-the-office` | `01.jpg` | Interior with a Woman Standing | `File:Interior with a Woman Standing by Vilhelm Hammershøi, 1913.jpg` |
| `b1/american-flag-symbols` | `01.jpg` | Join, or Die | `File:Benjamin Franklin - Join or Die.jpg` |
| `b1/american-flag-symbols` | `02.jpg` | The Grand Union flag, or Continental Colors, used from late 1775. Thirteen colonies acting together | `File:Grand Union Flag.svg` |
| `b1/american-flag-symbols` | `03.jpg` | One reading of the 1777 resolution: thirteen stars in rows. The resolution did not say how to arrange them, so flag-makers decided for themselves. | `File:Flag of the United States (1777-1795).svg` |
| `b1/american-flag-symbols` | `04.jpg` | The circle of thirteen stars, known as the Betsy Ross flag. The design is of the period; the story that she sewed the first one is family tradition from 1870, not a contemporary record. | `File:Betsy Ross flag.svg` |
| `b1/american-flag-symbols` | `05.jpg` | The Gadsden flag, 1775 | `File:Gadsden flag.svg` |
| `b1/american-flag-symbols` | `06.jpg` | The Pine Tree flag, used by New England units and Washington's armed schooners in 1775, in an 1894 printed illustration. The motto is John Locke's phrase for what a people may do when no court will hear them. | `File:Pine Tree "An Appeal To Heaven" Flag Illustration from 1894.png` |
| `b1/american-flag-symbols` | `07.jpg` | The Bennington design, photographed on a modern flag. It is traditionally tied to the battle of 1777, but the surviving historic flag is machine-woven and is now usually dated to the early nineteenth century. | `File:Bennington-Battle-Flag.jpg` |
| `b1/american-flag-symbols` | `08.jpg` | Fifteen stars and fifteen stripes, 1795–1818. This is the flag over Fort McHenry in 1814, and the only American flag ever to have more than thirteen stripes. | `File:Flag of the United States (1795-1818).svg` |
| `b1/american-flag-symbols` | `09.jpg` | Fifty stars since 1960. Thirteen stripes, by the law of 1818, for the colonies that started it. | `File:Flag of the United States.svg` |
| `b1/cachacas` | `01.jpg` | Harvesting the Sugar-Cane in Minas Gerais, Brazil | `File:Marianne North (1830-1890) - Harvesting the Sugar-Cane in Minas Geraes, Brazil - MN45 - Marianne North Gallery.jpg` |
| `b1/cars-and-their-parts` | `01.jpg` | A 1920 Handley-Knight engine with the chain case off. Almost every part this text names is somewhere in this picture. | `File:Handley-Knight-Engine 1920.jpg` |
| `b1/frederick-douglass` | `01.jpg` | Frederick Douglass in 1856. He sat for photographs constantly and deliberately: he was the most photographed American of the nineteenth century. | `File:Frederick Douglass ambrotype (1856).jpg` |
| `b1/golden-gate-bridge-present-perfect` | `01.jpg` | The Golden Gate Bridge | `File:Golden Gate Bridge, HAER CA-31-4.jpg` |
| `b1/hachiko` | `01.jpg` | Hachiko at Shibuya station, around 1933 | `File:Chuken Hachiko at Shibuya Station c1933.png` |
| `b1/hachiko` | `02.jpg` | Hachiko, photographed in the 1930s. The folded left ear is how people at the station picked him out; it had been injured years earlier and never stood up again. | `File:Faithful Dog Hachiko Photo.png` |
| `b1/harriet-tubman` | `01.jpg` | Harriet Tubman, photographed around 1868, about twenty years after her own escape. | `File:Harriet Tubman c1868-69.jpg` |
| `b1/harriet-tubman` | `02.jpg` | The Underground Railroad | `File:The Underground Railroad by Charles T. Webber, 1893.jpg` |
| `b1/kitchen-chaos` | `01.jpg` | A kitchen in a federal housing project, 1942 | `File:Federal housing project. Mrs. Leslie Atkins preparing dinner8d20971v.jpg` |
| `b1/lewis-and-clark-unknown` | `02.jpg` | Lewis and Clark on the Lower Columbia | `File:Lewis and clark-expedition.jpg` |
| `b1/lincoln-and-the-civil-war` | `01.jpg` | The Battle of Antietam | `File:Thure de Thulstrup - Battle of Antietam.jpg` |
| `b1/louisiana-purchase` | `02.jpg` | Louisiana, mapped by Samuel Lewis in 1804. Notice how much of it is blank: this is the map the United States had just bought. | `File:Map of "Louisiana" by Samuel Lewis, from New and Elegant General Atlas, Philadelphia, 1804.jpg` |
| `b1/nfl` | `01.jpg` | Princeton against Chicago, 1922. The game in this text, before the helmets, the television contracts and the league. | `File:1922 Princeton v. Chicago football game.jpg` |
| `b1/say-speak-talk-tell-02` | `01.jpg` | A radio dealer's window | `File:J. Fred Huber Radio, window LCCN2016826306.jpg` |
| `b1/transcontinental-railroad` | `02.jpg` | Promontory Summit, Utah, 10 May 1869. No Chinese worker appears in the photograph of the line they largely built. | `File:East and West Shaking hands at the laying of last rail Union Pacific Railroad - Restoration.jpg` |
| `b1/transcontinental-railroad` | `03.jpg` | Chinese workers on the Central Pacific in the Sierra Nevada. At the peak they were about four out of five of the company's workforce. | `File:Chinese railroad workers sierra nevada.jpg` |
| `b2/civil-war-nation-divided` | `01.jpg` | Pickett's Charge at Gettysburg | `File:Thure de Thulstrup - L. Prang and Co. - Battle of Gettysburg - Restoration by Adam Cuerden.jpg` |
| `b2/fdr-new-deal` | `01.jpg` | Roosevelt signs the Social Security Act, 14 August 1935 | `File:Signing Of The Social Security Act.jpg` |
| `b2/fdr-new-deal` | `02.jpg` | A WPA poster. The agency employed artists to design the posters as well as laborers to build the roads. | `File:WPA-Work-Pays-America-Poster.jpg` |
| `b2/great-depression` | `01.jpg` | A bank run in Michigan, February 1933. A bank holds only part of its deposits as cash; the rest of this picture explains itself. | `File:Bank Run in Michigan, USA, February 1933.jpg` |
| `b2/great-depression` | `02.jpg` | Migrant Mother | `File:Lange-MigrantMother02.jpg` |
| `b2/great-depression` | `03.jpg` | A dust storm approaching Stratford, Texas, 1935. The soil in the air had been plowed grassland a decade earlier. | `File:Dust storm approaching Stratford, Texas.jpg` |
| `b2/intelligence-pills` | `01.jpg` | Stewart's Pharmacy, Seattle, around 1900. Everything on these shelves was sold to somebody who wanted to feel better than they did. | `File:Stewart's Pharmacy interior, ca 1900 (SEATTLE 282).jpg` |
| `b2/it-and-jiu-jitsu` | `01.jpg` | A jujutsu lock, from *Japanese Physical Training*, 1904. The whole point of the technique is that force applied in the wrong direction does the work for you | `File:Japanese Physical Training illustration 16.jpg` |
| `b2/it-interview` | `01.jpg` | “A worried applicant waiting to be interviewed” | `File:Los Angeles, California. Lockheed Employment. A worried applicant waiting to be interviewed - NARA - 532210.jpg` |
| `b2/jackie-robinson` | `01.jpg` | Jackie Robinson, Brooklyn Dodgers, 1954 | `File:Jackie Robinson, Brooklyn Dodgers, 1954.jpg` |
| `b2/project-management-can-could-able-do-make` | `01.jpg` | Working through county land-use plans together | `File:Working on the county maps at the colored County Land Use Pl... (3110578334).jpg` |
| `b2/recent-advancements-in-it` | `02.jpg` | ENIAC, around 1946 | `File:Classic shot of the ENIAC.jpg` |
| `b2/reconstruction` | `01.jpg` | The First Vote | `File:"The first vote" by A.R. Waud Harper's Weekly 1867-11-16 Retrieved from the Library of Congress.jpg` |
| `b2/reconstruction` | `02.jpg` | The first Black senator and representatives in Congress, printed in 1872. Within thirty years almost none of their voters were still on the rolls. | `File:First Colored Senator and Representatives.jpg` |
| `b2/trail-of-tears` | `01.jpg` | Sequoyah with his syllabary | `File:Henry Inman - Sequoyah - Google Art Project.jpg` |
| `b2/trail-of-tears` | `02.jpg` | West of the Mississippi, as mapped in 1804. This is where removal sent sixteen thousand people, on foot, in winter. | `File:Map of "Louisiana" by Samuel Lewis, from New and Elegant General Atlas, Philadelphia, 1804.jpg` |
| `c1/apollo-11` | `01.jpg` | Buzz Aldrin on the surface | `File:Aldrin Apollo 11.jpg` |
| `c1/apollo-11` | `02.jpg` | The Laser Ranging Retroreflector, photographed where it was left | `File:AS11-40-5952 - Apollo 11 - Apollo 11 Mission image - The Laser Ranging Retroreflector (LRRR) - NARA - 16685293.jpg` |
| `c1/haiti` | `01.jpg` | The Daily Times-Advocate, 22 August 1912. Every claim on this page is attributed, hedged or stated flat, and telling the three apart is what this text teaches. | `File:Times-Advocate-Front-Page-1912-08-22.jpg` |
| `c1/it-management` | `01.jpg` | The Banker and His Wife | `File:Marinus van Reymerswale - The Banker and His Wife - WGA19323.jpg` |
| `c1/malcolm-x` | `01.jpg` | Malcolm X and Martin Luther King Jr. | `File:MLK and Malcolm X USNWR cropped.jpg` |
| `c1/malcolm-x` | `02.jpg` | Malcolm X | `File:Malcolm X in 1964.jpg` |
| `c1/martin-luther-king` | `01.jpg` | Martin Luther King Jr. at the March on Washington | `File:Civil Rights March on Washington, D.C. (Dr. Martin Luther King, Jr. and Mathew Ahmann in a crowd.) - NARA - 542015 - Restoration.jpg` |
| `c1/martin-luther-king` | `02.jpg` | Fire hoses turned on demonstrators in Birmingham, Alabama | `File:Firemen spraying protestors in Downtown Birmingham 01.jpg` |
| `c1/physiological-stressors` | `01.jpg` | Dorando Pietri at the end of the 1908 Olympic marathon. He was helped across the line and disqualified for it. This is what the six systems in this text look like when they stop coping. | `File:Dorando Pietri 1908.jpg` |
| `c1/rosa-parks` | `01.jpg` | Rosa Parks fingerprinted by Deputy Sheriff D. H. Lackey | `File:Rosa Parks being fingerprinted by Deputy Sheriff D.H. Lackey after being arrested on February 22, 1956, during the Montgomery bus boycott.jpg` |
| `c1/rosa-parks` | `02.jpg` | Flyer circulated in Montgomery after the court order, 1956 | `File:Montgomery Improvement Association, flyer on bus desegregation, c. 1956 (NYPL).jpg` |
| `c1/rosa-parks` | `03.jpg` | Rosa Parks on a Montgomery bus | `File:Rosa Parks on bus on December 21, 1956.jpg` |
| `c1/the-space-race` | `01.jpg` | A full-size replica of Sputnik 1 on display | `File:Sputnik 1.jpg` |
| `c1/the-space-race` | `02.jpg` | Yuri Gagarin | `File:Yuri Gagarin (1961) - Restoration.jpg` |
| `c1/the-space-race` | `03.jpg` | An N1 mockup on the pad at Baikonur, 1967. The figures at the base give the scale: it stood as tall as a Saturn V, it failed on all four launch attempts, and the Soviet Union denied that the program existed until 1989. | `File:N1 1M1 mockup on the launch pad at the Baikonur Cosmodrome in late 1967.jpg` |
| `c1/watergate` | `01.jpg` | The Watergate complex, Washington D.C. Offices, flats and a hotel on the Potomac; the Democratic National Committee rented the sixth floor of one of the office buildings. | `File:WatergateFromAir.JPG` |
| `c1/watergate` | `02.jpg` | Nixon's letter of resignation, 9 August 1974. One sentence, addressed to the Secretary of State because that is where the law says such a letter goes; the pen notation in the corner | `File:Letter of Resignation of Richard M. Nixon, 1974.jpg` |
| `c1/women-win-the-vote` | `01.jpg` | Official program for the suffrage procession | `File:Official Program Woman Suffrage Procession - March 3, 1913.jpg` |
| `c1/women-win-the-vote` | `02.jpg` | The Silent Sentinels at the White House gates, 1917. They stood there daily for over two years | `File:Suffragists picketing the White House.jpg` |
| `c2/immigration-and-modern-america` | `01.jpg` | The Usual Irish Way of Doing Things | `File:TheUsualIrishWayofDoingThings.jpg` |
| `c2/immigration-and-modern-america` | `02.jpg` | The Chinese Exclusion Act, 1882, in the enrolled original. The first federal law to bar a group of people from the United States by nationality, and it opens by reciting that their coming “endangers the good order of certain localities”. It was renewed repeatedly and not fully repealed until 1943. | `File:Chineseexclusionact.JPG` |
| `c2/manifest-destiny` | `01.jpg` | American Progress | `File:American Progress (1872) by John Gast.jpg` |
| `c2/reconstruction-revolution` | `01.jpg` | One of the data portraits W. E. B. Du Bois and his students prepared for the 1900 Paris Exposition. Industrial training, 2,252 students; the classical course, 98. The bar is folded because the page could not hold it. Thirty-five years before the book that was ignored, he was already answering the question with evidence. | `File:The Georgia Negro LCCN2013650436.jpg` |
| `c2/slavery-and-the-american-economy` | `01.jpg` | Auction broadside, New Orleans, 14 January 1860. Twenty-eight people by name, age and trade | `File:SlaveAuctionBroadside-1860-01-14.jpg` |
| `c2/slavery-and-the-american-economy` | `02.jpg` | Cotton Merchants in New Orleans | `File:Edgar Degas - Cotton Merchants in New Orleans.jpg` |
| `c2/the-american-dream` | `01.jpg` | Toward Los Angeles | `File:Toward Los Angeles, California LOC 3549663710.jpg` |
| `c2/the-west-was-not-empty` | `01.jpg` | Indian Family Alarmed at the Approach of a Prairie Fire | `File:George Catlin - Indian Family Alarmed at the Approach of a Prairie Fire - 1985.66.595 - Smithsonian American Art Museum.jpg` |
| `c2/what-makes-an-american-hero` | `01.jpg` | Mission Control at the end of Apollo 11 | `File:Mission Operations Control Room at the conclusion of Apollo 11.jpg` |

<!-- gallery:end -->
