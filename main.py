import textwrap

import np
import sqlalchemy.orm
import tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sqlalchemy import create_engine, Column, Integer, String, Boolean, MetaData, desc, func
from sqlalchemy.orm import sessionmaker
from PIL import Image
from customtkinter import *
from CTkTable import *
import matplotlib.pyplot as plt


engine = create_engine('sqlite:///books.db', echo=True)
Base = sqlalchemy.orm.declarative_base()


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    author = Column(String)
    title = Column(String)
    year = Column(Integer)
    numberOfPages = Column(Integer)
    isFinished = Column(Boolean)
    isFavorite = Column(Boolean)
    rating = Column(Integer)


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

FONT_25_B = ("Helvetica", 25, "bold")
FONT_20_B = ("Helvetica", 20, "bold")
FONT_15_B = ("Helvetica", 15, "bold")
FONT_15 = ("Helvetica", 15)


def get_img(image):
    img = Image.open(f"Images/{image}")
    img_resize = img.resize((100, 100))
    confirm_img = CTkImage(img_resize)
    return confirm_img


def add_from_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'r') as file:
                book_details_list = []
                current_book = {}

                for line in file:
                    parts = line.strip().split(': ')
                    if len(parts) == 2:

                        key, value = parts

                        if key == 'Year' or key == 'Number of Pages':
                            current_book[key.lower().replace(' ', '_')] = int(value)
                        elif key == 'Finished' or key == 'Favorite':
                            current_book['is' + key] = value.lower() == 'yes'
                        else:
                            current_book[key.lower()] = value

                    if not line.strip() and current_book:
                        current_book['numberOfPages'] = current_book.pop('number_of_pages', None)
                        book_details_list.append(current_book)
                        current_book = {}

                if current_book:
                    current_book['numberOfPages'] = current_book.pop('number_of_pages', None)
                    book_details_list.append(current_book)

                for book_details in book_details_list:
                    book = Book(**book_details)
                    session.add(book)

            session.commit()

        except Exception as e:
            print(f"Error: {e}")


def export_library():
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "a") as file:
            file.write("|Your Biblio Library| \n\n")
            engine_ = create_engine('sqlite:///books.db')
            metadata = MetaData()
            metadata.reflect(bind=engine_)
            books_table = metadata.tables['books']
            with engine.connect() as connection:
                query = books_table.select()
                result = connection.execute(query)
                for row in result:
                    book_info = f"""
                    ID: {row[0]}
                    Title: {row[2]}
                    Author: {row[1]}
                    Year: {row[3]}
                    Number of Pages: {row[4]}
                    Finished: {'Yes' if row[5] else 'No'}
                    Favorite: {'Yes' if row[6] else 'No'}
                    Rating : {row[7]}
                    """
                    formatted_book_info = textwrap.dedent(book_info).strip()
                    file.write(formatted_book_info + "\n\n")


def show_to_read_list():
    number_of_unfinished_books = session.query(Book).filter_by(isFinished=False).count()
    to_read_list_window = CTkToplevel(window)
    to_read_list_window.after(10, to_read_list_window.lift)
    to_read_list_window.title("To Read List")
    unfinished_books = session.query(Book.title, Book.author, Book.year, Book.numberOfPages, Book.rating) \
        .filter_by(isFinished=False).order_by(Book.title).all()
    book_list = [book for book in unfinished_books]

    if number_of_unfinished_books < 5:
        to_read_list_window.geometry("750x300+600+200")
    else:
        to_read_list_window.geometry(f"750x{number_of_unfinished_books * 40}+600+300")

    to_read_table = CTkTable(to_read_list_window, row=number_of_unfinished_books, column=5, values=book_list)
    to_read_table.place(x=20, y=50)
    title_label = CTkLabel(to_read_list_window, text="title", font=FONT_20_B)
    title_label.place(x=75, y=20)
    author_label = CTkLabel(to_read_list_window, text="author", font=FONT_20_B)
    author_label.place(x=205, y=20)
    year_label = CTkLabel(to_read_list_window, text="year", font=FONT_20_B)
    year_label.place(x=360, y=20)
    pages_label = CTkLabel(to_read_list_window, text="pages", font=FONT_20_B)
    pages_label.place(x=490, y=20)
    rating_label = CTkLabel(to_read_list_window, text="rating", font=FONT_20_B)
    rating_label.place(x=628, y=20)


def show_favorites_list():
    number_of_favorite_books = session.query(Book).filter_by(isFavorite=True).count()
    favorites_list_window = CTkToplevel(window)
    favorites_list_window.after(10, favorites_list_window.lift)
    favorites_list_window.title("Favorite Books")
    favorite_books = session.query(Book.title, Book.author, Book.year, Book.numberOfPages, Book.rating).filter_by(
        isFavorite=True).order_by(Book.title).all()
    book_list = [book for book in favorite_books]

    if number_of_favorite_books < 5:
        favorites_list_window.geometry("750x300+600+200")
    else:
        favorites_list_window.geometry(f"750x{number_of_favorite_books * 40}+600+300")

    favorites_table = CTkTable(favorites_list_window, row=number_of_favorite_books, column=5, values=book_list)
    favorites_table.place(x=20, y=50)
    title_label = CTkLabel(favorites_list_window, text="title", font=FONT_20_B)
    title_label.place(x=75, y=20)
    author_label = CTkLabel(favorites_list_window, text="author", font=FONT_20_B)
    author_label.place(x=205, y=20)
    year_label = CTkLabel(favorites_list_window, text="year", font=FONT_20_B)
    year_label.place(x=360, y=20)
    pages_label = CTkLabel(favorites_list_window, text="pages", font=FONT_20_B)
    pages_label.place(x=490, y=20)
    rating_label = CTkLabel(favorites_list_window, text="rating", font=FONT_20_B)
    rating_label.place(x=630, y=20)


def current_read():
    def update_last_read_frame():

        global last_book_title_label
        global lastBookAuthorLabel
        global last_read_frame

        last_book = session.query(Book).filter_by(isFinished=True).order_by(desc(Book.id)).first()

        if last_book:
            if last_book_title_label:
                last_book_title_label.destroy()
            if lastBookAuthorLabel:
                lastBookAuthorLabel.destroy()

            last_book_title_label = CTkLabel(last_read_frame, text=f"{last_book.title}", font=("Helvetica", 40, "bold"))
            last_book_title_label.place(x=20, y=60)
            lastBookAuthorLabel = CTkLabel(last_read_frame, text=f"by {last_book.author}", font=("Helvetica", 15))
            lastBookAuthorLabel.place(x=23, y=100)

        else:
            pass

    def add_current_read():

        def close_window():
            invalid_input.destroy()

        def save_book_info():

            global current_book_info
            global pages_read
            global cr_title, cr_author

            book_author = author_entry.get()
            book_title = title_entry.get()
            book_length = length_entry.get()
            book_year = year_entry.get()

            if book_author != "" and book_title != "" and book_length != "" and book_year != "":
                current_book_info = {
                    'author': book_author,
                    'title': book_title,
                    'numberOfPages': book_length,
                    'year': book_year
                }
                add_current_read_window.destroy()

                cr_title = CTkLabel(current_read_frame, text=current_book_info['title'], font=FONT_25_B)
                cr_title.place(x=20, y=50)
                cr_author = CTkLabel(current_read_frame, text=f"by {current_book_info['author']}", font=FONT_15)
                cr_author.place(x=20, y=75)
                pages_read = CTkLabel(current_read_frame, text=f"0 / {current_book_info['numberOfPages']}  (0%)",
                                      font=FONT_20_B)
                pages_read.place(x=20, y=100)

            else:

                global invalid_input
                invalid_input_ = CTkToplevel(add_current_read_window)
                invalid_input_.after(10, invalid_input_.lift)
                invalid_input_.title("Invalid Input")
                invalid_input_.geometry("200x100+1100+400")
                confirm_img_ = get_img("confirm_image.png")
                invalid_input_.image = confirm_img_
                not_found_label = CTkLabel(invalid_input_, text="Invalid Input!", font=FONT_25_B)
                not_found_label.place(x=20, y=10)
                confirm_button_ = CTkButton(invalid_input_, image=confirm_img_, text="", width=160, height=40,
                                            command=close_window)
                confirm_button_.place(x=20, y=50)

        addBook.destroy()
        create_finished_button()
        create_update_progress_button()
        add_current_read_window = CTkToplevel(current_read_frame)
        add_current_read_window.after(10, add_current_read_window.lift)
        add_current_read_window.protocol("WM_DELETE_WINDOW", add_current_read_window)
        add_current_read_window.title("Add Current Read")
        add_current_read_window.geometry("350x210+650+300")
        confirm_img = get_img("confirm_image.png")
        add_current_read_window.image = confirm_img
        author_label = CTkLabel(add_current_read_window, text="Author:", font=FONT_25_B)
        author_label.place(x=20, y=13)
        author_entry = CTkEntry(add_current_read_window, width=220, font=FONT_25_B)
        author_entry.place(x=120, y=10)
        title_label = CTkLabel(add_current_read_window, text="Title:", font=FONT_25_B)
        title_label.place(x=20, y=65)
        title_entry = CTkEntry(add_current_read_window, width=220, font=FONT_25_B)
        title_entry.place(x=120, y=60)
        length_label = CTkLabel(add_current_read_window, text="Pages:", font=FONT_25_B)
        length_label.place(x=20, y=115)
        length_entry = CTkEntry(add_current_read_window, width=70, font=FONT_25_B)
        length_entry.place(x=120, y=110)
        year_label = CTkLabel(add_current_read_window, text="Year:", font=FONT_25_B)
        year_label.place(x=20, y=165)
        year_entry = CTkEntry(add_current_read_window, width=70, font=FONT_25_B)
        year_entry.place(x=120, y=160)
        confirm_button = CTkButton(add_current_read_window, width=140, text="", image=confirm_img, height=40,
                                   command=save_book_info)
        confirm_button.place(x=200, y=158)

    def update_progress():

        def close_window():
            invalid_input_.destroy()

        global pages_read
        global progress_window
        global progress_entry

        progress_value = int(progress_entry.get()) if progress_entry.get().isdigit() else 0

        if progress_value != "" and progress_value < int(current_book_info['numberOfPages']):

            current_progress = int(progress_value)
            total_pages = int(current_book_info['numberOfPages'])
            pages_text = f"{current_progress} / {total_pages}  ({round((current_progress / total_pages) * 100, 2)}%)"

            if not pages_read:

                pages_read = CTkLabel(current_read_frame, text=pages_text, font=FONT_20_B)
                pages_read.place(x=20, y=100)

            else:

                pages_read.configure(text=pages_text)

            progress_window.destroy()

        else:

            invalid_input_ = CTkToplevel(progress_window)
            invalid_input_.after(10, invalid_input_.lift)
            invalid_input_.title("Invalid Input")
            invalid_input_.geometry("190x120+700+600")
            confirm_img = get_img("confirm_image.png")
            invalid_input_.image = confirm_img
            not_found_label = CTkLabel(invalid_input_, text="Invalid Input!", font=FONT_25_B)
            not_found_label.place(x=20, y=20)
            confirm_button = CTkButton(invalid_input_, image=confirm_img, text="", width=155, height=40,
                                       command=close_window)
            confirm_button.place(x=20, y=60)

    def update_progress_window():

        global progress_entry
        global progress_window

        progress_window = CTkToplevel(current_read_frame)
        progress_window.title("Update Progress")
        progress_window.geometry("350x130+600+300")
        progress_window.after(10, progress_window.lift)
        progress_label1 = CTkLabel(progress_window, text="Currently on", font=FONT_25_B)
        progress_label1.place(x=20, y=20)
        progress_entry = CTkEntry(progress_window, width=70, height=40, font=FONT_25_B)
        progress_entry.place(x=180, y=15)
        progress_label2 = CTkLabel(progress_window, text=f"of {current_book_info['numberOfPages']}", font=FONT_25_B)
        progress_label2.place(x=260, y=20)
        update_button = CTkButton(progress_window, text="Update Progress", font=FONT_25_B, command=update_progress)
        update_button.place(x=70, y=80)

    def create_add_button():

        global addBook

        addBook = CTkButton(current_read_frame, text="Add CR", width=50, font=FONT_15_B, command=add_current_read)
        addBook.place(x=225, y=5)

    def create_update_progress_button():

        global update_progress_button
        global progress_entry

        update_progress_button = CTkButton(current_read_frame, text="Update Progress", width=100,
                                           font=FONT_15_B, command=update_progress_window)
        update_progress_button.place(x=6, y=165)

    def create_finished_button():

        def add_to_db():

            def close_window():
                invalid_input.destroy()

            global cr_title, cr_author
            global update_progress_button
            global current_book_info
            global progress_entry

            title = current_book_info['title']
            author = current_book_info['author']
            pages = current_book_info['numberOfPages']
            year = current_book_info['year']
            is_finished = True
            is_favorite = is_fav_checkbox.get()

            try:
                rating = int(rating_entry.get())
                if 1 <= rating <= 10:
                    book_to_add = Book(title=title, author=author, numberOfPages=pages, isFavorite=is_favorite,
                                       isFinished=is_finished, year=year, rating=rating)
                    session.add(book_to_add)
                    session.commit()
                    update_last_read_frame()
                    update_last_five_reads_frame()

                    is_favorite_window.destroy()
                    current_book_info = {}

                    im_finished.destroy()
                    update_progress_button.destroy()
                    create_add_button()

                    cr_title.destroy()
                    cr_author.destroy()
                    pages_read.destroy()
                else:
                    global invalid_input

                    invalid_input = CTkToplevel(is_favorite_window)
                    invalid_input.after(10, invalid_input.lift)
                    invalid_input.title("Invalid Input")
                    invalid_input.geometry("200x100+1100+400")
                    confirm_img_ = get_img("confirm_image.png")
                    invalid_input.image = confirm_img_
                    not_found_label = CTkLabel(invalid_input, text="Invalid Input!",
                                               font=FONT_25_B)
                    not_found_label.place(x=20, y=10)
                    confirm_button_ = CTkButton(invalid_input, image=confirm_img_, text="", width=160, height=40,
                                                command=close_window)
                    confirm_button_.place(x=20, y=50)
            except ValueError:
                print("Error")


        def book_finished():
            global is_fav_checkbox
            global rating_entry
            global is_favorite_window
            global progress_entry

            is_favorite_window = CTkToplevel(window)
            is_favorite_window.after(10, is_favorite_window.lift)
            is_favorite_window.title("Is Favorite?")
            is_favorite_window.geometry("470x120+600+400")
            confirm_img = get_img("confirm_image.png")
            is_favorite_window.image = confirm_img
            question_label = CTkLabel(is_favorite_window, text="Was this book your favorite?", font=FONT_25_B)
            question_label.place(x=20, y=15)
            is_fav_checkbox = CTkCheckBox(is_favorite_window, text="")
            is_fav_checkbox.place(x=370, y=18)
            rating = CTkLabel(is_favorite_window, text="Rating 1-10:", font=FONT_25_B)
            rating.place(x=20, y=60)
            rating_entry = CTkEntry(is_favorite_window, font=FONT_25_B, width=70)
            rating_entry.place(x=180, y=58)
            confirm_button = CTkButton(is_favorite_window, text="", image=confirm_img, width=40, height=30,
                                       command=add_to_db)
            confirm_button.place(x=410, y=16)

        im_finished = CTkButton(current_read_frame, text="I'm finished!", width=100, font=FONT_15_B,
                                command=book_finished)
        im_finished.place(x=195, y=165)

    current_read_frame = CTkFrame(window, width=300, height=200)
    current_read_frame.place(x=35, y=530)
    current_read_label = CTkLabel(current_read_frame, text="Current Read", font=("Helvetica", 15, "bold"))
    current_read_label.place(x=10, y=3)
    create_add_button()


last_book_title_label = None
lastBookAuthorLabel = None


def last_read():
    global last_book_title_label
    global lastBookAuthorLabel
    global last_read_frame

    def update_last_read_frame():

        global last_book_title_label
        global lastBookAuthorLabel

        last_book = session.query(Book).filter_by(isFinished=True).order_by(desc(Book.id)).first()

        if last_book:
            if last_book_title_label:
                last_book_title_label.destroy()
            if lastBookAuthorLabel:
                lastBookAuthorLabel.destroy()

            last_book_title_label = CTkLabel(last_read_frame, text=f"{last_book.title}",
                                             font=("Helvetica", 40, "bold"))
            last_book_title_label.place(x=20, y=60)
            lastBookAuthorLabel = CTkLabel(last_read_frame, text=f"by {last_book.author}", font=FONT_15)
            lastBookAuthorLabel.place(x=23, y=100)

        else:
            pass

    last_read_frame = CTkFrame(window, width=300, height=200)
    last_read_frame.place(x=395, y=530)
    last_read_label = CTkLabel(last_read_frame, text="Last Read", font=FONT_15_B)
    last_read_label.place(x=10, y=3)
    update_last_read_frame()


def update_last_five_reads_frame():
    for widget in last_five_reads_frame.winfo_children():
        widget.destroy()

    last_five_reads_label = CTkLabel(last_five_reads_frame, text="Last 5 Reads", font=FONT_25_B)
    last_five_reads_label.place(x=74, y=8)

    last_five_books = session.query(Book).filter_by(isFinished=True).order_by(desc(Book.id)).limit(5).all()

    y_pos = 50
    yy_pos = 81

    for book in last_five_books[:5]:
        book_label = CTkLabel(last_five_reads_frame, text=book.title, font=("Helvetica", 30, "bold"))
        book_label.place(x=10, y=y_pos)
        author_label = CTkLabel(last_five_reads_frame, text=f"by {book.author}", font=FONT_15)
        author_label.place(x=15, y=yy_pos)
        y_pos += 73
        yy_pos += 73


def last_five_reads():
    global last_five_reads_frame

    last_five_reads_frame = CTkFrame(window, width=370, height=400)
    last_five_reads_frame.place(x=360, y=60)

    update_last_five_reads_frame()

def show_graph():
    ratings_count = session.query(Book.rating, func.count(Book.id)).group_by(Book.rating).all()
    ratings_count_np = np.array(ratings_count)

    ratings = ratings_count_np[:, 0]
    counts = ratings_count_np[:, 1]

    plt.bar(ratings, counts, color='blue', alpha=0.7)
    plt.xlabel('Rating')
    plt.ylabel('Number of Books')
    plt.title('Number of Books for Each Rating')
    plt.yticks(np.arange(0, max(counts) + 1, step=1))
    plt.xticks(range(1, 11))
    plt.show()


def window_f():
    # Config
    global window

    window = CTk()
    window.title("Biblio")
    window.geometry("750x800+200+50")

    # Buttons
    add_book = CTkButton(window, text="ADD BOOK", font=FONT_25_B, width=280, height=50, corner_radius=30,
                         command=show_add_book_window)
    add_book.place(x=45, y=30)

    remove_book = CTkButton(window, text="REMOVE BOOK", font=FONT_25_B, width=280, height=50, corner_radius=30,
                            command=show_remove_book_window)
    remove_book.place(x=45, y=100)

    add_via_file = CTkButton(window, text="ADD VIA FILE", font=FONT_25_B, width=280, height=50, corner_radius=30,
                             command=add_from_file)
    add_via_file.place(x=45, y=170)

    export_file = CTkButton(window, text="EXPORT FILE", font=FONT_25_B, width=280, height=50, corner_radius=30,
                            command=export_library)
    export_file.place(x=45, y=240)

    to_read_list = CTkButton(window, text="TO READ LIST", font=FONT_25_B, width=280, height=50, corner_radius=30,
                             command=show_to_read_list)
    to_read_list.place(x=45, y=310)

    favorites_list = CTkButton(window, text="FAVORITES LIST", font=FONT_25_B, width=280, height=50, corner_radius=30,
                               command=show_favorites_list)
    favorites_list.place(x=45, y=380)

    graph = CTkButton(window, text="GRAPH", font=FONT_25_B, width=280, height=50, corner_radius=30, command=show_graph)
    graph.place(x=45, y=450)

    current_read()

    last_read()

    last_five_reads()

    window.mainloop()


def show_remove_book_window():
    def close_window():

        book_not_found.destroy()

    def remove_book():

        book_name = u_input.get()
        book_to_delete = session.query(Book).filter_by(title=book_name).first()

        if book_to_delete:

            session.delete(book_to_delete)
            session.commit()
            remove_book_window.destroy()
            update_last_five_reads_frame()

        else:

            global book_not_found

            book_not_found = CTkToplevel(remove_book_window)
            book_not_found.after(10, book_not_found.lift)
            book_not_found.title("Book Not Found")
            book_not_found.geometry("450x120+700+600")
            confirm_img_ = get_img("confirm_image.png")
            book_not_found.image = confirm_img_
            not_found_label = CTkLabel(book_not_found, text="Book was not found in your library!", font=FONT_25_B)
            not_found_label.place(x=20, y=20)
            confirm_button_ = CTkButton(book_not_found, image=confirm_img_, text="", width=415, height=40,
                                        command=close_window)
            confirm_button_.place(x=20, y=60)

    # Config
    remove_book_window = CTkToplevel(window)
    remove_book_window.after(10, remove_book_window.lift)
    remove_book_window.title("Remove Book")
    remove_book_window.geometry("420x110+700+400")
    confirm_img = get_img("confirm_image.png")
    remove_book_window.image = confirm_img
    question = CTkLabel(remove_book_window, text="Which book would you want to remove?", font=FONT_20_B)
    question.place(x=20, y=20)
    u_input = CTkEntry(remove_book_window, font=FONT_25_B, width=230)
    u_input.place(x=20, y=60)
    confirm_button = CTkButton(remove_book_window, image=confirm_img, text="", width=140, height=40,
                               command=remove_book)
    confirm_button.place(x=260, y=58)


def show_add_book_window():
    global current_book_info

    def close_window():
        invalid_input.destroy()

    def add_book():
        def update_last_read_frame():
            global last_book_title_label
            global lastBookAuthorLabel

            last_book = session.query(Book).filter_by(isFinished=True).order_by(desc(Book.id)).first()

            if last_book:

                global last_read_frame

                if last_book_title_label:
                    last_book_title_label.destroy()
                if lastBookAuthorLabel:
                    lastBookAuthorLabel.destroy()

                last_book_title_label = CTkLabel(last_read_frame, text=f"{last_book.title}",
                                                 font=("Helvetica", 40, "bold"))
                last_book_title_label.place(x=20, y=60)
                lastBookAuthorLabel = CTkLabel(last_read_frame, text=f"by {last_book.author}", font=FONT_15_B)
                lastBookAuthorLabel.place(x=23, y=100)

            else:
                pass

        if (author_entry.get() != "" and book_entry.get() != "" and length_entry.get() != "" and
                year_published_entry.get() != "" and 1 <= int(rating_entry.get()) <= 10):

            finished = False
            favorite = False

            if is_finished.get() == 1:
                finished = True

            if is_favorite.get() == 1:
                favorite = True

            book_to_add = Book(author=author_entry.get(), title=book_entry.get(), numberOfPages=length_entry.get(),
                               year=year_published_entry.get(), isFavorite=favorite, isFinished=finished, rating=int(rating_entry.get()))
            session.add(book_to_add)
            session.commit()
            update_last_read_frame()
            update_last_five_reads_frame()
            add_book_window.destroy()

        else:

            global invalid_input

            invalid_input = CTkToplevel(add_book_window)
            invalid_input.after(10, invalid_input.lift)
            invalid_input.title("Invalid Input")
            invalid_input.geometry("200x100+1100+400")
            confirm_img_ = get_img("confirm_image.png")
            invalid_input.image = confirm_img_
            not_found_label = CTkLabel(invalid_input, text="Invalid Input!",
                                       font=FONT_25_B)
            not_found_label.place(x=20, y=10)
            confirm_button_ = CTkButton(invalid_input, image=confirm_img_, text="", width=160, height=40,
                                        command=close_window)
            confirm_button_.place(x=20, y=50)

    add_book_window = CTkToplevel(window)
    add_book_window.after(10, add_book_window.lift)
    add_book_window.title("Add Book")
    add_book_window.geometry("360x460+700+300")
    confirm_img = get_img("confirm_image.png")
    add_book_window.image = confirm_img

    author_label = CTkLabel(add_book_window, text="Author:", font=FONT_25_B)
    author_label.place(x=20, y=20)
    author_entry = CTkEntry(add_book_window, font=FONT_25_B, width=200)
    author_entry.place(x=130, y=20)
    book_label = CTkLabel(add_book_window, text="Title:", font=FONT_25_B)
    book_label.place(x=20, y=80)
    book_entry = CTkEntry(add_book_window, font=FONT_25_B, width=200)
    book_entry.place(x=130, y=80)
    length_label = CTkLabel(add_book_window, text="Pages:", font=FONT_25_B)
    length_label.place(x=20, y=140)
    length_entry = CTkEntry(add_book_window, font=FONT_25_B, width=70)
    length_entry.place(x=130, y=140)
    year_published = CTkLabel(add_book_window, text="Year:", font=FONT_25_B)
    year_published.place(x=20, y=200)
    year_published_entry = CTkEntry(add_book_window, font=FONT_25_B, width=70)
    year_published_entry.place(x=130, y=200)
    rating_label = CTkLabel(add_book_window, text="Rating 1-10:", font=FONT_25_B)
    rating_label.place(x=20, y=260)
    rating_entry = CTkEntry(add_book_window, font=FONT_25_B, width=70)
    rating_entry.place(x=180, y=257)
    is_finished_label = CTkLabel(add_book_window, text="Finished?", font=FONT_25_B)
    is_finished_label.place(x=20, y=310)
    is_finished = CTkCheckBox(add_book_window, text="")
    is_finished.place(x=150, y=313)
    is_favorite_label = CTkLabel(add_book_window, text="Favorite?", font=FONT_25_B)
    is_favorite_label.place(x=20, y=350)
    is_favorite = CTkCheckBox(add_book_window, text="")
    is_favorite.place(x=150, y=353)
    confirm_button = CTkButton(add_book_window, image=confirm_img, text="", width=320, height=50, command=add_book)
    confirm_button.place(x=20, y=400)


window_f()
