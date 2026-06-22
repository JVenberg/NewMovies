# Backtest: non-English relevance heuristics, 2025-12-21 to 2026-06-21

Universe: non-English films with an in-window US digital/physical release that **already pass `MIN_POPULARITY=10`** (the digest's first gate). Both heuristics only act on this set.

- **Heuristic 1 - vote-count floor:** keep if `vote_count >= 50`
- **Heuristic 2 - pop/votes ratio cap:** keep if `vote_count > 0` and `popularity/vote_count <= 3`  (this is the one currently wired in)

Non-English films in scope: **25**. Floor keeps **16**, ratio keeps **20**. They disagree on **6**.

| Title | Lang | Pop | Votes | Ratio | Rating | Floor>=50 | Ratio<=3 |
|---|---|--:|--:|--:|--:|:--:|:--:|
| Karuppu | Tamil | 271.0 | 18 | 15.1 | 6.7 | drop | drop |
| Bhooth Bangla | Hindi | 378.9 | 31 | 12.2 | 5.4 | drop | drop |
| Husbands in Action | Korean | 121.4 | 17 | 7.1 | 6.7 | drop | drop |
| Maa Behen | Hindi | 56.5 | 10 | 5.6 | 6.7 | drop | drop |
| Your Heart Will Be Broken | Russian | 299.4 | 98 | 3.1 | 7.0 | keep | drop | **DIFF**
| Kara | Tamil | 44.4 | 23 | 1.9 | 6.0 | drop | keep | **DIFF**
| Milky☆Subway: The Galactic Limited Express - the Movie | Japanese | 27.5 | 26 | 1.1 | 9.3 | drop | keep | **DIFF**
| Kartavya | Hindi | 20.1 | 19 | 1.1 | 6.5 | drop | keep | **DIFF**
| Dhurandhar: The Revenge | Hindi | 120.6 | 121 | 1.0 | 7.3 | keep | keep |
| Colors of Evil: Black | Polish | 42.6 | 83 | 0.5 | 7.0 | keep | keep |
| Toaster | Hindi | 11.6 | 27 | 0.4 | 5.8 | drop | keep | **DIFF**
| The Marked Woman | Spanish | 27.9 | 73 | 0.4 | 5.5 | keep | keep |
| Tu Yaa Main | Hindi | 13.0 | 49 | 0.3 | 6.4 | drop | keep | **DIFF**
| Mexico 86 | Spanish | 19.6 | 80 | 0.2 | 7.6 | keep | keep |
| Kraken | Norwegian | 34.9 | 164 | 0.2 | 6.4 | keep | keep |
| Dhurandhar | Hindi | 63.1 | 308 | 0.2 | 7.2 | keep | keep |
| The Legend of Hei 2 | Chinese | 11.8 | 59 | 0.2 | 8.5 | keep | keep |
| My Dearest Assassin | Thai | 40.8 | 248 | 0.2 | 8.7 | keep | keep |
| Vengeance | Spanish | 40.8 | 259 | 0.2 | 7.5 | keep | keep |
| I Am Frankelda | Spanish | 11.9 | 93 | 0.1 | 8.3 | keep | keep |
| Humint | Korean | 15.5 | 150 | 0.1 | 7.5 | keep | keep |
| The Last Viking | Danish | 14.2 | 140 | 0.1 | 7.2 | keep | keep |
| Accidental Partners | Spanish | 21.6 | 273 | 0.1 | 9.1 | keep | keep |
| The Tank | German | 11.2 | 443 | 0.0 | 7.1 | keep | keep |
| No Other Choice | Korean | 10.2 | 1106 | 0.0 | 7.5 | keep | keep |

## Where they disagree (the cases that matter)

### Floor KEEPS, ratio DROPS  (1)
_Films with few votes but a *low* pop/votes ratio (not regionally spiked). Ratio lets these through; the floor cuts them._

- **Your Heart Will Be Broken** (Russian) - pop 299.4, votes 98, ratio 3.1, rating 7.0  
  High school student Polina is saved from bullying at her new school and makes a deal with the main bully Bars: he must pretend to be her boyfriend and protect her, and she must do everything he says. During this game, the couple develops real feelings, but…

### Ratio KEEPS, floor DROPS  (5)
_Films the floor would cut for low votes, but ratio keeps because popularity is proportionate (watched, just niche)._

- **Kara** (Tamil) - pop 44.4, votes 23, ratio 1.9, rating 6.0  
  A thief tries to go straight, but when predatory banks trap his father in debt, he returns to crime — with a determined cop closing in on his trail.
- **Milky☆Subway: The Galactic Limited Express - the Movie** (Japanese) - pop 27.5, votes 26, ratio 1.1, rating 9.3  
  Six delinquents are tasked with cleaning a train as part of a community service program. But when the train suddenly takes off, chaos ensues.
- **Kartavya** (Hindi) - pop 20.1, votes 19, ratio 1.1, rating 6.5  
  With his family's safety at stake and menacing threats closing in, a police officer must decide how far he'll go to uphold his duty.
- **Toaster** (Hindi) - pop 11.6, votes 27, ratio 0.4, rating 5.8  
  Murder and chaos erupt when a miser becomes obsessed with a toaster he gave as a wedding gift.
- **Tu Yaa Main** (Hindi) - pop 13.0, votes 49, ratio 0.3, rating 6.4  
  A wannabe rapper from the outskirts of Mumbai and an affluent influencer elope to a coastal town, only to find themselves trapped in the pool of a derelict resort fighting for survival against the wrath of a ferocious crocodile.

## Both DROP  (4) - the regional spikes we want gone

- **Karuppu** (Tamil) - pop 271.0, votes 18, ratio 15.1, rating 6.7  
  In a world where justice falters, guardian deity Vettai Karuppu takes the guise of a lawyer to battle a corrupt legal system preying on the powerless.
- **Bhooth Bangla** (Hindi) - pop 378.9, votes 31, ratio 12.2, rating 5.4  
  A man inherits a palace in rural Mangalpur and plans his sister's wedding there, but strange supernatural events and panicked locals force him to investigate the property's mysterious past.
- **Husbands in Action** (Korean) - pop 121.4, votes 17, ratio 7.1, rating 6.7  
  A detective teams up with his ex-wife's new husband to chase down her kidnappers. Can this unlikely duo put aside their differences for one wild rescue?
- **Maa Behen** (Hindi) - pop 56.5, votes 10, ratio 5.6, rating 6.7  
  In this dark comedy, a woman calls her estranged daughters in the middle of the night with chilling news — there's a dead body in her kitchen.

## Both KEEP  (15) - the foreign films we want to surface

- **Dhurandhar: The Revenge** (Hindi) - pop 120.6, votes 121, ratio 1.0, rating 7.3  
  As rival gangs, corrupt officials and a ruthless Major Iqbal close in, Hamza's mission for his country spirals into a bloody personal war where the line between patriot and monster disappears in the streets of Lyari.
- **Colors of Evil: Black** (Polish) - pop 42.6, votes 83, ratio 0.5, rating 7.0  
  Investigating the disappearance of children in a remote Polish town, prosecutor Leopold Bilski must unravel a sinister local legend before it's too late.
- **The Marked Woman** (Spanish) - pop 27.9, votes 73, ratio 0.4, rating 5.5  
  When a woman is found in a shipping container with no memory of who she is, two detectives race to figure out her identity — and who wants her dead.
- **Mexico 86** (Spanish) - pop 19.6, votes 80, ratio 0.2, rating 7.6  
  When a last-minute chance to host the 1986 World Cup appears, a cunning Mexican bureaucrat, armed with nothing but guts and audacity, cons his way through FIFA to beat the United States, but in a country of power games, every victory has a price.
- **Kraken** (Norwegian) - pop 34.9, votes 164, ratio 0.2, rating 6.4  
  A marine biologist is doing research on a fish farm when she encounters several strange occurrences. Along with the brutal deaths of two teenagers, all signs point to the deep fjord; can there be more to the depths than the eye can see?
- **Dhurandhar** (Hindi) - pop 63.1, votes 308, ratio 0.2, rating 7.2  
  A mysterious traveler slips into the heart of Karachi's underbelly and rises through its ranks with lethal precision, only to tear the notorious ISI-Underworld nexus apart from within.
- **The Legend of Hei 2** (Chinese) - pop 11.8, votes 59, ratio 0.2, rating 8.5  
  When an attack shatters the fragile peace between the spirit world and humanity, Hei teams up with Luye, the last disciple of his Shifu Wuxian, to expose a conspiracy that threatens both realms - and the bond they've sworn to protect.
- **My Dearest Assassin** (Thai) - pop 40.8, votes 248, ratio 0.2, rating 8.7  
  Hunted for her rare blood type, a caged woman vows to fight alongside the assassin she loves to protect their future when an old enemy resurfaces.
- **Vengeance** (Spanish) - pop 40.8, votes 259, ratio 0.2, rating 7.5  
  The brutal murder of the wife of “Toro,” a military hero in the special forces, turns him into a man with a single purpose: revenge. After a stroke of fate makes him a millionaire, Carlos transforms his fortune into an arsenal and, together with his closest…
- **I Am Frankelda** (Spanish) - pop 11.9, votes 93, ratio 0.1, rating 8.3  
  A gifted young writer in 19th-century Mexico journeys into her subconscious and comes face to face with characters from her own spooky stories.
- **Humint** (Korean) - pop 15.5, votes 150, ratio 0.1, rating 7.5  
  A South Korean agent hunts a drug ring in Russia and goes head-to-head with a North Korean operative — pulling both into peril and tangled secrets.
- **The Last Viking** (Danish) - pop 14.2, votes 140, ratio 0.1, rating 7.2  
  After serving fourteen years for robbery, Anker is released from prison and reunites with his mentally ill brother Manfred, who alone knows where the stolen money is hidden but has forgotten its location, sending them on a journey to recover the loot and…
- **Accidental Partners** (Spanish) - pop 21.6, votes 273, ratio 0.1, rating 9.1  
  Two women discover they were both scammed by the same man (who also got them pregnant). They form an alliance to take revenge.
- **The Tank** (German) - pop 11.2, votes 443, ratio 0.0, rating 7.1  
  A German Tiger tank crew is sent on a dangerous mission to rescue the missing officer Paul von Hardenburg from a top-secret bunker behind enemy lines. As they make their way through the lethal no-man's land, they must confront not only the enemy, but also…
- **No Other Choice** (Korean) - pop 10.2, votes 1106, ratio 0.0, rating 7.5  
  After being laid off and humiliated by a ruthless job market, a veteran paper mill manager descends into violence in a desperate bid to reclaim his dignity.
