import re
import pickle
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate_phone():
            raise ValueError("Invalid phone number format.")

    def validate_phone(self):
        return re.match(r'^\d{10}$', self.value) is not None

class Birthday(Field):
    def __init__(self, value):
        date_format = "%d.%m.%Y"
        try:
            self.date = datetime.strptime(value, date_format).date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found.")

    def edit_phone(self, new_phone):
        if self.phones:
            self.phones[0] = Phone(new_phone)
        else:
            self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        raise ValueError("Phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phone: {'; '.join(str(p) for p in self.phones)}"

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError("Contact not found.")

    def find_next_weekday(self, d, weekday): 
        days_ahead = weekday - d.weekday()
        if days_ahead <= 0:  
            days_ahead += 7
        return d + timedelta(days_ahead)

    def get_upcoming_birthdays(self, days=7) -> list:
        today = datetime.today().date()
        upcoming_birthdays = []

        for user in self.data.values():
            if user.birthday is None:
                continue
            birthday_this_year = user.birthday.date.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:  
                    birthday_this_year = self.find_next_weekday(
                        birthday_this_year, 0
                    )  

                congratulation_date_str = birthday_this_year.strftime("%Y.%m.%d")
                upcoming_birthdays.append(f"User {user.name.value} has a birthday this week! {congratulation_date_str}")

        return upcoming_birthdays

def save_data(book, filename="phonebook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="phonebook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return AddressBook()  

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Enter user name."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Enter the argument for the command."
    return inner

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        return "Please provide both name and phone number."
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) < 2:
        return "Please provide both name and new phone number."
    name, new_phone, *_ = args
    record = book.find(name)
    if record:
        record.edit_phone(new_phone)
        return "Contact updated."
    else:
        raise KeyError

@input_error
def show_phone(args, book):
    if len(args) < 1:
        return "Please provide the name."
    (name,) = args
    record = book.find(name)
    if record:
        return "; ".join([str(phone) for phone in record.phones])
    else:
        raise KeyError

def show_all(book):
    return "\n".join([str(record) for record in book.data.values()])

@input_error
def add_birthday(args, book):
    if len(args) < 2:
        return "Please provide both name and birthday."
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    if len(args) < 1:
        return "Please provide the name."
    (name,) = args
    record = book.find(name)
    if record:
        if record.birthday:
            return str(record.birthday)
        else:
            return "Birthday not set."
    else:
        raise KeyError


def main():
    book = load_data()
    print("Welcome, USER! This is your personal bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("You'll be back, right? :C")
            save_data(book)
            break

        elif command == "hello":
            print("Hello there!\n*That was Star Wars Reference ^_^*\nHow can I help, partner?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            birthdays = book.get_upcoming_birthdays()
            if not len(birthdays):
                print("There are no upcoming birthdays.")
                continue
            for day in birthdays:
                print(f"{day}")

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
