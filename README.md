# This is a project in heavy development


## aistory

Trying to make an interactive fiction world with the power of LLM.

### Deepseek

A large amount of code in the repository is written by Deepseek. However you could not deny my work :D

### Stacks

- Sentence embedding - mGTE: Local deployed, details of how the model is trained can be found in this paper 
[mGTE: Generalized Long-Context Text Representation and Reranking Models for Multilingual Text Retrieval](https://arxiv.org/abs/2407.19669). Model
can be downloaded from [modelscope](https://www.modelscope.cn/models/iic/gte_sentence-embedding_multilingual-base/files).
Note that you will need to install pytorch[cuda] to run it in full speed. You should put the model under folder 
*models/iic_gte_multilingual*.
- Database - PostgreSQL, you need to install **PostgreSQL 16** and create a database named '**aistory**', then install **pgvector** extension.
- Server - **Flask**, written in python, requirements of 3rd party libraries are listed in `requirements.txt`.
- Website - **React**, uses **RSbuild** as building framework. To build, just go to the `website/` folder and run 
`npm install`.

### Our Story happens at the City: Karavelle, A Steampunk Empire Atop the Uhr Mountains

Karavelle is a sprawling steampunk city perched atop the Uhr Mountains, a mechanical colossus with claws sunk into jagged rock, belching coal smoke and steam. Its vast skyline bristles with spires, pipes, and airships, stretching across the horizon as if to grasp the heavens. Furnace roars blend with church bells in a cacophony that echoes through its endless streets, a testament to a city vast enough to cradle boundless ambitions, forbidden loves, fleeting dreams, and the intricate tapestry of human and non-human lives intertwined.

#### Three Tiers
The city sprawls in three concentric tiers—Upper City (Celestial Ring), Middle City (Iron Ring), and Lower City (Ash Ring)—each a world unto itself, yet bound by the mountain’s embrace. Upper and Middle Cities blur in the labyrinthine Cloudbridge District, their gritty steam and machinery sustaining a metropolis that pulses with the weight of countless aspirations.

#### Energy and Infrastructure
At the mountain’s shadowed peak, the Ironthorn Forest looms, its conifers piercing the smog to encircle the hidden Source River. Its waters feed the sprawling Ashsteel Reservoir, cooling the city’s labyrinth of machinery, especially the Giant Furnace buried deep within the mountain. The Wall of Sighs, a colossal network of pipes and vents, hums across the city’s expanse, containing the furnace’s heat and shielding Karavelle’s vastness from collapse.

#### Class Structure and Social Dynamics
Karavelle’s tiered immensity mirrors its hierarchies of power and oppression, yet its sheer scale allows dreams of ascension and ruin to coexist, particularly where Upper and Middle Cities merge in Cloudbridge District.

- **Upper City (Celestial Ring):** Crowned by brass bridges and towers that scrape the clouds, the Celestial Ring sprawls with palaces adorned in intricate carvings, glowing under steam lamps across boundless avenues. Nobles, draped in gem-studded prosthetics, glide in steam carriages, their intrigues as vast as the city itself. Weak air filters battle the smog that blankets this gilded expanse. While Steam Sentinels—armored, steam-driven guards with high-pressure cannons—patrol with immense power, their cumbersome bulk limits their agility. Thus, nobles outwardly honor non-humans, relying on their swift skills in power struggles for protection, all while secretly conducting vile experiments to steal the longevity of elves and vampires, craving their near-eternal lives.
- **Cloudbridge District:** A sprawling transitional zone where noble estates and middle-class mansions tangle in a maze of steam-lit streets. Steam carriages jostle with pedal cycles, reflecting a fragile social mobility that fuels both hope and betrayal in this microcosm of Karavelle’s grandeur.
- **Middle City (Iron Ring):** An industrial sprawl wrapping the mountainside, its cobbled streets and dim steam lamps stretch endlessly past workshops, markets, and austere apartments. Engineers and merchants chase elegance and influence, their dreams dwarfed yet nurtured by the city’s scale.
- **Lower City (Ash Ring):** A smog-choked slum sprawling at the mountain’s base, where shanties house workers, outcasts, and criminals amid sulfurous leaks and clanking prosthetics. Humanity persists in shared soups and children’s games within scrap heaps, but protests vanish in the city’s vast underbelly, silenced by steam whistles and crackdowns.

#### Energy and Lifeblood
Karavelle’s survival hinges on the Giant Furnace, a brass-and-iron titan devouring red coal to power airships and workshops across its immense districts. The Wall of Sighs traps its heat, its spectral hum resonating through the city’s arteries. Coolant from the Source River, channeled via the Ashsteel Reservoir, sustains this inferno, binding Karavelle’s sprawling machinery. The Upper City masks this reliance with claims of divine favor, while the Church exalts the furnace as the “Empire’s Sacred Heart,” a symbol for a city vast enough to harbor both devotion and deceit.

#### Political Structure
Power converges in the Celestial Council, a human-dominated body ruling from the crystalline Crystal Sovereign Tower, its spire piercing Karavelle’s endless skyline. The Grand Chancellor, chosen from elite families, wields the furnace for clan gain, their schemes sprawling across the city’s factions. The Iron Assembly in Middle City, a weaker council, manages trade and tech under the Celestial Council’s shadow, where middle-class and non-humans—vampires, elves, drow—barter secrets to sway the furnace’s keepers. The Ash Ring lies voiceless, its Rustblade rebels lurking in the city’s shadowed fringes. The Church, omnipresent, manipulates all, profiting from black-market coal in a political web as vast as Karavelle itself.

#### Humans and Non-Humans
Non-humans—vampires, elves, drow, werewolves, gnomes, centaurs—thrive and suffer in Karavelle’s immense crucible, where magic fades but diversity endures. Vampires weave coal trades in Upper City, their bloodlust tied to vanishings, unaware of nobles’ experiments targeting their immortality. Elves craft machinery with waning magic, hoarding coal scraps, their long lives coveted in secret labs. Drow broker deals in Ash Ring’s alleys, werewolves toil in mines with simmering rage, gnomes innovate despite scorn, and centaurs haul cargo, their pride broken. Relations fray across the city’s expanse: nobles feign respect for non-humans to secure their prowess in intrigues, Middle City sways between envy and disdain, and Ash Ring harbors both gratitude and fear, all within a metropolis vast enough to hold every shade of alliance and enmity.

#### Magic and Machinery
Magic lingers in red coal, afflicting miners with Coalblight and threatening spellcasters with collapse, yet elves and drow chase its fading glory in hidden corners of the city’s sprawl. Nobles hoard coal for airships and weapons, fueling Karavelle’s might. Steam and brass form its skeleton; red coal machinery blends brute force with industrial power, though explosions and toxic fumes haunt its workshops. Ash Ring rebels scorn this tech, Middle City sees it as a ladder, and Upper City wields it as a crown. The Church condemns magic yet stockpiles coal for “Divine Judicator” constructs. Steam Mechs, hulking red coal war machines piloted by elites, guard Upper City and crush dissent, their clanking steps echoing through Karavelle’s endless streets, yet their ponderous movements necessitate non-human agility for finer conflicts.

#### Transportation
Transport mirrors class across the city’s vastness: Upper City’s brass steam airships soar above, Middle City’s steam railcars rattle on suspended tracks, and Ash Ring’s steam mule carts and centaur wagons creep under Sentinel patrols. Elevators link the tiers—opulent for nobles, sturdy for Middle City, decrepit for Ash Ring—spanning a city so immense that a failed rebel sabotage only scarred a fraction of its Lower City.

#### Entertainment
Karavelle’s scale offers hollow revelries for every tier. Upper City elites indulge in mechanical operas and steam hunts across grand arenas, their spectacles masking their dark experiments. Middle City numbs itself in steam ballrooms and crystal-screen theaters, while pit fights ruin gamblers in hidden dens. Ash Ring finds solace in scrap taverns, where rotgut and makeshift games foster fleeting bonds; non-humans like elves with ballads or gnomes juggling gears brighten these hovels. Church “Redemption Rallies” brainwash workers, and Middle City spies masquerade as performers, all within a city vast enough to host every joy and deception.

#### The City’s Soul
Karavelle is a titan that devours hope yet cradles it in its immensity. The furnace’s glow gilds Upper City excess—where nobles hide their cruel pursuit of eternal life—and Middle City bustle, but reduces Ash Ring to ash across its sprawling slums. The Ironthorn Forest’s vitality is locked behind the Wall of Sighs, a barrier spanning the city’s heart. Noble hypocrisy, cloaked in false respect for non-humans, Middle City lies, and Ash Ring despair churn in steam-choked air, yet Karavelle’s vastness holds room for wild ambitions, clandestine loves, and dreams that flicker in every tier. Human-non-human ties fray, strained by secret experiments and uneasy alliances; magic and machinery spark chaos, and politics conceal cracks while transport and leisure entrench power. Contradictions erupt across its expanse: miners crushed for stealing medicine, artisans sabotaging rivals, nobles bombing slums to quell unrest. The air reeks of sulfur, blood, and betrayal. Steam gears grind humanity to dust, but Karavelle’s sheer scale ensures that the ruthless and resilient find space to endure. This is no mere city—it is a soul-devouring purgatory, vast enough to contain every triumph and tragedy, awaiting the furnace’s final conflagration.