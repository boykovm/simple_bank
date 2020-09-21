# генерируем номер карты и пин номер
import random
import sqlite3


# connection to database
conn = sqlite3.connect('card.s3db')
global cur
cur = conn.cursor()


# creating table
cur.execute('drop table if exists card')
cur.execute('create table if not exists card(id INTEGER PRIMARY KEY,number TEXT, pin TEXT, balance INTEGER DEFAULT 0)')
conn.commit()


global current_card, is_quit
current_card = None
is_quit = False


def luhn_algoritm(number):
    l = []
    for i in range(15):
        l.append(int(str(number)[i]))
    for i in range(15):
        if i % 2 == 0:
            l[i] = l[i] * 2
    for i in range(15):
        if l[i] > 9:
            l[i] -= 9

    if sum(l) % 10 == 0:
        last_number = '0'
    else:
        last_number = str(10 - sum(l) % 10)

    return last_number


def generate_card_number():
    number = '400000' + "".join([str(random.randint(0, 9)) for i in range(0, 9)])

    last_number = luhn_algoritm(number)

    return str(number) + str(last_number)


def generate_pin():
    pin = "".join([str(random.randint(0, 9)) for i in range(0, 4)])
    return pin


def create_an_account():
    card_number = generate_card_number()
    pin = generate_pin()
    global cur
    cur.execute('insert into card (number, pin) values ({}, {})'.format(card_number, pin))
    conn.commit()
    print('Your card has been created')
    print('Your card number:')
    print(card_number)
    print('Your card PIN:')
    print(pin)
    print()


# показать меню
def show_menu():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit\n")


def show_menu_in():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit\n')


# выбор пользователя первое меню
def user_choice_1():
    choice = input()
    print()
    # while choice.isdigit() != True:
    #     choice = input('enter digits')
    if choice == '1':
        create_an_account()
    elif choice == '2':
        log_in()
    elif choice == '0':
        exit()


# выбор пользователя второе меню
def user_choice_2():
    choice = input()
    print()
    # while choice.isdigit() != True:
    #     choice = input('enter digits')
    if choice == '1':
        balance()
    elif choice == '2':
        add_income()
    elif choice == '3':
        transfer_money()
    elif choice == '4':
        close_account()
    elif choice == '5':
        log_out()
    elif choice == '0':
        exit()


# логинимся
def log_in():
    print('Enter your CARD NUMBER')
    card_num = input()
    global cur, current_card
    card = cur.execute('select number from card where number = "' + str(card_num) + '"')
    card_exists = False
    for i in card:
        card_exists = i[0]
        break
    if card_exists:
        print('Enter your pin')
        input_pin = input()
        pin = cur.execute('select pin from card where number = "' + str(card_num) + '" and pin = "' + str(input_pin) + '"')
        pin_exists = False
        for i in pin:
            pin_exists = i[0]
            break
        if pin_exists:
            print('\nYou have successfully logged in!\n')
            current_card = cur.execute('select id from card where number = "' + str(card_num) + '" and pin = "' + str(input_pin) + '"')
            for i in current_card:
                current_card = i[0]
                break
            show_menu_in()
            user_choice_2()
        else:
            print('Wrong card number or pin')
    else:
        print('Wrong card number or pin')


# выход из аккаунта
def log_out():
    print('You have successfully logged out!\n')
    global current_card
    current_card = None
    show_menu()
    user_choice_1()


# меню баланса
def balance():
    global cur, current_card
    balance = cur.execute('select balance from card where id = "' + str(current_card) + '"')
    for i in balance:
        balance = i[0]
        break

    print('Balance: {}\n'.format(balance))
    show_menu_in()
    user_choice_2()


def add_income():
    add_funds = -1
    print('Enter income:')
    while add_funds <= 0:
        add_funds = int(input())
    global cur, current_card
    funds = cur.execute('select balance from card where id = ' + str(current_card))
    for i in funds:
        funds = i[0]
        break
    funds += add_funds
    cur.execute('update card set balance = ' + str(funds) + ' where id = ' + str(current_card))
    conn.commit()
    print('\nIncome was added!\n')
    show_menu_in()
    user_choice_2()


def transfer_money():
    print('\nTransfer')
    transfer_to = input('Enter card number:\n')

    success = luhn_algoritm(transfer_to[:-1])
    global cur, current_card

    cant_transfer_to = cur.execute('select number from card where id = ' + str(current_card))
    for i in cant_transfer_to:
        cant_transfer_to = i[0]
        break
    can_transfer = True

    card_exists = cur.execute('select number from card where number = "' + str(transfer_to) + '"')
    card_not_exists = True
    for i in card_exists:
        card_not_exists = False
        break

    if success != transfer_to[-1]:
        can_transfer = False
        print("Probably you made a mistake in the card number.\nPlease try again!\n")
    elif cant_transfer_to == transfer_to:
        can_transfer = False
        print("You can't transfer money to the same account!\n")
    elif card_not_exists:
        can_transfer = False
        print("Such a card does not exist.\n")

    if can_transfer:
        would_transfer = int(input('Enter how much money you want to transfer:\n'))
        current_funds = cur.execute('select balance from card where id = ' + str(current_card))
        for i in current_funds:
            current_funds = i[0]
        if would_transfer > current_funds:
            print("Not enough money!\n")
        else:
            print('Success!\n')
            cur.execute('update card set balance = ' + str(current_funds - would_transfer) + ' where id = ' + str(current_card))
            cur.execute('update card set balance = ' + str(would_transfer) + ' where number = "' + str(transfer_to) + '"')
            conn.commit()
    show_menu_in()
    user_choice_2()


def close_account():
    global cur, current_card
    cur.execute('delete from card where id = ' + str(current_card))
    conn.commit()
    current_card = None
    show_menu()
    user_choice_1()


# выход
def exit():
    global is_quit, current_card
    print('Bye!')
    conn.commit()
    current_card = None
    is_quit = True
    return


# работа основной программы


while is_quit == False:
    show_menu()
    user_choice_1()