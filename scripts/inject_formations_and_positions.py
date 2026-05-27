import json
import re
import unicodedata
import os

FORMATIONS = {
    'MEX': '4-3-3', 'RSA': '4-2-3-1', 'KOR': '4-4-2', 'CZE': '3-4-3', 
    'CAN': '4-4-2', 'BIH': '4-3-3', 'QAT': '4-3-3', 'SUI': '3-4-3', 
    'BRA': '4-2-3-1', 'MAR': '4-3-3', 'HAI': '4-3-3', 'SCO': '3-4-3', 
    'USA': '4-3-3', 'PAR': '4-4-2', 'AUS': '4-2-3-1', 'TUR': '4-2-3-1', 
    'GER': '4-2-3-1', 'CUR': '4-3-3', 'CIV': '4-3-3', 'ECU': '4-3-3', 
    'NED': '4-3-3', 'JPN': '4-2-3-1', 'SWE': '4-4-2', 'TUN': '3-4-3', 
    'BEL': '4-2-3-1', 'EGY': '4-3-3', 'IRN': '4-2-3-1', 'NZL': '4-3-3', 
    'ESP': '4-3-3', 'CPV': '4-3-3', 'KSA': '4-3-3', 'URU': '4-2-3-1', 
    'FRA': '4-2-3-1', 'SEN': '4-3-3', 'COD': '4-3-3', 'NOR': '4-3-3', 
    'ARG': '4-4-2', 'ALG': '4-3-3', 'AUT': '4-2-3-1', 'JOR': '3-4-3', 
    'POR': '4-3-3', 'IRQ': '4-2-3-1', 'UZB': '3-4-3', 'COL': '4-2-3-1', 
    'ENG': '4-2-3-1', 'CRO': '4-3-3', 'GHA': '4-2-3-1', 'PAN': '3-4-3'
}

AI_KNOWLEDGE = {
    # Previously injected teams + updates
    'Unai Simón': 'GK', 'Dani Carvajal': 'RB', 'Jesús Navas': 'RB', 'Robin Le Normand': 'RCB', 
    'Aymeric Laporte': 'LCB', 'Nacho': 'CB', 'Pau Torres': 'CB', 'Pau Cubarsí': 'CB', 
    'Marc Cucurella': 'LB', 'Alejandro Grimaldo': 'LB', 'Rodri': 'CDM', 'Martín Zubimendi': 'CDM', 
    'Fabián Ruiz': 'CM', 'Mikel Merino': 'CM', 'Pedri': 'CM', 'Gavi': 'CM', 
    'Lamine Yamal': 'RW', 'Ferran Torres': 'RW', 'Nico Williams': 'LW', 'Mikel Oyarzabal': 'LW', 
    'Dani Olmo': 'CAM', 'Álvaro Morata': 'ST', 'Joselu': 'ST',
    'Mike Maignan': 'GK', 'Jules Koundé': 'RB', 'Jonathan Clauss': 'RB', 'Dayot Upamecano': 'RCB', 
    'William Saliba': 'LCB', 'Ibrahima Konaté': 'CB', 'Benjamin Pavard': 'CB', 
    'Theo Hernández': 'LB', 'Ferland Mendy': 'LB', 'Aurélien Tchouaméni': 'CDM', "N'Golo Kanté": 'CDM', 
    'Eduardo Camavinga': 'CM', 'Adrien Rabiot': 'CM', 'Youssouf Fofana': 'CM', 
    'Ousmane Dembélé': 'RW', 'Kingsley Coman': 'RW', 'Kylian Mbappé': 'ST', 'Marcus Thuram': 'ST', 
    'Olivier Giroud': 'ST', 'Antoine Griezmann': 'CAM', 'Bradley Barcola': 'LW',
    'Alisson': 'GK', 'Ederson': 'GK', 'Danilo Luiz': 'RB', 'Danilo': 'RB', 'Yan Couto': 'RB', 
    'Marquinhos': 'RCB', 'Gabriel Magalhães': 'LCB', 'Éder Militão': 'CB', 'Bremer': 'CB', 
    'Wendell': 'LB', 'Guilherme Arana': 'LB', 'Casemiro': 'CDM', 'João Gomes': 'CDM', 'Douglas Luiz': 'CM', 
    'Bruno Guimarães': 'CM', 'Lucas Paquetá': 'CAM', 'Andreas Pereira': 'CAM', 
    'Raphinha': 'RW', 'Rodrygo': 'ST', 'Vinícius Júnior': 'LW', 'Gabriel Martinelli': 'LW', 'Endrick': 'ST',
    'Jordan Pickford': 'GK', 'Kyle Walker': 'RB', 'Trent Alexander-Arnold': 'RB', 'Kieran Trippier': 'RB', 
    'John Stones': 'RCB', 'Marc Guéhi': 'LCB', 'Harry Maguire': 'CB', 'Ezri Konsa': 'CB', 
    'Luke Shaw': 'LB', 'Ben Chilwell': 'LB', 'Declan Rice': 'CDM', 'Kobbie Mainoo': 'CM', 
    'Conor Gallagher': 'CM', 'Jude Bellingham': 'CAM', 'Phil Foden': 'LW', 'Jack Grealish': 'LW', 
    'Bukayo Saka': 'RW', 'Cole Palmer': 'RW', 'Harry Kane': 'ST', 'Ollie Watkins': 'ST', 'Ivan Toney': 'ST',
    'Diogo Costa': 'GK', 'João Cancelo': 'RB', 'Diogo Dalot': 'RB', 'Rúben Dias': 'LCB', 
    'Pepe': 'RCB', 'Gonçalo Inácio': 'CB', 'António Silva': 'CB', 'Nuno Mendes': 'LB', 
    'João Palhinha': 'CDM', 'Rúben Neves': 'CDM', 'Vitinha': 'CM', 'Matheus Nunes': 'CM', 
    'Bruno Fernandes': 'CAM', 'Bernardo Silva': 'RW', 'Francisco Conceição': 'RW', 
    'Rafael Leão': 'LW', 'João Félix': 'LW', 'Cristiano Ronaldo': 'ST', 'Gonçalo Ramos': 'ST',
    'Manuel Neuer': 'GK', 'Marc-André ter Stegen': 'GK', 'Joshua Kimmich': 'RB', 'Benjamin Henrichs': 'RB', 
    'Antonio Rüdiger': 'RCB', 'Jonathan Tah': 'LCB', 'Nico Schlotterbeck': 'CB', 'Waldemar Anton': 'CB', 
    'Maximilian Mittelstädt': 'LB', 'David Raum': 'LB', 'Robert Andrich': 'CDM', 'Pascal Groß': 'CM', 
    'Toni Kroos': 'CM', 'Ilkay Gündogan': 'CAM', 'Jamal Musiala': 'CAM', 'Florian Wirtz': 'CAM', 
    'Leroy Sané': 'RW', 'Kai Havertz': 'ST', 'Niclas Füllkrug': 'ST', 'Thomas Müller': 'ST',
    'Sergio Rochet': 'GK', 'Nahitan Nández': 'RB', 'Guillermo Varela': 'RB', 
    'Ronald Araujo': 'RCB', 'José María Giménez': 'LCB', 'Mathías Olivera': 'CB', 'Sebastián Cáceres': 'CB', 
    'Matías Viña': 'LB', 'Lucas Olaza': 'LB', 'Manuel Ugarte': 'CDM', 'Rodrigo Bentancur': 'CM', 
    'Federico Valverde': 'CM', 'Nicolás de la Cruz': 'CAM', 'Giorgian de Arrascaeta': 'CAM', 
    'Facundo Pellistri': 'RW', 'Maximiliano Araújo': 'LW', 'Darwin Núñez': 'ST', 'Luis Suárez': 'ST',
    'Bart Verbruggen': 'GK', 'Denzel Dumfries': 'RWB', 'Jeremie Frimpong': 'RWB', 
    'Stefan de Vrij': 'RCB', 'Virgil van Dijk': 'CB', 'Nathan Aké': 'LCB', 'Matthijs de Ligt': 'CB', 
    'Micky van de Ven': 'LB', 'Daley Blind': 'LB', 'Jerdy Schouten': 'CDM', 'Tijjani Reijnders': 'CM', 
    'Joey Veerman': 'CM', 'Georginio Wijnaldum': 'CAM', 'Xavi Simons': 'CAM', 
    'Cody Gakpo': 'LW', 'Donyell Malen': 'RW', 'Steven Bergwijn': 'LW', 'Memphis Depay': 'ST', 'Wout Weghorst': 'ST',
    'Gianluigi Donnarumma': 'GK', 'Giovanni Di Lorenzo': 'RB', 'Matteo Darmian': 'RWB', 
    'Alessandro Bastoni': 'LCB', 'Riccardo Calafiori': 'CB', 'Gianluca Mancini': 'RCB', 'Alessandro Buongiorno': 'CB', 
    'Federico Dimarco': 'LWB', 'Andrea Cambiaso': 'LB', 'Jorginho': 'CDM', 'Nicolò Barella': 'CM', 
    'Davide Frattesi': 'CM', 'Bryan Cristante': 'CM', 'Lorenzo Pellegrini': 'CAM', 
    'Federico Chiesa': 'RW', 'Mattia Zaccagni': 'LW', 'Gianluca Scamacca': 'ST', 'Mateo Retegui': 'ST',
    'Koen Casteels': 'GK', 'Timothy Castagne': 'RB', 'Wout Faes': 'RCB', 'Jan Vertonghen': 'LCB', 
    'Zeno Debast': 'CB', 'Arthur Theate': 'LB', 'Amadou Onana': 'CDM', 'Orel Mangala': 'CDM', 
    'Youri Tielemans': 'CM', 'Kevin De Bruyne': 'CAM', 'Leandro Trossard': 'LW', 
    'Jérémy Doku': 'RW', 'Johan Bakayoko': 'RW', 'Romelu Lukaku': 'ST', 'Loïs Openda': 'ST',
    'Camilo Vargas': 'GK', 'Daniel Muñoz': 'RB', 'Santiago Arias': 'RB', 
    'Davinson Sánchez': 'RCB', 'Jhon Lucumí': 'LCB', 'Carlos Cuesta': 'CB', 'Yerry Mina': 'CB', 
    'Johan Mojica': 'LB', 'Jefferson Lerma': 'CDM', 'Richard Ríos': 'CM', 'Mateus Uribe': 'CM', 
    'James Rodríguez': 'CAM', 'Juan Fernando Quintero': 'CAM', 'Jhon Arias': 'RW', 
    'Luis Díaz': 'LW', 'Luis Sinisterra': 'LW', 'Jhon Córdoba': 'ST', 'Rafael Santos Borré': 'ST',
    'Dominik Livakovic': 'GK', 'Josip Juranovic': 'RB', 'Josip Stanisic': 'RB', 
    'Josip Sutalo': 'RCB', 'Marin Pongracic': 'LCB', 'Josko Gvardiol': 'LB', 'Borna Sosa': 'LB', 
    'Marcelo Brozovic': 'CDM', 'Mateo Kovacic': 'CM', 'Luka Modric': 'CM', 'Mario Pasalic': 'CAM', 
    'Lovro Majer': 'RW', 'Andrej Kramaric': 'LW', 'Luka Ivanusec': 'LW', 'Bruno Petkovic': 'ST', 'Ante Budimir': 'ST',
    'Guillermo Ochoa': 'GK', 'Luis Malagón': 'GK', 'Jorge Sánchez': 'RB', 'Julián Araujo': 'RB',
    'César Montes': 'RCB', 'Johan Vásquez': 'LCB', 'Jesús Gallardo': 'LB', 'Gerardo Arteaga': 'LB',
    'Edson Álvarez': 'CDM', 'Luis Romo': 'CM', 'Luis Chávez': 'CM', 'Erick Sánchez': 'CM',
    'Uriel Antuna': 'RW', 'Roberto Alvarado': 'RW', 'Hirving Lozano': 'LW', 'Julián Quiñones': 'LW',
    'Santiago Giménez': 'ST', 'Henry Martín': 'ST',
    'Matt Turner': 'GK', 'Sergiño Dest': 'RB', 'Joe Scally': 'RB',
    'Chris Richards': 'RCB', 'Tim Ream': 'LCB', 'Cameron Carter-Vickers': 'CB', 'Antonee Robinson': 'LB',
    'Tyler Adams': 'CDM', 'Yunus Musah': 'CM', 'Weston McKennie': 'CM', 'Gio Reyna': 'CAM',
    'Timothy Weah': 'RW', 'Christian Pulisic': 'LW', 'Folarin Balogun': 'ST', 'Ricardo Pepi': 'ST',
    'Zion Suzuki': 'GK', 'Takehiro Tomiyasu': 'RB', 'Yukinari Sugawara': 'RB',
    'Ko Itakura': 'RCB', 'Shogo Taniguchi': 'LCB', 'Koki Machida': 'CB', 'Hiroki Ito': 'LB',
    'Wataru Endo': 'CDM', 'Hidemasa Morita': 'CM', 'Reo Hatate': 'CM',
    'Junya Ito': 'RW', 'Takefusa Kubo': 'RW', 'Kaoru Mitoma': 'LW', 'Takumi Minamino': 'LW',
    'Ayase Ueda': 'ST', 'Daizen Maeda': 'ST',
    'Yassine Bounou': 'GK', 'Achraf Hakimi': 'RB', 'Noussair Mazraoui': 'LB', 'Yahya Attiat-Allah': 'LB',
    'Nayef Aguerd': 'LCB', 'Romain Saïss': 'RCB', 'Sofyan Amrabat': 'CDM', 'Azzedine Ounahi': 'CM',
    'Selim Amallah': 'CM', 'Hakim Ziyech': 'RW', 'Brahim Díaz': 'CAM', 'Amine Adli': 'RW',
    'Sofiane Boufal': 'LW', 'Youssef En-Nesyri': 'ST', 'Ayoub El Kaabi': 'ST',
    
    # NEW Additions based on Audit
    'Alphonso Davies': 'LB', 'Alistair Johnston': 'RB', 'Stephen Eustáquio': 'CM', 'Jonathan David': 'ST',
    'Ismaël Koné': 'CM', 'Tajon Buchanan': 'RW', 'Niko Sigur': 'RB', 'Derek Cornelius': 'LCB', 'Kamal Miller': 'RCB',
    'Joel Waterman': 'RCB', 'Moise Bombito': 'RCB', 
    'Granit Xhaka': 'CM', 'Manuel Akanji': 'CB', 'Ricardo Rodriguez': 'LCB', 'Nico Elvedi': 'RCB', 'Xherdan Shaqiri': 'CAM',
    'Hakan Çalhanoğlu': 'CAM', 'Ferdi Kadıoğlu': 'LB', 'Merih Demiral': 'CB', 'Zeki Çelik': 'RB', 'Ozan Kabak': 'CB',
    'Arda Güler': 'RW', 'Kenan Yıldız': 'LW', 'Barış Alper Yılmaz': 'ST', 'Orkun Kökçü': 'CM', 'İsmail Yüksek': 'CDM',
    'Erling Braut Haaland': 'ST', 'Martin Ødegaard': 'CAM', 'Alexander Sorloth': 'ST', 'Julian Ryerson': 'RB',
    'Kristoffer Vassbakk Ajer': 'CB', 'Leo Østigård': 'CB', 'David Møller Wolfe': 'LB',
    'Son Heung-min': 'LW', 'Kim Min-jae': 'CB', 'Lee Kang-in': 'RW', 'Hwang Hee-chan': 'LW', 'Seol Young-woo': 'LB',
    'Mohammed Kudus': 'CAM', 'Thomas Partey': 'CDM', 'Iñaki Williams': 'RW', 'Tariq Lamptey': 'RB', 'Mohammed Salisu': 'CB',
    'Moisés Caicedo': 'CDM', 'Pervis Estupiñán': 'LB', 'Piero Hincapié': 'CB', 'Félix Torres': 'CB', 'Ángelo Preciado': 'RB',
    'Enner Valencia': 'ST', 'Kendry Páez': 'CAM', 'Willian Pacho': 'CB',
    'Isak Hien': 'CB', 'Victor Lindelöf': 'CB', 'Ludwig Augustinsson': 'LB', 'Emil Holm': 'RB', 'Daniel Svensson': 'LB',
    'Alexander Isak': 'ST', 'Viktor Gyökeres': 'ST', 'Dejan Kulusevski': 'RW', 'Anthony Elanga': 'LW',
    'Andrew Robertson': 'LB', 'Kieran Tierney': 'LCB', 'Scott McTominay': 'CM', 'John McGinn': 'CM', 'Aaron Hickey': 'RB',
    'Nathan Patterson': 'RB', 'Ché Adams': 'ST', 'Billy Gilmour': 'CM',
    'Gustavo Gómez': 'CB', 'Omar Alderete': 'CB', 'Miguel Almirón': 'RW', 'Julio Enciso': 'LW', 'Ramón Sosa': 'LW',
    'Mathew Ryan': 'GK', 'Harry Souttar': 'CB', 'Kye Rowles': 'CB', 'Jordan Bos': 'LB', 'Alessandro Circati': 'CB',
    'Rayan Aït-Nouri': 'LB', 'Ramy Bensebaini': 'CB', 'Riyad Mahrez': 'RW', 'Ismaël Bennacer': 'CM',
    'Amine Gouiri': 'ST', 'Houssem Aouar': 'CAM', 'Farès Chaïbi': 'CAM',
    'David Alaba': 'CB', 'Marcel Sabitzer': 'CM', 'Konrad Laimer': 'CM', 'Christoph Baumgartner': 'CAM',
    'Kevin Danso': 'CB', 'Philipp Lienhart': 'CB', 'Stefan Posch': 'RB', 'Marco Friedl': 'LB', 'Marko Arnautović': 'ST'
}

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower()

ai_normalized = {normalize(k): v for k, v in AI_KNOWLEDGE.items()}

def patch_squads_js():
    filepath = 'frontend/js/ui/squads.js'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    formations_str = json.dumps(FORMATIONS, indent=2)
    # Reemplazar el diccionario KNOWN_FORMATIONS viejo con el nuevo.
    new_content = re.sub(r'const KNOWN_FORMATIONS = \{.*?\};', f'const KNOWN_FORMATIONS = {formations_str};', content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Patched squads.js KNOWN_FORMATIONS")

def patch_json():
    with open('data/wc2026_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Heuristic roles mapping for fallback
    # To ensure visual sanity, if players aren't identified by AI, we assign them pseudo-randomly but strictly
    # For instance, if 4 defenders are available, we assign LB, CB, CB, RB based on their array index.
    
    for code, team in data['teams'].items():
        if team.get('is_placeholder'): continue
        
        squad = sorted(team.get('squad', []), key=lambda x: x.get('market_value_eur') or 0, reverse=True)
        
        # Categorize
        defs, mids, fwds = [], [], []
        for p in squad:
            norm = normalize(p['name'])
            # 1. Apply AI mapping if available
            if norm in ai_normalized:
                p['exact_position'] = ai_normalized[norm]
            else:
                matched = False
                for ai_name, pos in ai_normalized.items():
                    if ai_name in norm or norm in ai_name:
                        p['exact_position'] = pos
                        matched = True
                        break
                
                # 2. If no AI mapping, we rely on generic positional assignment 
                # but we will ENHANCE it dynamically to guarantee RB/LB/CB presence for unknown teams
                if not matched:
                    pos_str = (p.get('position', '') or '').lower()
                    if 'defensa' in pos_str or 'lateral' in pos_str or 'central' in pos_str:
                        defs.append(p)
                    elif 'centro' in pos_str or 'medio' in pos_str or 'volante' in pos_str:
                        mids.append(p)
                    elif 'delantero' in pos_str or 'extremo' in pos_str or 'atacante' in pos_str:
                        fwds.append(p)

        # Distribute fallback defenders to LB, CB, RB
        if len(defs) > 0:
            for i, d in enumerate(defs):
                if i % 4 == 0: d['exact_position'] = 'LB'
                elif i % 4 == 1 or i % 4 == 2: d['exact_position'] = 'CB'
                else: d['exact_position'] = 'RB'
                
        # Distribute fallback midfielders
        if len(mids) > 0:
            for i, m in enumerate(mids):
                if i % 3 == 0: m['exact_position'] = 'CDM'
                elif i % 3 == 1: m['exact_position'] = 'CM'
                else: m['exact_position'] = 'CAM'
                
        # Distribute fallback forwards
        if len(fwds) > 0:
            for i, f in enumerate(fwds):
                if i % 3 == 0: f['exact_position'] = 'RW'
                elif i % 3 == 1: f['exact_position'] = 'LW'
                else: f['exact_position'] = 'ST'
                
    with open('data/wc2026_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Patched wc2026_data.json with AI knowledge and structural heuristic fallback")

if __name__ == '__main__':
    patch_squads_js()
    patch_json()
