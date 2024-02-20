from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Button, Footer, Label, ListItem, ListView, Input, Static


class Library:
    def __init__(self, file_name: str) -> None:
        self.file = open(file_name, "a+")
        self.file.seek(0)
        self.__books: list[dict[str, str]] = []
        self.__parse_books()

    def __del__(self) -> None:
        self.file.close()

    def __parse_books(self):
        book_list = self.file.read()
        lines = book_list.splitlines()
        for line in lines:
            book = line.split(",")
            self.__books.append({
                "title": book[0],
                "author": book[1],
                "release_year": book[2],
                "pages": book[3]
            })

    def __write_books(self):
        self.file.seek(0)
        self.file.truncate()
        for book in self.__books:
            self.file.write(f"{book["title"]},{book["author"]},{book["release_year"]},{book["pages"]}\n")
        self.file.flush()

    def add_book(self, book: dict[str, str]) -> int:
        try:
            self.file.write(f"{book["title"]},{book["author"]},{book["release_year"]},{book["pages"]}\n")
            self.file.flush()
            self.__books.append(book)
        except Exception as err:
            print(err)

        return self.__books.index(book)

    def edit_book(self, old_title: str, edited_book: dict[str, str]) -> int:
        book = next((book for book in self.__books if book["title"] == old_title), None)
        book["title"] = edited_book["title"]
        book["author"] = edited_book["author"]
        book["release_year"] = edited_book["release_year"]
        book["pages"] = edited_book["pages"]
        self.__write_books()

        return self.__books.index(book)

    def remove_book(self, title: str) -> None:
        book = next((book for book in self.__books if book["title"] == title), None)
        self.__books.remove(book)
        self.__write_books()

    @property
    def books(self) -> list[dict[str, str]]:
        return self.__books


class BookList(ListView):
    async def on_mount(self) -> None:
        arr = [ListItem(Label(book["title"]), name=book["title"]) for book in super().app.library.books]
        await self.extend(arr)

    def on_list_view_highlighted(self, event: ListView.Highlighted):
        self.fill_the_form(event.item.name)

    def fill_the_form(self, title: str):
        form = super().app.query_one(Form)
        form.disabled = True
        book = next((book for book in super().app.library.books if book["title"] == title), None)
        form.old_title = book["title"]
        form.query_one("#title-input", Input).value = book["title"]
        form.query_one("#author-input", Input).value = book["author"]
        form.query_one("#release-year-input", Input).value = book["release_year"]
        form.query_one("#pages-input", Input).value = book["pages"]
        form.query_one(Button).label = "Edit"


class Form(Static):
    old_title: str

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Title", id="title-input")
        yield Input(placeholder="Author", id="author-input")
        yield Input(placeholder="Release Year", id="release-year-input")
        yield Input(placeholder="Pages", id="pages-input")
        yield Button("Edit", id="submit-button")

    async def on_button_pressed(self, event: Button.Pressed):
        title = self.query_one("#title-input", Input)
        author = self.query_one("#author-input", Input)
        release_year = self.query_one("#release-year-input", Input)
        pages = self.query_one("#pages-input", Input)

        book = {
            "title": title.value,
            "author": author.value,
            "release_year": release_year.value,
            "pages": pages.value
        }
        book_list = super().app.query_one(BookList)

        if event.button.label.plain == "Add":
            i = super().app.library.add_book(book)
            self.notify(message=f"{title.value} - {author.value}", title="Book added successfully!")
            await book_list.append(ListItem(Label(title.value), name=title.value))
            book_list.index = i
        else:
            i = super().app.library.edit_book(self.old_title, book)
            self.notify(message=f"{title.value} - {author.value}", title="Book edited successfully!")
            await book_list.remove_children()
            await book_list.on_mount()
            book_list.index = i

        title.value = ""
        author.value = ""
        release_year.value = ""
        pages.value = ""
        self.query_one(Button).label = "Add"
        
        self.disabled = True
        super().app.query_one(BookList).focus()
    
    def on_key(self, event: events.Key):
        if event.key == "escape":
            book_list = super().app.query_one(BookList)
            book_list.focus()
            button = self.query_one(Button)
            if button.label.plain == "Add":
                book_list.fill_the_form(self.old_title)
            self.disabled = True


class MyApp(App):
    CSS_PATH = "list_view.tcss"
    BINDINGS = [
        ("e", "edit_book", "Edit the book"), 
        ("d", "delete_book", "Delete the book"),
        ("a", "add_book", "Add a new book"),
        ("q", "quit", "Quit the application")
    ]

    def __init__(self) -> None:
        super().__init__()
        self.library = Library("books.txt")

    def compose(self) -> ComposeResult:
        yield BookList(classes="box")
        yield Form(classes="box", disabled=True)
        yield Footer()

    def action_edit_book(self):
        self.query_one(Form).disabled = False
        self.query_one("#title-input", Input).focus()
        self.query_one(Button).label = "Edit"

    def action_add_book(self):
        form = self.query_one(Form)
        form.query_one(Button).label = "Add"
        form.disabled = False
        self.query_one("#title-input", Input).value = ""
        self.query_one("#author-input", Input).value = ""
        self.query_one("#release-year-input", Input).value = ""
        self.query_one("#pages-input", Input).value = ""
        self.query_one("#title-input", Input).focus()

    # TODO add a confirmation dialog
    async def action_delete_book(self):
        title = self.query_one(Form).old_title
        self.library.remove_book(title)
        book_list = self.query_one(BookList)
        await book_list.remove_children()
        await book_list.on_mount()
        book_list.index = 0

    def action_quit(self):
        self.exit()


if __name__ == "__main__":
    MyApp().run()
