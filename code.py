import textwrap
import os
import json


class Game:

    def __init__(self):
        self.title = 'the Journey to Mount Qaf'
        self.user = self.username = self.story = None
        self.scene = 1

    def play(self):
        self.story = Data.load_story()
        self.loop_story()
        
    def select_menu(self):
        choice = input(textwrap.dedent(f'''\
        ***Welcome to {self.title}***\n
        1- Press key '1' or type 'start' to start a new game
        2- Press key '2' or type 'load' to load your progress
        3- Press key '3' or type 'quit' to quit the game\n'''))
        if choice.lower() in ['1', 'start']:
            print('Starting a new game...')
            self.username = input('''Enter a user name to save your progress or type '/b' to go back\n''')
            if self.username == '/b':
                print('Going back to menu...\n')
                self.select_menu()
            else:
                self.user = User().create()
                self.play()
        elif choice.lower() in ['2', 'load']:
            user = Data.load_user()
            if user:
                print('Loading your progress...')
                self.user = user
                self.play()
            else:
                print('No save data found!')
                self.select_menu()
        elif choice.lower() in ['3', 'quit']:
            print('Goodbye!')
            quit()
        else:
            print('Unknown input! Please enter a valid one.')
            self.select_menu()

    def loop_story(self):
        level = 'lvl' + str(self.user['level'])
        scene = 'scene' + str(self.scene)
        story_level = self.story['story'][level]
        if self.scene == 1:
            print(story_level['title'], '\n\n')
        if self.user['lives'] > 0:
            current_scene = story_level['scenes'][scene]
            print(current_scene, '\n')
            self.select_choice(level, scene)

    def select_choice(self, level, scene):
        scene_choices = self.story['choices'][level][scene]
        print('''What will you do? Type the number of the option or type '/h' to show help.\n''')
        for options, choice in scene_choices.items():
            print(options[-1] + '-', choice.strip())
        option = input()
        if option in ['1', '2', '3']:
            self.show_outcome(level, scene, option)
        elif option in ['/i', '/c', '/h', '/q']:
            exec(f'self.select_{option[-1]}()')
            self.select_choice(level, scene)
        else:
            print('Unknown input! Please enter a valid one.')
            self.select_choice(level, scene)

    def select_i(self):
        print(f'''Inventory: {self.user['inventory']['snack']}, {self.user['inventory']['weapon']}, {self.user['inventory']['tool']}''')

    def select_c(self):
        print(f'''Your character: {self.user['char_attrs']['name']}, {self.user['char_attrs']['species']}, {self.user['char_attrs']['gender']}.''')
        print(f'''Lives remaining: {self.user['lives']}\n''')

    def select_h(self):
        print(textwrap.dedent('''\
        Type the number of the option you want to choose.
        Commands you can use:
        /i => Shows inventory.
        /q => Exits the game.
        /c => Shows the character traits.
        /h => Shows help.
        '''))

    def select_q(self):
        print('You sure you want to quit the game? Y/N')
        choice = input().lower()
        if choice == 'y':
            print('Goodbye!')
            quit()
        elif choice == 'n':
            pass
        else:
            print('Unknown input! Please enter a valid one.')
            self.select_q()

    def show_outcome(self, level, scene, option):
        choice_outcome = self.story['outcomes'][level][scene]['outcome' + str(option)]
        if 'repeat' in choice_outcome:
            print(choice_outcome.split(' (')[0])
            self.select_choice(level, scene)
        elif 'game over' in choice_outcome:
            Data.save_user(self.username, self.user)
            print('Congratulations! You beat the game!')
            quit()
        elif 'save' in choice_outcome:
            self.user['level'] = 2
            self.scene = 1
            Data.save_user(self.username, self.user)
            print(choice_outcome.split(' (')[0])
            print(textwrap.dedent(f'''\
            \nLevel 2\n
            Goodbye!'''))
            self.select_menu()
        elif 'move' in choice_outcome:
            if '''inventory+'key''' in choice_outcome:
                print(choice_outcome.split(' (')[0])
                print('A new item has been added to your inventory: Key\n')
                self.user['inventory']['extra'] = 'key'
            elif 'tool' in choice_outcome:
                print(choice_outcome.replace('{tool}', self.user['inventory']['tool'] + '.').split(' (')[0])
            self.scene += 1
            self.loop_story()
        elif 'life-1' in choice_outcome:
            print(choice_outcome.split(' (')[0])
            self.check_lives()
        elif choice_outcome['option1']:
            print(choice_outcome['option1'].split(' (')[0])
            print('An item has been removed from your inventory: Key\n')
            self.user['inventory']['extra'] = 'None'
            self.scene += 1
            self.loop_story()
        elif choice_outcome['option2'].split(' (')[0]:
            print(choice_outcome['option2'])
            self.select_choice(level, scene)

    def check_lives(self):
        self.user['lives'] -= 1
        if self.user['lives'] >= 1:
            print(f'''You died! Life count: {self.user['lives']}''')
            self.loop_story()
        else:
            print(textwrap.dedent(f'''\
            You died! Life count: {self.user['lives']}
            You've run out of lives! Game over!\n'''))
            self.scene = 1
            self.select_menu()


class User:

    def __init__(self):
        self.user = {}
        self.character = dict(name=None, species=None, gender=None)
        self.inventory = dict(snack=None, weapon=None, tool=None)

    def create(self):
        self.create_character()
        self.stock_inventory()
        self.select_difficulty()
        self.review_character()
        return self.user

    def create_character(self):
        count = '123'
        print('Create your character:')
        for i, attribute in zip(count, self.character):
            print(f'{i}- {attribute}')
            self.character[attribute] = input()
        self.user['char_attrs'] = self.character

    def stock_inventory(self):
        print('Pack your bag for the journey:')
        prompt = '1- Favourite Snack', '2- A weapon for the journey', '3- A traversal tool'
        for option, item in zip(prompt, self.inventory):
            print(option)
            self.inventory[item] = input()
        self.user['inventory'] = self.inventory

    def select_difficulty(self):
        print(textwrap.dedent('''\
            Choose your difficulty:1
            1- Easy
            2- Medium
            3- Hard'''))
        self.user['difficulty'] = None
        while not self.user['difficulty']:
            choice = input().lower()
            if choice in ['1', 'easy']:
                self.user['difficulty'] = 'easy'
                self.user['lives'] = 1
            elif choice in ['2', 'medium']:
                self.user['difficulty'] = 'medium'
                self.user['lives'] = 3
            elif choice in ['3', 'hard']:
                self.user['difficulty'] = 'hard'
                self.user['lives'] = 5
            else:
                print('Unknown input! Please enter a valid one.')
                self.user['difficulty'] = None
        self.user['level'] = 1

    def review_character(self):
        print(textwrap.dedent(f'''\
        Good luck on your journey!
        Your character: {self.character['name']}, {self.character['species']}, {self.character['gender']}
        Your inventory: {self.inventory['snack']}, {self.inventory['weapon']}, {self.inventory['tool']}
        Difficulty: {self.user['difficulty']}
        Number of lives: {self.user['lives']}'''))


class Data:

    @staticmethod
    def load_story():
        file = os.path.join(os.getcwd(), 'story', 'story.json')
        with open(file) as game_story:
            return json.load(game_story)

    @staticmethod
    def save_user(user, data):
        file = os.path.join(os.getcwd(), 'game', 'saves', user + '.json')
        with open(file, 'w+') as new_user:
            json.dump(data, new_user)

    @staticmethod
    def load_user():
        directory = os.path.join(os.getcwd(), 'game', 'saves')
        users = os.listdir(directory)
        if not directory:
            return None
        else:
            print('Type your user name from the list:')
            for username in users:
                print(username.replace('.json', ''))
            print('Type your user name:')
            user = input() + '.json'
            if user in users:
                file = os.path.join(os.getcwd(), 'game', 'saves', user)
                with open(file) as past_user:
                    return json.load(past_user)
            else:
                return None


text_adventure = Game()
text_adventure.select_menu()
