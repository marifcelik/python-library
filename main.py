class Library:
    def __init__(self, file_name: str) -> None:
        self.file = open(file_name, "a+")
        self.file.seek(0)
        self.__books: list[dict[str, str]] = []
        self.__parse_books()

    def __del__(self) -> None:
        self.file.close()

    def __parse_books(self):
        book_list = self.file.readlines()
        for line in book_list:
            book = line.split(",")
            self.__books.append({
                "title": book[0],
                "author": book[1],
                "release_year": book[2],
                "pages": book[3]
            })

    def add_book(self, title: str, author: str, release_year: str, pages: str) -> None:
        book = {
            "title": title,
            "author": author,
            "release_year": release_year,
            "pages": pages
        }
        try:
            self.file.write(f"{title},{author},{release_year},{pages}\n")
            self.file.flush()
            self.__books.append(book)
            print("Book added successfully!")
        except Exception as err:
            print(err)

    def remove_book(self, title: str) -> None:
        for book in self.__books:
            if book["title"] == title:
                self.__books.remove(book)
                break
        self.file.seek(0)
        self.file.truncate()
        for book in self.__books:
            self.file.write(f"{book['title']},{book['author']},{
                            book['release_year']},{book['pages']}\n")
        self.file.flush()
        print("Book removed successfully!")

    def list_books(self):
        for book in self.__books:
            print("---"+book["title"]+"---")
            print("Author: "+book["author"])
            print("Release Year: "+book["release_year"])
            print("Pages: "+book["pages"])

    @property
    def books(self) -> list[dict[str, str]]:
        return self.__books


def main():
    library = Library("books.txt")
    print("Welcome to the Library!")
    while True:
        print("1. List all books")
        print("2. Add a book")
        print("3. Remove a book")
        print("4. Exit")
        choice = int(input("Enter your choice: "))
        if choice == 1:
            library.list_books()
        elif choice == 2:
            title = input("Enter the title: ")
            author = input("Enter the author: ")
            release_year = input("Enter the release year: ")
            pages = input("Enter the number of pages: ")
            library.add_book(title, author, release_year, pages)
        elif choice == 3:
            title = input("Enter the title: ")
            library.remove_book(title)
        elif choice == 4:
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
