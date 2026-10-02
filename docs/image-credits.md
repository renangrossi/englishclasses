# Image credits

Every image used on a reading page, with its source and rights.

`scripts/fetch_public_domain_image.py` reads the licence metadata from the
Commons API, and `scripts/add_commons_image.py` acts on it in three tiers:

- **Public domain and CC0** — used as they are, nothing owed.
- **CC BY and CC BY-SA, the UK Open Government Licence, and Commons'
  {{Attribution}} licence** — used, with the licence and the author recorded on
  the image in its source JSON and printed in small type under the picture
  itself. That is the condition those licences attach, and putting it under the
  picture rather than in a file somewhere keeps it with the thing it applies to.
  The last two are not Creative Commons, so they are matched on the licence's
  exact short name ("OGL 3", "Attribution") rather than searched for: "ogl" sits
  inside "Google". They came in for the House of Commons chamber (OGL) and the
  Sentinel-2 view of North Sentinel Island (Copernicus imagery, published under
  {{Attribution}}, credited in the wording Copernicus asks for).
- **Anything carrying NC or ND, and anything unfree** — refused outright. ND
  forbids the resize every image here goes through, and NC puts a condition on
  the whole site that nobody should have to reason about later.

The library ran public-domain-only for most of its life, and most of it still
is. The middle tier was opened deliberately: modern subjects — a coffee shop, a
server room, a 1990s bedroom — are very thinly covered by public-domain
photography, and the alternative was illustrating them with whatever old
painting was nearest, which is how a Byzantine court scene came to sit over a
text about an office.

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

88 images, imported with `scripts/import_local_artwork.py` from the local
gallery of painting and print scans. Each one is a work old enough to be free of
rights; the gallery also holds living and recent artists, and none of that is used.

| Page | File | Work | Gallery source |
|---|---|---|---|
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
| `a2/st-patricks-day` | `02.jpg` | Riders of the Sidhe | `john-duncan-riders-of-the-sidhe-1911.jpg` |
| `a2/thanksgiving` | `01.jpg` | Harvest | `vladimir-orlovsky-harvest-in-the-ukraine-1880.jpeg` |
| `a2/thanksgiving` | `02.jpg` | The Roast Beef of Old England | `frank-moss-bennett-the-roast-beef-of-old-england.jpeg` |
| `a2/the-day-at-the-market` | `01.jpg` | Venetian Fruit Sellers | `stefano-novo-venetian-fruit-sellers-1898.jpeg` |
| `a2/two-small-errands` | `02.jpg` | A Town Scene with a Farrier | `jacques-carabain-a-town-scene-with-a-farrier.jpeg` |
| `a2/two-very-different-trips` | `01.jpg` | People on a Beach | `amaldus-nielsen-people-on-a-beach-1894.jpg` |
| `b1/a-day-in-the-house` | `01.jpg` | A Sleeping Dog | `gerrit-dou-a-sleeping-dog.jpeg` |
| `b1/a-freelance-accounting-assignment` | `01.jpg` | The Cartographers' Circle | `fritz-wagner-the-cartographers-circle.jpeg` |
| `b1/animal-solutions` | `01.jpg` | Cattle and Sheep on Canterbury Meadows | `thomas-sidney-cooper-cattle-and-sheep-on-canterbury-meadows-1803-1902.jpg` |
| `b1/animal-solutions` | `02.jpg` | Shepherd with Cows | `rudolf-koller-shepherd-with-cows-1828-1905.jpeg` |
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
| `b1/my-day-in-vienna-to-by-for` | `01.jpg` | St Stephen's Cathedral in Vienna | `rudolf-von-alt-st-stephens-cathedral-in-vienna-1832.jpg` |
| `b1/my-day-in-vienna-to-by-for` | `02.jpg` | The Roman Ruins at Schönbrunn | `ferdinand-georg-waldmuller-the-roman-ruins-at-schonbrunn-1832.jpeg` |
| `b1/my-life-and-plans` | `01.jpg` | Distracted from His Studies | `jules-girardet-1856-1938-distracted-from-his-studies.jpeg` |
| `b1/snowy-days` | `01.jpg` | First Snow | `ivan-shishkin-first-snow.jpeg` |
| `b1/snowy-days` | `02.jpg` | Winter Landscape | `caspar-david-friedrich-winter-landscape.jpg` |
| `b1/state-fair-food` | `01.jpg` | Village Fair by Night | `hendrik-gerrit-ten-cate-village-fair-by-night-1803-1856.jpeg` |
| `b1/state-fair-food` | `02.jpg` | Fair in the Oude Beurs, Antwerp | `pierre-jean-van-der-ouderaa-fair-in-the-oude-beurs-in-antwerp-1892.jpeg` |
| `b1/transcontinental-railroad` | `01.jpg` | The Last of the Buffalo | `albert-bierstadt-the-last-of-the-buffalo-1888.jpg` |
| `b1/travel-dialogues-02` | `01.jpg` | A Scene of Everyday Life at the Nuremberg Town Hall | `heinrich-hansen-a-scene-of-everyday-life-at-the-nuremberg-town-hall.jpeg` |
| `b1/usa-restaurants` | `01.jpg` | Muddy Alligators | `john-singer-sargent-muddy-alligators.jpeg` |
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
| `b2/romania` | `02.jpg` | Vlad the Impaler's Night Attack at Târgoviște | `theodor-aman-draculas-night-attack-at-targoviste.jpg` |
| `b2/the-marathon-and-the-wall` | `01.jpg` | The Heraean Games | `prospero-piatti-the-heraean-games-1901.jpg` |
| `c1/attention-economy` | `01.jpg` | Public Exhibition of a Picture | `joan-ferrer-miro-1850-1931-public-exhibition-of-a-picture.jpg` |
| `c1/real-estate` | `01.jpg` | Estes Park and Longs Peak | `albert-bierstadt-estes-park-and-longs-peak-c-1876.png` |
| `c1/technology-and-ethics` | `01.jpg` | The Death of Icarus | `alexandre-cabanel-the-death-of-icarus.jpeg` |
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

141 images the gallery could not answer -- flags, maps, photographs and
portraits of particular people. Fetched with `scripts/add_commons_image.py`, which
reads the Commons licence metadata and refuses anything carrying NC or ND. The
few used under a licence that requires a credit are listed separately below.

| Page | File | Work | Commons file |
|---|---|---|---|
| `a1/abraham-lincoln` | `01.jpg` | Abraham Lincoln, photographed by Alexander Gardner, 1863. | `File:Abraham Lincoln O-80 by Gardner, 1863.jpg` |
| `a1/abraham-lincoln` | `02.jpg` | The Battle of Gettysburg | `File:Battle of Gettysburg, by Currier and Ives.png` |
| `a1/george-washington` | `02.jpg` | George Washington* (the Athenaeum portrait) | `File:Gilbert Stuart - George Washington (The Athenaeum Portrait) - Google Art Project.jpg` |
| `a1/going-to-the-airport` | `01.jpg` | Washington National Airport, 1941 | `File:Terminal waiting room Washington National Airport 1941 LOC fsa.8a36226.jpg` |
| `a1/greetings-and-names` | `01.jpg` | The soda fountain at People's Drug Store, Washington D.C. | `File:Interior of People's Drug Store, 11th and G Streets, Washington, D.C., with employees behind the counter of soda fountain and customers LCCN2001701747.jpg` |
| `a1/my-room` | `01.jpg` | A living room on Waverly Place, New York, 1942 | `File:Mrs. Marianna Costanzo in the living room of her apartment on Waverly Place8d11560v.jpg` |
| `a1/statue-of-liberty` | `01.jpg` | Unveiling the Statue of Liberty | `File:EdwardMoran-UnveilingTheStatueofLiberty1886Large.jpg` |
| `a1/statue-of-liberty` | `02.jpg` | Ellis Island, 1902. | `File:Ellis island 1902.jpg` |
| `a1/taking-the-train` | `01.jpg` | The waiting room of Chicago Union Station, 1943 | `File:Chicago, Illinois. In the waiting room of the Union Station LOC 3548859587.jpg` |
| `a1/the-american-flag` | `01.jpg` | The flag of 1777: thirteen stripes and thirteen stars, one for each of the first states. | `File:Flag of the United States (1777-1795).svg` |
| `a1/the-american-flag` | `02.jpg` | The flag today. Same thirteen stripes, fifty stars. | `File:Flag of the United States.svg` |
| `a2/boston-tea-party` | `01.jpg` | The Destruction of Tea at Boston Harbor | `File:Boston Tea Party Currier colored.jpg` |
| `a2/california-gold-rush` | `01.jpg` | Miners washing gravel with a “long tom”, California, around 1850. | `File:California gold miners with long tom.jpg` |
| `a2/california-gold-rush` | `02.jpg` | Yerba Buena Cove, San Francisco, 1849. | `File:Ships-abandoned-in-Yerba-Buena-Cove-San-Francisco-during-the-California-gold-rush.-1849.jpg` |
| `a2/coffee-brewing` | `01.jpg` | Pouring over the filter. | `File:Brewing coffee in a jug (Unsplash).jpg` |
| `a2/declaration-of-independence` | `02.jpg` | The document itself, now in Washington, D.C. | `File:United States Declaration of Independence.jpg` |
| `a2/flying-to-the-us` | `01.jpg` | The first United Airlines service into Allentown, 1935. | `File:1935 - United Airlines begins service to Allentown Airport.jpg` |
| `a2/flying-to-the-us` | `02.jpg` | Check-in counters at Suvarnabhumi, Bangkok. | `File:VTBS-Thai Airways Check-in counters.JPG` |
| `a2/oregon-trail` | `02.jpg` | Emigrants Crossing the Plains | `File:Emigrants Crossing the Plains, or The Oregon Trail (Albert Bierstadt), 1869.jpg` |
| `a2/sacagawea` | `01.jpg` | Lewis and Clark on the Lower Columbia | `File:Lewis and clark-expedition.jpg` |
| `a2/saying-and-telling` | `01.jpg` | A Piggly Wiggly store | `File:Interior view of a Piggly Wiggly self-service grocery store showing check out counter with cash registers LCCN92520726.jpg` |
| `a2/something-wrong-with-the-order` | `01.jpg` | Lunch arriving in a Dominican restaurant. | `File:Dominican Restaurant (Unsplash).jpg` |
| `a2/st-patricks-day` | `01.jpg` | The Fifth Avenue parade, New York. | `File:New York City St. Patrick's Day Parade DVIDS261048.jpg` |
| `b1/a-day-in-the-house` | `02.jpg` | A laundry room in an apartment building. | `File:Laundry room in apartment building.png` |
| `b1/a-day-in-the-office` | `01.jpg` | Interior with a Woman Standing | `File:Interior with a Woman Standing by Vilhelm Hammershøi, 1913.jpg` |
| `b1/american-flag-symbols` | `01.jpg` | Join, or Die | `File:Benjamin Franklin - Join or Die.jpg` |
| `b1/american-flag-symbols` | `02.jpg` | The Grand Union flag, or Continental Colors, used from late 1775. | `File:Grand Union Flag.svg` |
| `b1/american-flag-symbols` | `03.jpg` | One reading of the 1777 resolution: thirteen stars in rows. | `File:Flag of the United States (1777-1795).svg` |
| `b1/american-flag-symbols` | `04.jpg` | The circle of thirteen stars, known as the Betsy Ross flag. | `File:Betsy Ross flag.svg` |
| `b1/american-flag-symbols` | `05.jpg` | The Gadsden flag, 1775 | `File:Gadsden flag.svg` |
| `b1/american-flag-symbols` | `06.jpg` | The Pine Tree flag, used by New England units and Washington's armed schooners in 1775, in an 1894 printed illustration. | `File:Pine Tree "An Appeal To Heaven" Flag Illustration from 1894.png` |
| `b1/american-flag-symbols` | `07.jpg` | The Bennington design, photographed on a modern flag. | `File:Bennington-Battle-Flag.jpg` |
| `b1/american-flag-symbols` | `08.jpg` | Fifteen stars and fifteen stripes, 1795–1818. | `File:Flag of the United States (1795-1818).svg` |
| `b1/american-flag-symbols` | `09.jpg` | Fifty stars since 1960. | `File:Flag of the United States.svg` |
| `b1/cachacas` | `01.jpg` | Harvesting the Sugar-Cane in Minas Gerais, Brazil | `File:Marianne North (1830-1890) - Harvesting the Sugar-Cane in Minas Geraes, Brazil - MN45 - Marianne North Gallery.jpg` |
| `b1/cars-and-their-parts` | `01.jpg` | A 1920 Handley-Knight engine with the chain case off. | `File:Handley-Knight-Engine 1920.jpg` |
| `b1/climbing` | `03.jpg` | On the rock. | `File:Rock Climber (53328079241).jpg` |
| `b1/coffee-and-it` | `01.jpg` | A full coffee shop in the middle of the afternoon. | `File:Chatting in a coffee shop (Unsplash).jpg` |
| `b1/common-chores` | `01.jpg` | Washing out on the lines behind a row of houses | `File:An elevated view of row houses probably in S.W., showing laundry hanging on clothesline in backyards LCCN2016647096.jpg` |
| `b1/cybersecurity` | `01.jpg` | A cybersecurity operations floor | `File:Cybersecurity Operations at Port San Antonio.jpg` |
| `b1/frederick-douglass` | `01.jpg` | Frederick Douglass in 1856. | `File:Frederick Douglass ambrotype (1856).jpg` |
| `b1/golden-gate-bridge-present-perfect` | `01.jpg` | The Golden Gate Bridge | `File:Golden Gate Bridge, HAER CA-31-4.jpg` |
| `b1/hachiko` | `01.jpg` | Hachiko at Shibuya station, around 1933 | `File:Chuken Hachiko at Shibuya Station c1933.png` |
| `b1/hachiko` | `02.jpg` | Hachiko, photographed in the 1930s. | `File:Faithful Dog Hachiko Photo.png` |
| `b1/harriet-tubman` | `01.jpg` | Harriet Tubman, photographed around 1868, about twenty years after her own escape. | `File:Harriet Tubman c1868-69.jpg` |
| `b1/harriet-tubman` | `02.jpg` | The Underground Railroad | `File:The Underground Railroad by Charles T. Webber, 1893.jpg` |
| `b1/kitchen-chaos` | `01.jpg` | A kitchen in a federal housing project, 1942 | `File:Federal housing project. Mrs. Leslie Atkins preparing dinner8d20971v.jpg` |
| `b1/lewis-and-clark-unknown` | `02.jpg` | Lewis and Clark on the Lower Columbia | `File:Lewis and clark-expedition.jpg` |
| `b1/lincoln-and-the-civil-war` | `01.jpg` | The Battle of Antietam | `File:Thure de Thulstrup - Battle of Antietam.jpg` |
| `b1/lincoln-and-the-civil-war` | `02.jpg` | Gettysburg, 19 November 1863. | `File:Crowd of citizens, soldiers, and etc. with Lincoln at Gettysburg. - NARA - 529085 -crop.jpg` |
| `b1/louisiana-purchase` | `02.jpg` | Louisiana, mapped by Samuel Lewis in 1804. | `File:Map of "Louisiana" by Samuel Lewis, from New and Elegant General Atlas, Philadelphia, 1804.jpg` |
| `b1/maringa` | `02.jpg` | The lakefront from the south. | `File:Morning view of the downtown skyline from near Morgan Point along Lakefront Trail, Chicago, 2025.jpg` |
| `b1/nfl` | `01.jpg` | Princeton against Chicago, 1922. | `File:1922 Princeton v. Chicago football game.jpg` |
| `b1/physical-education` | `01.jpg` | Plates from *Athletic Training for School Boys*, 1910. | `File:Athletic training for school boys (1910) (14598149930).jpg` |
| `b1/say-speak-talk-tell-02` | `01.jpg` | A radio dealer's window | `File:J. Fred Huber Radio, window LCCN2016826306.jpg` |
| `b1/transcontinental-railroad` | `02.jpg` | Promontory Summit, Utah, 10 May 1869. | `File:East and West Shaking hands at the laying of last rail Union Pacific Railroad - Restoration.jpg` |
| `b1/transcontinental-railroad` | `03.jpg` | Chinese workers on the Central Pacific in the Sierra Nevada. | `File:Chinese railroad workers sierra nevada.jpg` |
| `b2/civil-war-nation-divided` | `01.jpg` | Pickett's Charge at Gettysburg | `File:Thure de Thulstrup - L. Prang and Co. - Battle of Gettysburg - Restoration by Adam Cuerden.jpg` |
| `b2/civil-war-nation-divided` | `02.jpg` | A Harvest of Death | `File:A Harvest of Death, Gettysburg, Pennsylvania MET DP274823.jpg` |
| `b2/fdr-new-deal` | `01.jpg` | Roosevelt signs the Social Security Act, 14 August 1935 | `File:Signing Of The Social Security Act.jpg` |
| `b2/fdr-new-deal` | `02.jpg` | A WPA poster. | `File:WPA-Work-Pays-America-Poster.jpg` |
| `b2/great-depression` | `01.jpg` | A bank run in Michigan, February 1933. | `File:Bank Run in Michigan, USA, February 1933.jpg` |
| `b2/great-depression` | `02.jpg` | Migrant Mother | `File:Lange-MigrantMother02.jpg` |
| `b2/great-depression` | `03.jpg` | A dust storm approaching Stratford, Texas, 1935. | `File:Dust storm approaching Stratford, Texas.jpg` |
| `b2/intelligence-pills` | `01.jpg` | Stewart's Pharmacy, Seattle, around 1900. | `File:Stewart's Pharmacy interior, ca 1900 (SEATTLE 282).jpg` |
| `b2/it-and-jiu-jitsu` | `01.jpg` | A jujutsu lock, from *Japanese Physical Training*, 1904. | `File:Japanese Physical Training illustration 16.jpg` |
| `b2/it-interview` | `01.jpg` | “A worried applicant waiting to be interviewed” | `File:Los Angeles, California. Lockheed Employment. A worried applicant waiting to be interviewed - NARA - 532210.jpg` |
| `b2/jackie-robinson` | `01.jpg` | Jackie Robinson, Brooklyn Dodgers, 1954 | `File:Jackie Robinson, Brooklyn Dodgers, 1954.jpg` |
| `b2/jackie-robinson` | `02.jpg` | Branch Rickey. | `File:Branch Rickey Cardinals.jpg` |
| `b2/phrasal-verbs-02-trip-abroad` | `01.jpg` | Manhattan from the air, 1932 | `File:New York City, circa 1932.jpg` |
| `b2/project-management-can-could-able-do-make` | `01.jpg` | Working through county land-use plans together | `File:Working on the county maps at the colored County Land Use Pl... (3110578334).jpg` |
| `b2/project-management-can-could-able-do-make` | `02.jpg` | A meeting room with a long table and the chairs still pushed in. | `File:Minimalist meeting room (Unsplash).jpg` |
| `b2/recent-advancements-in-it` | `02.jpg` | ENIAC, around 1946 | `File:Classic shot of the ENIAC.jpg` |
| `b2/reconstruction` | `01.jpg` | The First Vote | `File:"The first vote" by A.R. Waud Harper's Weekly 1867-11-16 Retrieved from the Library of Congress.jpg` |
| `b2/reconstruction` | `02.jpg` | The first Black senator and representatives in Congress, printed in 1872. | `File:First Colored Senator and Representatives.jpg` |
| `b2/romania` | `01.jpg` | The Carpathians. | `File:Carpathian Mountains (Unsplash alpqdm9yhb4).jpg` |
| `b2/sales-strategy` | `01.jpg` | A shop assistant showing a customer a product, Selfridges, 1940 | `File:A shop assistant shows a customer a luminous flower in Selfridge's department store, London. These flowers were one of numerous blackout accessories available in 1940 to make pedestrians more visible on the dark street D73.jpg` |
| `b2/trail-of-tears` | `01.jpg` | Sequoyah with his syllabary | `File:Henry Inman - Sequoyah - Google Art Project.jpg` |
| `b2/trail-of-tears` | `02.jpg` | West of the Mississippi, as mapped in 1804. | `File:Map of "Louisiana" by Samuel Lewis, from New and Elegant General Atlas, Philadelphia, 1804.jpg` |
| `c1/america-in-1776` | `02.jpg` | Louis XVI in Coronation Robes | `File:Antoine-François Callet - Louis XVI, roi de France et de Navarre (1754-1793), revêtu du grand costume royal en 1779 - Google Art Project.jpg` |
| `c1/america-in-1776` | `03.jpg` | Scene at the Signing of the Constitution | `File:Scene at the Signing of the Constitution of the United States.jpg` |
| `c1/america-in-1776` | `04.jpg` | Arriving at Ellis Island, around 1900. | `File:Arriving at Ellis Island LCCN97519082.jpg` |
| `c1/apollo-11` | `01.jpg` | Buzz Aldrin on the surface | `File:Aldrin Apollo 11.jpg` |
| `c1/apollo-11` | `02.jpg` | The Laser Ranging Retroreflector, photographed where it was left | `File:AS11-40-5952 - Apollo 11 - Apollo 11 Mission image - The Laser Ranging Retroreflector (LRRR) - NARA - 16685293.jpg` |
| `c1/apollo-11` | `03.jpg` | What Michael Collins saw. | `File:Apollo 11 Lunar Module ascent stage photographed from Command Module.jpg` |
| `c1/haiti` | `01.jpg` | The Daily Times-Advocate, 22 August 1912. | `File:Times-Advocate-Front-Page-1912-08-22.jpg` |
| `c1/haiti` | `02.jpg` | The New York Times newsroom in the 1940s. | `File:Newsroom of the New York Times newspaper. 8d22685v.jpg` |
| `c1/it-management` | `01.jpg` | The Banker and His Wife | `File:Marinus van Reymerswale - The Banker and His Wife - WGA19323.jpg` |
| `c1/it-management` | `03.jpg` | The London Stock Exchange floor, early twentieth century. | `File:Crowd on stock exchange floor, London LCCN2014683111.jpg` |
| `c1/malcolm-x` | `01.jpg` | Malcolm X and Martin Luther King Jr. | `File:MLK and Malcolm X USNWR cropped.jpg` |
| `c1/malcolm-x` | `02.jpg` | Malcolm X | `File:Malcolm X in 1964.jpg` |
| `c1/malcolm-x` | `03.jpg` | The first edition, 1965, published months after his death. | `File:The Autobiography of Malcolm X (1st ed dust jacket cover).jpg` |
| `c1/martin-luther-king` | `01.jpg` | Martin Luther King Jr. at the March on Washington | `File:Civil Rights March on Washington, D.C. (Dr. Martin Luther King, Jr. and Mathew Ahmann in a crowd.) - NARA - 542015 - Restoration.jpg` |
| `c1/martin-luther-king` | `02.jpg` | Fire hoses turned on demonstrators in Birmingham, Alabama | `File:Firemen spraying protestors in Downtown Birmingham 01.jpg` |
| `c1/physiological-stressors` | `01.jpg` | Dorando Pietri at the end of the 1908 Olympic marathon. | `File:Dorando Pietri 1908.jpg` |
| `c1/questionnaire-company-management` | `01.jpg` | The typing office of the Veterans Administration, Washington, 1924. | `File:Typists, Veterans Administration Central Office, Washington DC 20 May 1924.jpg` |
| `c1/questionnaire-company-management` | `02.jpg` | Delegates at a professional forum, half of them on a phone or a laptop. | `File:2024 Agricultural Outlook Forum - Day 2 (20240216-USDA-OSEC-TEW-0940).jpg` |
| `c1/rosa-parks` | `01.jpg` | Rosa Parks fingerprinted by Deputy Sheriff D. H. Lackey | `File:Rosa Parks being fingerprinted by Deputy Sheriff D.H. Lackey after being arrested on February 22, 1956, during the Montgomery bus boycott.jpg` |
| `c1/rosa-parks` | `02.jpg` | Flyer circulated in Montgomery after the court order, 1956 | `File:Montgomery Improvement Association, flyer on bus desegregation, c. 1956 (NYPL).jpg` |
| `c1/rosa-parks` | `03.jpg` | Rosa Parks on a Montgomery bus | `File:Rosa Parks on bus on December 21, 1956.jpg` |
| `c1/shadows-in-the-server-room` | `01.jpg` | The Columbia supercomputer at the NASA Advanced Supercomputing Facility. | `File:Columbia Supercomputer - NASA Advanced Supercomputing Facility.jpg` |
| `c1/shadows-in-the-server-room` | `03.jpg` | A server room the size of a store cupboard. | `File:EFTA00000738 - Cluttered server room filled with racks of equipment cables and power supplies.jpg` |
| `c1/the-cost-of-convenience` | `01.jpg` | The Horn & Hardart Automat, Times Square, around 1939. | `File:Horn & Hardart Times Square New York circa 1939.JPG` |
| `c1/the-cost-of-convenience` | `02.jpg` | The signs say save time, and they are telling the truth. | `File:Billa supermarket, Blagoevgrad centre, self-checkout, 2026.jpg` |
| `c1/the-meeting-problem` | `01.jpg` | An all-hands meeting at NASA's Kennedy Space Center | `File:KSC-20170815-PH KLS01 0079 (36212683960).jpg` |
| `c1/the-meeting-problem` | `02.jpg` | An hour of eight people's time, waiting to be booked. | `File:Small conference room (Unsplash).jpg` |
| `c1/the-night-shift` | `01.jpg` | A ward at night, Guy's Hospital, 1941. | `File:Guy's Hospital- Life in a London Hospital, England, 1941 D2326.jpg` |
| `c1/the-space-race` | `01.jpg` | A full-size replica of Sputnik 1 on display | `File:Sputnik 1.jpg` |
| `c1/the-space-race` | `02.jpg` | Yuri Gagarin | `File:Yuri Gagarin (1961) - Restoration.jpg` |
| `c1/the-space-race` | `03.jpg` | An N1 mockup on the pad at Baikonur, 1967. | `File:N1 1M1 mockup on the launch pad at the Baikonur Cosmodrome in late 1967.jpg` |
| `c1/trials` | `02.jpg` | Darrow questioning Bryan, Dayton, Tennessee, 20 July 1925. | `File:Clarence S. Darrow interrogating William Jennings Bryan, Scopes trial, Dayton, Tennessee, July 20, 1925. (4324506037).jpg` |
| `c1/trials` | `03.jpg` | Twelve chairs and a narrow question. | `File:Jury box in 3rd floor courtroom of the Conway County Courthouse in Morrilton, AR.jpg` |
| `c1/watergate` | `01.jpg` | The Watergate complex, Washington D.C. | `File:WatergateFromAir.JPG` |
| `c1/watergate` | `02.jpg` | Nixon's letter of resignation, 9 August 1974. | `File:Letter of Resignation of Richard M. Nixon, 1974.jpg` |
| `c1/watergate` | `03.jpg` | The Senate Watergate Committee, 1973. | `File:Senate Watergate Hearing.jpg` |
| `c1/women-win-the-vote` | `01.jpg` | Official program for the suffrage procession | `File:Official Program Woman Suffrage Procession - March 3, 1913.jpg` |
| `c1/women-win-the-vote` | `02.jpg` | The Silent Sentinels at the White House gates, 1917. | `File:Suffragists picketing the White House.jpg` |
| `c1/women-win-the-vote` | `03.jpg` | Mott, Stanton and Anthony, carved by Adelaide Johnson. | `File:PortraitMonumentImage01.jpg` |
| `c2/immigration-and-modern-america` | `01.jpg` | The Usual Irish Way of Doing Things | `File:TheUsualIrishWayofDoingThings.jpg` |
| `c2/immigration-and-modern-america` | `02.jpg` | The Chinese Exclusion Act, 1882, in the enrolled original. | `File:Chineseexclusionact.JPG` |
| `c2/immigration-and-modern-america` | `03.jpg` | Johnson signing the 1965 Act, at the foot of the Statue of Liberty. | `File:President Lyndon B. Johnson Signing of the Immigration Act of 1965 (02) - restoration1.jpg` |
| `c2/manifest-destiny` | `01.jpg` | American Progress | `File:American Progress (1872) by John Gast.jpg` |
| `c2/manifest-destiny` | `02.jpg` | The Battle of Buena Vista | `File:Battle of Buena Vista Nebel.jpg` |
| `c2/reconstruction-revolution` | `01.jpg` | One of the data portraits W. | `File:The Georgia Negro LCCN2013650436.jpg` |
| `c2/reconstruction-revolution` | `02.jpg` | Hiram Rhodes Revels | `File:Oil portrait of Hiram Rhodes Revels by Theodor Kaufmann.jpg` |
| `c2/reconstruction-revolution` | `03.jpg` | Worse than Slavery | `File:Worse than Slavery (1874), by Thomas Nast.jpg` |
| `c2/saying-no-without-saying-no` | `02.jpg` | The last session of the Potsdam Conference, 1945. | `File:Last meeting of the Potsdam Conference in Potsdam, Germany. Seated around the conference table, President Harry S.... - NARA - 198951.jpg` |
| `c2/saying-no-without-saying-no` | `03.jpg` | The Tower of Babel | `File:Pieter Bruegel the Elder - The Tower of Babel (Vienna) - Google Art Project - edited.jpg` |
| `c2/slavery-and-the-american-economy` | `01.jpg` | Auction broadside, New Orleans, 14 January 1860. | `File:SlaveAuctionBroadside-1860-01-14.jpg` |
| `c2/slavery-and-the-american-economy` | `02.jpg` | Cotton Merchants in New Orleans | `File:Edgar Degas - Cotton Merchants in New Orleans.jpg` |
| `c2/slavery-and-the-american-economy` | `03.jpg` | The Levee | `File:The levee-New Orleans LCCN2002708517.jpg` |
| `c2/the-american-dream` | `01.jpg` | Toward Los Angeles | `File:Toward Los Angeles, California LOC 3549663710.jpg` |
| `c2/the-american-dream` | `03.jpg` | A new development, photographed for the EPA in the 1970s. | `File:AERIAL OF A NEW HOUSING DEVELOPMENT. SOME 84 PERCENT OF THE RESIDENTS IN THE STATE LIVE WITHIN 30 MILES OF THE COAST... - NARA - 557461.jpg` |
| `c2/the-case-against-plain-english` | `03.jpg` | Terms of sale, Philadelphia, nineteenth century. | `File:(Text page to) Terms and Conditions of Sale of Lots of the Pleasant Hill Land Association, of 23d. Ward. Philadelphia. (IA dr text-page-to-terms-and-conditions-of-sale-of-lots-of-the-pleasant-hill-la-3427008).jpg` |
| `c2/the-second-language-self` | `02.jpg` | A conversation lesson, photographed by Frances Benjamin Johnston around 1900. | `File:Conversation lesson, subject - the chair LCCN2004676659.tif` |
| `c2/the-second-language-self` | `03.jpg` | Interpreters' booths above a UN meeting. | `File:Interpreters' booth at UN peackeeping meeting at UN Headquarters, 2009 (cropped).jpg` |
| `c2/the-west-was-not-empty` | `01.jpg` | Indian Family Alarmed at the Approach of a Prairie Fire | `File:George Catlin - Indian Family Alarmed at the Approach of a Prairie Fire - 1985.66.595 - Smithsonian American Art Museum.jpg` |
| `c2/the-west-was-not-empty` | `03.jpg` | Buffalo Hunt, A Numerous Group | `File:George Catlin - Buffalo Hunt, A Numerous Group.jpg` |
| `c2/what-makes-an-american-hero` | `01.jpg` | Mission Control at the end of Apollo 11 | `File:Mission Operations Control Room at the conclusion of Apollo 11.jpg` |
| `c2/what-makes-an-american-hero` | `02.jpg` | The Minute Man | `File:Minute Man, Daniel Chester French, Concord MA (cropped).jpg` |
| `c2/what-makes-an-american-hero` | `03.jpg` | The March on Washington, 28 August 1963. | `File:View of Crowd at 1963 March on Washington.jpg` |

### Used under a licence that requires credit

70 image(s). The credit is also printed under the picture on
the page itself, which is where the licence requires it to be.

| Page | File | Author | Licence | Source |
|---|---|---|---|---|
| `a1/at-the-store` | `01.jpg` | Harrison Keely | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:The_interior_of_a_Smith%27s_supermarket_in_Las_Vegas,_Nevada.jpg) |
| `a2/restaurant-dialogue` | `01.jpg` | Jim.henderson | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Joe%27s_Pizza_2022_jeh.jpg) |
| `a2/two-small-errands` | `01.jpg` | PattayaPatrol | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:DFC_4093_Assorted_mini_cream-topped_pastries_drizzled_with_fruit_sauce_and_chocolate_ready_to_tempt_at_the_bakery_counter.jpg) |
| `a2/two-very-different-trips` | `02.jpg` | Nawit science | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Temple_of_the_Emerald_Buddha.jpg) |
| `b1/a-day-in-the-office` | `02.jpg` | John M | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:A_snowy_view_out_of_the_office_window_-_geograph.org.uk_-_3300587.jpg) |
| `b1/a-freelance-accounting-assignment` | `02.jpg` | AgnosticPreachersKid | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:22_West_-_home_office.jpg) |
| `b1/arriving-in-johannesburg` | `01.jpg` | Aleph500Adam | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Johannesburg_in_December.jpg) |
| `b1/arriving-in-johannesburg` | `02.jpg` | Nick-D | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Waiting_area_in_Terminal_B_of_OR_Tambo_International_Airport_June_2026.jpg) |
| `b1/beers` | `02.jpg` | Bernt Rostad from Oslo, Norway | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Schouskjelleren_Thunder_Bear_Stout_(5053316703).jpg) |
| `b1/cars-and-their-parts` | `02.jpg` | unknown | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Porsche-gearbox-cutaway.jpg) |
| `b1/cars` | `03.jpg` | CEphoto, Uwe Aranas | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Cologne_Germany_Electric-Car-Charging-Point-at-TUV-Rheinland-01.jpg) |
| `b1/coffee-and-it` | `02.jpg` | Petterin | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Myyr_York_Cafe.jpg) |
| `b1/common-chores` | `02.jpg` | Nick-D | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Aisle_in_Daily_Market_Groceries_Canberra_City_October_2025.jpg) |
| `b1/cybersecurity` | `02.jpg` | Tony Webster from Minneapolis, Minnesota, United States | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Yubikey_USB_2FA_U2F_Security_Token_(46900270791).jpg) |
| `b1/detective-story` | `02.jpg` | Cory Doctorow from London, UK | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:George_Price_strongbox,_Barclays_Bank,_Town,_Beamish_Museum,_25_January_2014_(1).jpg) |
| `b1/frederick-douglass` | `02.jpg` | TradingCardsNPS | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:The_North_Star_(7222833218).jpg) |
| `b1/glamping` | `02.jpg` | Shabicht | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Glamping_hut_Visole_07.jpg) |
| `b1/golden-gate-bridge-present-perfect` | `02.jpg` | Brocken Inaglory | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Golden_Gate_Bridge_at_sunset_1.jpg) |
| `b1/kitchen-chaos` | `02.jpg` | Sarah5252 | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Chopping_Welsh_onion_(Allium_fistulosum)_on_a_wooden_cutting_board.jpg) |
| `b1/milan-restaurants` | `02.jpg` | Gordon Leggett | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:2021-09-04_Fluffy_Clam_Chowder.jpg) |
| `b1/nfl` | `02.jpg` | U.S. Secretary of Defense | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:125th_playing_of_the_Army-Navy_football_game_attended_by_United_States_Secretary_of_Defense_Lloyd_Austin_at_Northwest_Stadium,_Landover,_Maryland_on_December_14,_2024_-_8.jpg) |
| `b1/ny-visitation` | `01.jpg` | Adjoajo | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Autumn_in_Central_Park._NYC.jpg) |
| `b1/ny-visitation` | `02.jpg` | Christian David | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Lower_Manhattan_skyline_and_Brooklyn_Bridge_from_the_East_River,_New_York.jpg) |
| `b1/physical-education` | `02.jpg` | Nwaeke Daniel (Danzisky) | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:School_children_happily_playing_in_playground.jpg) |
| `b1/rio-de-janeiro-exercises` | `01.jpg` | Halley Pacheco de Oliveira | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Floresta_da_Tijuca_60.jpg) |
| `b1/rio-de-janeiro-exercises` | `02.jpg` | Pierre André | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Rio_de_Janeiro_Tijuca_Forest_Cascatinha_Taunay_(1).jpg) |
| `b1/robot-birds` | `02.jpg` | JoeInQueens from Queens, USA | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Feeding_Pigeons_in_Washington_Square_Park.jpg) |
| `b1/santa-catarina` | `01.jpg` | Jeffhollett | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Cannon_Beach_at_Pacific_Coast_in_Oregon_1.jpg) |
| `b1/santa-catarina` | `02.jpg` | Jeffhollett | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Sunset_at_Cannon_Beach_in_Oregon_1.jpg) |
| `b1/southeast-asia-adventure` | `01.jpg` | Satdeep Gill | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Angkor_Wat_with_its_reflection_(cropped).jpg) |
| `b1/southeast-asia-adventure` | `02.jpg` | Vyacheslav Argenberg | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Rice_terraces,_Ubud,_Bali.jpg) |
| `b1/travel-dialogues-02` | `02.jpg` | JIP | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Reception_desk_at_Hotel_Esplanade_in_Stockholm.jpg) |
| `b1/usa-restaurants` | `02.jpg` | Tony Webster from Minneapolis, Minnesota, United States | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Pensacola_Beach_-_White_Sands,_Florida_Coast_(27268946483).jpg) |
| `b1/usa-restaurants` | `03.jpg` | Kramtronik | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Tampa_Cuban_Sandwich.jpg) |
| `b2/business-war-it` | `03.jpg` | Campus Party México | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Kevin_Mitnick_ex_hacker_y_ahora_famoso_consultor_en_redes_en_Campus_Party_M%C3%A9xico_2010.jpg) |
| `b2/describing-a-place` | `02.jpg` | W.carter | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Entrance_in_Torp_shopping_mall,_Uddevalla.jpg) |
| `b2/egypt-a-journey-through-history-and-culture` | `03.jpg` | en:User:Hajor | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Egypt.Giza.Sphinx.01.jpg) |
| `b2/egypt` | `02.jpg` | Vyacheslav Argenberg | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Thebes,_Luxor,_Egypt,_Temple_of_Hatshepsut,_Deir_el-Bahari.jpg) |
| `b2/formal-informal` | `02.jpg` | Shixart1985 | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:In_a_warm_and_inviting_home_office,_a_person_inserts_a_blank_sheet_of_paper_into_a_vintage_typewriter_while_preparing_to_write_a_heartfelt_letter.jpg) |
| `b2/formula-1` | `02.jpg` | Lukas Raich | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:FIA_F1_Austria_2022_Nr._44_Hamilton.jpg) |
| `b2/intelligence-pills` | `02.jpg` | MorgueFile : see [1] | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:VariousPills.jpg) |
| `b2/it-and-jiu-jitsu` | `02.jpg` | parhessiastes | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Brazilian_Jiu-Jitsu_Gi_Competition-Armbar.jpg) |
| `b2/it-interview` | `02.jpg` | Gangulybiswarup | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Audience_Of_Sudeshna_Mukherjee%27s_Talk_On_Gender_Equality_Digital_Rights_And_AI_Ethics_-_WikiConference_India_2026_-_Kochi_2026-09-05_04077.jpg) |
| `b2/north-sentinel-island` | `01.jpg` | Contains modified Copernicus Sentinel data 2022 (ESA) | Attribution | [Commons](https://commons.wikimedia.org/wiki/File:North_Sentinel_Island_2022-03-06_Sentinel-2_L2A_True_color.jpg) |
| `b2/north-sentinel-island` | `02.jpg` | Vyacheslav Argenberg | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Andaman_Islands,_Full_moon_night,_Forest_by_the_sea_at_night.jpg) |
| `b2/phrasal-verbs-01-bed-and-breakfast` | `01.jpg` | Infrogmation of New Orleans | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Mess_at_Home_-_Uptown_New_Orleans_Bedroom_January_1990_01.jpg) |
| `b2/phrasal-verbs-01-bed-and-breakfast` | `02.jpg` | HaJunkiyada | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Liat_Portal_for_Foodie_Disorder_-_Breakfast_in_Israel_scrambled_eggs_with_herbs_and_vegetables.jpg) |
| `b2/recent-advancements-in-it` | `01.jpg` | Carl Lender from Sunrise, USA | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Datacenter_Server_Racks_(22370909788).jpg) |
| `b2/romania` | `03.jpg` | Joe Mabel | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Bucharest_Grand_Hotel_2.jpg) |
| `b2/sales-strategy` | `02.jpg` | Mr. Snatch | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Vendors_selling_goods_in_the_market.jpg) |
| `b2/soma-nomaoi` | `02.jpg` | PekePON | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:The_Soma_Nomaoi_2005-3.jpg) |
| `b2/the-marathon-and-the-wall` | `02.jpg` | U.S. Army | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Joseph_Chirlee_2010.jpg) |
| `c1/it-management` | `02.jpg` | SimonWaldherr | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:CERN_Computer_Center_13.jpg) |
| `c1/physiological-stressors` | `02.jpg` | Shixart1985 | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Runner_pours_water_over_his_head_after_finishing_a_race_in_an_outdoor_setting_during_a_sunny_day.jpg) |
| `c1/physiological-stressors` | `03.jpg` | Riga Marathon | CC BY-SA 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Water_station_Rimi_Riga_Marathon_2021_Van%C5%A1u_bridge.jpg) |
| `c1/real-estate` | `02.jpg` | Quintin Soloviev | CC BY 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Denver,_Colorado_skyline_(cropped).jpg) |
| `c1/real-estate` | `03.jpg` | Jeffrey Beall | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:DenverCountryClubHD.JPG) |
| `c1/rs-japan` | `02.jpg` | FERNANDAQUINTANA1 | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Amanhecer_do_Pampa_Gaucho.JPG) |
| `c1/rs-japan` | `03.jpg` | ccfarmer | CC BY 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Cherry_blossom_viewing_in_Maruyama_Park_-_panoramio.jpg) |
| `c1/shadows-in-the-server-room` | `02.jpg` | Bill Bradford | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Tangled_cables_mrbill.jpg) |
| `c1/shadows-in-the-server-room` | `04.jpg` | Birkenkrahe | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Change_management_whiteboard.jpg) |
| `c1/shadows-in-the-server-room` | `05.jpg` | Jemimus | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:DHL_Netherlands_local_site_computer_room_air_conditioning_unit_and_ductwork_-_IMG_3295.jpg) |
| `c2/saying-no-without-saying-no` | `01.jpg` | UK government | OGL 3 | [Commons](https://commons.wikimedia.org/wiki/File:House_of_Commons_2010.jpg) |
| `c2/the-accent-you-keep` | `02.jpg` | unknown | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Spectrogram_-iua-.png) |
| `c2/the-american-dream` | `02.jpg` | Peter Elfelt | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Assembly_line_Ford_T,_1923.jpg) |
| `c2/the-case-against-plain-english` | `02.jpg` | Blogtrepreneur | CC BY 2.0 | [Commons](https://commons.wikimedia.org/wiki/File:Legal_Contract_%26_Signature_-_Warm_Tones.jpg) |
| `c2/the-same-news-four-ways` | `02.jpg` | AinarsM | CC BY-SA 3.0 | [Commons](https://commons.wikimedia.org/wiki/File:Latvia,_Riga_-_Former_textile_factory_Tekstiliana_(Riga)_WMID2365439.jpg) |
| `c2/the-same-news-four-ways` | `03.jpg` | Helar Lukats | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Whatsapp_texting.jpg) |
| `c2/what-doesnt-translate` | `02.jpg` | Cullen328 | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Compact_Oxford_English_Dictionary_2.jpg) |
| `c2/what-doesnt-translate` | `03.jpg` | JorisEnter | CC BY-SA 4.0 | [Commons](https://commons.wikimedia.org/wiki/File:Asser-serie_UB_Leiden.jpg) |

<!-- gallery:end -->
