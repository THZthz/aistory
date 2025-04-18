## 生成地点网络
接下来你需要填充两个地点之间的联系，参考之前的wiki_entries.Locations，如有必要，你可以新添地点，但必须要告诉我。JSON范例如下：

```json
{
    "networks": [
        {
            "loc_a": "Locations.HollowLanten",
            "loc_b": "Locations.HollowLanten_GroundFloor",
            "travel_time": 0,
            "description": "Ground floor comprises the tavern's main hall"
        }
    ]
}
```

其中，loc_a和loc_b指的是地理空间上相连的两个地点，它们两个为一组，不用考虑顺序（无向图），travel_time以分钟为单位，指的是从一个地点到另一个地点之间的最少旅行时间，description是对这两个相连地点的描述，描述要客观，并保证信息丰富。此外，你还需要注意不要添加不必要的连系，如Hollow Lantern内的第一楼只需和Locations.HollowLanten和Locations.HollowLanten_SecondFloor以及Locations.HollowLanten_Cellar相连，外部的连系则有Locations.HollowLanten负责

## Generate Locations
List locations which is within Karavelle {modifiers}.

------------------------------------------

This is the classfication hierachy tree of city space:

```text
{cityspace_classfication}
```

------------------------------------------

Output Template:
```markdown
#### ... (location's ID, should be unqiue, can be prefixed)
- name: ... (name of the location)
- type: ... (e.g. if the location is 'Steamways', then its type should be 'City.Infrastructure.Steamways', write the whole hierachy)
- description: ... (detailed introduction)
```

## Generate Locations JSON
Task: You are required to comprehensively list locations within Karavelle, 
systematically categorizing them into "tiers", "infrastructure", "zones", "structures", and "spaces". 
Additionally, you must populate "flat_hierarchies" with the direct sub-categories of 
each location classification.

------------------------------------------

This is the introduction of city Karavelle:

```markdown
{karavelle_introduction}
```

------------------------------------------

This is the classfication hierachy tree of city space:

```text
{cityspace_classfication}
```

------------------------------------------

This is the template of output:

```json
{
    "name": "Karavelle",
    "type": "city",
    "tiers": [
        "CelestialRing",
        ...
    ],
    "infrastructure": [
        "WallOfSighs",
        ...
    ],
    "zones": [
        ...
    ],
    "structures": [
        ...
    ],
    "spaces": [
        ...
    ],
  
    "flat_hierachies": {
      "Karavelle": ["CelestialRing", ...],
      "CelestialRing": ["CelestialCouncil", ...],
      ...
    }
}
```

------------------------------------------

Pay Attention:
1) "CelestialRing", "CelestialCouncil" and similar terms are unique location IDs and cannot be duplicated;
2) 

## Generate Items
This is the profile of {profile_owner}:

{profile_content}

------------------------------------------

This is the item's classfication hierachy tree:

{items_classfication}

------------------------------------------

Invent what items will {profile_owner} carry and wear? You don't need to cover all categories. 
Each item should have its name (unique), quality (common/uncommon/rare/exquisite/legendary),
a description (description must be objective, avoiding the owner's subjective emotions, and should focus on the item's physical appearance, with minimal speculative interpretation based on its exterior)
and a category (e.g. if an item is a 'LegGear', its category should be 'Item.Equipment.WearableGear.LegGear', write the whole hierachy).

This is the example format for one single item:

```markdown
## ... (item's name)
quality: ...
category: ...
description: ...
```
