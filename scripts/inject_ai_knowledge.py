import json

ai_knowledge = {
    # Spain
    'Unai Simón': 'GK', 'Dani Carvajal': 'RB', 'Jesús Navas': 'RB', 'Robin Le Normand': 'RCB', 
    'Aymeric Laporte': 'LCB', 'Nacho': 'CB', 'Pau Torres': 'CB', 'Pau Cubarsí': 'CB', 
    'Marc Cucurella': 'LB', 'Alejandro Grimaldo': 'LB', 'Rodri': 'CDM', 'Martín Zubimendi': 'CDM', 
    'Fabián Ruiz': 'CM', 'Mikel Merino': 'CM', 'Pedri': 'CM', 'Gavi': 'CM', 
    'Lamine Yamal': 'RW', 'Ferran Torres': 'RW', 'Nico Williams': 'LW', 'Mikel Oyarzabal': 'LW', 
    'Dani Olmo': 'CAM', 'Álvaro Morata': 'ST', 'Joselu': 'ST',

    # France
    'Mike Maignan': 'GK', 'Jules Koundé': 'RB', 'Jonathan Clauss': 'RB', 'Dayot Upamecano': 'RCB', 
    'William Saliba': 'LCB', 'Ibrahima Konaté': 'CB', 'Benjamin Pavard': 'CB', 
    'Theo Hernández': 'LB', 'Ferland Mendy': 'LB', 'Aurélien Tchouaméni': 'CDM', "N'Golo Kanté": 'CDM', 
    'Eduardo Camavinga': 'CM', 'Adrien Rabiot': 'CM', 'Youssouf Fofana': 'CM', 
    'Ousmane Dembélé': 'RW', 'Kingsley Coman': 'RW', 'Kylian Mbappé': 'ST', 'Marcus Thuram': 'ST', 
    'Olivier Giroud': 'ST', 'Antoine Griezmann': 'CAM', 'Bradley Barcola': 'LW',

    # Brazil
    'Alisson': 'GK', 'Ederson': 'GK', 'Danilo': 'RB', 'Yan Couto': 'RB', 
    'Marquinhos': 'RCB', 'Gabriel Magalhães': 'LCB', 'Éder Militão': 'CB', 'Bremer': 'CB', 
    'Wendell': 'LB', 'Guilherme Arana': 'LB', 'Casemiro': 'CDM', 'João Gomes': 'CDM', 'Douglas Luiz': 'CM', 
    'Bruno Guimarães': 'CM', 'Lucas Paquetá': 'CAM', 'Andreas Pereira': 'CAM', 
    'Raphinha': 'RW', 'Rodrygo': 'ST', 'Vinícius Júnior': 'LW', 'Gabriel Martinelli': 'LW', 'Endrick': 'ST',

    # England
    'Jordan Pickford': 'GK', 'Kyle Walker': 'RB', 'Trent Alexander-Arnold': 'RB', 'Kieran Trippier': 'RB', 
    'John Stones': 'RCB', 'Marc Guéhi': 'LCB', 'Harry Maguire': 'CB', 'Ezri Konsa': 'CB', 
    'Luke Shaw': 'LB', 'Ben Chilwell': 'LB', 'Declan Rice': 'CDM', 'Kobbie Mainoo': 'CM', 
    'Conor Gallagher': 'CM', 'Jude Bellingham': 'CAM', 'Phil Foden': 'LW', 'Jack Grealish': 'LW', 
    'Bukayo Saka': 'RW', 'Cole Palmer': 'RW', 'Harry Kane': 'ST', 'Ollie Watkins': 'ST', 'Ivan Toney': 'ST',

    # Portugal
    'Diogo Costa': 'GK', 'João Cancelo': 'RB', 'Diogo Dalot': 'RB', 'Rúben Dias': 'LCB', 
    'Pepe': 'RCB', 'Gonçalo Inácio': 'CB', 'António Silva': 'CB', 'Nuno Mendes': 'LB', 
    'João Palhinha': 'CDM', 'Rúben Neves': 'CDM', 'Vitinha': 'CM', 'Matheus Nunes': 'CM', 
    'Bruno Fernandes': 'CAM', 'Bernardo Silva': 'RW', 'Francisco Conceição': 'RW', 
    'Rafael Leão': 'LW', 'João Félix': 'LW', 'Cristiano Ronaldo': 'ST', 'Gonçalo Ramos': 'ST',

    # Germany
    'Manuel Neuer': 'GK', 'Marc-André ter Stegen': 'GK', 'Joshua Kimmich': 'RB', 'Benjamin Henrichs': 'RB', 
    'Antonio Rüdiger': 'RCB', 'Jonathan Tah': 'LCB', 'Nico Schlotterbeck': 'CB', 'Waldemar Anton': 'CB', 
    'Maximilian Mittelstädt': 'LB', 'David Raum': 'LB', 'Robert Andrich': 'CDM', 'Pascal Groß': 'CM', 
    'Toni Kroos': 'CM', 'Ilkay Gündogan': 'CAM', 'Jamal Musiala': 'CAM', 'Florian Wirtz': 'CAM', 
    'Leroy Sané': 'RW', 'Kai Havertz': 'ST', 'Niclas Füllkrug': 'ST', 'Thomas Müller': 'ST',

    # Uruguay
    'Sergio Rochet': 'GK', 'Nahitan Nández': 'RB', 'Guillermo Varela': 'RB', 
    'Ronald Araujo': 'RCB', 'José María Giménez': 'LCB', 'Mathías Olivera': 'CB', 'Sebastián Cáceres': 'CB', 
    'Matías Viña': 'LB', 'Lucas Olaza': 'LB', 'Manuel Ugarte': 'CDM', 'Rodrigo Bentancur': 'CM', 
    'Federico Valverde': 'CM', 'Nicolás de la Cruz': 'CAM', 'Giorgian de Arrascaeta': 'CAM', 
    'Facundo Pellistri': 'RW', 'Maximiliano Araújo': 'LW', 'Darwin Núñez': 'ST', 'Luis Suárez': 'ST',
    
    # Netherlands
    'Bart Verbruggen': 'GK', 'Denzel Dumfries': 'RWB', 'Jeremie Frimpong': 'RWB', 
    'Stefan de Vrij': 'RCB', 'Virgil van Dijk': 'CB', 'Nathan Aké': 'LCB', 'Matthijs de Ligt': 'CB', 
    'Micky van de Ven': 'LB', 'Daley Blind': 'LB', 'Jerdy Schouten': 'CDM', 'Tijjani Reijnders': 'CM', 
    'Joey Veerman': 'CM', 'Georginio Wijnaldum': 'CAM', 'Xavi Simons': 'CAM', 
    'Cody Gakpo': 'LW', 'Donyell Malen': 'RW', 'Steven Bergwijn': 'LW', 'Memphis Depay': 'ST', 'Wout Weghorst': 'ST',
    
    # Italy
    'Gianluigi Donnarumma': 'GK', 'Giovanni Di Lorenzo': 'RB', 'Matteo Darmian': 'RWB', 
    'Alessandro Bastoni': 'LCB', 'Riccardo Calafiori': 'CB', 'Gianluca Mancini': 'RCB', 'Alessandro Buongiorno': 'CB', 
    'Federico Dimarco': 'LWB', 'Andrea Cambiaso': 'LB', 'Jorginho': 'CDM', 'Nicolò Barella': 'CM', 
    'Davide Frattesi': 'CM', 'Bryan Cristante': 'CM', 'Lorenzo Pellegrini': 'CAM', 
    'Federico Chiesa': 'RW', 'Mattia Zaccagni': 'LW', 'Gianluca Scamacca': 'ST', 'Mateo Retegui': 'ST',

    # Belgium
    'Koen Casteels': 'GK', 'Timothy Castagne': 'RB', 'Wout Faes': 'RCB', 'Jan Vertonghen': 'LCB', 
    'Zeno Debast': 'CB', 'Arthur Theate': 'LB', 'Amadou Onana': 'CDM', 'Orel Mangala': 'CDM', 
    'Youri Tielemans': 'CM', 'Kevin De Bruyne': 'CAM', 'Leandro Trossard': 'LW', 
    'Jérémy Doku': 'RW', 'Johan Bakayoko': 'RW', 'Romelu Lukaku': 'ST', 'Loïs Openda': 'ST',

    # Colombia
    'Camilo Vargas': 'GK', 'Daniel Muñoz': 'RB', 'Santiago Arias': 'RB', 
    'Davinson Sánchez': 'RCB', 'Jhon Lucumí': 'LCB', 'Carlos Cuesta': 'CB', 'Yerry Mina': 'CB', 
    'Johan Mojica': 'LB', 'Jefferson Lerma': 'CDM', 'Richard Ríos': 'CM', 'Mateus Uribe': 'CM', 
    'James Rodríguez': 'CAM', 'Juan Fernando Quintero': 'CAM', 'Jhon Arias': 'RW', 
    'Luis Díaz': 'LW', 'Luis Sinisterra': 'LW', 'Jhon Córdoba': 'ST', 'Rafael Santos Borré': 'ST',

    # Croatia
    'Dominik Livakovic': 'GK', 'Josip Juranovic': 'RB', 'Josip Stanisic': 'RB', 
    'Josip Sutalo': 'RCB', 'Marin Pongracic': 'LCB', 'Josko Gvardiol': 'LB', 'Borna Sosa': 'LB', 
    'Marcelo Brozovic': 'CDM', 'Mateo Kovacic': 'CM', 'Luka Modric': 'CM', 'Mario Pasalic': 'CAM', 
    'Lovro Majer': 'RW', 'Andrej Kramaric': 'LW', 'Luka Ivanusec': 'LW', 'Bruno Petkovic': 'ST', 'Ante Budimir': 'ST',
    
    # Mexico
    'Guillermo Ochoa': 'GK', 'Luis Malagón': 'GK', 'Jorge Sánchez': 'RB', 'Julián Araujo': 'RB',
    'César Montes': 'RCB', 'Johan Vásquez': 'LCB', 'Jesús Gallardo': 'LB', 'Gerardo Arteaga': 'LB',
    'Edson Álvarez': 'CDM', 'Luis Romo': 'CM', 'Luis Chávez': 'CM', 'Erick Sánchez': 'CM',
    'Uriel Antuna': 'RW', 'Roberto Alvarado': 'RW', 'Hirving Lozano': 'LW', 'Julián Quiñones': 'LW',
    'Santiago Giménez': 'ST', 'Henry Martín': 'ST',

    # USA
    'Matt Turner': 'GK', 'Sergiño Dest': 'RB', 'Joe Scally': 'RB',
    'Chris Richards': 'RCB', 'Tim Ream': 'LCB', 'Cameron Carter-Vickers': 'CB', 'Antonee Robinson': 'LB',
    'Tyler Adams': 'CDM', 'Yunus Musah': 'CM', 'Weston McKennie': 'CM', 'Gio Reyna': 'CAM',
    'Timothy Weah': 'RW', 'Christian Pulisic': 'LW', 'Folarin Balogun': 'ST', 'Ricardo Pepi': 'ST',

    # Japan
    'Zion Suzuki': 'GK', 'Takehiro Tomiyasu': 'RB', 'Yukinari Sugawara': 'RB',
    'Ko Itakura': 'RCB', 'Shogo Taniguchi': 'LCB', 'Koki Machida': 'CB', 'Hiroki Ito': 'LB',
    'Wataru Endo': 'CDM', 'Hidemasa Morita': 'CM', 'Reo Hatate': 'CM',
    'Junya Ito': 'RW', 'Takefusa Kubo': 'RW', 'Kaoru Mitoma': 'LW', 'Takumi Minamino': 'LW',
    'Ayase Ueda': 'ST', 'Daizen Maeda': 'ST',
    
    # Morocco
    'Yassine Bounou': 'GK', 'Achraf Hakimi': 'RB', 'Noussair Mazraoui': 'LB', 'Yahya Attiat-Allah': 'LB',
    'Nayef Aguerd': 'LCB', 'Romain Saïss': 'RCB', 'Sofyan Amrabat': 'CDM', 'Azzedine Ounahi': 'CM',
    'Selim Amallah': 'CM', 'Hakim Ziyech': 'RW', 'Brahim Díaz': 'CAM', 'Amine Adli': 'RW',
    'Sofiane Boufal': 'LW', 'Youssef En-Nesyri': 'ST', 'Ayoub El Kaabi': 'ST'
}

# Normalize string logic (remove accents for loose matching)
import unicodedata
def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

ai_normalized = {normalize(k): v for k, v in ai_knowledge.items()}

with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

changed_count = 0
for team in data['teams'].values():
    if team.get('is_placeholder'): continue
    for p in team.get('squad', []):
        norm_name = normalize(p['name'])
        
        # Check direct match
        if norm_name in ai_normalized:
            p['exact_position'] = ai_normalized[norm_name]
            changed_count += 1
        else:
            # Check partial match (e.g. 'Kylian Mbappe Lottin' matches 'Kylian Mbappe')
            for ai_name, pos in ai_normalized.items():
                if ai_name in norm_name or norm_name in ai_name:
                    p['exact_position'] = pos
                    changed_count += 1
                    break

with open('data/wc2026_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Injected {changed_count} precise AI positions!")
