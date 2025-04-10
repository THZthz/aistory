import json
from dataclasses import asdict

import requests

from aistory.interactive.world import World
from waitress import serve

from aistory.db.initialize_step1 import initialize_step1, time_str
from aistory.db.initialize_step2 import initialize_step2
from aistory.db.wikis import get_wiki, get_useful_wikis
from aistory.server.deepseek import get_tool, DeepSeek
from aistory.server.server import app
from aistory.types.character import EChr, MChr, Character
from aistory.types.item import MItem, EItem
from aistory.types.location import ELoc, MLoc

if __name__ == '__main__':
    # initialize_step1()
    # initialize_step2()

    # DeepSeek()

    # print(Character.get_profile_description(EChr.Veyla.value))
    # print()
    # print(Character.get_profile_description(EChr.Ginny.value))
    # print()
    # print(Character.get_items_description(EChr.Veyla.value))
    # print()
    #
    # print(MItem[EItem.RagDoll.value].fullname)
    # print(MItem[EItem.RagDoll.value].description)
    # print(MItem[EItem.RagDoll.value].category)
    # print(MItem[EItem.RagDoll.value].quality)
    # print(MItem[EItem.RagDoll.value].attributes)
    # print()
    #
    # print(MLoc[ELoc.Gallowrest_WestDocks.value].fullname)
    # print(MLoc[ELoc.Gallowrest_WestDocks.value].type)
    # print(MLoc[ELoc.Gallowrest_WestDocks.value].description)
    # print(MLoc[ELoc.Gallowrest_WestDocks.value].path)
    # print()
    #
    # print(get_wiki('Item'))
    #
    # # class = "Item.Equipment.HeadGear.Coverings"
    # print(get_useful_wikis('A threadbare hood of coarse-spun wool, frayed at the edges and bleached by sun and rain. A long rent mars the brim—perhaps from a blade, perhaps from thorns. He does not recall.'))
    #
    # # class = "Item.Equipment.HandGear.Protective"
    # print(get_useful_wikis("Gambler's Gloves: Gloves of black lambskin, worn at the fingertips for nimble theft and cardplay."))
    #
    # print(get_useful_wikis("What is the world like?"))
    #
    # print(get_useful_wikis("The classification of items?"))
    #
    # print(get_useful_wikis("Gambler's Gloves should be classified into which category?"))

    print(time_str() + ' - Prepare to run Flask Server.')
    app.run(port=5000, debug=True)
    pass







