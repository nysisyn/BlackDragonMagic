-- BlackDragonMagic, Black Dragon Disciple.
-- The kit's spells (Draconic Transformations, Black Dragon Breaths, reserved
-- spells) are wizard spells: without this file every sorcerer (and every mage
-- at character creation) is offered them. Here they are taken out of the
-- spell choice list unless the character choosing is a Black Dragon Disciple.
-- Called by UI.MENU (menu CHARGEN_CHOOSE_SPELLS, onOpen), before the list is
-- sorted. Technique (rows removed from chargen.choose_spell) from
-- OlvynChuru's ClassSpellTool.

-- the kit's names (strrefs: lower case, mixed case)
ny_bdd_kitNames = { %ny_kit_lower%, %ny_kit_mixed% }

-- the kit's spells (spell resrefs)
ny_bdd_kitSpells = { %ny_kit_spells% }

-- The kit name of the character choosing spells: the class line of the
-- record screen at level-up, the kit picked at character creation.
-- nil when it cannot be told.
function ny_bdd_chooserKitName()
	if chargen.levelingUp then
		if characters ~= nil and currentID ~= nil and characters[currentID] ~= nil then
			return characters[currentID].class
		end
	elseif chargen.kit ~= nil and currentChargenKit ~= nil and chargen.kit[currentChargenKit] ~= nil then
		return Infinity_FetchString(chargen.kit[currentChargenKit].name)
	end
	return nil
end

function ny_bdd_filterSpells()
	local name = ny_bdd_chooserKitName()
	if name == nil then
		return                                  -- unknown: nothing is hidden
	end
	name = string.lower(name)
	for _, strref in ipairs(ny_bdd_kitNames) do
		if name == string.lower(Infinity_FetchString(strref)) then
			return                              -- a disciple: nothing is hidden
		end
	end
	local i = 1
	while i <= #chargen.choose_spell do
		if ny_bdd_kitSpells[string.upper(chargen.choose_spell[i].key)] then
			table.remove(chargen.choose_spell, i)
		else
			i = i + 1
		end
	end
end
