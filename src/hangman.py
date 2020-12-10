import random
import wikiquote


HANGMAN_SYMBOL = r"""
_                                             
|   |                                            
|   |__    __ _ _ __   __ _  _ __ __    _  _ _  _ 
|   '_   \ /  _`  |  '_   \/  _`   |  '_  ` _ \ /  _`  |  '_   \ 
|   |  |   |  (_|  |  |  |  |  (_|   |  |  |  | |  |  (_|  |  |  |  |
|_ |  |_ |\__,_|_|  |_|\ __,  |_|  |_| |_|\__,_ |_|  |_|
                               __/  |                      
                              |___/      
"""

HANGMANPICS = [
r'''
+ ----- +
 |        |
          |
          |
          |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
          |
          |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
 |        |
          |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
/|        |
          |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
/|\       |
          |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
/|\       |
/         |
          |
=========

''',
r'''
+ ----- +
 |        |
O       |
/|\       |
/ \       |
          |
=========

'''
]

WIN_MESSAGE = '''
YOU WIN! CONGRATULATIONS!
'''

LOSE_MESSAGE = '''
GAME OVER
'''

PREVIOUS_TRAIL_MESSAGE = '''
previous trail: '''



HANGMAN_DICT = {}

'''
channel_id:{
    current_state
    current_word
    current_output
    previous_trail
}
'''

def get_current_state(channel_id):
    for key in HANGMAN_DICT.keys():
        if key == channel_id:
            return HANGMAN_DICT[channel_id]['current_state']

def get_current_word(channel_id):
    for key in HANGMAN_DICT.keys():
        if key == channel_id:
            return HANGMAN_DICT[channel_id]['current_word']

def get_current_output(channel_id):
    for key in HANGMAN_DICT.keys():
        if key == channel_id:
            return HANGMAN_DICT[channel_id]['current_output']

def get_previous_trail(channel_id):
    for key in HANGMAN_DICT.keys():
        if key == channel_id:
            return HANGMAN_DICT[channel_id]['previous_trail']

# generat word
def generate_word():
    word_list = wikiquote.quote_of_the_day(lang='en')[0]
    word_list = word_list.split()
    possible_list = []
    for single_word in word_list:
        if single_word.isalpha() and len(single_word) >= 4:
            single_word.lower()
            possible_list.append(single_word)
    if possible_list == []:
        possible_list.append('hello')
    return possible_list[random.randint(0, len(possible_list)-1)]
    


# check if the command is hangman
def hangman_check_message(message):
    word = message.split()
    if len(word) != 2:
        return False
    if word[0] != '/guess':
        return False
    if len(word[1]) != 1:
        return False
    if word[1][0].islower() is False:
        return False
    return True


# get the output message for hangman
def get_hangman(message, channel_id):
    if channel_id not in HANGMAN_DICT.keys():
        HANGMAN_DICT[channel_id] = {
            "current_state": 0,
            "current_word": "",
            "current_output": "",
            "previous_trail": ""
        }
    current_output = get_current_output(channel_id)
    current_word = get_current_word(channel_id)
    current_state = get_current_state(channel_id)

    if current_state == 0:
        current_word = generate_word()
        HANGMAN_DICT[channel_id]['current_word'] = current_word
        for _ in range(0, len(current_word)):
            current_output += ' _'
        HANGMAN_DICT[channel_id]['current_output'] = current_output
        current_state += 1
        HANGMAN_DICT[channel_id]['current_state'] = current_state
    word = message.split()
    character = word[1][0]
    hangman_add_word(character, channel_id)
    current_output = get_current_output(channel_id)
    previous_trail = get_previous_trail(channel_id)
    current_state = get_current_state(channel_id)
    new_message = message
    new_message += HANGMAN_SYMBOL
    new_message += HANGMANPICS[current_state-1]
    if current_state == 7:  # if lose the game, print lost and reset
        new_message += get_current_word(channel_id)
        new_message += LOSE_MESSAGE
        #current_state = 0
        #current_word = ''
        #current_output = ''
        #previous_trail = ''
        del HANGMAN_DICT[channel_id]
    elif '_' not in current_output: # if win the game, print congrats and reset
        new_message += get_current_word(channel_id)
        new_message += WIN_MESSAGE
        #current_state = 0
        #current_word = ''
        #current_output = ''
        #previous_trail = ''
        del HANGMAN_DICT[channel_id]
    else: # not finish, print the current state
        new_message += get_current_output(channel_id)
        new_message += PREVIOUS_TRAIL_MESSAGE
        new_message += previous_trail
        HANGMAN_DICT[channel_id]['current_output'] = current_output
        HANGMAN_DICT[channel_id]['previous_trail'] = previous_trail
        HANGMAN_DICT[channel_id]['current_state'] = current_state
    return new_message


# 1 for found character
# 2 for not found
# 3 for nothing happened(unput the same word twice)
def hangman_add_word(character, channel_id):
    current_output = get_current_output(channel_id)
    current_word = get_current_word(channel_id)
    current_state = get_current_state(channel_id)
    previous_trail = get_previous_trail(channel_id)

    if character in current_output:
        pass
    previous_trail += character
    previous_trail += ' '
    if character in current_word:
        for i in range(0, len(current_word)):
            if current_word[i] == character:
                current_output = current_output[:2*i] + ' ' + character + current_output[(i+1)*2:] 
    else:
        current_state += 1

    HANGMAN_DICT[channel_id]['current_output'] = current_output
    HANGMAN_DICT[channel_id]['current_word'] = current_word
    HANGMAN_DICT[channel_id]['previous_trail'] = previous_trail
    HANGMAN_DICT[channel_id]['current_state'] = current_state


def check_hangman(message, channel_id):
    if hangman_check_message(message) is True:
        message = get_hangman(message, channel_id)  
    return message
'''

if __name__ == "__main__":
    if hangman_check_message('/guess a') is True:
        message = get_hangman('/guess a', 1)  
        print(message)

'''