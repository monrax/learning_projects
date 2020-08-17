from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


class Table(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def add_task(input_task, input_deadline):
    new_row = Table(task=input_task, deadline=input_deadline.date())
    session.add(new_row)
    session.commit()
    print("The task has been added!\n")


def print_tasks(day, today=True):
    tasks = session.query(Table).filter_by(deadline=day.date())
    if today:
        print(f"\n{day.strftime('Today %d %b')}:")
    else:
        print(f"\n{day.strftime('%A %d %b')}:")
    if tasks.count():
        for i, task in enumerate(tasks, 1):
            print(i, task, sep='. ')
    else:
        print("Nothing to do!")
    print()


def print_week_tasks():
    for i in range(7):
        print_tasks(datetime.today() + timedelta(days=i), today=False)


def print_all_tasks():
    tasks = session.query(Table).all()
    print("\nAll tasks:")
    for i, task in enumerate(tasks, 1):
        print(i, task, task.deadline.strftime("%d %b"), sep=". ")
    print()


def print_missed_tasks():
    tasks = session.query(Table).\
        filter(Table.deadline < datetime.today().date()).\
        order_by(Table.deadline)
    print("\nMissed tasks:")
    if tasks.count():
        for i, task in enumerate(tasks, 1):
            print(i, task, task.deadline.strftime("%d %b"), sep=". ")
    else:
        print("Nothing is missed!")
    print()


def delete_task():
    print("Chose the number of the task you want to delete:")
    tasks = session.query(Table).order_by(Table.deadline).all()
    if tasks:
        for i, task in enumerate(tasks, 1):
            print(i, task, task.deadline.strftime("%d %b"), sep=". ")
        choice = int(input('\n'))
        session.delete(tasks[choice - 1])
        session.commit()
        print("The task has been deleted!\n")
    else:
        print("Nothing to delete\n")


while True:
    user_input = input('''1) Today's tasks
                          2) Week's tasks
                          3) All tasks
                          4) Missed tasks
                          5) Add task
                          6) Delete task
                          0) Exit
                          '''.replace("  ", ''))
    if user_input == '0':
        break
    elif user_input == '1':
        print_tasks(datetime.today())
    elif user_input == '2':
        print_week_tasks()
    elif user_input == '3':
        print_all_tasks()
    elif user_input == '4':
        print_missed_tasks()
    elif user_input == '5':
        new_task = input("\nEnter task\n")
        new_deadline = datetime.strptime(
            input("Enter deadline\n"), "%Y-%m-%d")
        add_task(new_task, new_deadline)
    elif user_input == '6':
        delete_task()
print("\nBye!")
