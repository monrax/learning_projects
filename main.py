# This is a command-line battleship game with online multiplayer capabilities.
# author: Ramón Márquez, @monrax on github
import argparse
import random
import socket
from requests import get
from colorama import init, Back

FORMS_OF_ADDRESS = ("Captain",
                    "Admiral",
                    "sir",
                    "CO",
                    "boss",
                    "commander",
                    "chief",
                    "skipper")
DEFAULT_PORT = 4248
init(autoreset=True)
cli_options_parser = argparse.ArgumentParser(description="*** Battleship: a"
                                                         " command-line-based"
                                                         " naval battle game"
                                                         " with online"
                                                         " multiplayer"
                                                         " capabilities ***")
cli_options_parser.add_argument("-v", "--version", action="version",
                                version="Battleship v0.1 by monrax")


def address_pair(address_string):
    ip, port = address_string.split(':')
    return ip, int(port)


def args_from_parser(options_parser, alt_list=None):
    network_subparser = options_parser.add_subparsers(dest="mode",
                                                      metavar="game_mode",
                                                      help="can be either "
                                                           "'offline' or "
                                                           "'online'",
                                                      required=True)
    network_subparser.add_parser("offline", help="offline version of the "
                                                 "game. You'll play against "
                                                 "the CPU")
    online_parser = network_subparser.add_parser("online",
                                                 description="Battleship "
                                                             "comes with "
                                                             "added online "
                                                             "multiplayer "
                                                             "functionality. "
                                                             "You can either "
                                                             "'host' a game "
                                                             "or join a game "
                                                             "as a 'guest' "
                                                             "To carry out "
                                                             "the connection"
                                                             ", a network "
                                                             "address must "
                                                             "be provided",
                                                 help="online version of the "
                                                      "game. Use 'online -h' "
                                                      "for more help")
    role_subparser = online_parser.add_subparsers(dest="role", metavar='role',
                                                  help="network role. Can be "
                                                       "either 'host' or "
                                                       "'guest'",
                                                  required=True)
    role_subparser.add_parser("host", help="the game will be hosted by your "
                                           "computer acting as server, using "
                                           "its current ip address and port "
                                           f"{DEFAULT_PORT} [MAKE SURE YOUR "
                                           "FIREWALL & ROUTER CONFIGURATION "
                                           "ALLOW PORT FORWARDING FOR THIS "
                                           "NETWORK ADDRESS]")
    guest_parser = role_subparser.add_parser("guest",
                                             help="join a game hosted by a "
                                                  "friend. You will need a "
                                                  "valid network address "
                                                  "in the form 'ip:port'")
    guest_parser.add_argument("address", type=address_pair,
                              help="network address in the form 'ip:port'")
    options_parser.add_argument("-s", "--size", metavar='',
                                help="grid size (must be an integer value). "
                                     "Default value is 10",
                                type=int, default=10)
    options_parser.add_argument("-p", "--placement", metavar='',
                                help="initial ship placement (either at "
                                     "'random' or in a 'custom' manner). "
                                     "Default is 'random'",
                                choices=('random', 'custom'),
                                default='random')
    return options_parser.parse_args(alt_list)


def menu():
    options = []
    mode = input("\nEnter mode (offline or online): ")
    size = input("\nEnter grid size (or just press enter to load "
                 "default value 10): ")
    if size:
        size = ('-s', size)
    placement = input("\nEnter ship placement type (random or custom, "
                      "default value is random): ")
    if placement:
        placement = ('-p', placement)
    options.extend((*size, *placement, mode))
    if mode == 'online':
        role = input("\nEnter role (host or guest): ")
        address = input("\nEnter address (in ip:port form): ")
        options.extend((role, address))
    return options


def create_server(ip='', port=DEFAULT_PORT):
    host = None
    server_sock = socket.socket()
    server_sock.bind((ip, port))
    server_sock.settimeout(60)
    server_sock.listen(1)
    if not ip:
        ip = get('https://api.ipify.org').text
    print("\nYour public IP address is: {} \nThe address port is: {}"
          "\nShare it only with your friend!".format(ip, port))
    print("\nWaiting for guest...")
    try:
        host, address = server_sock.accept()
    except socket.timeout:
        print("Timed out. Guest not found")
    return host


def join_server(address):
    guest = socket.socket()
    guest.settimeout(60)
    try:
        guest.connect(address)
    except socket.timeout:
        print("Timed out. Host not found")
        return None
    except OSError as ex:
        print("Can't connect to this address:", ex.strerror)
        return None
    return guest


def convert_coord(coord, n=10):
    # printable i,j coordinates to ship.coordinates x,y coordinates
    # x,y coordinates: (1, 1) -> (n, n)
    # i,j coordinates: (n-1, 0) -> (0, n-1)
    i, j = coord
    x, y = j + 1, n - i
    return x, y


def coord_from_bow(bow, ship_size, ship_direction):
    # generator function to get all ship coordinates from its bow coordinates
    for i in range(ship_size):
        if ship_direction:
            yield bow[0] + i, bow[1]
        else:
            yield bow[0], bow[1] - i


def random_bow(ship_size, ship_direction, grid_size):
    if ship_direction:
        bow_x = random.randint(1, grid_size - ship_size + 1)
        bow_y = random.randint(1, grid_size)
    else:
        bow_x = random.randint(1, grid_size)
        bow_y = random.randint(ship_size, grid_size)
    return bow_x, bow_y


class Fleet:
    def __init__(self, grid_size=10, is_random=True, blueprints=None):
        self.grid_size = grid_size
        self.ships = []
        self.occupied = []
        self.shots_fired = []
        self.shots_received = []
        if blueprints:
            self.build_ships_from(blueprints)
        else:
            self.build_ships(grid_size, is_random)

    def ship_from_coord(self, coord):
        for ship in self.ships:
            if coord in ship.coordinates:
                return ship
        return None

    def same_ship(self, coord_1, coord_2):
        # check whether two coordinates belong to the same ship
        ship = self.ship_from_coord(coord_1)
        if ship:
            return coord_2 in ship.coordinates
        return None

    def build_ships(self, g_size, random_choice):
        # total number of ships = grid size
        ship_sizes = range(1, g_size // 2)
        for size in ship_sizes:
            ships = range(1, g_size // 2 - size + 1)
            for n_ship in ships:
                if random_choice:
                    while True:
                        direction = random.choice((0, 1))
                        bow = random_bow(size, direction, g_size)
                        new_ship = Ship(size, bow, direction, self)
                        if new_ship:
                            break
                else:
                    while True:
                        enter_bow = input(f"\nEnter bow coordinates for"
                                          f"ship #{n_ship}, class {size}: "
                                          ).split()
                        enter_dir = input("Enter direction (0 for vertical,"
                                          " 1 for horizontal): ")
                        if len(enter_bow) == 2 and enter_dir in ('0', '1'):
                            enter_bow = tuple(enter_bow)
                            enter_dir = int(enter_dir)
                            new_ship = Ship(size, enter_bow, enter_dir, self)
                            if new_ship:
                                break
                            else:
                                print("Cell(s) already occupied. Try again\n")
                        else:
                            print("Invalid parameters. Try again\n")

    def build_ships_from(self, fleet_blueprints):
        for ship in fleet_blueprints:
            Ship(ship[0], (ship[1], ship[2]), ship[3], self)

    def make_blueprints(self):
        return tuple((ship.size, *ship.bow, ship.direction)
                     for ship in self.ships)

    def print_grid(self, cell_width=3, enemy_fleet=None, all_visible=False):
        if self.grid_size != enemy_fleet.grid_size:
            print("All fleets must have equal grid sizes")
            return None
        n = self.grid_size
        fleets = (self, enemy_fleet)
        water, hit, miss = ' ', 'X', '·'

        # draw top grid frame, for each fleet
        for _ in filter(None, fleets):
            print('╔', *(('═' * cell_width, '╤') * n)[:-1], '╗',
                  sep='', end='')
        print()

        # draw grid content
        for row in range(n):
            for fleet in filter(None, fleets):
                visible = fleet is self or all_visible
                print('║', end='')  # frame, left side

                for col in range(n):
                    cell = convert_coord((row, col))
                    next_cell = convert_coord((row, col + 1))
                    color = Back.BLUE
                    symbol = water
                    vertical_line = color + '│'
                    if cell in fleet.occupied:
                        if visible:
                            color = Back.WHITE
                        if cell in fleet.shots_received:
                            color = Back.RED
                            symbol = hit
                        if fleet.same_ship(cell, next_cell) and \
                                (visible or
                                 fleet.ship_from_coord(cell).health == 0):
                            vertical_line = color + '│'
                    elif cell in fleet.shots_received:
                        color = Back.CYAN
                        symbol = miss
                    symbol = '{: ^{}}'.format(symbol, cell_width)
                    print(color + symbol, vertical_line, sep='', end='')

                print('\b', '║', sep='', end='')  # frame, right side
            # row numbers at the end of each row
            print(' ', convert_coord((row, 0))[1], sep='')

            # draw row of crosses, for each fleet
            if row < n - 1:
                for fleet in filter(None, fleets):
                    visible = fleet is self or all_visible
                    print('╟', end='')  # frame, left side

                    for col in range(n):
                        cell = convert_coord((row, col))
                        next_cell = convert_coord((row + 1, col))
                        color = Back.BLUE
                        if fleet.same_ship(cell, next_cell):
                            if visible:
                                color = Back.WHITE
                            if fleet.ship_from_coord(cell).health == 0:
                                color = Back.RED
                        h = color + '─'
                        print(h * cell_width, Back.BLUE + '┼', sep='', end='')

                    print('\b', '╢', sep='', end='')  # frame, right side
                print()

        # draw bottom grid frame, for each fleet
        for _ in filter(None, fleets):
            print('╚', *(('═' * cell_width, '╧') * n)[:-1], '╝',
                  sep='', end='')
        print()

        # column numbers at the bottom of each column, for each fleet
        for _ in filter(None, fleets):
            print(' ', end='')
            for col in range(1, n + 1):
                print('{: ^{}}'.format(col, cell_width), end=' ')
        print()

    def update_status(self):
        for ship in self.ships:
            shots = [i in self.shots_received for i in ship.coordinates]
            damage = (shots.count(True) / ship.size) * 100
            ship.update(round(100 - damage))

    def random_shot(self):
        coord = (random.randint(1, self.grid_size),
                 random.randint(1, self.grid_size))
        while coord in self.shots_fired:
            coord = (random.randint(1, self.grid_size),
                     random.randint(1, self.grid_size))
        return coord

    def fire_at(self, coord):
        self.shots_fired.append(coord)

    def incoming(self, coord):
        self.shots_received.append(coord)
        self.update_status()
        return coord in self.occupied

    def send_blueprints(self, client_socket):
        for ship in self.make_blueprints():
            for feature in ship:
                client_socket.send(int.to_bytes(feature, 1, 'big'))


class Ship:
    def __new__(cls, size, bow_coord, direction, fleet):
        coords = coord_from_bow(bow_coord, size, direction)
        invalid_coord = any(coord in fleet.occupied for coord in coords)
        if not invalid_coord:
            return object.__new__(cls)

    def __init__(self, size, bow_coord, direction, fleet):
        self.size = size
        self.bow = bow_coord
        self.direction = direction
        self.coordinates = [*coord_from_bow(bow_coord, size, direction)]
        self.status = 'AFLOAT'
        self.health = 100
        fleet.ships.append(self)
        fleet.occupied.extend(self.coordinates)

    def __str__(self):
        desc_status = f"{self.status}"
        desc_health = f" {self.health}%" if self.health else ''
        desc_class = f" - Ship class {self.size}"
        desc_loc = f", located at coordinates {self.bow}"
        if self.size == 1:
            desc_dir = ''
        else:
            desc_dir = f", {'HORZ.' if self.direction else 'VERT.'}"
        return desc_status + desc_health + desc_class + desc_loc + desc_dir

    def update(self, new_health):
        self.health = new_health
        if self.health == 0:
            self.status = 'SUNK'


class Player:
    def __init__(self, name, size=10, rand_fleet=True, ship_list=None):
        self.name = name
        if ship_list:
            self.fleet = Fleet(blueprints=ship_list)
        else:
            self.fleet = Fleet(size, rand_fleet)

    def fire_and_report(self, engaged_fleet, log,
                        coord=None, my_turn=False, live_socket=None):
        if my_turn:
            hit_rpt, miss_rpt = "ENEMY SHIP HIT!", "MISSED SHOT..."
        else:
            hit_rpt, miss_rpt = "WE'VE TAKEN SOME DAMAGE...", "ENEMY MISS!"
        if live_socket:
            if my_turn:
                for c in coord:
                    live_socket.send(int.to_bytes(c, 1, 'big'))
            else:
                x = int.from_bytes(live_socket.recv(1), 'big')
                y = int.from_bytes(live_socket.recv(1), 'big')
                coord = x, y
        elif not coord:
            coord = self.fleet.random_shot()
        self.fleet.fire_at(coord)
        hit = engaged_fleet.incoming(coord)
        print(f"\n{self.name}'s shot at:", coord)
        if hit:
            log.append((self.name + ':', coord, "- hit"))
            print("- REPORT:", hit_rpt)
        else:
            log.append((self.name + ':', coord, "- miss"))
            print("- REPORT:", miss_rpt)
        return hit


def game(options):
    moves = []
    # prev_command = None
    prev_command, p2, network_socket, my_turn = None, None, None, None
    grid_size = options.size
    initial_placement = options.placement == 'random'
    player_name = "Admiral " + input("\nEnter your name: ")
    p1 = Player(player_name, size=grid_size, rand_fleet=initial_placement)
    if options.mode == 'offline':
        p2 = Player("CPU", size=grid_size, rand_fleet=initial_placement)
        my_turn = True
    elif options.mode == 'online':
        if options.role == 'host':
            network_socket = create_server()
            my_turn = True
        elif options.role == 'guest':
            network_socket = join_server(options.address)
            my_turn = False
        if network_socket is None:
            return None
        # check if chosen grids are equal sizes
        network_socket.send(int.to_bytes(grid_size, 1, 'big'))
        p2_grid_size = int.from_bytes(network_socket.recv(1), 'big')
        if grid_size != p2_grid_size:
            print("Both grids must be the same size! "
                  f"Yours is {grid_size} and your friend's is {p2_grid_size}")
            return None
        # determine fleet size to receive blueprints
        network_socket.send(int.to_bytes(len(p1.fleet.ships), 1, 'big'))
        p1.fleet.send_blueprints(network_socket)
        p2_fleet_size = int.from_bytes(network_socket.recv(1), 'big')
        p2_blueprint = []
        for i in range(p2_fleet_size):
            p2_blueprint.append([int.from_bytes(network_socket.recv(1), 'big')
                                for _ in range(4)])
        p2 = Player("Opponent", ship_list=p2_blueprint)
    while True:
        if my_turn:
            p1.fleet.print_grid(enemy_fleet=p2.fleet)
            while True:
                command = input("\nEnter -command or coordinates to engage: ")
                if command.startswith("-"):
                    if command == "-help":
                        print("\nYou are the Admiral of this fleet.\n"
                              "It is your duty to protect all men and "
                              "ships under your command.\n"
                              "Your fleet is represented on the left side.\n"
                              "To fire at the enemy fleet, "
                              "enter coordinates in the form: x y\n"
                              "To list all commands, enter: -commands\n"
                              "After a successful hit, shoot again!\n"
                              "You must sink all enemy ships to win.\n"
                              "Semper fortis, good luck!\n")
                    elif command in ("-command", "-commands"):
                        print("-help: display help message\n"
                              "-status: display status report\n"
                              "-commands: displays this list\n"
                              "-fleet: same as status\n"
                              "-command: same as commands\n"
                              "-recon: obtain intel regarding enemy position"
                              " [WARNING: it may compromise your own"
                              " position]\n"
                              "-grid: print grid to screen\n"
                              f"-log: print {p1.name}'s log."
                              " It contains a record of each play\n")
                    elif command in ("-fleet", "-status"):
                        print(*p1.fleet.ships, sep='\n')
                    elif command == "-recon":
                        coord = random.choice(p2.fleet.occupied)
                        print(*(i + random.randint(-1, 1) for i in coord))
                        if prev_command == command:
                            compromised = random.choice((0, 1, 2))
                            if compromised:
                                coord = random.choice(p1.fleet.occupied)
                                print(f"Your ship location at {coord} "
                                      f"has been temporarily compromised")
                                coord = tuple(i + random.randint(0, 1)
                                              for i in coord)
                                p2.fire_and_report(p1.fleet, moves, coord,
                                                   live_socket=network_socket)
                                p1.fleet.print_grid(enemy_fleet=p2.fleet)
                    elif command == "-grid":
                        p1.fleet.print_grid(enemy_fleet=p2.fleet)
                    elif command == "-log":
                        print(f"\n{p1.name}'s log.")
                        if moves:
                            print("\n This is a record of plays executed"
                                  " by each\n fleet, and their corresponding"
                                  " result:\n")
                            for move in moves:
                                print('', *move)
                        else:
                            print("\nThis ship is built to fight."
                                  " You’d better know how.\n")
                    else:
                        print("Unknown command")
                    prev_command = command
                else:
                    coord = tuple(int(i) for i in command.split()
                                  if i.isdigit() and 1 <= int(i) <= grid_size)
                    if len(coord) != 2:
                        print("- XO: Invalid coordinates,"
                              " {}".format(random.choice(FORMS_OF_ADDRESS)))
                    elif coord in p1.fleet.shots_fired:
                        print("- XO: We've fired at those coordinates before,"
                              " {}".format(random.choice(FORMS_OF_ADDRESS)))
                    else:
                        print('\x1b[1J')  # clear screen
                        hit = p1.fire_and_report(p2.fleet, moves, coord, True,
                                                 live_socket=network_socket)
                        if hit:
                            p1.fleet.print_grid(enemy_fleet=p2.fleet)
                        else:
                            break
        else:
            while True:
                hit = p2.fire_and_report(p1.fleet, moves,
                                         live_socket=network_socket)
                if not hit:
                    break
        my_turn = not my_turn
        if all(cell in p1.fleet.shots_received for cell in p1.fleet.occupied):
            result = "DEFEAT"
            break
        elif all(cell in p1.fleet.shots_fired for cell in p2.fleet.occupied):
            result = "VICTORY"
            break
    if network_socket:
        network_socket.close()
    p1.fleet.print_grid(enemy_fleet=p2.fleet, all_visible=True)
    print(f"\nGAME OVER - {p1.name.upper()}'S {result}")


def run():
    if __name__ == '__main__':
        cli_options = args_from_parser(cli_options_parser)
    else:
        cli_options = args_from_parser(cli_options_parser, menu())
    # print(cli_options)
    game(cli_options)


run()
