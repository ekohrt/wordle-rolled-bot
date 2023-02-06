# TODO: Tera Types
# TODO: handle skill swap, simple beam, etc.
# |-activate|p2a: Iron Thorns|ability: Quark Drive|[fromitem]    --> Quark Drive ability && Booster Energy item
# |-curestatus|p2a: Altaria|par|[from] ability: Natural Cure
# |-item|p1a: Arboliva|Sitrus Berry|[from] ability: Harvest
import re
import requests

# Source: https://github.com/ndhhhk/ndhhhk.github.io/blob/master/js/PokemonShowdownReplayParser.js
class PokemonShowdownReplayParser:

  # constructor
  def __init__(self, log_text):
    # data = requests.get(replay_url+'.log')
    self.log = log_text
    self.players = {"p1": Player("p1"), "p2": Player("p2")}
    
  # run the parse, return formatted team string
  def run(self):
    self.parse()
    return self.players["p1"].getTeamFormatString() + self.players["p2"].getTeamFormatString()
  
  # loop over lines, extract information and save to local variables
  def parse(self):

    # get starting pokemon (handle the first 'switch' tags after 'start')
    for line in self.log.split('|start\n')[1].split('\n'):
      if line.startswith('|switch|'): 
        self.processSwitch(line)
      else:
        break
    
    # begin processing every line
    lines = self.log.split('\n');
    for line in lines:
      if line.startswith("|player|"):
        self.processPlayer(line);
      elif line.startswith("|poke|"):
        self.processPoke(line);
      elif line.startswith("|move|"):
        self.processMove(line)
      elif line.startswith("|-ability|"):
        self.processAbility(line)
      elif line.startswith("|switch|"):
        self.processSwitch(line)
      elif line.startswith("|drag|"):
        self.processDrag(line)
      elif line.startswith("|-mega|"):
        self.processMega(line)
      elif line.startswith("|detailschange|"):
        self.processDetailsChange(line)
      # elif line.startswith("|-item|"):
      #   self.processItem(line)
      elif line.startswith("|-enditem|"):
        self.processEndItem(line)
      elif line.startswith("|faint|"):
        self.processFaint(line)
      elif "|[from] move:" in line:
        if line.startswith("|-item|"):
          # self.processItemFromMove(line)
          pass
      elif "|[from] item:" in line:
        # leftovers
        if line.startswith("|-heal|"):
          self.processHealFromItem(line);
        elif line.startswith("|-damage|"):
          self.processDamageFromItem(line)
      elif "[from] ability: " in line:
        if line.startswith("|-weather|"):
          self.processWeatherFromAbility(line);
        elif line.startswith("|-fieldstart|"):
          self.processTerrainFromAbility(line)
      else:
        tags = ["|J|", "|j|", "|L|", "|l|", "|inactive|", "|choice|", "|seed|", "|rated",
                "|upkeep", "|-resisted|", "|gametype|", "|gen|", "|tier|", "|-miss|", 
                "|clearpoke", "|teampreview", "|c|", "|rule|", "|turn|", "|-sidestart|", 
                "|-start|", "|-damage|", "|-fail|", "|-activate|", "|-boost|", "|start", 
                "|win|", "|-supereffective|", "|-crit|", "|-end|", "|-singleturn|",
                "|-message|", "|cant|", "|-status|", "|-unboost|", "|-terastallize|", 
                '|teamsize|', '|-sideend|', '|-immune|', '|t:|', '|raw|']
        if any([line.startswith(x) for x in tags]) or line == "|":
          pass
        else:
          # print(line)
          pass
  
  def processPlayer(self, line):
    fields = line.split("|")
    if len(fields) >= 4:
      self.players[fields[2]].username = fields[3]
  
  # TODO: get level and gender?
  # |poke|p1|Talonflame, L50, M|
  def processPoke(self, line):
    fields = line.split("|")
    player = fields[2]
    species = fields[3].split(',')[0] 
    pokemon = self.players[player].getPokemonBySpecies(species)
    if pokemon == None:
      pokemon = Pokemon(species=species)
      self.players[player].pokemon.append(pokemon) 
  
  # |switch|PLAYER+POSITION: NICKNAME|NAME
  # |switch|p1a: whynofeathers|Aerodactyl, F|100/100
  def processSwitch(self, line):
    matches = re.match('\|switch\|(p[12])([abc]):\s+([^|]+)\|([^,|]+)', line)
    player = matches.group(1)
    position = matches.group(2) # a b or c
    nickname = matches.group(3)
    species = matches.group(4)
    # set new current pokemon - if not yet tracked, add new to list. don't think this will ever happen but idk.
    pokemon = self.players[player].getPokemonBySpecies(species)
    if pokemon == None:
      pokemon = Pokemon(species=species)
      self.players[player].pokemon.append(pokemon) 
    pokemon.nickname = nickname
    self.players[player].active_pokemon[position] = pokemon
  
  # |move|SOURCE_PLAYER: NICKNAME|MOVE|TARGET_PLAYER: NICKNAME
	# |move|p1a: BigFloppah|Ice Beam|p2a: PikaChooChoo
  def processMove(self, line):
    matches = re.match('\|move\|(p[12])[abc]:\s+([^|]+)\|([^|]+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    move = matches.group(3)
    # skip all G-Max moves
    if 'G-Max' in move:   
      return 
    pokemon = self.players[player].getPokemonByNickname(nickname)
    pokemon.moves.add(move) # TODO: why?? just use a set instead of dict
    # 'Trick'
    if move in {'Trick', 'Switcheroo'}:
      self.handleTrickMove(line)
  
  # |-ability|p1a: Landorus|Intimidate|boost
  def processAbility(self, line):
    matches = re.match('\|-ability\|(p[12])[abc]:\s+([^|]+)\|([^|]+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    ability = matches.group(3)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    pokemon.ability = ability

  # |-mega|p2a: PlantyMcPlantFace|Venusaur|Venusaurite
  def processMega(self, line):
    matches = re.match('\|-mega\|(p[12])[abc]:\s+([^|]+)\|([^|]+)\|(.+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    # species = matches.group(3)
    megastone = matches.group(4)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    if pokemon.item == "": pokemon.item = megastone
  
  # |detailschange|p1a: fireDragon|Charizard-Mega-Y, M
  def processDetailsChange(self, line):
    matches = re.match('\|detailschange\|(p[12])[abc]:\s+([^|]+)\|([^,]+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    species = matches.group(3)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    pokemon.species = species
  
  # just set that active_pokemon slot to None
  # |faint|p1a: BestNicknameEver
  def processFaint(self, line):
    matches = re.match('\|faint\|(p[12])([abc]): (.+)', line)
    player = matches.group(1)
    position = matches.group(2)
    self.players[player].active_pokemon[position] = None

  # handles when items break / are eaten / use 'Fling' move
  # |-enditem|p1a: Greninja|Focus Sash
  def processEndItem(self, line):
    matches = re.match('\|-enditem\|(p[12])[abc]:\s+([^|]+)\|([^|]+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    item = matches.group(3)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    if pokemon.item == "": pokemon.item = item

  # -heal|p1a: Gothitelle|135/343|[from] item: Leftovers
  def processHealFromItem(self, line):
    matches = re.match('\|-heal\|(p[12])[abc]:\s+([^|]+)\|[^|]+\|\[from\] item: (.+)', line)
    player = matches.group(1)
    nickname = matches.group(2)
    item = matches.group(3)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    if pokemon.item == "": pokemon.item = item

  # |-damage|p2a: Maushold|84/100 tox|[from] item: Rocky Helmet|[of] p1a: Grafaiai   # https://replay.pokemonshowdown.com/gen91v1-1715469091.log
  # |-damage|p1a: Gallade|88/249|[from] item: Life Orb
  def processDamageFromItem(self, line):
    ms = re.match('\|-damage\|(p[12])([abc]): ([^|]+)\|[^|]+\|\[from\] item: ([^|]+)', line)
    damaged_player, damaged_position, damaged_nickname = ms.group(1), ms.group(2), ms.group(3)
    item = ms.group(4)
    damaged_pokemon = self.players[damaged_player].active_pokemon[damaged_position]
    
    # if the line contains "[of]" then assign item to that other pkmn; otherwise assign to damaged pkmn.
    splits = line.split('|[of] ')
    if len(splits) > 1:
      matches = re.match('(p[12])([abc])', splits[1])
      player, position = matches.group(1), matches.group(2)
      pokemon = self.players[player].active_pokemon[position]
      if pokemon.item == "": pokemon.item = item
    else:
      if damaged_pokemon.item == "": damaged_pokemon.item = item

  
  # |-weather|SunnyDay|[from] ability: Drought|[of] p1a: Sagittarius
  def processWeatherFromAbility(self, line):
    matches = re.match('\|-weather\|[^|]+\|\[from\] ability: ([^|]+)\|\[of\] (p[12])[abc]: (.+)', line)
    ability, player, nickname = matches.group(1), matches.group(2), matches.group(3)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    pokemon.ability = ability

  def processTerrainFromAbility(self, line):
    matches = re.match('\|-fieldstart\|move: [^|]+\|\[from\] ability: ([^|]+)\|\[of\] (p[12])([abc]): ([^|]+)', line)
    ability, player, position, nickname = matches.group(1), matches.group(2), matches.group(3), matches.group(4)
    pokemon = self.players[player].getPokemonByNickname(nickname)
    pokemon.ability = ability

  # https://replay.pokemonshowdown.com/gen8vgc2021-1758502605.log
  # |move|p2a: Call Me|Trick|p1b: CoalyBoi
  # |-activate|p2a: Call Me|move: Trick|[of] p1b: CoalyBoi
  # |-item|p1b: CoalyBoi|Eject Button|[from] move: Trick
  # |-item|p2a: Call Me|Assault Vest|[from] move: Trick
  def handleTrickMove(self, line):
    # find the line where the move happens (trick or switcheroo), grab the next 3 lines: 
    searchlines = self.log.split(line+'\n')[1].split('\n')[:3] # janky but idc
    activate_line = searchlines[0]
    item_line_1 = searchlines[1]
    item_line_2 = searchlines[2]
    
    # get source and target pokemon
    ms = re.match('\|-activate\|(p[12])([abc]): (.+)\|move: (.+)\|\[of\] (p[12])([abc]): (.+)', activate_line)
    source_player, source_position = ms.group(1), ms.group(2)
    target_player, target_position = ms.group(5), ms.group(6)
    source_pokemon = self.players[source_player].active_pokemon[source_position]
    target_pokemon = self.players[target_player].active_pokemon[target_position]

    for searchline in (searchlines[1], searchlines[2]):
      matches = re.match('\|-item\|(p[12])([abc]):\s+([^|]+)\|([^|]+)', searchline)
      player, position, item_received = matches.group(1), matches.group(2), matches.group(4)
      this_pokemon = self.players[player].active_pokemon[position]
      # whatever pokemon this is, the item came from the other pokemon.
      other_pokemon = source_pokemon if this_pokemon is target_pokemon else target_pokemon
      if other_pokemon.item == "": 
        other_pokemon.item = item_received

class Player:
  def __init__(self, player_name):
    self.name = player_name
    self.username = ""
    self.pokemon = []
    self.active_pokemon = {'a': None, 'b': None}

  def getPokemonBySpecies(self, species):
    for p in self.pokemon:
      if p.species == species:
        return p
    return None;

  def getPokemonByNickname(self, nickname):
    for p in self.pokemon:
      if p.nickname == nickname:
        return p
    return None

  def getTeamFormatString(self):
    output = "-------------------------\n";
    output += "Player: "+self.username+"\n";
    output += "-------------------------\n";
    for p in self.pokemon:
      output += p.getTeamFormatString() + "\n";
    return output;


class Pokemon:
  def __init__(self, species="", nickname=""):
    self.species = species;
    self.nickname = nickname;
    self.item = ""; # never update this if it has a value.
    # self.nature = "";
    self.ability = "";
    self.moves = set();

  def getTeamFormatString(self):
    name = self.nickname if self.nickname != "" else self.species
    item = f'@ {self.item}' if self.item != "" else ""
    s = f"{name} ({self.species}) {item} \n"
    s += f"Ability: {self.ability}\n"
    for move in self.moves:
      s += f"- {move}\n";
    return s;
  
  def __str__(self):
    return self.getTeamFormatString()